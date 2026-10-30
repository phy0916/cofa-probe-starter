# GitHub 게시와 시험 중 다운로드

현재 ZIP은 로컬 산출물입니다. 자동 게시되지 않습니다.

1. ZIP을 풀고 cofa-probe-starter 폴더의 모든 파일을 검토합니다. work/, 실제 과제, 로그, 개인 링크, 토큰을 업로드하지 않습니다.
2. GitHub에서 새 **Public** 빈 저장소를 만듭니다. 예: cofa-probe-starter. README 자동 생성은 선택하지 않습니다.
3. 아래 명령은 검토한 폴더에서 직접 실행합니다. URL은 본인 저장소 주소로 바꿉니다.

```powershell
git init
git add AGENTS.md README.md PUBLISH.md .gitignore requirements-dev.txt pytest.ini docs prompts scripts templates tests
git diff --cached --stat
git diff --cached
# 내용 검토 후 실행
git commit -m "Add neutral reusable development starter"
git branch -M main
git remote add origin https://github.com/YOUR_ACCOUNT/cofa-probe-starter.git
git push -u origin main
```

GitHub 인증은 본인 환경에서 수행하고 토큰을 문서나 대화에 붙이지 않습니다. Git이 없다면 GitHub 웹의 Upload files로 같은 파일만 올립니다. .gitignore도 포함됐는지 확인하세요.

게시 후 로그아웃/비공개 창에서 저장소가 보이는지, Code → Download ZIP이 되는지 확인합니다. 커밋 SHA를 기록하고 시험에서 사용할 버전을 고정하세요. 공식 지침이 요구하는 기간 동안 공개 상태를 유지합니다. 시험 후 산출물을 이 공개 저장소로 push하지 마세요.

규정에서 허용할 때만 시험 환경에서:
```powershell
git clone https://github.com/YOUR_ACCOUNT/cofa-probe-starter.git
cd cofa-probe-starter
git checkout YOUR_VERIFIED_COMMIT_SHA
python scripts/check_environment.py
python scripts/run_tests.py
```

Git이 없으면 공개 저장소의 Download ZIP을 사용합니다. 실제 시험이 시작된 뒤 다운로드가 차단될 수 있으므로, 허용된 사전 체험에서 접근 가능 여부를 확인하세요. 위 주소와 SHA는 예시이며 실제 업로드 주소가 아닙니다.
