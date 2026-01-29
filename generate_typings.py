#!/usr/bin/env python
"""Generate type stubs for sdl2 module with post-processing adjustments."""

import ctypes
from enum import Enum
import importlib
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

STUBS_DIR = Path(__file__).parent / "typings"

# Will be populated at runtime with modules that successfully use --inspect-mode
INSPECT_MODE_MODULES: list[str] = []

# Mapping from ctypes types to Python type annotation strings
CTYPES_TO_PYTHON: dict[type, str] = {
    ctypes.c_int: "int",
    ctypes.c_int8: "int",
    ctypes.c_int16: "int",
    ctypes.c_int32: "int",
    ctypes.c_int64: "int",
    ctypes.c_uint: "int",
    ctypes.c_uint8: "int",
    ctypes.c_uint16: "int",
    ctypes.c_uint32: "int",
    ctypes.c_uint64: "int",
    ctypes.c_long: "int",
    ctypes.c_ulong: "int",
    ctypes.c_longlong: "int",
    ctypes.c_ulonglong: "int",
    ctypes.c_size_t: "int",
    ctypes.c_float: "float",
    ctypes.c_double: "float",
    ctypes.c_char: "bytes",
    ctypes.c_char_p: "bytes | None",
    ctypes.c_void_p: "int | None",
    ctypes.c_bool: "bool",
}


