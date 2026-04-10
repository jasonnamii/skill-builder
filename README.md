# skill-builder

**The only authorized path for creating and modifying skill files.**

## Goal

skill-builder is the gatekeeper for the entire skill ecosystem. Direct modification of skill files without skill-builder is not allowed. It ensures every skill is properly designed, tested, validated, and packaged before deployment.

## When & How to Use

Trigger whenever creating a new skill or modifying an existing one. Handles: trigger design, lean SKILL.md writing, validation, .skill packaging. Supports parallel processing (up to 4 skills) and batch edits.

## Use Cases

| Scenario | Prompt | What Happens |
|---|---|---|
| Create new skill | `"Build a skill for X workflow"` | Define trigger→write SKILL.md→validate→test→package→deploy-ready |
| Modify existing skill | `"Add new mode to skill-X"` | Load→identify edit zones→apply changes→re-validate→test |
| Batch updates | `"Update 3 skills with shared function"` | Parallel processing→validate each→batch results→status report |

## Key Features

- Gatekeeper enforcement — direct modification without skill-builder = rejected
- Trigger design assistant for P1/P2/P3 keywords
- Lean SKILL.md writing in compact, standard format
- Parallel processing: up to 4 skills simultaneously
- Automated validation: syntax, trigger uniqueness, dependency mapping

## Works With

- **[git-sync](https://github.com/jasonnamii/git-sync)** — pushes validated skills to GitHub
- **[autoloop](https://github.com/jasonnamii/autoloop)** — feeds skills for optimization
- **[meta-skill](https://github.com/jasonnamii/meta-skill)** — discovers and routes to created skills

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

This is one of 25+ custom skills. See the full catalog: [github.com/jasonnamii/cowork-skills](https://github.com/jasonnamii/cowork-skills)

## License

MIT License — feel free to use, modify, and share.
