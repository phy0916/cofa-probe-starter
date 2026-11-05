"""One-time local installer for Codex study notes. Does not run Git."""
import argparse
from pathlib import Path
import shutil

MARK='<!-- LOCAL_COFA_STUDY_V1 -->'
INSTRUCTION=(
    '\n\n## Codex local study automation\n'+MARK+'\n'
    '- Follow official exam instructions first. Never invoke Git, inspect .git, install hooks, or publish inputs.\n'
    '- Read work/STUDY_AGENT.md; after meaningful development milestones run '
    'python tools/study_checkpoint.py --project . --label \"milestone\".\n'
    '- Enrich version notes, module flow, AI collaboration and six technical Q&As '
    'from real source and tests only. Mark unsupported claims as 확인 필요.\n'
    '- Keep study data in work/study locally. Do not upload exam information.\n'
)

def main(argv=None):
    parser=argparse.ArgumentParser(description='Install Git-free Codex study support')
    parser.add_argument('--project',required=True)
    args=parser.parse_args(argv)
    project=Path(args.project).resolve()
    if not project.is_dir():
        parser.error('Project directory does not exist')
    source=Path(__file__).resolve().parents[1]
    tool=project/'tools'/'study_checkpoint.py'
    tool.parent.mkdir(parents=True,exist_ok=True)
    original=source/'scripts'/'study_checkpoint.py'
    if tool.exists():
        if tool.read_bytes()!=original.read_bytes():
            parser.error('Existing study_checkpoint.py differs; will not overwrite')
    else:
        shutil.copyfile(original,tool)
    assistant=project/'work'/'STUDY_AGENT.md'
    assistant.parent.mkdir(parents=True,exist_ok=True)
    if not assistant.exists():
        assistant.write_text((source/'AGENTS.md').read_text(encoding='utf-8'),encoding='utf-8')
    agents=project/'AGENTS.md'
    if agents.exists():
        text=agents.read_text(encoding='utf-8')
        if MARK not in text:
            agents.write_text(text.rstrip()+INSTRUCTION,encoding='utf-8')
    else:
        agents.write_text('# Project assistant instructions\n'+INSTRUCTION,encoding='utf-8')
    print('Local study kit installed. No Git commands or .git access.')
    print('Codex should use the project AGENTS.md and create work/study notes.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
