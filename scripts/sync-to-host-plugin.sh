#!/usr/bin/env bash
# sync-to-host-plugin.sh — VM .skill → host plugin path rsync
# v3.0 신규. git-sync가 host 원본을 보기 때문에 필수.
# usage: sync-to-host-plugin.sh <skill-name>

set -eu
SKILL="${1:?skill name required}"
OUTPUTS_HOST="$HOME/Library/Application Support/Claude/local-agent-mode-sessions"
# outputs path는 세션별로 다름. .git-sync-env에서 PLUGIN_SKILLS_PATH 추출.
ENV_FILE="$HOME/github-repos/skill-repos/git-sync/.git-sync-env"

if [ ! -f "$ENV_FILE" ]; then
    echo "WARN .git-sync-env not found at $ENV_FILE — host sync 스킵"
    exit 0
fi

PLUGIN_PATH=$(grep '^export PLUGIN_SKILLS_PATH=' "$ENV_FILE" | cut -d'"' -f2)
if [ -z "$PLUGIN_PATH" ] || [ ! -d "$PLUGIN_PATH" ]; then
    echo "WARN PLUGIN_SKILLS_PATH invalid — host sync 스킵"
    exit 0
fi

# outputs에서 .skill 위치 자동 탐색 (가장 최근)
SKILL_FILE=$(find "$OUTPUTS_HOST" -name "$SKILL.skill" -mmin -10 2>/dev/null | head -1)
if [ -z "$SKILL_FILE" ]; then
    echo "WARN $SKILL.skill not found in outputs (10min) — host sync 스킵"
    exit 0
fi

TMP=$(mktemp -d)
unzip -q "$SKILL_FILE" -d "$TMP"
if [ ! -d "$TMP/$SKILL" ]; then
    echo "ERR unzip 결과에 $SKILL/ 디렉토리 없음"
    rm -rf "$TMP"
    exit 1
fi

rsync -a --delete "$TMP/$SKILL/" "$PLUGIN_PATH/$SKILL/"
echo "✅ host plugin path synced: $PLUGIN_PATH/$SKILL/"
rm -rf "$TMP"
