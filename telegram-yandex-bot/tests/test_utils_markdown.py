"""
Тесты для модуля утилит markdown.
"""
import pytest
import sys
import os

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from utils.markdown import escape_markdown_v2, escape_markdown_v2_keep, transform_to_markdown_v2


@pytest.mark.utils
class TestMarkdownUtils:
    """Тесты для утилит работы с Markdown"""

    def test_escape_markdown_v2_basic(self):
        """Тест базового экранирования MarkdownV2"""
        text = "Hello_world [test] (parentheses) *bold*"
        result = escape_markdown_v2(text)
        expected = "Hello\\_world \\[test\\] \\(parentheses\\) \\*bold\\*"
        assert result == expected

    def test_escape_markdown_v2_empty_string(self):
        """Тест экранирования пустой строки"""
        assert escape_markdown_v2("") == ""
        assert escape_markdown_v2(None) == ""

    def test_escape_markdown_v2_special_characters(self):
        """Тест экранирования специальных символов"""
        text = "_*[]()~`>#+-=|{}.!"
        result = escape_markdown_v2(text)
        expected = "\\_\\*\\[\\]\\(\\)\\~\\`\\>\\#\\+\\-\\=\\|\\{\\}\\.\\!"
        assert result == expected

    def test_escape_markdown_v2_backslash(self):
        """Тест экранирования обратных слешей"""
        text = "test\\backslash"
        result = escape_markdown_v2(text)
        expected = "test\\\\backslash"
        assert result == expected

    def test_escape_markdown_v2_keep_basic(self):
        """Тест экранирования с сохранением базовых символов форматирования"""
        text = "Hello_world [test] *bold* _italic_ `code`"
        result = escape_markdown_v2_keep(text, keep=("*", "_", "`"))
        expected = "Hello\\_world \\[test\\] *bold* _italic_ `code`"
        assert result == expected

    def test_escape_markdown_v2_keep_custom(self):
        """Тест экранирования с сохранением пользовательских символов"""
        text = "Hello_world [test] (parentheses)"
        result = escape_markdown_v2_keep(text, keep=("_", "("))
        expected = "Hello_world \\[test\\] (parentheses)"
        assert result == expected

    def test_escape_markdown_v2_keep_empty(self):
        """Тест экранирования с пустым списком сохраняемых символов"""
        text = "Hello_world [test] *bold*"
        result = escape_markdown_v2_keep(text, keep=())
        expected = "Hello\\_world \\[test\\] \\*bold\\*"
        assert result == expected

    def test_transform_to_markdown_v2_bold(self):
        """Тест преобразования жирного текста"""
        text = "**bold text**"
        result = transform_to_markdown_v2(text)
        expected = "*bold text*"
        assert result == expected

    def test_transform_to_markdown_v2_italic(self):
        """Тест преобразования курсива"""
        text = "__italic text__"
        result = transform_to_markdown_v2(text)
        expected = "_italic text_"
        assert result == expected

    def test_transform_to_markdown_v2_mixed_formatting(self):
        """Тест смешанного форматирования"""
        text = "**bold** and __italic__ text"
        result = transform_to_markdown_v2(text)
        expected = "*bold* and _italic_ text"
        assert result == expected

    def test_transform_to_markdown_v2_lists(self):
        """Тест преобразования списков"""
        text = "- First item\n* Second item\n- Third item"
        result = transform_to_markdown_v2(text)
        expected = "• First item\n• Second item\n• Third item"
        assert result == expected

    def test_transform_to_markdown_v2_lists_with_indentation(self):
        """Тест преобразования списков с отступами"""
        text = "  - Indented item\n    * Another indented item"
        result = transform_to_markdown_v2(text)
        expected = "  • Indented item\n    • Another indented item"
        assert result == expected

    def test_transform_to_markdown_v2_complex_text(self):
        """Тест сложного текста с различными элементами"""
        text = "**Bold** and __italic__ text with - list item and * another item"
        result = transform_to_markdown_v2(text)
        expected = "*Bold* and _italic_ text with • list item and • another item"
        assert result == expected

    def test_transform_to_markdown_v2_special_characters(self):
        """Тест преобразования с специальными символами"""
        text = "Text with [brackets] and (parentheses) and _underscores_"
        result = transform_to_markdown_v2(text)
        expected = "Text with \\[brackets\\] and \\(parentheses\\) and _underscores_"
        assert result == expected

    def test_transform_to_markdown_v2_empty_string(self):
        """Тест преобразования пустой строки"""
        assert transform_to_markdown_v2("") == ""
        assert transform_to_markdown_v2(None) == ""

    def test_transform_to_markdown_v2_code_blocks(self):
        """Тест преобразования с блоками кода"""
        text = "Here is `inline code` and **bold text**"
        result = transform_to_markdown_v2(text)
        expected = "Here is `inline code` and *bold text*"
        assert result == expected

    def test_transform_to_markdown_v2_multiline_lists(self):
        """Тест многострочных списков"""
        text = """- First item
- Second item
  - Nested item
- Third item"""
        result = transform_to_markdown_v2(text)
        expected = """• First item
• Second item
  • Nested item
• Third item"""
        assert result == expected

    def test_transform_to_markdown_v2_preserve_formatting(self):
        """Тест сохранения форматирования"""
        text = "**Bold** _italic_ `code` text"
        result = transform_to_markdown_v2(text)
        expected = "*Bold* _italic_ `code` text"
        assert result == expected

    def test_transform_to_markdown_v2_escape_special_chars(self):
        """Тест экранирования специальных символов"""
        text = "Text with dots... and exclamation! and question?"
        result = transform_to_markdown_v2(text)
        expected = "Text with dots\\.\\.\\. and exclamation\\! and question\\?"
        assert result == expected

    def test_transform_to_markdown_v2_real_world_example(self):
        """Тест реального примера текста"""
        text = """**Привет!** Я бот с интеграцией GPT-5.

Доступные команды:
- /start - начать общение
- /help - помощь
- /ping - проверить работу

Просто отправьте сообщение, и я отвечу!"""
        
        result = transform_to_markdown_v2(text)
        expected = """*Привет\\!* Я бот с интеграцией GPT\\-5\\.

Доступные команды:
• /start \\- начать общение
• /help \\- помощь
• /ping \\- проверить работу

Просто отправьте сообщение, и я отвечу\\!"""
        assert result == expected

    def test_escape_markdown_v2_keep_all_special_chars(self):
        """Тест экранирования всех специальных символов"""
        special_chars = "_*[]()~`>#+-=|{}.!"
        result = escape_markdown_v2_keep(special_chars, keep=())
        expected = "\\_\\*\\[\\]\\(\\)\\~\\`\\>\\#\\+\\-\\=\\|\\{\\}\\.\\!"
        assert result == expected

    def test_escape_markdown_v2_keep_none(self):
        """Тест экранирования без сохранения символов"""
        text = "test_text"
        result = escape_markdown_v2_keep(text, keep=None)
        expected = "test\\_text"
        assert result == expected

