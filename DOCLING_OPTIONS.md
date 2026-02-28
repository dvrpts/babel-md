# Docling 파이프라인 옵션 가이드

docling v2.75+ 기준. 문서→마크다운 변환 품질 향상을 위한 옵션 정리.

적용 상태: **적용됨** = converter.py에 반영, **기본값** = Docling 기본값 사용, **미적용** = 사용 안 함

## 1. PdfPipelineOptions 전체 필드

| 필드 | 타입 | 기본값 | 적용 상태 | 설명 |
|------|------|--------|----------|------|
| `do_ocr` | bool | `True` | 기본값 | OCR 활성화 |
| `do_table_structure` | bool | `True` | 기본값 | 테이블 구조 추출 |
| `do_code_enrichment` | bool | `True` | 기본값 | 코드 블록 감지 + 언어 식별 |
| `do_formula_enrichment` | bool | `True` | 기본값 | 수식 감지 + LaTeX 추출 |
| `do_picture_classification` | bool | `False` | **적용됨** `True` | 이미지 분류 (26가지 카테고리) |
| `do_picture_description` | bool | `False` | **적용됨** `True` (API키 필요) | VLM/API 기반 이미지 캡션 |
| `do_chart_extraction` | bool | `False` | **적용됨** `True` | 차트에서 CSV 데이터 추출 |
| `ocr_options` | OcrOptions | `OcrAutoOptions()` | **적용됨** `lang=["ko","en"]` | OCR 엔진 설정 |
| `table_structure_options` | TableStructureOptions | FAST | **적용됨** `ACCURATE` | 테이블 모델 설정 |
| `layout_options` | LayoutOptions | 기본값 | 기본값 | 레이아웃 감지 설정 |
| `images_scale` | float | `2.0` | 기본값 | 이미지 스케일링 팩터 |
| `generate_page_images` | bool | `False` | 미적용 | 페이지 이미지 생성 |
| `generate_picture_images` | bool | `False` | **적용됨** `True` | 내장 이미지 추출 |
| `picture_description_options` | PictureDescriptionOptions | - | **적용됨** Gemini API | 이미지 설명 모델 설정 |
| `accelerator_options` | AcceleratorOptions | CPU | 기본값 | 하드웨어 가속 |
| `artifacts_path` | Optional[Path] | `None` | 기본값 | 로컬 모델 저장 경로 |
| `enable_remote_services` | bool | `False` | **적용됨** `True` (API키 필요) | 원격 API 호출 허용 |
| `document_timeout` | int | - | 기본값 | 최대 처리 시간(초) |

## 2. TableFormerMode — **적용됨: ACCURATE**

| 모드 | 설명 |
|------|------|
| `TableFormerMode.FAST` | 속도 우선, 간단한 테이블용 |
| `TableFormerMode.ACCURATE` | 품질 우선, 병합 셀 등 복잡한 테이블용 **← 적용** |

```python
from docling.datamodel.pipeline_options import TableFormerMode, TableStructureOptions

pipeline_options.table_structure_options = TableStructureOptions(
    do_cell_matching=True,
    mode=TableFormerMode.ACCURATE,
)
```

## 3. OCR 옵션 — **적용됨: lang=["ko", "en"]**

### 지원 엔진

| 엔진 | 클래스 | 특징 |
|------|--------|------|
| Auto | `OcrAutoOptions` | 자동 선택 |
| Tesseract CLI | `TesseractCliOcrOptions` | 100+ 언어, 안정적 |
| Tesseract Python | `TesseractOcrOptions` | Python 바인딩 |
| EasyOCR | `EasyOcrOptions` | GPU 가속, 딥러닝 기반 |
| RapidOCR | `RapidOcrOptions` | 빠름, 다양한 백엔드 |
| macOS Vision | `OcrMacOptions` | 네이티브, macOS 전용 |

### 공통 필드

```python
bitmap_area_threshold: float = 0.05  # OCR 트리거 임계값 (페이지 면적 비율)
force_full_page_ocr: bool = False     # 전체 페이지 OCR 강제
lang: list[str] = ["en"]             # OCR 언어 목록
```

### 엔진별 예시

```python
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    TesseractCliOcrOptions,
    OcrMacOptions,
    RapidOcrOptions,
)

# macOS Vision (네이티브, 빠름)
ocr_options = OcrMacOptions(lang=["ko", "en"])

# EasyOCR (GPU 가속)
ocr_options = EasyOcrOptions(
    lang=["ko", "en"],
    use_gpu=True,
    confidence_threshold=0.5,
)

# Tesseract CLI
ocr_options = TesseractCliOcrOptions(lang=["kor", "eng"])

# RapidOCR
ocr_options = RapidOcrOptions(
    lang=["en"],
    backend="onnxruntime",  # "onnxruntime", "openvino", "paddle", "torch"
)

pipeline_options.ocr_options = ocr_options
```

### 스캔 PDF 최적 설정

```python
pipeline_options.do_ocr = True
pipeline_options.ocr_options = EasyOcrOptions(
    force_full_page_ocr=True,
    lang=["ko", "en"],
    use_gpu=True,
    confidence_threshold=0.3,
)
```

## 4. 포맷별 옵션 (DOCX, PPTX, XLSX)

```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
    PowerpointFormatOption,
    ImageFormatOption,
    HTMLFormatOption,
)

converter = DocumentConverter(
    allowed_formats=[
        InputFormat.PDF,
        InputFormat.DOCX,
        InputFormat.PPTX,
        InputFormat.XLSX,
        InputFormat.IMAGE,
        InputFormat.HTML,
    ],
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
        InputFormat.DOCX: WordFormatOption(pipeline_options=doc_options),
        InputFormat.PPTX: PowerpointFormatOption(pipeline_options=doc_options),
    },
)
```

