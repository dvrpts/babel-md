from functools import lru_cache
from io import BytesIO

from docling.datamodel.base_models import DocumentStream
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    PictureDescriptionApiOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

from babel_md.config import settings
from babel_md.models import OutputFormat

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx"}


@lru_cache(maxsize=1)
def get_converter() -> DocumentConverter:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.generate_picture_images = True
    pipeline_options.do_picture_description = bool(settings.gemini_api_key)
    pipeline_options.enable_remote_services = bool(settings.gemini_api_key)

    if settings.gemini_api_key:
        pipeline_options.picture_description_options = PictureDescriptionApiOptions(
            url=f"{settings.gemini_base_url}/chat/completions",
            params={"model": settings.gemini_model},
            headers={"Authorization": f"Bearer {settings.gemini_api_key}"},
        )

    return DocumentConverter(
        format_options={
            "pdf": PdfFormatOption(pipeline_options=pipeline_options),
        }
    )


def convert_document(
    file_content: bytes,
    filename: str,
    output_format: OutputFormat,
) -> str:
    converter = get_converter()
    source = DocumentStream(name=filename, stream=BytesIO(file_content))
    result = converter.convert(source)

    if output_format == OutputFormat.markdown:
        return result.document.export_to_markdown()
    return result.document.export_to_dict()
