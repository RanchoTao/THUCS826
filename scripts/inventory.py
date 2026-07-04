#!/usr/bin/env python3
"""Generate a conservative Markdown inventory for the THUCS826 repository.

The script scans files, prints a Markdown report, summarizes file types,
infers likely categories/subjects from paths, and flags possible duplicates.
It does not move, rename, or delete files.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__"}
YEAR_RE = re.compile(r"(?<!\d)(19\d{2}|20\d{2}|\d{2})(?!\d)")


def iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_name(path_text: str) -> str:
    stem = Path(path_text).stem.lower()
    stem = re.sub(r"[\s_\-（）()]+", "", stem)
    stem = re.sub(r"答案|解析|回忆版|综合|真题|考研题|duplicate", "", stem)
    return stem


def infer_year(path_text: str) -> str:
    match = YEAR_RE.search(path_text)
    if not match:
        return ""
    raw = match.group(1)
    if len(raw) == 2:
        year = int(raw)
        return str(2000 + year if year <= 30 else 1900 + year)
    return raw


def infer_file_type(path: Path) -> str:
    if path.name == ".gitignore":
        return "configuration file"
    suffix = path.suffix.lower()
    if not suffix:
        return "file without extension"
    return suffix.lstrip(".")


def infer_category(path_text: str) -> str:
    lower = path_text.lower()
    if lower.startswith("exams/") or any(key in path_text for key in ["回忆", "真题", "考研题", "考题"]):
        return "past exam / recall version"
    if lower.startswith("references/") or "参考书目" in path_text:
        return "textbook / book list"
    if lower.startswith("docs/"):
        return "generated document" if "previous-826-layout" in lower else "personal notes"
    if lower.startswith("outputs/"):
        return "generated document"
    if lower.startswith("scripts/"):
        return "script"
    if path_text == ".gitignore":
        return "configuration file"
    if lower.startswith("raw/"):
        return "raw material"
    return "unclear / needs manual review"


def infer_subject(path_text: str) -> str:
    rules = [
        ("数据结构", "data structures"),
        ("data_structure", "data structures"),
        ("dsa", "data structures"),
        ("algorithm", "algorithms"),
        ("算法", "algorithms"),
        ("计算机组成原理", "computer organization"),
        ("计组", "computer organization"),
        ("computer_principles", "computer organization"),
        ("操作系统", "operating systems"),
        ("operating_system", "operating systems"),
        ("计算机网络", "computer networks"),
        ("computer_network", "computer networks"),
        ("数学", "mathematics"),
        ("linear", "mathematics"),
        ("英语", "unclear"),
        ("912", "general CS"),
        ("826", "general CS"),
        ("reference-books", "general CS"),
        ("参考书目", "general CS"),
    ]
    lower = path_text.lower()
    hits = []
    for key, label in rules:
        if key.lower() in lower and label not in hits:
            hits.append(label)
    return ", ".join(hits) if hits else "unclear"


def recommended_action(path_text: str, duplicate: str) -> str:
    if path_text.startswith("raw/duplicates/"):
        return "manually reviewed"
    if duplicate.startswith("exact"):
        return "manually reviewed"
    if path_text.startswith(("README.md", "LICENSE", ".gitignore", "docs/", "exams/", "references/", "raw/", "scripts/", "outputs/")):
        return "kept in place"
    return "manually reviewed"


def suggested_path(path_text: str) -> str:
    return path_text


def reason(path_text: str, category: str, duplicate: str) -> str:
    if path_text.startswith("raw/duplicates/"):
        return "Moved here because an exact duplicate or likely duplicate needs safe review."
    if path_text.startswith("exams/"):
        return "Year-based past exam/recall file location keeps root clean."
    if path_text.startswith("references/"):
        return "Reference material belongs outside the root directory."
    if path_text.startswith("raw/legacy-before-2025-11/"):
        return "Legacy time-based archive preserved without broad deletion."
    if path_text.startswith("raw/legacy-after-2026-01/"):
        return "Later legacy archive preserved for manual review."
    if path_text.startswith("outputs/"):
        return "Generated report belongs under outputs."
    if path_text.startswith("scripts/"):
        return "Utility script belongs under scripts."
    if path_text.startswith("docs/"):
        return "Documentation or preserved notes belong under docs."
    if duplicate != "no":
        return "Potential duplicate; compare content and provenance before deleting anything."
    return f"Conservative classification as {category}."


def duplicate_label(rel: str, exact_dups: set[str], fuzzy_dups: set[str]) -> str:
    if rel in exact_dups:
        return "exact duplicate candidate"
    if rel in fuzzy_dups:
        return "possible duplicate candidate"
    return "no"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    files = list(iter_files(root))

    hashes: dict[str, list[str]] = defaultdict(list)
    norm_names: dict[str, list[str]] = defaultdict(list)
    rows = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        digest = sha256(path)
        hashes[digest].append(rel)
        norm_names[normalize_name(rel)].append(rel)
        rows.append((path, rel, digest))

    exact_dups = {p for group in hashes.values() if len(group) > 1 for p in group}
    fuzzy_dups = {p for group in norm_names.values() if len(group) > 1 for p in group}

    print("# Material Inventory\n")
    print("> Generated by `scripts/inventory.py`. The script only scans and reports; it does not move, rename, or delete files.\n")

    print("## File type summary\n")
    counts = Counter(infer_file_type(path) for path, _, _ in rows)
    print("| File type | Count |")
    print("| --- | ---: |")
    for file_type, count in sorted(counts.items()):
        print(f"| {file_type} | {count} |")

    print("\n## Detailed inventory\n")
    print("| Current path | File type | Likely category | Likely subject area | Year | Recommended action | Suggested new path | Short reason |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    manual_review = []
    duplicate_rows = []
    for path, rel, _ in rows:
        duplicate = duplicate_label(rel, exact_dups, fuzzy_dups)
        category = infer_category(rel)
        subject = infer_subject(rel)
        action = recommended_action(rel, duplicate)
        why = reason(rel, category, duplicate)
        if action == "manually reviewed" or category == "unclear / needs manual review" or subject == "unclear":
            manual_review.append(rel)
        if duplicate != "no":
            duplicate_rows.append(rel)
        print(
            f"| `{rel}` | {infer_file_type(path)} | {category} | {subject} | {infer_year(rel)} | "
            f"{action} | `{suggested_path(rel)}` | {why} |"
        )

    print("\n## Summary\n")
    print("### What materials the repo currently contains\n")
    print("- Year-based historical 912 recall files for 2017, 2018, 2019, and 2020 under `exams/`.")
    print("- Legacy pre-2025-11 archive containing older exams, data-structure materials, computer-organization materials, operating-system notes, network notes, math/English materials, and miscellaneous files.")
    print("- Post-2026-01 legacy archive with limited currently visible content.")
    print("- Reference materials under `references/`, including the Tsinghua CS undergraduate reference book list PDF and the original `王道` note.")
    print("- Generated documentation, previous planning notes, scripts, and audit outputs.\n")

    print("### Main organizational problems\n")
    print("- Historical 912 materials and current 826 planning notes were previously mixed together.")
    print("- Time-based Chinese folders made long-term navigation difficult.")
    print("- Some binary documents cannot be classified beyond filename/context without manual parsing.")
    print("- Duplicate or near-duplicate historical exam files need provenance review before deletion.\n")

    print("### Recommended target structure\n")
    print("- Keep root limited to `README.md`, `LICENSE`, `.gitignore`, and major folders.")
    print("- Keep normalized recall files in `exams/{year}/`.")
    print("- Keep reference materials in `references/`.")
    print("- Keep raw legacy archives in `raw/legacy-before-2025-11/` and `raw/legacy-after-2026-01/`.")
    print("- Keep generated reports in `outputs/` and scripts in `scripts/`.\n")

    print("### Files that need manual review\n")
    if manual_review:
        for item in manual_review:
            print(f"- `{item}`")
    else:
        print("- None identified by the current heuristic.")

    print("\n### Files that may be duplicates\n")
    if duplicate_rows:
        for item in duplicate_rows:
            print(f"- `{item}`")
    else:
        print("- None identified by the current heuristic.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