### 지원 InputFormat 전체 목록

`ASCIIDOC`, `AUDIO`, `CSV`, `DOCX`, `HTML`, `IMAGE`, `JSON_DOCLING`, `LATEX`, `MD`,
`METS_GBS`, `PDF`, `PPTX`, `VTT`, `XLSX`, `XML_JATS`, `XML_USPTO`, `XML_XBRL`

## 5. DocumentConverter.convert() 옵션

```python
result = converter.convert(
    source=document_stream,
    max_num_pages=200,               # 최대 페이지 수
    max_file_size=50 * 1024 * 1024,  # 최대 파일 크기 (50MB)
    page_range=(1, 10),              # 페이지 범위
    raises_on_error=True,            # 에러 시 예외 발생
)
```

## 6. 인리치먼트 옵션

| 옵션 | 기본 | 적용 상태 | 설명 |
|------|------|----------|------|
| `do_code_enrichment` | `True` | 기본값 | 코드 블록 감지 + 언어 식별 |
| `do_formula_enrichment` | `True` | 기본값 | 수식 → LaTeX 변환 |
| `do_picture_classification` | `False` | **적용됨** `True` | 26종 이미지 카테고리 분류 |
| `do_picture_description` | `False` | **적용됨** `True` | 이미지 캡션 생성 (Gemini API) |
| `do_chart_extraction` | `False` | **적용됨** `True` | 차트 → CSV (classification 필수) |

### 차트 추출

```python
pipeline_options.do_picture_classification = True  # 전제조건
pipeline_options.do_chart_extraction = True
# 지원: bar_chart, pie_chart, line_chart
```

### 이미지 분류 카테고리 (26종)

`bar_chart`, `pie_chart`, `line_chart`, `scatter_plot`, `box_plot`, `histogram`,
`flow_chart`, `tree_diagram`, `network_diagram`, `mind_map`, `photograph`,
`illustration`, `icon`, `logo`, `screenshot`, `architectural_plan`,
`technical_drawing`, `schematic`, `circuit_diagram`, `geographical_map`,
`infographic`, `table_image`, `graph_plot`, `heatmap`, `venn_diagram`, `other_figure`

## 7. 이미지 처리 옵션

### 로컬 VLM 이미지 설명

```python
from docling.datamodel.pipeline_options import PictureDescriptionVlmOptions

pipeline_options.do_picture_description = True
pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
    repo_id="HuggingFaceTB/SmolVLM-256M-Instruct",
    prompt="Describe the image in three sentences. Be concise and accurate.",
    batch_size=4,
    scale=2.0,
)
```

### 원격 API 이미지 설명 — **적용됨: Gemini 2.5 Flash**

```python
from docling.datamodel.pipeline_options import PictureDescriptionApiOptions

pipeline_options.enable_remote_services = True
pipeline_options.do_picture_description = True
pipeline_options.picture_description_options = PictureDescriptionApiOptions(
    url="https://api.example.com/v1/chat/completions",
    params={"model": "gemini-2.5-flash", "max_completion_tokens": 200},
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    prompt="Describe the image in three sentences.",
    concurrency=4,
    timeout=30,
)
```

### 이미지 설명 필터링 (공통 옵션)

```python
batch_size: int                    # 병렬 처리 수
scale: float                       # 이미지 스케일링
picture_area_threshold             # 최소 이미지 크기
classification_allow               # 허용 카테고리 (화이트리스트)
classification_deny                # 제외 카테고리 (블랙리스트)
classification_min_confidence      # 분류 최소 신뢰도
```

### 마크다운 export 이미지 모드

```python
from docling_core.types.doc import ImageRefMode

md = result.document.export_to_markdown(
    image_mode=ImageRefMode.PLACEHOLDER,  # "<!-- image -->" (기본값, 권장)
    # image_mode=ImageRefMode.REFERENCED, # URI 참조
)
# EMBEDDED(base64 인라인)는 토큰 소모가 과도하므로 사용하지 않음
```

## 8. 레이아웃 분석 — 미적용 (기본 heron 사용)

```python
from docling.datamodel.pipeline_options import LayoutObjectDetectionOptions

pipeline_options.layout_options = LayoutObjectDetectionOptions.from_preset("heron-101")
```

| 프리셋 | 특징 |
|--------|------|
| `heron` | 기본값, 균형 |
| `heron-101` | 최고 품질 (78% mAP) |
| `egret-medium` | 가장 빠름 |
| `egret-large` | 중간 |
| `egret-xlarge` | EGRET 중 최고 |

## 9. 하드웨어 가속 — 미적용 (기본 CPU)

호스팅 환경: Linux Ubuntu (GPU 있으면 CUDA, 없으면 CPU)

```python
from docling.datamodel.pipeline_options import AcceleratorOptions

pipeline_options.accelerator_options = AcceleratorOptions(
    num_threads=8,
    device="auto",  # CUDA GPU 있으면 자동 감지, 없으면 CPU 폴백
    # device="cuda"  # GPU 명시 지정
    # device="cpu"   # CPU 전용
)
```

## 10. Chunking (RAG용) — 미적용

```python
from docling.chunking import HierarchicalChunker, HybridChunker

# 구조 기반
chunker = HierarchicalChunker(merge_list_items=True)
chunks = list(chunker.chunk(result.document))

# 토크나이저 인식 하이브리드
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

chunker = HybridChunker(
    tokenizer=tokenizer,
    merge_peers=True,
    max_tokens=512,
)
chunks = list(chunker.chunk(result.document))

for chunk in chunks:
    text_with_context = chunker.contextualize(chunk)
```
