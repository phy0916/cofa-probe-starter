# 단계별 기록과 학습자료

Python 3.10+, Git, 테스트 실행에는 기존 pytest가 필요합니다. 자동 설치·네트워크·commit·tag·push는 없습니다.
AGENTS.md가 현재 Codex의 단계 완료 절차를 지정합니다. Python은 AI 추론을 하지 않습니다.

## 즉시 사용

```powershell
python scripts/run_tests.py tests -q
python scripts/checkpoint.py step-01 --evidence work/logs/ACTUAL_FILE.json
```

JSON 파일명은 실행 출력에서 복사합니다. 과제에 맞는 테스트 경로/인자를 사용하세요.
테스트가 없으면 `python scripts/checkpoint.py step-01`로 만들되 미실행으로 남습니다.
이름은 1~64자 영문/숫자/_/-이며 첫 문자는 영문/숫자입니다. 기존 단계는 덮어쓰지 않습니다.
여러 실패/성공 기록은 `--evidence`를 반복합니다. 오래된 로그는 UNVERIFIED로 남습니다.

생성 폴더의 CODEX_REVIEW.md를 현재 Codex에게 읽고 수행하도록 요청하면 실제 코드와 diff를 검토하여
DEVELOPMENT.md, ARCHITECTURE.md, STUDY_PACK.md를 작성합니다. 각 문항에 30초/2분 답안,
사실·제안·확인 필요·근거를 분리합니다. 자동 생성 문서는 검토용 초안이며 시험 정답이 아닙니다.
Python만 사용한 STUDY_DRAFT.md의 확인 필요 문구를 완성 답안으로 제출하지 마세요.

## 결과와 근거

`work/checkpoints/INDEX.md`는 단계별 버전 색인입니다. 각 폴더에는 다음이 있습니다.

- snapshot.json: HEAD, tag 기반 describe 버전, dirty 지문, 기준 commit, 파일 hash, 상태, 테스트 연결과 가능한 GitHub 링크
- committed.diff: 기본 HEAD 부모→HEAD (첫 commit은 전체 show). `--base v0.1`로 명시 범위 선택
- working.diff: HEAD→현재 작업 파일의 staged+unstaged 변경. 새 untracked 파일은 diff에 없으므로 code.txt/manifest도 확인
- code.txt: 비무시 Python 소스의 행 번호 스냅샷. 파일당 200,000자 제한과 잘림 표시. 다른 언어는 Codex가 로컬 원문 확인
- history.txt: 최근 20개 commit. 전체 이력이 필요하면 별도로 git log 검토
- test-N.json/log: 명시적으로 연결한 실제 runner 기록의 복사본
- CHANGE.md, AI_COLLABORATION.md, TECHNICAL_CHECKLIST.md: 검토 가능한 메모
- STUDY_DRAFT.md, CODEX_REVIEW.md: 질문 6개와 현재 Codex의 분석 지침

실제 commit URL은 해당 commit의 내용만 가리킵니다. dirty diff는 그 링크에 포함되지 않습니다.
이전 기록 전체나 AI 대화를 자동 수집하지 않습니다. 필요한 로컬 기록의 위치를 Codex에 알려주고
최소 근거 요약만 남기세요. 과거 assistant 주장이나 Git 작성자는 개인 판단의 증거가 아닙니다.

## clone 후 선택형 hook 활성화

```powershell
python scripts/install_hook.py
```

Git hook은 clone/ZIP에 따라오지 않으므로 **각 clone에서 명시적으로 한 번** 설치합니다.
현재 Python 실행 경로와 저장소 경로에 연결되므로 이동/가상환경 삭제 후에는 재설치해야 합니다.
기존 post-commit 또는 core.hooksPath가 있으면 설치를 거부합니다. 그 경우 수동 checkpoint를 쓰세요.
삭제는 `git rev-parse --git-path hooks/post-commit`로 위치를 확인하고
`# cofa-evidence-hook-v1`이 들어 있는 이 도구의 hook만 직접 제거하세요.

이후 사용자가 직접 commit할 때 로컬 체크포인트를 만듭니다. 가장 최근 runner 로그 1개를 후보로 연결하며
파일 지문이 다르면 UNVERIFIED입니다. hook은 테스트/AI 분석을 실행하지 않습니다.
Codex의 단계 완료 절차가 의미 분석을 담당합니다. hook 실패 시 commit은 이미 존재하므로 수동 checkpoint로 복구하세요.
commit/tag 없이 끝난 개발 단계도 AGENTS.md 절차로 기록됩니다.

## 버전

버전명은 실제 tag/commit에서 구합니다. v0.1 등의 tag는 자동 생성하지 않습니다.
검토 후 사용자가 직접 commit/tag를 생성하면 다음 checkpoint가 해당 버전에 연결됩니다.
tag가 없으면 commit SHA, 변경 중이면 dirty 지문이 붙습니다. 날짜/단계이름이 release tag를 대신하지 않습니다.
두 버전 비교는 `python scripts/checkpoint.py review-v02 --base v0.1`처럼 수행합니다.

## 다른 과제에서 사용

scripts/의 모든 Python 파일과 templates/를 같은 상대 구조로 복사하세요.
과제 저장소의 기존 AGENTS.md를 보존하고 이 저장소의 단계 완료 절차를 병합하세요.
그 과제의 실제 테스트 경로를 지정하고 clone마다 필요한 경우 hook을 설치합니다.
이 저장소 자체는 범용 도구이며 스케줄러나 특정 과제 풀이를 포함하지 않습니다.

## 신뢰 범위와 비공개

명령은 로컬 Git exclude에 /work/를 추가합니다. 이미 추적된 work/ 파일은 자동 해제하지 않고 실행을 거부합니다.
시험 입력·출력·대화 요약·벤치마크 데이터도 work/에 보관하세요. 강제 add나 다른 경로의 비밀까지 보호하지는 못합니다.
테스트 출력/diff/code에는 민감정보가 들어갈 수 있어 로컬 결과 폴더를 공개 저장소에 올리지 않습니다.

MATCHED는 테스트 전후와 checkpoint의 **비무시 파일 내용**이 같다는 뜻입니다. 시험 데이터처럼
무시된 입력, 설치 패키지, 환경, 외부 서비스, submodule 내용은 지문 범위 밖입니다.
필요한 입력 식별자/hash·환경·seed·예상값은 민감 원문 없이 로컬 메모에 기록하세요.
기록은 서명된 증명이 아니며 동시 파일 수정 중 캡처는 피하세요. 코드가 테스트를 수정했다면
통과 여부와 별개로 기대값의 타당성을 검토하세요. 테스트 시간은 업무 처리 벤치마크가 아닙니다.
