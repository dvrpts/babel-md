from unittest.mock import MagicMock, patch

from babel_md.converter import ALLOWED_EXTENSIONS, get_converter
from babel_md.models import OutputFormat


class TestAllowedExtensions:
    def test_pdf_allowed(self):
        assert ".pdf" in ALLOWED_EXTENSIONS

    def test_docx_allowed(self):
        assert ".docx" in ALLOWED_EXTENSIONS

    def test_pptx_allowed(self):
        assert ".pptx" in ALLOWED_EXTENSIONS

    def test_txt_not_allowed(self):
        assert ".txt" not in ALLOWED_EXTENSIONS


class TestGetConverter:
    def test_returns_singleton(self):
        get_converter.cache_clear()
        with patch("babel_md.converter.DocumentConverter") as mock_cls:
            mock_cls.return_value = MagicMock()
            c1 = get_converter()
            c2 = get_converter()
        assert c1 is c2
        mock_cls.assert_called_once()
        get_converter.cache_clear()

    def test_enables_picture_description_with_api_key(self):
        get_converter.cache_clear()
        with (
            patch("babel_md.converter.settings") as mock_settings,
            patch("babel_md.converter.DocumentConverter") as mock_cls,
        ):
            mock_settings.gemini_api_key = "test-key"
            mock_settings.gemini_base_url = "https://example.com"
            mock_settings.gemini_model = "gemini-2.5-flash"
            mock_cls.return_value = MagicMock()
            get_converter()

        call_kwargs = mock_cls.call_args[1]
        pipeline_opts = call_kwargs["format_options"]["pdf"].pipeline_options
        assert pipeline_opts.do_picture_description is True
        get_converter.cache_clear()

    def test_disables_picture_description_without_api_key(self):
        get_converter.cache_clear()
        with (
            patch("babel_md.converter.settings") as mock_settings,
            patch("babel_md.converter.DocumentConverter") as mock_cls,
        ):
            mock_settings.gemini_api_key = ""
            mock_cls.return_value = MagicMock()
            get_converter()

        call_kwargs = mock_cls.call_args[1]
        pipeline_opts = call_kwargs["format_options"]["pdf"].pipeline_options
        assert pipeline_opts.do_picture_description is False
        get_converter.cache_clear()


class TestConvertDocument:
    def test_markdown_export(self):
        mock_result = MagicMock()
        mock_result.document.export_to_markdown.return_value = "# Title"
        mock_converter = MagicMock()
        mock_converter.convert.return_value = mock_result

        get_converter.cache_clear()
        with patch("babel_md.converter.DocumentConverter", return_value=mock_converter):
            from babel_md.converter import convert_document

            result = convert_document(b"fake pdf", "test.pdf", OutputFormat.markdown)

        assert result == "# Title"
        mock_result.document.export_to_markdown.assert_called_once()
        get_converter.cache_clear()

    def test_json_export(self):
        mock_result = MagicMock()
        mock_result.document.export_to_dict.return_value = {"key": "value"}
        mock_converter = MagicMock()
        mock_converter.convert.return_value = mock_result

        get_converter.cache_clear()
        with patch("babel_md.converter.DocumentConverter", return_value=mock_converter):
            from babel_md.converter import convert_document

            result = convert_document(b"fake pdf", "test.pdf", OutputFormat.json)

        assert result == {"key": "value"}
        mock_result.document.export_to_dict.assert_called_once()
        get_converter.cache_clear()
