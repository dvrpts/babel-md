from functools import lru_cache
from io import BytesIO
from typing import Any

from docling.datamodel.base_models import DocumentStream
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    PictureDescriptionApiOptions,
    TableFormerMode,
    TableStructureOptions,
)
from docling.document_converter import DocumentConverter

from babel_md.config import settings
from babel_md.models import OutputFormat

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx"}


@lru_cache(maxsize=1)
def get_converter() -> DocumentConverter:
    converter = DocumentConverter()
    has_api_key = bool(settings.gemini_api_key)

    for opt in converter.format_to_options.values():
        opts = opt.pipeline_options
        if not isinstance(opts, PdfPipelineOptions):
            continue

        opts.do_picture_classification = True
        opts.do_chart_extraction = True
        opts.generate_picture_images = True
        opts.table_structure_options = TableStructureOptions(
            do_cell_matching=True,
            mode=TableFormerMode.ACCURATE,
        )
        opts.ocr_options.lang = ["ko", "en"]

        if has_api_key:
            opts.do_picture_description = True
            opts.enable_remote_services = True
            opts.picture_description_options = PictureDescriptionApiOptions(
                url=f"{settings.gemini_base_url}/chat/completions",
                params={"model": settings.gemini_model},
                headers={"Authorization": f"Bearer {settings.gemini_api_key}"},
            )

    return converter


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
