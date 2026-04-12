#!/usr/bin/env python3
"""
Comprehensive validation script for Claude Code skills.
Validates YAML frontmatter, P-tier triggers, size/token budget, hub-spoke,
and performance gates.
"""

import sys
import os
import re
import json
from pathlib import Path
from collections import defaultdict


def parse_yaml_frontmatter(content):
    """Parse YAML frontmatter without yaml library (regex-based)."""
    if not content.startswith('---'):
        return None, "No YAML frontmatter found"

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None, "Invalid frontmatter format"

    frontmatter_text = match.group(1)
    fm = {}
    current_key = None
    current_value = []

    for line in frontmatter_text.split('\n'):
        # Handle multiline YAML values (indented lines)
        if line and not line[0].isspace() and ':' in line:
            # New key-value pair
            if current_key:
                fm[current_key] = '\n'.join(current_value).strip()
            key, value = line.split(':', 1)
            current_key = key.strip()
            current_value = [value.strip().strip('"').strip("'")]
        elif current_key and line:
            # Continuation of multiline value
            current_value.append(line.lstrip())

    # Add last key-value pair
    if current_key:
        fm[current_key] = '\n'.join(current_value).strip()

    return fm, None


def validate_frontmatter(fm, content):
    """Validate YAML frontmatter structure and content."""
    errors, warnings = [], []
    if 'name' not in fm:
        errors.append("Missing 'name' in frontmatter")
    elif not re.match(r'^[a-z0-9-]+$', fm['name']) or len(fm['name']) > 64:
        if not re.match(r'^[a-z0-9-]+$', fm['name']):
            errors.append(f"Name '{fm['name']}' must be kebab-case")
        else:
            errors.append(f"Name exceeds 64 chars ({len(fm['name'])})")

    if 'description' not in fm:
        errors.append("Missing 'description' in frontmatter")
    elif len(fm['description']) > 500 or '\t' in fm['description']:
        if len(fm['description']) > 500:
            errors.append(f"Description exceeds 500 chars ({len(fm['description'])})")
        if '\t' in fm['description']:
            errors.append("Description contains tabs")
        if len(fm['description']) > 400:
            warnings.append(f"Description is long ({len(fm['description'])} chars)")

    # Check @uses references (only in YAML frontmatter list format)
    uses = fm.get('"@uses"', '') or fm.get('@uses', '')
    if uses:
        for line in uses.split('\n'):
            line = line.strip().lstrip('- ').strip()
            if line and line.endswith('.md'):
                if not (Path(fm.get('_skill_dir', '.')) / line).exists():
                    warnings.append(f"@uses reference not found: {line}")
    return errors, warnings


def parse_description_for_p_tiers(content):
    """Extract P-tier trigger counts from description and HTML comments."""
    p_tiers = {
        'P1': 0,  # keywords (nouns)
        'P2': 0,  # verb patterns (Korean + English)
        'P3': 0,  # technical terms (English)
        'P5': 0,  # output formats
        'NOT': False  # must have routing (→)
    }

    # Extract P-tier info from frontmatter description or HTML comments
    # First, look for P-tiers in the entire content (including HTML comments)
    full_text = content

    # Split by P1/P2/P3/P5/NOT markers (case-insensitive to catch both in comments and frontmatter)
    p1_match = re.search(r'P1:\s*(.+?)(?=P2:|P3:|P5:|NOT:|-->|$)', full_text, re.DOTALL | re.IGNORECASE)
    p2_match = re.search(r'P2:\s*(.+?)(?=P1:|P3:|P5:|NOT:|-->|$)', full_text, re.DOTALL | re.IGNORECASE)
    p3_match = re.search(r'P3:\s*(.+?)(?=P1:|P2:|P5:|NOT:|-->|$)', full_text, re.DOTALL | re.IGNORECASE)
    p5_match = re.search(r'P5:\s*(.+?)(?=P1:|P2:|P3:|NOT:|-->|$)', full_text, re.DOTALL | re.IGNORECASE)
    not_match = re.search(r'NOT:\s*(.+?)(?=P1:|P2:|P3:|P5:|-->|$)', full_text, re.DOTALL | re.IGNORECASE)

    # Count P1 keywords (comma/space-separated nouns)
    if p1_match:
        text = p1_match.group(1).strip()
        # Split by comma, period, newline
        items = re.split(r'[,.\n]+', text)
        p_tiers['P1'] = len([x for x in items if x.strip() and not x.strip().startswith('P')])

    # Count P2 verb patterns
    if p2_match:
        text = p2_match.group(1).strip()
        items = re.split(r'[,.\n]+', text)
        p_tiers['P2'] = len([x for x in items if x.strip() and not x.strip().startswith('P')])

    # Count P3 technical terms
    if p3_match:
        text = p3_match.group(1).strip()
        items = re.split(r'[,.\n]+', text)
        p_tiers['P3'] = len([x for x in items if x.strip() and not x.strip().startswith('P')])

    # Count P5 output formats
    if p5_match:
        text = p5_match.group(1).strip()
        items = re.split(r'[,.\n]+', text)
        p_tiers['P5'] = len([x for x in items if x.strip() and not x.strip().startswith('N')])

    # Check NOT (routing with →)
    if not_match:
        not_text = not_match.group(1)
        p_tiers['NOT'] = '→' in not_text or 'references/' in not_text

    return p_tiers


