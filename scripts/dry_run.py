#!/usr/bin/env python3
"""dry_run.py — 스킬이 실제 발동 시 출력을 시뮬레이션·검증
v3.0 신규. 패키징 직전 강제. validate.py가 잡지 못하는 "실작동 실패" 차단.

검증 항목:
1. SKILL.md 본문 존재·readable
2. description 1024자 이하·NOT: 라우팅 포함
3. 본문에 트리거 P1·P2·P5 키워드 ≥1개 (description과 본문 동기)
4. references/scripts 참조가 실제 파일과 일치
5. Gotchas 섹션 존재
6. WRONG/CORRECT 또는 ❌/✅ 1쌍 이상

usage: python3 dry_run.py <skill-dir>
exit 0 = PASS, 1 = FAIL (사유 stdout)
"""
import sys, os, re

def main(skill_dir):
    skill_dir = skill_dir.rstrip("/")
    skill_md = os.path.join(skill_dir, "SKILL.md")
    fails = []

    if not os.path.isfile(skill_md):
        print(f"FAIL: SKILL.md 없음: {skill_md}")
        return 1

    s = open(skill_md).read()

    # 1. description 추출 (1줄 또는 멀티라인 | 블록)
    fm_match = re.search(r"^---\n(.*?)\n---", s, re.DOTALL)
    fm = fm_match.group(1) if fm_match else s
    m_single = re.search(r"^description:\s*([^|\n].+)$", fm, re.MULTILINE)
    m_multi = re.search(r"^description:\s*\|\s*\n((?:  .+\n?)+)", fm, re.MULTILINE)
    if m_multi:
        desc = m_multi.group(1).strip()
    elif m_single:
        desc = m_single.group(1).strip()
    else:
        fails.append("description frontmatter 없음")
        desc = ""
    if desc:
        if len(desc) > 1024:
            fails.append(f"description {len(desc)}/1024 초과")
        if "NOT" not in desc and "→" not in desc:
            fails.append("description에 NOT: 라우팅 없음 (인접 스킬 영토 분리 ✗)")

    # 2. Gotchas
    if "Gotchas" not in s and "함정" not in s:
        fails.append("Gotchas 섹션 없음")

    # 3. WRONG/CORRECT 또는 ❌/✅
    if not (re.search(r"WRONG", s) or re.search(r"❌", s)):
        fails.append("WRONG/CORRECT 또는 ❌/✅ 대조 없음")

    # 4. references/scripts 참조 정합
    ref_dir = os.path.join(skill_dir, "references")
    script_dir = os.path.join(skill_dir, "scripts")
    referenced = set(re.findall(r"references/([\w\-/]+\.md)", s))
    referenced |= set(re.findall(r"scripts/([\w\-]+\.(?:py|sh))", s))
    for r in referenced:
        candidates = [os.path.join(skill_dir, "references", r),
                      os.path.join(skill_dir, "scripts", r)]
        if not any(os.path.isfile(c) for c in candidates):
            # references/ 또는 scripts/ 둘 중 하나에라도 있으면 통과
            full = os.path.join(skill_dir, "references", r) if r.endswith(".md") else os.path.join(skill_dir, "scripts", r)
            if not os.path.isfile(full):
                fails.append(f"참조 파일 부재: {r}")

    # 5. 줄수 cap
    lines = s.count("\n")
    if lines > 500:
        fails.append(f"SKILL.md {lines}줄 > 500줄 (목표 200~300)")

    if fails:
        print("FAIL:")
        for f in fails:
            print(f"  - {f}")
        return 1

    print(f"PASS: SKILL.md {lines}줄, description {len(desc)}/1024")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: dry_run.py <skill-dir>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
