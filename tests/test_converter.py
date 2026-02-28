from unittest.mock import MagicMock, patch

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

from babel_md.converter import ALLOWED_EXTENSIONS, convert_document, get_converter
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
        with patch("babel_md.converter.DocumentConverter") as mock_cls:
            mock_cls.return_value = MagicMock()
            c1 = get_converter()
            c2 = get_converter()
        assert c1 is c2
        mock_cls.assert_called_once()

    def test_enables_picture_description_with_api_key(self):
        mock_pipeline_opts = MagicMock()
        mock_pipeline_opts.__class__ = PdfPipelineOptions
        mock_format_opt = MagicMock()
        mock_format_opt.pipeline_options = mock_pipeline_opts
        mock_converter = MagicMock()
        mock_converter.format_to_options = {InputFormat.PDF: mock_format_opt}

        with (
            patch("babel_md.converter.settings") as mock_settings,
            patch("babel_md.converter.DocumentConverter", return_value=mock_converter),
        ):
            mock_settings.gemini_api_key = "test-key"
            mock_settings.gemini_base_url = "https://example.com"
            mock_settings.gemini_model = "gemini-2.5-flash"
            get_converter()

        assert mock_pipeline_opts.do_picture_description is True
        assert mock_pipeline_opts.enable_remote_services is True

    def test_disables_picture_description_without_api_key(self):
        mock_converter = MagicMock()
        mock_converter.format_to_options = {}

        with (
            patch("babel_md.converter.settings") as mock_settings,
            patch("babel_md.converter.DocumentConverter", return_value=mock_converter),
        ):
            mock_settings.gemini_api_key = ""
            result = get_converter()

        assert result is mock_converter


class TestConvertDocument:
    def test_markdown_export(self):
        mock_result = MagicMock()
        mock_result.document.export_to_markdown.return_value = "# Title"
        mock_converter = MagicMock()
        mock_converter.convert.return_value = mock_result

        with patch("babel_md.converter.DocumentConverter", return_value=mock_converter):
            result = convert_document(b"fake pdf", "test.pdf", OutputFormat.markdown)

        assert result == "# Title"
        mock_result.document.export_to_markdown.assert_called_once()

    def test_json_export(self):
        mock_result = MagicMock()
        mock_result.document.export_to_dict.return_value = {"key": "value"}
        mock_converter = MagicMock()
        mock_converter.convert.return_value = mock_result

        with patch("babel_md.converter.DocumentConverter", return_value=mock_converter):
            result = convert_document(b"fake pdf", "test.pdf", OutputFormat.json)

        assert result == {"key": "value"}
        mock_result.document.export_to_dict.assert_called_once()
