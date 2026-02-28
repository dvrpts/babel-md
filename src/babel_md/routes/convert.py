import json
import logging
from pathlib import PurePosixPath
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse, Response

from babel_md.converter import ALLOWED_EXTENSIONS, convert_document
from babel_md.models import ErrorResponse, OutputFormat

router = APIRouter(prefix="/v1")


@router.post(
    "/convert/file",
    responses={
        200: {
            "content": {
                "text/markdown": {},
                "application/json": {},
            }
        },
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def convert_file(
    file: UploadFile,
    output_format: Annotated[OutputFormat, Query()] = OutputFormat.markdown,
) -> Response:
    filename = file.filename or "upload"
    path = PurePosixPath(filename)
    suffix = path.suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    file_content = await file.read()

    try:
        content = convert_document(file_content, filename, output_format)
    except Exception as exc:
        logging.exception("Conversion failed for %s", filename)
        raise HTTPException(
            status_code=500,
            detail=f"Conversion failed: {exc}",
        ) from exc

    stem = path.stem

    if output_format == OutputFormat.json:
        body = json.dumps(content, ensure_ascii=False, indent=2)
        return Response(
            content=body,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{stem}.json"'},
        )

    return PlainTextResponse(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{stem}.md"'},
    )
