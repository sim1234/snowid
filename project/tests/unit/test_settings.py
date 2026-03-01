"""Unit tests for settings module (KeyBinds, load_key_binds, save_key_binds)."""

import json
import os
import tempfile

import sdl2
from settings import KeyBinds, load_key_binds, save_key_binds


class TestKeyBinds:
    def test_defaults_match_sdlk_constants(self) -> None:
        binds = KeyBinds()
        assert binds.jump == sdl2.SDLK_w
        assert binds.move_left == sdl2.SDLK_a
        assert binds.move_right == sdl2.SDLK_d
        assert binds.shoot == sdl2.SDLK_e
        assert binds.console == sdl2.SDLK_F1
        assert binds.toggle_fps == sdl2.SDLK_F3
        assert binds.switch_scene == sdl2.SDLK_F2

    def test_get_returns_attribute_for_valid_action(self) -> None:
        binds = KeyBinds()
        assert binds.get("jump") == sdl2.SDLK_w
        assert binds.get("console") == sdl2.SDLK_F1

    def test_get_returns_zero_for_unknown_action(self) -> None:
        binds = KeyBinds()
        assert binds.get("nonexistent") == 0

    def test_to_dict_contains_all_actions_in_order(self) -> None:
        binds = KeyBinds()
        d = binds.to_dict()
        assert list(d.keys()) == KeyBinds.ACTION_ORDER
        assert d["jump"] == sdl2.SDLK_w
        assert d["move_left"] == sdl2.SDLK_a

    def test_update_from_dict_updates_only_given_actions(self) -> None:
        binds = KeyBinds()
        new_key = 999
        binds.update_from_dict({"jump": new_key})
        assert binds.jump == new_key
        assert binds.move_left == sdl2.SDLK_a

    def test_update_from_dict_ignores_unknown_keys(self) -> None:
        binds = KeyBinds()
        binds.update_from_dict({"unknown_action": 123, "jump": 456})
        assert binds.jump == 456
        assert getattr(binds, "unknown_action", None) is None


class TestLoadKeyBinds:
    def test_missing_file_returns_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "nonexistent.json")
            result = load_key_binds(path=path)
        assert isinstance(result, KeyBinds)
        assert result.jump == sdl2.SDLK_w

    def test_invalid_json_returns_defaults(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json {")
            path = f.name
        try:
            result = load_key_binds(path=path)
            assert isinstance(result, KeyBinds)
            assert result.jump == sdl2.SDLK_w
        finally:
            os.unlink(path)

    def test_valid_file_returns_parsed_binds(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"jump": 100, "move_left": 200}, f)
            path = f.name
        try:
            result = load_key_binds(path=path)
            assert result.jump == 100
            assert result.move_left == 200
            assert result.move_right == sdl2.SDLK_d
        finally:
            os.unlink(path)

    def test_partial_file_fills_missing_with_defaults(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"jump": 42}, f)
            path = f.name
        try:
            result = load_key_binds(path=path)
            assert result.jump == 42
            assert result.move_left == sdl2.SDLK_a
        finally:
            os.unlink(path)

    def test_non_int_values_ignored_use_default(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"jump": "not_an_int", "move_left": 200}, f)
            path = f.name
        try:
            result = load_key_binds(path=path)
            assert result.jump == sdl2.SDLK_w
            assert result.move_left == 200
        finally:
            os.unlink(path)


class TestSaveKeyBinds:
    def test_save_key_binds_instance_writes_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "key_binds.json")
            binds = KeyBinds()
            binds.jump = 111
            save_key_binds(binds, path=path)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            assert data["jump"] == 111
            assert "move_left" in data

    def test_save_dict_writes_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "key_binds.json")
            save_key_binds({"jump": 222, "move_left": 333}, path=path)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            assert data["jump"] == 222
            assert data["move_left"] == 333

    def test_round_trip_restores_binds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "key_binds.json")
            original = KeyBinds()
            original.jump = 100
            original.console = 200
            save_key_binds(original, path=path)
            loaded = load_key_binds(path=path)
            assert loaded.jump == 100
            assert loaded.console == 200
            assert loaded.to_dict() == original.to_dict()

    def test_save_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "subdir", "nested", "key_binds.json")
            save_key_binds(KeyBinds(), path=path)
            assert os.path.isfile(path)
            with open(path, encoding="utf-8") as f:
                json.load(f)
