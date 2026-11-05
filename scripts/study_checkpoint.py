"""Git-free local study snapshots. Python 3.10+; no external dependencies."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

IGNORE={'.git','.venv','venv','node_modules','__pycache__','.pytest_cache','.next',
        'work','logs','data','outputs','dist','build','coverage','.idea','.vscode'}
CODE={'.py','.js','.jsx','.ts','.tsx','.html','.css','.sql','.toml','.yaml','.yml','.json','.ps1'}
QUESTIONS=[
('알고리즘 및 기술적 한계','실제 구현 알고리즘, 선정 이유, 대안, 장단점과 한계는 무엇인가?'),
('모듈 구성과 흐름','각 모듈의 역할과 입력에서 결과·화면까지의 처리 흐름은?'),
('데이터 처리','제공 CSV 등 입력 형식 검증, 정규화, 참조 관계 및 오류 처리는?'),
('규모 변화 및 검증','작업량/사용자 증가 시 병목을 어떤 테스트와 정량 지표로 확인하는가?'),
('운영 조건 변경','재계산, 상태 보호, 장애 및 예외 상황을 어떻게 처리하고 검증하는가?'),
('AI 협업과 직접 기여','AI와 해결한 가장 큰 문제, 본인의 결정, AI 없이 재검증한 결과는?')]

def snapshot(root):
    result={}
    for directory, subdirs, files in os.walk(root):
        subdirs[:]=sorted(x for x in subdirs if x not in IGNORE and not x.startswith('.'))
        for name in sorted(files):
            path=Path(directory)/name
            if name.startswith('.env') or name in {'credentials.json','secrets.json'}:
                continue
            if path.suffix.lower() not in CODE or path.is_symlink():
                continue
            try:
                if path.stat().st_size>1000000:
                    continue
                body=path.read_bytes()
            except OSError:
                continue
            result[path.relative_to(root).as_posix()]=hashlib.sha256(body).hexdigest()
    return result

def test_logs(root):
    found=[]
    for location in [root/'work'/'logs',root/'logs']:
        if not location.is_dir():
            continue
        for path in sorted(location.glob('*.json'),reverse=True)[:5]:
            try:
                d=json.loads(path.read_text(encoding='utf-8'))
                if isinstance(d.get('exit_code'),int):
                    found.append('- {} 종료코드={} 근거={}'.format(
                        d.get('started_utc','시각 미기록'),d['exit_code'],
                        path.relative_to(root).as_posix()))
            except (OSError,ValueError,AttributeError):
                pass
    return found

def seed(path,text):
    if not path.exists():
        path.write_text(text,encoding='utf-8')

def main(argv=None):
    p=argparse.ArgumentParser(description='Make local study notes; never touch Git.')
    p.add_argument('--project',default='.')
    p.add_argument('--label',default='개발 마일스톤')
    a=p.parse_args(argv)
    root=Path(a.project).resolve()
    if not root.is_dir():
        p.error('Project directory not found')
    out=root/'work'/'study'
    versions=out/'versions'
    versions.mkdir(parents=True,exist_ok=True)
    state=versions/'manifest.json'
    if state.exists():
        try:
            last=json.loads(state.read_text(encoding='utf-8'))
            old=last['files']
            num=int(last['number'])
        except (OSError,ValueError,KeyError,TypeError):
            p.error('Unreadable manifest; not overwriting')
    else:
        old={};num=0
    new=snapshot(root)
    added=sorted(set(new)-set(old))
    removed=sorted(set(old)-set(new))
    updated=sorted(k for k in set(new)&set(old) if new[k]!=old[k])
    if not (added or removed or updated):
        print('No source change; no new version. Git untouched.')
        return 0
    num+=1
    ver='v0.{}'.format(num)
    stamp=datetime.now(timezone.utc).isoformat(timespec='seconds')
    changed='\n'.join('- {}: {}'.format(kind,name)
                      for kind,items in [('ADDED',added),('MODIFIED',updated),('REMOVED',removed)]
                      for name in items)
    logs='\n'.join(test_logs(root)) or '- 구조화된 테스트 실행 기록 없음; 성공 여부 확인 필요'
    note=('## {} — {} ({})\n\n'.format(ver,a.label,stamp)
          + '개발 목적/요구사항: 확인 필요\n선택 이유/대안/한계: 확인 필요\n'
          + 'AI 기여: 확인 필요\n본인 직접 판단: 사용자 확인 필요\n\n'
          + '### 실제 변경 파일\n'+changed+'\n\n'
          + '### 최근 실행 로그 (현재 변경과 연결 여부 별도 확인)\n'+logs+'\n\n'
          + '### 제한사항/미완료\n확인 필요\n\n')
    with (out/'DEVELOPMENT_HISTORY.md').open('a',encoding='utf-8') as f:
        f.write(note)
    (versions/(ver+'.md')).write_text(note,encoding='utf-8')
    with (out/'TEST_EVIDENCE.md').open('a',encoding='utf-8') as f:
        f.write('## {} ({})\n{}\n\n'.format(ver,stamp,logs))
    seed(out/'MODULE_FLOW.md','# 모듈 흐름\n실제 코드 파일·함수명을 기준으로 입력→검증→처리→출력/화면까지 분석. 확인 필요.\n')
    seed(out/'AI_COLLABORATION.md',
         '# AI 협업 기록\n가장 큰 문제: 확인 필요\nAI가 한 일: 확인 필요\n'
         '본인이 직접 결정한 일: 사용자 확인 필요\n독립 검증과 실제 근거: 확인 필요\n')
    qa='# 기술 서술형 6문항 — 실제 코드/로그에 근거한 답변만 작성\n\n'
    for i,(topic,q) in enumerate(QUESTIONS,1):
        qa+='## Q{}. {}\n질문: {}\n답변 초안: 확인 필요\n근거 파일/함수/로그: 확인 필요\n확인 수준: 사용자 확인 필요\n\n'.format(i,topic,q)
    seed(out/'TECHNICAL_QA.md',qa)
    seed(out/'FINAL_STUDY_GUIDE.md',
         '# 최종 1분 설명\n목표/모듈/설계 이유/테스트/한계: 확인 필요\n'
         '## 검토 질문\n1. 실제 코드에 있는가?\n2. 실제 실행 로그가 있는가?\n3. 본인의 직접 기여인가?\n')
    state.write_text(json.dumps({'number':num,'files':new,'utc':stamp},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Created {} in {}; Git untouched.'.format(ver,out))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
