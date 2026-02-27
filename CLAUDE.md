# CLAUDE.md

프로젝트 컨텍스트는 AGENTS.md를 참고.

## 규칙

- 한국어로 소통
- `make format && make lint && make test` 통과 확인 후 작업 완료
- 테스트에서 Docling ML 모델 로딩 금지 — 반드시 mock 사용
- `.env`에 시크릿 저장, 절대 커밋하지 않음
- src 레이아웃: `src/babel_md/` 패키지 구조 유지
