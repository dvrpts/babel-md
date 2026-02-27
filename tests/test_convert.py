from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Patch the converter before importing the app so lifespan doesn't load ML models
with patch("babel_md.main.get_converter"):
    from babel_md.main import app

client = TestClient(app, raise_server_exceptions=False)


class TestFileValidation:
    def test_rejects_unsupported_extension(self):
        response = client.post(
            "/v1/convert/file",
            files={"file": ("test.txt", b"hello", "text/plain")},
        )
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]

    @pytest.mark.parametrize("ext", [".pdf", ".docx", ".pptx"])
    def test_accepts_supported_extensions(self, ext):
        with patch("babel_md.routes.convert.convert_document", return_value="# Hello"):
            response = client.post(
                "/v1/convert/file",
                files={
                    "file": (f"test{ext}", b"fake content", "application/octet-stream")
                },
            )
        assert response.status_code == 200


class TestConvertMarkdown:
    def test_returns_markdown_content(self):
        with patch(
            "babel_md.routes.convert.convert_document",
            return_value="# Title\n\nSome text",
        ):
            response = client.post(
                "/v1/convert/file",
                files={"file": ("doc.pdf", b"fake", "application/pdf")},
            )
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"
        assert response.text == "# Title\n\nSome text"

    def test_content_disposition_has_filename(self):
        with patch(
            "babel_md.routes.convert.convert_document",
            return_value="content",
        ):
            response = client.post(
                "/v1/convert/file",
                files={"file": ("report.pdf", b"fake", "application/pdf")},
            )
        assert 'filename="report.md"' in response.headers["content-disposition"]

    def test_default_format_is_markdown(self):
        with patch(
            "babel_md.routes.convert.convert_document",
            return_value="content",
        ) as mock:
            client.post(
                "/v1/convert/file",
                files={"file": ("doc.pdf", b"fake", "application/pdf")},
            )
        # output_format is the 3rd positional arg
        assert mock.call_args[0][2].value == "markdown"


class TestConvertJson:
    def test_returns_json_content(self):
        fake_dict = {"title": "Test", "pages": []}
        with patch(
            "babel_md.routes.convert.convert_document",
            return_value=fake_dict,
        ):
            response = client.post(
                "/v1/convert/file?output_format=json",
                files={"file": ("doc.pdf", b"fake", "application/pdf")},
            )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert response.json()["title"] == "Test"

    def test_json_content_disposition(self):
        with patch(
            "babel_md.routes.convert.convert_document",
            return_value={"key": "val"},
        ):
            response = client.post(
                "/v1/convert/file?output_format=json",
                files={"file": ("doc.pdf", b"fake", "application/pdf")},
            )
        assert 'filename="doc.json"' in response.headers["content-disposition"]


class TestConversionErrors:
    def test_conversion_failure_returns_500(self):
        with patch(
            "babel_md.routes.convert.convert_document",
            side_effect=RuntimeError("OCR failed"),
        ):
            response = client.post(
                "/v1/convert/file",
                files={"file": ("doc.pdf", b"fake", "application/pdf")},
            )
        assert response.status_code == 500
        assert "Conversion failed" in response.json()["detail"]