def count_bytes_and_estimate_tokens(text):
    """Calculate file size and estimate token count."""
    byte_size = len(text.encode('utf-8'))
    return byte_size, int(len(text.split()) * 1.3)


def analyze_hub_spoke(skill_path, content):
    """Analyze hub-spoke architecture."""
    skill_kb = len(content.encode('utf-8')) / 1024
    has_refs = (skill_path / 'references').exists()
    ref_blocks = len(re.findall(r'→\s+references/', content))
    return ("yes" if (skill_kb > 5 and has_refs) else
            "recommended" if skill_kb > 5 else "no"), ref_blocks


def analyze_performance(skill_path, content):
    """Analyze performance: phases, scripts, automatable sections."""
    phases = len(re.findall(r'(?:Phase|Step|단계)', content, re.IGNORECASE))
    scripts_count = len(list((skill_path / 'scripts').glob('*'))) if (skill_path / 'scripts').exists() else 0
    automatable = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'-\s*\[\s*\]', line):
            for j in range(i - 1, max(0, i - 10), -1):
                if lines[j].startswith('#'):
                    header = lines[j].lstrip('#').strip()
                    if header not in automatable:
                        automatable.append(header)
                    break
    return phases, scripts_count, automatable


def calculate_refs_size(skill_path):
    """Calculate total size of all references."""
    refs_dir = skill_path / 'references'
    if not refs_dir.exists():
        return 0, 0
    total_bytes, total_tokens = 0, 0
    for ref_file in refs_dir.rglob('*'):
        if ref_file.is_file():
            try:
                content = ref_file.read_text(encoding='utf-8', errors='ignore')
                b, t = count_bytes_and_estimate_tokens(content)
                total_bytes, total_tokens = total_bytes + b, total_tokens + t
            except:
                pass
    return total_bytes, total_tokens


def check_reference_pointers(skill_path, content):
    """Check that all → references/xxx.md pointers resolve to actual files."""
    broken = []
    pointers = re.findall(r'→\s+references/([^\s]+\.md)', content)
    refs_dir = skill_path / 'references'
    for ptr in pointers:
        # Skip template placeholders like {파일명}.md
        if re.search(r'\{.*?\}', ptr):
            continue
        if not (refs_dir / ptr).exists():
            broken.append(ptr)
    return broken


def check_gotchas_section(content):
    """Check that a Gotchas section exists (Lean principle: Gotchas required)."""
    return bool(re.search(r'^#+\s*Gotchas', content, re.MULTILINE | re.IGNORECASE))


def check_duplicate_skill_md(skill_path):
    """Check that only one SKILL.md exists in the skill directory tree."""
    count = len(list(skill_path.rglob('SKILL.md')))
    return count


def check_description_body_coherence(fm, content):
    """
    Check that P1 keywords in description appear somewhere in the body text.
    Returns list of P1 keywords missing from body.
    """
    desc = fm.get('description', '')
    p1_match = re.search(r'P1:\s*(.+?)(?=P2:|P3:|P5:|NOT:|$)', desc, re.DOTALL)
    if not p1_match:
        return []

    # Extract body (everything after frontmatter)
    body_match = re.match(r'^---\n.*?\n---\n(.*)', content, re.DOTALL)
    body = body_match.group(1).lower() if body_match else content.lower()

    items = re.split(r'[,.\n]+', p1_match.group(1).strip())
    keywords = [x.strip().lower() for x in items if x.strip() and not x.strip().startswith('P')]

    missing = []
    for kw in keywords:
        # Allow partial match (e.g. "스킬수정" matches if "수정" is in body)
        if kw not in body and not any(part in body for part in kw.split() if len(part) > 1):
            missing.append(kw)
    return missing


