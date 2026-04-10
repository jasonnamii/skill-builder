# Skill Builder

**Skill creation and packaging gatekeeper.**

The only authorized path for creating/modifying SKILL.md files. Trigger design → Lean writing → Validation → .skill packaging.

### Example Prompts

```
"Create a skill for code review" → triggers→SKILL.md→validate→package
"Fix this skill's triggers" → load→edit→revalidate→package
```

## Installation

```bash
git clone https://github.com/jasonnamii/skill-builder.git ~/.claude/skills/skill-builder
```

## Update

```bash
cd ~/.claude/skills/skill-builder && git pull
```

Skills placed in `~/.claude/skills/` are automatically available in Claude Code and Cowork sessions.

## Part of Cowork Skills

This is one of 25 custom skills. See the full catalog: [https://github.com/jasonnamii/cowork-skills](https://github.com/jasonnamii/cowork-skills)

## License

MIT License — feel free to use, modify, and share.
