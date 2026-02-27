from functools import lru_cache
from io import BytesIO
from typing import Any

from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.datamodel.pipeline_options import (
    ConvertPipelineOptions,
    PdfPipelineOptions,
    PictureDescriptionApiOptions,
)
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    PowerpointFormatOption,
    WordFormatOption,
)

from babel_md.config import settings
from babel_md.models import OutputFormat

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx"}


def _gemini_description_options() -> PictureDescriptionApiOptions:
    return PictureDescriptionApiOptions(
        url=f"{settings.gemini_base_url}/chat/completions",
        params={"model": settings.gemini_model},
        headers={"Authorization": f"Bearer {settings.gemini_api_key}"},
    )


@lru_cache(maxsize=1)
def get_converter() -> DocumentConverter:
    has_api_key = bool(settings.gemini_api_key)

    pdf_options = PdfPipelineOptions()
    pdf_options.generate_picture_images = True
    pdf_options.do_picture_description = has_api_key
    pdf_options.enable_remote_services = has_api_key

    doc_options = ConvertPipelineOptions()
    doc_options.do_picture_description = has_api_key
    doc_options.enable_remote_services = has_api_key

    if has_api_key:
        api_opts = _gemini_description_options()
        pdf_options.picture_description_options = api_opts
        doc_options.picture_description_options = api_opts

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
            InputFormat.PPTX: PowerpointFormatOption(pipeline_options=doc_options),
            InputFormat.DOCX: WordFormatOption(pipeline_options=doc_options),
        }
    )


def convert_document(
    file_content: bytes,
    filename: str,
    output_format: OutputFormat,
) -> str | dict[str, Any]:
    converter = get_converter()
    source = DocumentStream(name=filename, stream=BytesIO(file_content))
    result = converter.convert(source)

    if output_format == OutputFormat.markdown:
        return result.document.export_to_markdown()
    return result.document.export_to_dict()
