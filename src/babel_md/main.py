from contextlib import asynccontextmanager

from fastapi import FastAPI

from babel_md.converter import get_converter
from babel_md.routes import convert, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_converter()  # warm up: load ML models at startup
    yield


app = FastAPI(
    title="babel-md",
    description="Convert PDF/DOCX/PPTX documents to Markdown/JSON",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(convert.router)
