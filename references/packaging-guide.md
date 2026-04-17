# Packaging Guide — ③ 패키징 + 제공 상세

허브(SKILL.md § ③)의 스포크. 실제 bash 명령·환경 특이사항·엣지케이스 전담.

---

## ③-a 기존 산출물 선삭제 (필수) — `-1` 접미사 차단 3중 방어

```bash
# 1. 세션 스크래치 제거
cd /sessions/{session-id}
rm -f {skill-name}.skill {skill-name}-*.skill    # 기존 + 이전 접미사본 전부

# 2. 마운트 산출물 존재 확인 (덮어쓰기 불가 환경 대비)
ls -la mnt/outputs/{skill-name}*.skill 2>/dev/null
```

**마운트(`mnt/outputs/`)에 구파일 존재 시 필수 절차:**

1. 사용자에게 "이전 `{skill-name}.skill` 있음. 교체할까요?" 1줄 컨펌
2. 컨펌 시 → `mcp__cowork__allow_cowork_file_delete` 호출 → `rm mnt/outputs/{skill-name}.skill`
3. 미삭제 상태로 present_files 진행 → **Cowork 또는 Mac 로컬이 `-1` 접미사 자동 부여** (= 버전 꼬임 근본원인)

---

## ③-b zip 생성

```bash
cd /sessions/{session-id}
zip -r {skill-name}.skill {skill-name}/ \
  -x "*.pyc" -x "__pycache__/*" -x ".DS_Store" -x ".git/*" -x "*-workspace/*" -x "evals/*"
```

제외 항목: 캐시·시스템파일·워크스페이스·평가자료. evals는 의도적 제외(용량·내부자료).

---

## ③-c 제공

**출력 경로 우선순위:**

1. **스크래치패드 직접 제공 (기본)** — `/sessions/{session-id}/{skill-name}.skill`. present_files가 outputs 폴더로 자동 복사. **단 ③-a 선삭제 미수행 시 `-1` 자동 접미사 위험** — 선삭제 반드시.
2. **마운트 폴더 명시 요청 시만** — `cp {skill-name}.skill mnt/{마운트폴더명}/` (PREFLIGHT ③에서 확인한 실존 경로). 대상 파일 존재 시 ③-a의 `allow_cowork_file_delete` 선행.
3. **`mnt/outputs/` 임의 생성 금지** — 환경 기본값 아님. 임의 mkdir → present_files INVALID_PATH

```
mcp__cowork__present_files([{"file_path": "/sessions/{session-id}/{skill-name}.skill"}])
```

---

## ③-d 검증

```bash
ls -la mnt/outputs/{skill-name}*.skill    # 정확히 1개, 접미사 없음 확인
```

2개+ 발견 → ③-a 재실행(구파일 삭제) → 재패키징. **루프 하드캡 2회 초과 시 STOP + 형에게 수동 정리 요청.**

---

## 보조 규칙

- **네이밍:** .skill 파일명 = 원본 폴더명 **그대로**. `-1`·`_copy` 접미사 금지(형의 명시적 지시 시만 예외).
- **재패키징:** 기존 .skill → 형 컨펌 → `allow_cowork_file_delete` → 재zip.
- **서브에이전트:** zip+cp는 가능. `present_files`는 반드시 부모 세션(메인 대화)에서 호출.
- **git-sync:** 패키징 완료 후 "git push 할까요?" 1줄 제안. 형 컨펌 시 git-sync 발동.

---

## 1턴 예시 (경미 경로)

```
사용자: "ruby-skill P1에 '분해' 키워드 추가해줘"

① PREFLIGHT → SKILL.md 존재·1개·mnt/outputs 확인
① 복사+Read+validate → errors=[]
① 판정 → 경미 (P1 1개 추가)
② Edit → description P1 끝에 '분해' 삽입
② validate → errors=[]
③-a rm -f ruby-skill.skill, mnt/outputs 스캔 → 구파일 없음
③-b zip -r ruby-skill.skill ruby-skill/
③-c present_files([{file_path: ".../ruby-skill.skill"}])
③-d ls → ruby-skill.skill 1개, 접미사 없음 ✓
제안 → "git push 할까요?"
```
