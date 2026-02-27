"""Tests for Paragraph and ScrollableParagraph components."""

from unittest.mock import MagicMock, patch

import pytest
from gamepart.gui.paragraph import Paragraph, ScrollableParagraph
from gamepart.gui.text import Text


class TestParagraph:
    def test_initialization(self) -> None:
        p = Paragraph(text="hello")
        assert p.text == "hello"
        assert p.line_spacing == 2
        assert p._text_cache == {}

    def test_initialization_with_line_spacing(self) -> None:
        p = Paragraph(text="hi", line_spacing=5)
        assert p.line_spacing == 5


class TestParagraphGetTexts:
    @pytest.fixture
    def mock_gui_system(self) -> MagicMock:
        system = MagicMock()
        system.font_manager.get_line_height.return_value = 17
        return system

    @pytest.fixture
    def paragraph_with_gui(self, mock_gui_system: MagicMock) -> Paragraph:
        p = Paragraph(text="line1\nline2")
        p.init_gui_system(mock_gui_system)
        return p

    def test_get_texts_returns_pairs_for_each_line(
        self, paragraph_with_gui: Paragraph
    ) -> None:
        with patch.object(
            Text,
            "get_rendered_text",
            return_value=MagicMock(size=(50, 17)),
        ):
            texts = paragraph_with_gui.get_texts()
        assert len(texts) == 2
        assert texts[0][1].text == "line1"
        assert texts[1][1].text == "line2"

    def test_get_texts_y_positions_increase(
        self, paragraph_with_gui: Paragraph
    ) -> None:
        with patch.object(
            Text,
            "get_rendered_text",
            return_value=MagicMock(size=(50, 17)),
        ):
            texts = paragraph_with_gui.get_texts()
        assert texts[0][0] == 0
        assert texts[1][0] == 17 + paragraph_with_gui.line_spacing

    def test_get_texts_empty_paragraph(self, mock_gui_system: MagicMock) -> None:
        p = Paragraph(text="")
        p.init_gui_system(mock_gui_system)
        texts = p.get_texts()
        assert len(texts) == 1
        assert texts[0][1].text == ""

    def test_get_texts_single_line(self, mock_gui_system: MagicMock) -> None:
        p = Paragraph(text="single")
        p.init_gui_system(mock_gui_system)
        with patch.object(
            Text,
            "get_rendered_text",
            return_value=MagicMock(size=(30, 17)),
        ):
            texts = p.get_texts()
        assert len(texts) == 1
        assert texts[0][1].text == "single"


class TestParagraphFitToText:
    @pytest.fixture
    def mock_gui_system(self) -> MagicMock:
        system = MagicMock()
        system.font_manager.get_line_height.return_value = 17
        return system

    def test_fit_to_text_sets_height_using_line_height(
        self, mock_gui_system: MagicMock
    ) -> None:
        p = Paragraph(text="a\nb\nc", line_spacing=2)
        p.init_gui_system(mock_gui_system)
        with patch.object(
            Text,
            "get_rendered_text",
            return_value=MagicMock(size=(10, 17)),
        ):
            p.fit_to_text()
        expected_height = 3 * 17 + 2 * 2
        assert p.height == expected_height


class TestScrollableParagraph:
    def test_initialization(self) -> None:
        sp = ScrollableParagraph(text="hello")
        assert sp.scroll_offset == 0.0
        assert sp.target_scroll_offset == 0.0
        assert sp.scroll_speed == 20
        assert sp.valign == "top"

    def test_initialization_valign_bottom(self) -> None:
        sp = ScrollableParagraph(text="hi", valign="bottom")
        assert sp.valign == "bottom"

    def test_scroll_offset_setter_clamps(self) -> None:
        sp = ScrollableParagraph(text="x", height=100)
        sp._get_content_height = lambda: 50
        sp.scroll_offset = 100
        assert sp.scroll_offset == 0.0

    def test_target_scroll_offset_setter_clamps(self) -> None:
        sp = ScrollableParagraph(text="x", height=100)
        sp._get_content_height = lambda: 50
        sp.target_scroll_offset = 100
        assert sp.target_scroll_offset == 0.0