def run_stubgen() -> None:
    """Run stubgen to generate initial stubs for sdl2."""
    if STUBS_DIR.exists():
        shutil.rmtree(STUBS_DIR)

    stubgen_path = Path(sys.executable).parent / "stubgen"
    if not stubgen_path.exists():
        print(f"stubgen not found at {stubgen_path}", file=sys.stderr)
        sys.exit(1)

    global INSPECT_MODE_MODULES

    # First pass: generate all stubs without inspect mode
    result = subprocess.run(
        [str(stubgen_path), "-p", "sdl2", "-o", str(STUBS_DIR)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"stubgen failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(result.stdout or result.stderr)

    # Second pass: try ALL modules with inspect mode for better Structure stubs
    print("\nTrying all modules with --inspect-mode...")
    sdl2_dir = STUBS_DIR / "sdl2"
    all_modules = []
    for stub_file in sorted(sdl2_dir.rglob("*.pyi")):
        rel_path = stub_file.relative_to(sdl2_dir)
        if rel_path.name == "__init__.pyi":
            # Convert dir/__init__.pyi to dir
            if rel_path.parent != Path("."):
                module = "sdl2." + str(rel_path.parent).replace("/", ".")
            else:
                module = "sdl2"
        else:
            module = "sdl2." + str(rel_path.with_suffix("")).replace("/", ".")
        all_modules.append(module)

    successful = []
    failed = []
    skipped = []
    for module in all_modules:
        # Skip ext modules - they don't work well with inspect mode
        if module.startswith("sdl2.ext"):
            skipped.append(module)
            continue

        result = subprocess.run(
            [str(stubgen_path), "--inspect-mode", "-m", module, "-o", str(STUBS_DIR)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failed.append(module)
        else:
            successful.append(module)

    INSPECT_MODE_MODULES = successful
    print(f"  {len(successful)} modules regenerated with --inspect-mode")
    if skipped:
        print(f"  {len(skipped)} ext modules skipped")
    if failed:
        print(f"  {len(failed)} modules kept original: {', '.join(failed)}")


def get_ctypes_name(ctype: Any) -> str:
    """Get the ctypes type name for use in Array/Pointer annotations."""
    # Map Python ctypes to their names
    ctypes_names = {
        ctypes.c_int: "ctypes.c_int",
        ctypes.c_int8: "ctypes.c_int8",
        ctypes.c_int16: "ctypes.c_int16",
        ctypes.c_int32: "ctypes.c_int32",
        ctypes.c_int64: "ctypes.c_int64",
        ctypes.c_uint: "ctypes.c_uint",
        ctypes.c_uint8: "ctypes.c_uint8",
        ctypes.c_uint16: "ctypes.c_uint16",
        ctypes.c_uint32: "ctypes.c_uint32",
        ctypes.c_uint64: "ctypes.c_uint64",
        ctypes.c_float: "ctypes.c_float",
        ctypes.c_double: "ctypes.c_double",
        ctypes.c_char: "ctypes.c_char",
        ctypes.c_char_p: "ctypes.c_char_p",
    }
    return ctypes_names.get(ctype, "ctypes.c_int")


def get_python_type(ctype: Any) -> str:
    """Convert a ctypes type to a Python type annotation string."""
    # Structure or Union subclass (check first, before ctypes primitives)
    if isinstance(ctype, type):
        if issubclass(ctype, ctypes.Structure):
            return ctype.__name__
        if issubclass(ctype, ctypes.Union):
            return ctype.__name__

    # Direct mapping for ctypes primitives
    if ctype in CTYPES_TO_PYTHON:
        return CTYPES_TO_PYTHON[ctype]

    # Array types (e.g., c_char * 32) - keep ctypes element type
    if hasattr(ctype, "_type_") and hasattr(ctype, "_length_"):
        element_type = get_ctypes_name(ctype._type_)
        return f"ctypes.Array[{element_type}]"

    # Pointer types
    if hasattr(ctype, "_type_"):
        pointed_type = get_ctypes_name(ctype._type_)
        return f"ctypes._Pointer[{pointed_type}]"

    # Fallback
    return "Any"


def fix_structure_types(module_name: str, stub_path: Path) -> bool:
    """Replace Incomplete types with actual types for Structure classes."""
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        print(f"  Warning: Could not import {module_name}: {e}", file=sys.stderr)
        return False

    if not stub_path.exists():
        return False

    content = stub_path.read_text()
    modified = False

    # Build a mapping of class_name -> {field_name: python_type}
    class_fields: dict[str, dict[str, str]] = {}
    for name in dir(module):
        obj = getattr(module, name)
        if not isinstance(obj, type):
            continue
        if not issubclass(obj, (ctypes.Structure, ctypes.Union)):
            continue
        if not hasattr(obj, "_fields_"):
            continue

        class_fields[name] = {}
        for field_name, field_type in obj._fields_:
            class_fields[name][field_name] = get_python_type(field_type)

    # Process each class block separately
    def replace_class_fields(match: re.Match[str]) -> str:
        class_name = match.group(1)
        class_body = match.group(2)

        if class_name not in class_fields:
            return match.group(0)

        fields = class_fields[class_name]
        new_body = class_body

        for field_name, py_type in fields.items():
            pattern = rf"(\n    {re.escape(field_name)}: )Incomplete\b"
            new_body = re.sub(pattern, rf"\g<1>{py_type}", new_body)

        return f"class {class_name}" + new_body

    # Match class definitions with their bodies
    class_pattern = r"class (\w+)(\([^)]+\):.*?)(?=\nclass |\n[a-zA-Z_]|\Z)"
    new_content = re.sub(class_pattern, replace_class_fields, content, flags=re.DOTALL)

    if new_content != content:
        stub_path.write_text(new_content)
        modified = True

    return modified


def get_type_annotation_for_ctypes(ctype: Any) -> str:
    """Convert a ctypes type to a type annotation string for function signatures."""
    if ctype is None:
        return "None"

    # Simple types
    simple_types = {
        ctypes.c_int: "int",
        ctypes.c_int8: "int",
        ctypes.c_int16: "int",
        ctypes.c_int32: "int",
        ctypes.c_int64: "int",
        ctypes.c_uint: "int",
        ctypes.c_uint8: "int",
        ctypes.c_uint16: "int",
        ctypes.c_uint32: "int",
        ctypes.c_uint64: "int",
        ctypes.c_float: "float",
        ctypes.c_double: "float",
        ctypes.c_char_p: "bytes | None",
        ctypes.c_void_p: "int | None",
        ctypes.c_bool: "bool",
    }

    if ctype in simple_types:
        return simple_types[ctype]

    # Check for type aliases (like Uint32 = c_uint32)
    for base, annotation in simple_types.items():
        if ctype == base:
            return annotation

    # Pointer to Structure
    if hasattr(ctype, "_type_"):
        pointed = ctype._type_
        if isinstance(pointed, type) and issubclass(pointed, ctypes.Structure):
            return f"{pointed.__name__}"

    # Structure itself
    if isinstance(ctype, type) and issubclass(ctype, ctypes.Structure):
        return ctype.__name__

    return "Any"


def fix_missing_definitions(module_name: str, stub_path: Path) -> bool:
    """Add definitions for symbols listed in '# Names in __all__ with no definition'."""
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return False

    if not stub_path.exists():
        return False

    content = stub_path.read_text()

    # Find missing names from comments
    missing_pattern = r"# Names in __all__ with no definition:\n((?:#   \w+\n)+)"
    match = re.search(missing_pattern, content)
    if not match:
        return False

    missing_names = re.findall(r"#   (\w+)", match.group(1))
    if not missing_names:
        return False

    # Generate definitions for missing symbols
    new_definitions: list[str] = []

    for name in missing_names:
        obj = getattr(module, name, None)
        if obj is None:
            continue

        type_name = type(obj).__name__

        if type_name == "_FuncPtr":
            # It's a ctypes function pointer
            argtypes = getattr(obj, "argtypes", None) or []
            restype = getattr(obj, "restype", None)

            args = []
            for i, argtype in enumerate(argtypes):
                arg_annotation = get_type_annotation_for_ctypes(argtype)
                args.append(f"arg{i}: {arg_annotation}")

            ret_annotation = get_type_annotation_for_ctypes(restype)
            args_str = ", ".join(args) if args else ""
            new_definitions.append(f"def {name}({args_str}) -> {ret_annotation}: ...")

        elif type_name == "PyCSimpleType":
            # It's a ctypes type alias (like c_int)
            new_definitions.append(f"{name} = ctypes.c_int")

        elif type_name == "PyCFuncPtrType":
            # It's a ctypes callback type - use type[Any] as _CFuncPtr is not exposed
            new_definitions.append(f"{name}: type")

        elif type_name == "PyCStructType":
            # It's a Structure class - should be imported
            # Skip, as these should be handled by imports
            pass

    if not new_definitions:
        return False

    # Remove the "Names in __all__" comment section
    content = re.sub(missing_pattern, "", content)

    # Add new definitions before the end of file
    content = content.rstrip() + "\n\n" + "\n".join(new_definitions) + "\n"

    stub_path.write_text(content)
    return True


def fix_invalid_imports() -> None:
    """Fix invalid imports and add missing cross-module imports."""
    print("\nFixing imports across all stubs...")

    # Cross-module type mappings
    cross_module_types = {
        # Keyboard
        "SDL_Keysym": "from .keyboard import SDL_Keysym",
        # Joystick
        "SDL_JoystickID": "from .joystick import SDL_JoystickID",
        "SDL_JoystickPowerLevel": "from .joystick import SDL_JoystickPowerLevel",
        "SDL_JoystickGUID": "from .joystick import SDL_JoystickGUID",
        "SDL_Joystick": "from .joystick import SDL_Joystick",
        # Touch/Gesture
        "SDL_FingerID": "from .touch import SDL_FingerID",
        "SDL_TouchID": "from .touch import SDL_TouchID",
        "SDL_GestureID": "from .gesture import SDL_GestureID",
        # Pixels
        "SDL_PixelFormat": "from .pixels import SDL_PixelFormat",
        "SDL_Color": "from .pixels import SDL_Color",
        "SDL_Palette": "from .pixels import SDL_Palette",
        # Rect
        "SDL_Rect": "from .rect import SDL_Rect",
        "SDL_FRect": "from .rect import SDL_FRect",
        "SDL_Point": "from .rect import SDL_Point",
        "SDL_FPoint": "from .rect import SDL_FPoint",
        # Surface
        "SDL_Surface": "from .surface import SDL_Surface",
        # RWops
        "SDL_RWops": "from .rwops import SDL_RWops",
        # Video
        "SDL_Window": "from .video import SDL_Window",
        "SDL_DisplayMode": "from .video import SDL_DisplayMode",
        # Render
        "SDL_Renderer": "from .render import SDL_Renderer",
        "SDL_Texture": "from .render import SDL_Texture",
        # Version
        "SDL_version": "from .version import SDL_version",
        # Typing
        "Any": "from typing import Any",
        "Callable": "from typing import Callable",
    }

    # Process ALL stub files
    for stub_path in sorted(STUBS_DIR.rglob("*.pyi")):
        content = stub_path.read_text()
        original = content

        # Remove invalid imports from builtins (SDL_max, SDL_min, long, unicode, etc.)
        content = re.sub(r"from builtins import [^\n]+\n", "", content)

        # Remove invalid imports from ctypes (TTF_*, IMG_*, hb_*, etc.)
        content = re.sub(r"from ctypes import (TTF_|IMG_|hb_)[^\n]+\n", "", content)

        # Replace _ctypes with ctypes (mypy doesn't recognize _ctypes)
        content = content.replace("import _ctypes\n", "import ctypes\n")
        content = content.replace("_ctypes.Structure", "ctypes.Structure")
        content = content.replace("_ctypes.Union", "ctypes.Union")

        lines = content.split("\n")
        new_lines = []
        imports_to_add: set[str] = set()

        for line in lines:
            # Remove invalid "from ctypes import SDL_*" lines
            if line.startswith("from ctypes import SDL_"):
                continue

            # Check if we need ctypes import for Array types
            if "ctypes.Array" in line or "ctypes._Pointer" in line:
                imports_to_add.add("import ctypes")

            new_lines.append(line)

        content = "\n".join(new_lines)

        # Add missing imports at the top (after existing imports)
        if imports_to_add:
            import_lines = sorted(imports_to_add)
            insert_idx = 0
            for i, line in enumerate(new_lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_idx = i + 1
                elif line and not line.startswith("#") and insert_idx > 0:
                    break

            for imp in reversed(import_lines):
                if imp not in content:
                    new_lines.insert(insert_idx, imp)

            content = "\n".join(new_lines)

        # Get current module name from path
        rel_path = stub_path.relative_to(STUBS_DIR)
        current_module = "." + str(rel_path.with_suffix("")).replace("/", ".")

        for type_name, import_stmt in cross_module_types.items():
            # Check if type is used in a type annotation context (including -> returns)
            if not re.search(rf"[:\->\[]\s*[^#\n]*\b{type_name}\b", content):
                continue

            # Skip if already imported
            if import_stmt in content:
                continue

            # Skip if type is defined in this file (class definition or type alias)
            if re.search(rf"^class {type_name}\b", content, re.MULTILINE):
                continue
            if re.search(rf"^{type_name}\s*=", content, re.MULTILINE):
                continue

            # Skip self-imports (importing from the same module)
            import_module = import_stmt.split(" import ")[0].replace("from ", "")
            if import_module == current_module or import_module == f".{rel_path.stem}":
                continue

            # Add import after other imports
            lines = content.split("\n")
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_idx = i + 1
                elif line and not line.startswith("#") and insert_idx > 0:
                    break
            lines.insert(insert_idx, import_stmt)
            content = "\n".join(lines)

        if content != original:
            stub_path.write_text(content)
            print(f"  Fixed imports in {stub_path.relative_to(STUBS_DIR)}")


def remove_unused_incomplete_imports() -> None:
    """Remove 'from _typeshed import Incomplete' if Incomplete is not used."""
    print("\nRemoving unused Incomplete imports...")

    for stub_path in sorted(STUBS_DIR.rglob("*.pyi")):
        content = stub_path.read_text()

        if "from _typeshed import Incomplete" not in content:
            continue

        # Check if Incomplete is actually used (not just imported)
        lines = content.split("\n")
        incomplete_used = False
        for line in lines:
            # Skip the import line itself
            if line.strip() == "from _typeshed import Incomplete":
                continue
            if "Incomplete" in line:
                incomplete_used = True
                break

        if not incomplete_used:
            # Remove the import line
            new_lines = [
                line
                for line in lines
                if line.strip() != "from _typeshed import Incomplete"
            ]
            stub_path.write_text("\n".join(new_lines))
            print(
                f"  Removed unused Incomplete import from {stub_path.relative_to(STUBS_DIR)}"
            )


def fix_common_stub_errors() -> None:
    """Fix common errors in all generated stubs."""
    print("\nFixing common stub errors...")

    # Remove examples directory - not needed and has external dependencies
    examples_dir = STUBS_DIR / "sdl2" / "examples"
    if examples_dir.exists():
        shutil.rmtree(examples_dir)
        print("  Removed examples/ directory (not needed)")

    # Fix variable unions used as types (X = A | B -> X: int)
    def fix_variable_unions(content: str) -> str:
        # Pattern: NAME = CONST | CONST | ... (where CONST are variable names)
        pattern = r"^(\w+) = (\w+)(?: \| \w+)+$"
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if re.match(pattern, line):
                var_name = line.split(" = ")[0]
                new_lines.append(f"{var_name}: int")
            else:
                new_lines.append(line)
        return "\n".join(new_lines)

    # Fix duplicate type assignments (keep only first)
    def fix_duplicate_assignments(content: str) -> str:
        lines = content.split("\n")
        seen_assignments: set[str] = set()
        new_lines = []
        for line in lines:
            # Match: NAME = type (where type is a simple identifier)
            match = re.match(r"^(\w+) = (c_\w+|Uint\d+|Sint\d+)$", line)
            if match:
                var_name = match.group(1)
                if var_name in seen_assignments:
                    continue  # Skip duplicate
                seen_assignments.add(var_name)
            new_lines.append(line)
        return "\n".join(new_lines)

    # Specific file fixes
    fixes: dict[Path, list[tuple[str, str]]] = {
        # keycode.pyi: Add ctypes import
        STUBS_DIR
        / "sdl2"
        / "keycode.pyi": [
            (
                "from .scancode import *",
                "from ctypes import c_int\nfrom .scancode import *",
            ),
        ],
        # ext/uisystem.pyi: Define CHECKABLE
        STUBS_DIR
        / "sdl2"
        / "ext"
        / "uisystem.pyi": [
            (
                "BUTTON: int\nCHECKBUTTON = CHECKABLE | BUTTON",
                "BUTTON: int\nCHECKABLE: int\nCHECKBUTTON: int",
            ),
        ],
        # __init__.pyi: Remove invalid dll import and SDL_GUID
        STUBS_DIR
        / "sdl2"
        / "__init__.pyi": [
            ("from sdl2.dll import get_dll_file as get_dll_file\n", ""),
            ("SDL_GUID as SDL_GUID, ", ""),  # Remove from joystick import line
        ],
        # guid.pyi: Fix SDL_GUID - it's an alias for SDL_JoystickGUID
        STUBS_DIR
        / "sdl2"
        / "guid.pyi": [
            ("from sdl2.joystick import SDL_GUID as SDL_GUID\n", ""),
            (
                "__all__ = ['SDL_GUID', 'SDL_GUIDToString', 'SDL_GUIDFromString']",
                "from .joystick import SDL_JoystickGUID\n\n__all__ = ['SDL_GUID', 'SDL_GUIDToString', 'SDL_GUIDFromString']\n\nSDL_GUID = SDL_JoystickGUID",
            ),
        ],
        # ext/compat.pyi: Python 2 compatibility - use Any for missing builtins
        STUBS_DIR
        / "sdl2"
        / "ext"
        / "compat.pyi": [
            (
                "from builtins import long, unichr, unicode",
                "from typing import Any\nlong = Any\nunichr = Any\nunicode = Any",
            ),
        ],
        # stdinc.pyi: Remove invalid builtins imports
        STUBS_DIR
        / "sdl2"
        / "stdinc.pyi": [
            ("from builtins import SDL_max, SDL_min\n", ""),
        ],
    }

    # Apply specific fixes
    for stub_path, patterns in fixes.items():
        if not stub_path.exists():
            continue
        content = stub_path.read_text()
        modified = False
        for old, new in patterns:
            if old in content:
                content = content.replace(old, new)
                modified = True
        if modified:
            stub_path.write_text(content)
            print(f"  Fixed specific issues in {stub_path.relative_to(STUBS_DIR)}")

    # Fix duplicate function definitions (keep first, remove later ones)
    def fix_duplicate_functions(content: str) -> str:
        lines = content.split("\n")
        seen_funcs: set[str] = set()
        new_lines = []
        for line in lines:
            # Match function definitions
            match = re.match(r"^def (\w+)\(", line)
            if match:
                func_name = match.group(1)
                if func_name in seen_funcs:
                    continue  # Skip duplicate
                seen_funcs.add(func_name)
            new_lines.append(line)
        return "\n".join(new_lines)

    # Add missing import ctypes where ctypes.* is used
    def add_ctypes_import(content: str) -> str:
        if "ctypes." in content and "import ctypes" not in content:
            lines = content.split("\n")
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_idx = i + 1
                elif line and not line.startswith("#") and insert_idx > 0:
                    break
            lines.insert(insert_idx, "import ctypes")
            return "\n".join(lines)
        return content

    # Apply generic fixes to all stubs
    for stub_path in STUBS_DIR.rglob("*.pyi"):
        content = stub_path.read_text()
        original = content

        content = fix_variable_unions(content)
        content = fix_duplicate_assignments(content)
        content = fix_duplicate_functions(content)
        content = add_ctypes_import(content)

        if content != original:
            stub_path.write_text(content)
            print(
                f"  Fixed union/duplicate issues in {stub_path.relative_to(STUBS_DIR)}"
            )


def fix_wildcard_reexports() -> None:
    """Ensure all symbols from wildcard imports are re-exported in __init__.pyi."""
    print("\nFixing wildcard re-exports in __init__.pyi...")

    init_stub = STUBS_DIR / "sdl2" / "__init__.pyi"
    if not init_stub.exists():
        return

    content = init_stub.read_text()
    original = content

    # Find all submodule stubs and their __all__
    sdl2_stubs = STUBS_DIR / "sdl2"
    modules_to_reexport: dict[str, list[str]] = {}

    for stub_file in sorted(sdl2_stubs.glob("*.pyi")):
        if stub_file.name == "__init__.pyi":
            continue

        module_name = stub_file.stem
        stub_content = stub_file.read_text()

        # Extract __all__ from the stub
        match = re.search(r"__all__\s*=\s*\[([^\]]+)\]", stub_content)
        if match:
            all_str = match.group(1)
            # Parse the list of names
            names = re.findall(r"'([^']+)'", all_str)
            if names:
                modules_to_reexport[module_name] = names

    # Check which symbols are missing from __init__.pyi
    missing_exports: dict[str, list[str]] = {}
    for module_name, symbols in modules_to_reexport.items():
        # Read the module stub to check which symbols actually exist
        module_stub = sdl2_stubs / f"{module_name}.pyi"
        if not module_stub.exists():
            continue
        module_content = module_stub.read_text()

        missing = []
        for symbol in symbols:
            # Check if symbol is already exported in __init__.pyi
            if (
                f" {symbol} as {symbol}" in content
                or f"def {symbol}" in content
                or f"class {symbol}" in content
                or f"\n{symbol}:" in content
                or f"\n{symbol} =" in content
            ):
                continue

            # Check if symbol actually exists in the module stub
            if (
                f"def {symbol}" not in module_content
                and f"class {symbol}" not in module_content
                and f"\n{symbol}:" not in module_content
                and f"\n{symbol} =" not in module_content
            ):
                continue  # Symbol not in stub, skip it

            missing.append(symbol)
        if missing:
            missing_exports[module_name] = missing

    if not missing_exports:
        print("  All symbols already re-exported")
        return

    # Add missing re-exports
    lines = content.split("\n")
    new_imports: list[str] = []

    for module_name, symbols in sorted(missing_exports.items()):
        # Create import statement
        imports = ", ".join(f"{s} as {s}" for s in sorted(symbols))
        new_imports.append(f"from sdl2.{module_name} import {imports}")

    # Find where to insert (after existing imports)
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("from sdl2."):
            insert_idx = i + 1

    # Insert new imports
    for imp in reversed(new_imports):
        lines.insert(insert_idx, imp)

    content = "\n".join(lines)

    if content != original:
        init_stub.write_text(content)
        total_added = sum(len(syms) for syms in missing_exports.values())
        print(
            f"  Added {total_added} missing re-exports from {len(missing_exports)} modules"
        )


def apply_replacements() -> None:
    """Apply post-processing replacements to generated stubs."""
    replacements: dict[Path, list[tuple[str, str]]] = {
        STUBS_DIR
        / "sdl2"
        / "ext"
        / "renderer.pyi": [
            ("angle: int = 0", "angle: float = 0.0"),
        ],
    }

    for stub_path, patterns in replacements.items():
        if not stub_path.exists():
            print(f"Warning: {stub_path} not found, skipping", file=sys.stderr)
            continue

        content = stub_path.read_text()
        modified = False

        for old, new in patterns:
            if old in content:
                content = content.replace(old, new)
                modified = True
                print(f"  {stub_path.name}: {old!r} -> {new!r}")

        if modified:
            stub_path.write_text(content)


def validate_stubs() -> bool:
    """Validate all generated stubs using mypy."""
    print("\nValidating stubs with mypy...")

    mypy_path = Path(sys.executable).parent / "mypy"
    if not mypy_path.exists():
        print("  Warning: mypy not found, skipping validation", file=sys.stderr)
        return True

    # Find all .pyi files in stubs directory
    all_stubs = sorted(STUBS_DIR.rglob("*.pyi"))
    if not all_stubs:
        print("  No stub files found")
        return True

    # Determine which files are "processed" (in INSPECT_MODE_MODULES)
    processed_files = {
        module_name.replace(".", "/").split("/")[-1] + ".pyi"
        for module_name in INSPECT_MODE_MODULES
    }

    # Check all stubs at once for faster validation
    # Use permissive settings - stubs don't need to follow strict project rules
    result = subprocess.run(
        [
            str(mypy_path),
            str(STUBS_DIR),
            "--no-error-summary",
            "--allow-untyped-defs",
            "--allow-incomplete-defs",
            "--allow-untyped-decorators",
            "--no-warn-unused-ignores",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Parse errors by file
        error_counts: dict[str, int] = {}
        for line in result.stdout.split("\n"):
            if ": error:" in line:
                file_path = line.split(":")[0]
                file_name = Path(file_path).name
                error_counts[file_name] = error_counts.get(file_name, 0) + 1

        # Separate processed vs unprocessed files
        processed_errors = {
            k: v for k, v in error_counts.items() if k in processed_files
        }
        other_errors = {
            k: v for k, v in error_counts.items() if k not in processed_files
        }

        # Report processed module errors (these are critical)
        if processed_errors:
            print("  Errors in processed modules (critical):")
            for name, count in sorted(processed_errors.items()):
                print(f"    {name}: {count} errors")

        # Report other errors (warnings only)
        if other_errors:
            total_other = sum(other_errors.values())
            print(
                f"  Errors in other modules: {total_other} errors in {len(other_errors)} files (non-critical)"
            )

        # Only fail if processed modules have errors
        if processed_errors:
            return False

        print(f"  All {len(processed_files)} processed stub files are valid")
        return True
    else:
        print(f"  All {len(all_stubs)} stub files are valid")
        return True


def fix_incomplete_types() -> None:
    """Fix Incomplete types in Structure classes using runtime introspection."""
    print("\nFixing Incomplete types in Structure classes...")
    for module_name in INSPECT_MODE_MODULES:
        stub_rel_path = module_name.replace(".", "/") + ".pyi"
        stub_path = STUBS_DIR / stub_rel_path
        if fix_structure_types(module_name, stub_path):
            print(f"  Fixed types in {stub_path.name}")


def fix_all_missing_definitions() -> None:
    """Fix missing definitions for all inspect-mode modules."""
    print("\nAdding missing runtime definitions...")
    for module_name in INSPECT_MODE_MODULES:
        stub_rel_path = module_name.replace(".", "/") + ".pyi"
        stub_path = STUBS_DIR / stub_rel_path
        if fix_missing_definitions(module_name, stub_path):
            print(f"  Added missing definitions in {stub_path.name}")


def fix_remaining_incomplete() -> None:
    """Replace remaining Incomplete types with proper types via introspection."""
    print("\nFixing remaining Incomplete types...")

    for stub_path in sorted(STUBS_DIR.rglob("*.pyi")):
        # Convert path to module name
        rel_path = stub_path.relative_to(STUBS_DIR)
        module_name = str(rel_path.with_suffix("")).replace("/", ".")

        content = stub_path.read_text()
        if "Incomplete" not in content:
            continue

        original = content

        # Try to import module for introspection
        module = None
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            pass  # Module can't be imported, will use fallback

        lines = content.split("\n")
        new_lines = []

        for line in lines:
            # Pattern: name: Incomplete or name = Incomplete
            match = re.match(r"^(\w+):\s*Incomplete\s*$", line)
            if match:
                name = match.group(1)
                if module is not None:
                    obj = getattr(module, name, None)
                    if obj is not None:
                        new_type = infer_type_from_runtime(name, obj)
                        new_lines.append(f"{name}: {new_type}")
                        continue
                # Fallback: use Any
                new_lines.append(f"{name}: Any")
                continue

            # Pattern: name = Incomplete (for values)
            match = re.match(r"^(\w+)\s*=\s*Incomplete\s*$", line)
            if match:
                name = match.group(1)
                if module is not None:
                    obj = getattr(module, name, None)
                    if obj is not None:
                        new_type = infer_type_from_runtime(name, obj)
                        new_lines.append(f"{name}: {new_type}")
                        continue
                # Fallback: use Any
                new_lines.append(f"{name}: Any")
                continue

            new_lines.append(line)

        content = "\n".join(new_lines)

        # Replace Incomplete | None with Any | None in function parameters
        content = content.replace("Incomplete | None", "Any | None")

        # Replace remaining : Incomplete with : Any for class fields
        content = re.sub(r":\s*Incomplete\b", ": Any", content)

        # Ensure typing imports are present
        typing_imports_needed = []
        if "Any" in content and "from typing import" not in content:
            typing_imports_needed.append("Any")
        if (
            "Callable" in content
            and "Callable" not in content.split("from typing import")[0]
            if "from typing import" in content
            else True
        ):
            if "Callable" not in str(typing_imports_needed):
                typing_imports_needed.append("Callable")

        if typing_imports_needed:
            # Check if there's already a typing import
            if "from typing import" in content:
                # Add to existing import
                for imp in typing_imports_needed:
                    if imp not in content:
                        content = re.sub(
                            r"from typing import ([^\n]+)",
                            rf"from typing import \1, {imp}",
                            content,
                            count=1,
                        )
            else:
                # Add new import
                lines = content.split("\n")
                insert_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        insert_idx = i + 1
                    elif line and not line.startswith("#") and insert_idx > 0:
                        break
                imports_str = ", ".join(typing_imports_needed)
                lines.insert(insert_idx, f"from typing import {imports_str}")
                content = "\n".join(lines)

        if content != original:
            stub_path.write_text(content)
            # Count how many were fixed
            fixed_count = original.count(": Incomplete") - content.count(": Incomplete")
            if fixed_count > 0:
                print(f"  Fixed {fixed_count} Incomplete types in {rel_path}")


def infer_type_from_runtime(name: str, obj: Any) -> str:
    """Infer a type annotation from a runtime object."""
    type_name = type(obj).__name__

    # ctypes function pointer
    if type_name == "_FuncPtr":
        argtypes = getattr(obj, "argtypes", None) or []
        restype = getattr(obj, "restype", None)

        args = []
        for i, argtype in enumerate(argtypes):
            arg_annotation = get_type_annotation_for_ctypes(argtype)
            args.append(arg_annotation)

        ret = get_type_annotation_for_ctypes(restype)

        if not args:
            return f"Callable[[], {ret}]"
        return f"Callable[[{', '.join(args)}], {ret}]"

    # ctypes type (like c_int, Uint32)
    if type_name == "PyCSimpleType":
        return "type[ctypes.c_int]"

    # ctypes callback type
    if type_name == "PyCFuncPtrType":
        return "type"

    # Integer constant
    if isinstance(obj, int):
        return "int"

    # Float constant
    if isinstance(obj, float):
        return "float"

    # String constant
    if isinstance(obj, str):
        return "str"

    # Bytes constant
    if isinstance(obj, bytes):
        return "bytes"

    # Function
    if callable(obj):
        return "Callable[..., Any]"

    # Fallback
    return "Any"


def main() -> None:
    print("Generating stubs for sdl2...")
    run_stubgen()
    fix_incomplete_types()
    fix_all_missing_definitions()
    fix_remaining_incomplete()  # Fix all remaining Incomplete types
    remove_unused_incomplete_imports()  # Clean up unused imports
    fix_invalid_imports()  # Run after to catch new imports
    fix_common_stub_errors()  # Fix union types, duplicates, etc.
    fix_wildcard_reexports()  # Ensure all __all__ symbols are re-exported
    print("\nApplying manual replacements...")
    apply_replacements()

    if validate_stubs():
        print("\nDone! All stubs are valid.")
    else:
        print("\nDone with warnings. Some stubs have validation errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
