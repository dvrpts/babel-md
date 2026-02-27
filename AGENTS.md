# babel-md

PDF/DOCX/PPTX/XLSX 문서를 Markdown/JSON으로 변환하는 셀프 호스팅 REST API.
Docling + FastAPI 기반. 이미지 설명은 Gemini API(OpenAI 호환)로 처리.

## 프로젝트 구조

```
src/babel_md/
├── main.py          # FastAPI 앱, lifespan으로 컨버터 웜업
├── config.py        # pydantic-settings, .env 자동 로드
├── converter.py     # DocumentConverter 싱글턴(@lru_cache), 변환 로직
├── models.py        # OutputFormat enum, HealthResponse, ErrorResponse
└── routes/
    ├── health.py    # GET /health
    └── convert.py   # POST /v1/convert/file
tests/
├── test_health.py
├── test_convert.py  # 라우트 테스트 (mock 기반)
└── test_converter.py # 컨버터 유닛테스트
```

## 기술 스택

- Python 3.12, uv (패키지 매니저)
- FastAPI + Uvicorn
- Docling (문서 변환 엔진, ML 모델 포함)
- Gemini 2.5 Flash (이미지 설명, GEMINI_API_KEY 없으면 비활성화)
- ruff (린팅/포매팅), pytest (테스트)

## 핵심 설계

- **컨버터 싱글턴**: `@lru_cache(maxsize=1)`로 ML 모델 재로딩 방지
- **Gemini 옵셔널**: API 키 없으면 이미지 설명만 비활성화, 나머지 정상 동작
- **응답 형식**: markdown이면 `text/markdown`, json이면 `application/json`으로 raw content 반환. `Content-Disposition` 헤더로 파일명 제공
- **파일 포맷 감지**: 확장자 기반 (DocumentStream)
- **이미지 설명**: Docling이 큰 이미지만 Gemini로 설명 생성 (picture_area_threshold=0.05). 본문 텍스트로 삽입됨 (alt text 아님)

## 환경변수

`.env` 파일 또는 환경변수로 설정.

| 변수 | 기본값 | 설명 |
|---|---|---|
| GEMINI_API_KEY | "" | 없으면 이미지 설명 비활성화 |
| GEMINI_MODEL | gemini-2.5-flash | Gemini 모델명 |
| GEMINI_BASE_URL | https://generativelanguage.googleapis.com/v1beta/openai | OpenAI 호환 base URL |

## 개발 명령어

```bash
make init      # uv sync --all-extras
make dev       # uvicorn 개발 서버 (--reload)
make format    # ruff format + check --fix
make lint      # ruff check
make test      # pytest -v
```

## 테스트 주의사항

- 테스트에서 ML 모델 로딩을 피하기 위해 `patch("babel_md.main.get_converter")`로 lifespan을 mock
- converter 테스트 후 반드시 `get_converter.cache_clear()` 호출
