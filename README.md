# Cofa Probe reusable starter

독립 제작한 범용 개발 연습 도구입니다. 공식 Cofa 제품이나 승인 자료가 아닙니다. 문제, 데이터, 도메인 구현, 정답은 포함하지 않습니다.

## 빠른 시작
1. 시험 전 공개 저장소로 게시하고 로그아웃 상태에서 내려받기를 확인하세요. 게시 방법은 PUBLISH.md를 보세요.
2. 실제 시험에서는 최신 공식 안내가 외부 자료·저장소·다운로드·설치를 허용하는지 먼저 확인하세요. 허용이 확인되지 않으면 연습에만 사용하세요.
3. 시험에서 받은 프로젝트에 기존 AGENTS.md가 있다면 덮어쓰지 말고 지침을 검토해 병합하세요. 이 도구를 제출물 전체로 복사하지 마세요.
4. 제공된 Codex와 모델을 그대로 사용하세요. 이 도구는 모델을 설치·업데이트·자동 전환하거나 외부 AI를 호출하지 않습니다.

Python 3.10 이상. 이미 pytest가 있다면 설치 단계를 건너뜁니다. 새 설치는 환경 규정에서 허용할 때만 수행하세요.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python scripts/check_environment.py
.venv\Scripts\python scripts/run_tests.py
```

macOS/Linux에서는 `.venv/bin/python`을 사용합니다. 가상환경 활성화는 필요하지 않습니다. 자동 패키지 업그레이드는 없습니다. pytest 버전 범위는 호환성 범위이며 잠금 파일은 아닙니다.

## 작업 흐름
- 버전별 결정·AI 협업 기록과 마지막 6문항 점검: [1분 체크포인트 사용법](docs/checkpoints.md). `python scripts/checkpoint.py v01`로 로컬 초안을 생성하며 자동 커밋·push는 없습니다.
- prompts/01-start.md로 요구사항을 정리하고 templates/requirements.csv를 work/requirements.csv에 복사합니다.
- prompts/02-implement.md로 한 요구사항씩 구현합니다. 시험 문제와 답안은 로컬 work/에만 기록합니다.
- prompts/03-debug.md와 실제 동작 검증으로 오류를 확인합니다.
- prompts/04-review.md로 미검증 항목과 한계를 확인하고 기록을 정리합니다.
- scripts/run_tests.py는 pytest 종료 코드를 유지하고 work/logs/에 실행 시각·버전·출력·종료 코드를 저장합니다. 로그에는 시험 정보가 들어갈 수 있으므로 공개하지 않습니다. 이 기록은 AI 전체 대화나 실제 토큰 사용량의 자동 수집이 아닙니다.

```powershell
python scripts/run_tests.py tests -q
python scripts/check_traceability.py work/requirements.csv
```

초기 테스트는 도구 자체만 검증합니다. 문제별 기능 테스트가 없으면 시험 과제의 성공을 증명하지 않습니다. traceability 검사는 표의 형식·증거 연결 여부만 확인하며 기능 정확성을 증명하지 않습니다. 테스트 선택으로 일부만 실행했다면 전체 통과로 보고하지 마세요.

## 모델 역할 (수동 선택)
사용자 안내의 명칭을 그대로 보존합니다: **6.1 Sol / 5.6 Terra / 6.0 Luna**. API 모델 ID를 추정하거나 설정 파일에 강제하지 않습니다.
- Sol: 요구사항 통합, 어려운 판단, 최종 검토 담당으로 사용하도록 제안합니다.
- Terra: 범위가 명확한 구현·수정 담당으로 사용하도록 제안합니다.
- Luna: 파일 탐색, 체크리스트, 작은 검증 담당으로 사용하도록 제안합니다.
이는 성능 비교나 최적성 보장이 아닌 역할 설계입니다. 한 모델로 순서대로 수행해도 됩니다. 하위 에이전트는 시험 규정과 현재 환경이 명시적으로 허용하고 사용자가 요청한 경우에만 사용하세요. 사용 불가 시 우회하지 마세요. 인계에는 요구사항 ID, 범위, 파일, 완료 기준, 검증 결과만 전달합니다.

## 공개 범위
공개할 것은 이 기본 도구뿐입니다. 시험 중 작업, 실제 문제·답안·데이터, 개인정보, 개인 접속 링크, 메일 원문, 인증정보는 공개하지 마세요. .gitignore는 이미 추적된 파일이나 다른 경로의 민감정보를 보호하지 못하므로 게시 전 파일 목록과 내용을 직접 검토하세요.

규정 확인 상태와 공식 문서 출처는 docs/constraints.md를 확인하세요. GitHub 게시나 시험 사용 승인을 자동으로 의미하지 않습니다.
