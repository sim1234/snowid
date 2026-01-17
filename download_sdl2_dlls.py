#!/usr/bin/env python3
"""
Python script to download SDL2 DLLs for Windows
Downloads SDL2, SDL2_ttf, SDL2_gfx, and SDL2_image DLLs to the lib folder
Uses only Python standard library
"""

import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path


def download_file(url: str, dest_path: Path) -> None:
    """Download a file from URL to destination path."""
    print(f"  Downloading from {url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"  [OK] Downloaded to {dest_path.name}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise FileNotFoundError(f"URL not found (404): {url}\nThe version may not exist. Please check available versions.")
        raise


def find_dll_in_extracted(extracted_dir: Path, dll_name: str) -> Path | None:
    """Find a DLL file in the extracted directory, looking in x64 folders."""
    for dll_path in extracted_dir.rglob(dll_name):
        # Check if it's in an x64 or x86_64 directory
        if "x64" in str(dll_path) or "x86_64" in str(dll_path):
            return dll_path
    # If not found in x64, try any location
    for dll_path in extracted_dir.rglob(dll_name):
        return dll_path
    return None


def download_and_extract_dll(
    url: str,
    dll_name: str,
    lib_dir: Path,
    temp_dir: Path,
    component_name: str,
    optional: bool = False,
) -> None:
    """Download a zip file, extract it, and copy the DLL to lib directory."""
    print(f"Downloading {component_name}...")
    
    try:
        # Download zip file
        zip_path = temp_dir / f"{component_name}.zip"
        download_file(url, zip_path)
        
        # Extract zip file
        extract_dir = temp_dir / component_name
        extract_dir.mkdir(exist_ok=True)
        print(f"  Extracting {zip_path.name}...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the DLL
        dll_path = find_dll_in_extracted(extract_dir, dll_name)
        if dll_path:
            dest_path = lib_dir / dll_name
            shutil.copy2(dll_path, dest_path)
            print(f"  [OK] Copied {dll_name}")
            
            # For SDL2_image, also copy dependency DLLs from the same directory
            if component_name == "SDL2_image":
                dll_dir = dll_path.parent
                for dep_dll in dll_dir.glob("*.dll"):
                    if dep_dll.name != dll_name:
                        dep_dest = lib_dir / dep_dll.name
                        shutil.copy2(dep_dll, dep_dest)
                        print(f"  [OK] Copied {dep_dll.name}")
        else:
            error_msg = f"  [FAIL] Could not find {dll_name} in x64 folder"
            if optional:
                print(f"  [WARN] {error_msg} - skipping (optional component)")
            else:
                print(error_msg)
                sys.exit(1)
    except (FileNotFoundError, urllib.error.HTTPError) as e:
        if optional:
            print(f"  [WARN] Failed to download {component_name}: {e} - skipping (optional component)")
        else:
            print(f"  [ERROR] Failed to download {component_name}: {e}")
            sys.exit(1)


def main() -> None:
    """Main function to download all SDL2 DLLs."""
    lib_dir = Path("lib")
    lib_dir.mkdir(exist_ok=True)
    
    print("Downloading SDL2 DLLs to lib folder...")
    print()
    
    # SDL2 versions
    sdl2_version = "2.30.5"
    sdl2_url = f"https://github.com/libsdl-org/SDL/releases/download/release-{sdl2_version}/SDL2-devel-{sdl2_version}-VC.zip"
    
    sdl2ttf_version = "2.22.0"
    sdl2ttf_url = f"https://github.com/libsdl-org/SDL_ttf/releases/download/release-{sdl2ttf_version}/SDL2_ttf-devel-{sdl2ttf_version}-VC.zip"
    
    sdl2gfx_version = "1.0.4"
    # SDL2_gfx from giroletm fork (official libsdl-org doesn't have VC builds for this version)
    sdl2gfx_url = f"https://github.com/giroletm/SDL2_gfx/releases/download/release-{sdl2gfx_version}/SDL2_gfx-{sdl2gfx_version}-win32-x64.zip"
    
    sdl2image_version = "2.8.2"
    sdl2image_url = f"https://github.com/libsdl-org/SDL_image/releases/download/release-{sdl2image_version}/SDL2_image-devel-{sdl2image_version}-VC.zip"
    
    # Create temporary directory
    with tempfile.TemporaryDirectory(prefix="sdl2_dlls_") as temp_dir:
        temp_path = Path(temp_dir)
        
        try:
            # Download and extract SDL2
            download_and_extract_dll(
                sdl2_url, "SDL2.dll", lib_dir, temp_path, "SDL2"
            )
            
            # Download and extract SDL2_ttf
            download_and_extract_dll(
                sdl2ttf_url, "SDL2_ttf.dll", lib_dir, temp_path, "SDL2_ttf"
            )
            
            # Download and extract SDL2_gfx (always overwrite)
            # Using giroletm fork which has VC builds
            download_and_extract_dll(
                sdl2gfx_url, "SDL2_gfx.dll", lib_dir, temp_path, "SDL2_gfx"
            )
            
            # Download and extract SDL2_image
            download_and_extract_dll(
                sdl2image_url, "SDL2_image.dll", lib_dir, temp_path, "SDL2_image"
            )
            
            print()
            print("[OK] Download complete! DLLs are in the lib folder:")
            for dll_file in sorted(lib_dir.glob("*.dll")):
                size = dll_file.stat().st_size
                size_mb = size / (1024 * 1024)
                print(f"  - {dll_file.name} ({size_mb:.2f} MB)")
                
        except Exception as e:
            print(f"[ERROR] Error downloading DLLs: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
