#!/usr/bin/env python3
"""
Convert Agency Agents into OpenClaw workspace integrations.
Each agent workspace produces:
- SOUL.md: persona, identity, tone, and operational boundaries.
- AGENTS.md: mission, deliverables, and execution workflows.
- IDENTITY.md: agent metadata, name, emoji, and vibe.
Cross-platform (Windows, macOS, Linux).
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "integrations" / "openclaw"

EXCLUDE_DIRS = {".git", ".github", "scripts", "strategy", "integrations", "examples", "agency-test-ui"}

SOUL_KEYWORDS = [
    r"identity",
    r"danh tính",
    r"learning.*memory",
    r"communication",
    r"giao tiếp",
    r"style",
    r"phong cách",
    r"critical.?rule",
    r"quy tắc",
    r"rules.?you.?must.?follow"
]

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")

def parse_frontmatter(content: str):
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    fm_text = parts[1]
    body = parts[2]
    
    meta = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip('"').strip("'")
            
    return meta, body

def is_soul_header(header_line: str) -> bool:
    h_lower = header_line.lower()
    for kw in SOUL_KEYWORDS:
        if re.search(kw, h_lower):
            return True
    return False

def convert_agent_to_openclaw(file_path: Path) -> bool:
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
        
    meta, body = parse_frontmatter(content)
    name = meta.get("name")
    if not name:
        return False
        
    slug = slugify(name)
    target_dir = OUT_DIR / slug
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Split body into SOUL.md and AGENTS.md
    lines = body.splitlines(keepends=True)
    soul_sections = []
    agents_sections = []
    
    current_target = "agents"
    current_lines = []
    in_code_fence = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            current_lines.append(line)
            continue
            
        if not in_code_fence and stripped.startswith("## "):
            # Flush accumulated section
            if current_lines:
                if current_target == "soul":
                    soul_sections.extend(current_lines)
                else:
                    agents_sections.extend(current_lines)
                current_lines = []
                
            if is_soul_header(stripped):
                current_target = "soul"
            else:
                current_target = "agents"
                
        current_lines.append(line)
        
    if current_lines:
        if current_target == "soul":
            soul_sections.extend(current_lines)
        else:
            agents_sections.extend(current_lines)
            
    # Write SOUL.md
    soul_content = "".join(soul_sections).strip()
    (target_dir / "SOUL.md").write_text(soul_content + "\n", encoding="utf-8")
    
    # Write AGENTS.md
    agents_content = "".join(agents_sections).strip()
    (target_dir / "AGENTS.md").write_text(agents_content + "\n", encoding="utf-8")
    
    # Write IDENTITY.md
    emoji = meta.get("emoji", "")
    vibe = meta.get("vibe", "")
    desc = meta.get("description", "")
    
    if emoji and vibe:
        identity_text = f"# {emoji} {name}\n\n{vibe}\n"
    elif emoji:
        identity_text = f"# {emoji} {name}\n\n{desc}\n"
    else:
        identity_text = f"# {name}\n\n{desc}\n"
        
    (target_dir / "IDENTITY.md").write_text(identity_text, encoding="utf-8")
    return True

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    converted_count = 0
    
    for item in REPO_ROOT.iterdir():
        if item.is_dir() and item.name not in EXCLUDE_DIRS and not item.name.startswith("."):
            for md_file in item.glob("*.md"):
                if convert_agent_to_openclaw(md_file):
                    converted_count += 1
                    
    print(f"[OK] Converted {converted_count} agents to OpenClaw workspaces at {OUT_DIR}")

if __name__ == "__main__":
    main()