def validate_skill(skill_path):
    """Main validation function."""
    skill_path = Path(skill_path)
    skill_md = skill_path / 'SKILL.md'

    def error_result(err_msg, name=skill_path.name):
        return {'valid': False, 'skill_name': name, 'errors': [err_msg], 'warnings': [], 'metrics': {}}

    if not skill_md.exists():
        return error_result('SKILL.md not found')

    try:
        content = skill_md.read_text(encoding='utf-8')
    except Exception as e:
        return error_result(f'Cannot read SKILL.md: {str(e)}')

    fm, fm_error = parse_yaml_frontmatter(content)
    if fm_error:
        return error_result(fm_error)

    fm['_skill_dir'] = skill_path
    errors, warnings = validate_frontmatter(fm, content)

    skill_bytes, skill_tokens = count_bytes_and_estimate_tokens(content)
    skill_kb = round(skill_bytes / 1024, 1)
    if skill_kb > 10:
        warnings.append(f"SKILL.md is large ({skill_kb}KB, recommend <10KB)")

    p_tiers = parse_description_for_p_tiers(content)
    refs_bytes, refs_tokens = calculate_refs_size(skill_path)
    combined_tokens = skill_tokens + refs_tokens

    if combined_tokens > 30000:
        warnings.append(f"Combined tokens large ({combined_tokens}, recommend <30000)")

    hub_spoke, _ = analyze_hub_spoke(skill_path, content)
    phases, scripts_count, automatable = analyze_performance(skill_path, content)

    # New validations: pointer integrity, gotchas, duplicate SKILL.md, desc↔body coherence
    broken_pointers = check_reference_pointers(skill_path, content)
    if broken_pointers:
        errors.append(f"Broken reference pointers: {', '.join(broken_pointers)}")

    has_gotchas = check_gotchas_section(content)
    if not has_gotchas:
        warnings.append("No Gotchas section found (Lean principle: Gotchas required)")

    skill_md_count = check_duplicate_skill_md(skill_path)
    if skill_md_count > 1:
        errors.append(f"Multiple SKILL.md files found ({skill_md_count}), must be exactly 1")

    desc_body_missing = check_description_body_coherence(fm, content)
    if desc_body_missing:
        warnings.append(f"P1 keywords not found in body: {', '.join(desc_body_missing)}")

    for tier, min_val in [('P1', 5), ('P2', 2), ('P3', 2), ('P5', 1)]:
        if p_tiers[tier] < min_val:
            desc = {
                'P1': 'keywords', 'P2': 'verb patterns', 'P3': 'technical terms', 'P5': 'output formats'
            }
            warnings.append(f"{tier} has {p_tiers[tier]} {desc[tier]} (recommend >={min_val})")
    if not p_tiers['NOT']:
        warnings.append("NOT trigger not found (should have routing with →)")

    metrics = {
        'skill_md_bytes': skill_bytes, 'skill_md_kb': skill_kb,
        'estimated_tokens': skill_tokens, 'description_chars': len(fm.get('description', '')),
        'refs_total_bytes': refs_bytes, 'refs_total_kb': round(refs_bytes / 1024, 1) if refs_bytes else 0,
        'combined_tokens_estimate': combined_tokens, 'p_tiers': p_tiers, 'hub_spoke': hub_spoke,
        'phases_count': phases, 'scripts_count': scripts_count, 'automatable_sections': automatable,
        'broken_ref_pointers': broken_pointers, 'has_gotchas': has_gotchas,
        'skill_md_count': skill_md_count, 'desc_body_missing_keywords': desc_body_missing
    }

    return {
        'valid': len(errors) == 0, 'skill_name': fm.get('name', skill_path.name),
        'errors': errors, 'warnings': warnings, 'metrics': metrics
    }


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python validate.py <skill-directory>', file=sys.stderr)
        sys.exit(1)

    result = validate_skill(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result['valid'] else 1)
