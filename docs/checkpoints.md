# 변경마다 1분 기록

이 흐름은 연습용 범용 기록 도구다. 시험 사용 가능 여부는 docs/constraints.md와 최신 공식 원문으로 확인한다. 문제별 정답은 포함하지 않는다.

1. 의미 있는 기능·설계 결정·오류 수정 단위로 work/requirements.csv의 ID를 연결한다. 매 AI 편집마다 기록하거나 커밋하지 않는다.
2. 필요한 테스트를 실제 실행한다. 기존 명령 `python scripts/run_tests.py tests -q`는 출력과 종료 코드를 work/logs/에 남긴다. 도구 테스트와 과제 테스트는 구분한다.
3. 변경을 직접 검토하고 필요할 때만 로컬 커밋한다. 아래 스크립트는 Git을 읽기만 한다.

```powershell
python scripts/checkpoint.py v01-input
# 실제 실행한 runner JSON을 연결할 때 (파일명은 출력에서 복사):
python scripts/checkpoint.py v02-validation --evidence work/logs/ACTUAL_FILE.json
```

4. work/checkpoints/이름/CHANGE.md의 UNKNOWN을 짧게 채운다. AI_COLLABORATION.md는 본인이 기여를 확인해 수정하고 TECHNICAL_CHECKLIST.md의 6문항을 말로 설명한다. 스크립트는 답·인과관계·사람 기여를 추론하지 않는다.

snapshot.json은 실행 시점 HEAD SHA, 그 커밋의 파일 목록, 별도 미커밋 파일 목록, 명시한 로그의 명령·종료 코드를 담는다. 로그 존재는 실행 버전 일치를 증명하지 않으며 수동 대조가 필요하다. 실패 로그도 그대로 기록한다. 로그를 지정하지 않으면 검증 증거는 빈 목록이다. 파일 내용/diff 전체나 비밀정보를 수집하지 않는다.

미커밋 변경은 HEAD에 포함되지 않는다. 구현 커밋 후 새 이름으로 다시 실행해 최종 SHA를 고정한다. 기존 체크포인트는 덮어쓰지 않는다. 잘못 지정한 증거는 수정 후 새 이름으로 재생성한다.

work/는 기본적으로 Git에서 제외된다. 실제 시험 문제·답·로그는 이 공개 저장소에 게시하지 않는다. 허용된 제출 위치에 필요한 문서만 직접 복사한다. 별도 과제 저장소에 이 도구를 가져올 때는 scripts/checkpoint.py와 templates/의 세 문서를 같은 상대 구조로 복사하고 기존 지침과 병합한다. 자동 설치·외부 AI 호출·Git hook·자동 커밋·자동 push는 없다.
