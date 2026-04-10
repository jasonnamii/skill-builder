# 스킬 빌더

**스킬 파일 생성 및 수정의 유일한 공식 경로.**

> 🇺🇸 [English README](./README.md)

## 사전 요구사항

- **Obsidian Vault** — 스킬 패키징 및 배포 중 참조되는 Vault 경로
- **Claude Cowork 또는 Claude Code** 환경

## 목적

skill-builder는 전체 스킬 생태계의 게이트키퍼입니다. skill-builder 없이 스킬 파일을 직접 수정하면 허용되지 않습니다. 모든 스킬이 제대로 설계되고, 테스트되고, 검증되고, 배포 전에 패키징되도록 보장합니다.

## 사용 시점 및 방법

새 스킬을 생성하거나 기존 스킬을 수정할 때마다 발동하세요. 처리 항목: 트리거 설계, 간결한 SKILL.md 작성, 검증, .skill 패키징. 병렬 처리 지원 (최대 4개 스킬) 및 배치 수정.

## 사용 예시

| 상황 | 프롬프트 | 결과 |
|---|---|---|
| 새 스킬 생성 | `"X 워크플로우용 스킬 만들어"` | 트리거 정의→SKILL.md 작성→검증→테스트→패키징→배포 준비 |
| 기존 스킬 수정 | `"스킬 X에 새 모드 추가"` | 로드→수정 영역 식별→변경 적용→재검증→테스트 |
| 배치 업데이트 | `"3개 스킬을 공유 함수로 업데이트"` | 병렬 처리→각 검증→배치 결과→상태 보고 |

## 핵심 기능

- 게이트키퍼 강제 — skill-builder 없이 직접 수정 시도 = 거절
- P1/P2/P3 키워드용 트리거 설계 어시스턴트
- 간결한 SKILL.md 작성 (표준 포맷)
- 병렬 처리: 최대 4개 스킬 동시 처리
- 자동화된 검증: 문법, 트리거 유일성, 의존성 매핑
## 연관 스킬

- **[git-sync](https://github.com/jasonnamii/git-sync)** — 검증된 스킬을 GitHub로 푸시
- **[autoloop](https://github.com/jasonnamii/autoloop)** — 최적화를 위해 스킬 제공
- **[meta-skill](https://github.com/jasonnamii/meta-skill)** — 생성된 스킬 발견 및 라우팅

## 설치

```bash
git clone https://github.com/jasonnamii/skill-builder.git ~/.claude/skills/skill-builder
```

## 업데이트

```bash
cd ~/.claude/skills/skill-builder && git pull
```

`~/.claude/skills/`에 배치된 스킬은 Claude Code 및 Cowork 세션에서 자동으로 사용할 수 있습니다.

## Cowork 스킬 생태계

25개 이상의 커스텀 스킬 중 하나입니다. 전체 카탈로그: [github.com/jasonnamii/cowork-skills](https://github.com/jasonnamii/cowork-skills)

## 라이선스

MIT 라이선스 — 자유롭게 사용, 수정, 공유하세요.
