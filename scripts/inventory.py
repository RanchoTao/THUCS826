#!/usr/bin/env python3
"""Generate a Markdown inventory for the THUCS826 repository.

The script scans files, prints a Markdown report, summarizes file types,
and flags possible duplicates. It does not move, rename, or delete files.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__"}
PAPER_RE = re.compile(r"(19\d{2}|20\d{2}|\d{2})")


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


def normalize_name(path: Path) -> str:
    stem = path.stem.lower()
    stem = re.sub(r"[\s_\-（）()]+", "", stem)
    stem = re.sub(r"答案|解析|回忆版|综合|真题|考研题", "", stem)
    return stem


def infer_year(path_text: str) -> str:
    text = path_text
    match = PAPER_RE.search(text)
    if not match:
        return "待识别"
    raw = match.group(1)
    if len(raw) == 2:
        year = int(raw)
        return str(2000 + year if year <= 30 else 1900 + year)
    return raw


def infer_subject(path_text: str) -> str:
    text = path_text
    rules = [
        ("数据结构", "数据结构"),
        ("DSA", "数据结构"),
        ("dsa", "数据结构"),
        ("计算机组成原理", "计算机原理"),
        ("计组", "计算机原理"),
        ("操作系统", "操作系统"),
        ("计算机网络", "计算机网络"),
        ("英语", "英语/公共课"),
        ("数学", "数学/公共课"),
        ("考题", "历史考题"),
        ("912", "912 综合"),
        ("826", "826 综合"),
        ("王道", "统考参考"),
    ]
    hits = [label for key, label in rules if key in text]
    return "、".join(dict.fromkeys(hits)) if hits else "待分类"


def infer_kind(path: Path, path_text: str) -> str:
    text = path_text
    suffix = path.suffix.lower() or "无扩展名"
    if any(key in text for key in ["真题", "考研题", "回忆版", "考题"]):
        return "真题/回忆资料"
    if "README" in path.name:
        return "说明文件"
    if "ppt" in text.lower():
        return "课件"
    if any(key in text for key in ["笔记", "notes", "chp", "conclusion"]):
        return "笔记"
    if "lab" in text.lower():
        return "实验报告"
    if suffix in {".jpg", ".jpeg", ".png"}:
        return "图片"
    return suffix.lstrip(".").upper() + " 文件"


def keep_note(path_text: str, duplicate: str) -> str:
    text = path_text
    if duplicate.startswith("是"):
        return "保留一个权威版本，暂不删除原件"
    if "912" in text or "考题" in text:
        return "保留：912/历史参考，不等同于当前 826"
    if any(s in text for s in ["数据结构", "计算机组成原理", "操作系统", "计算机网络"]):
        return "保留：826 四科相关参考"
    if any(s in text for s in ["英语", "数学"]):
        return "保留：公共课/辅助资料，非 826 主线"
    if path_text.startswith("raw/"):
        return "保留：原始资料归档区"
    return "保留：待进一步分类"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    files = list(iter_files(root))

    hashes = defaultdict(list)
    norm_names = defaultdict(list)
    rows = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        digest = sha256(path)
        hashes[digest].append(rel)
        norm_names[normalize_name(path)].append(rel)
        rows.append((path, rel, digest))

    dup_by_hash = {p for group in hashes.values() if len(group) > 1 for p in group}
    dup_by_name = {p for group in norm_names.values() if len(group) > 1 for p in group}

    print("# 资料清单\n")
    print("> 本报告由 `scripts/inventory.py` 生成；脚本只扫描并输出报告，不移动、不删除文件。\n")
    print("## 文件类型统计\n")
    counts = Counter((p.suffix.lower() or "无扩展名") for p, _, _ in rows)
    print("| 类型 | 数量 |")
    print("| --- | ---: |")
    for ext, count in sorted(counts.items()):
        print(f"| {ext} | {count} |")

    print("\n## 资料明细\n")
    print("| 名称 | 类型 | 年份 | 所属科目 | 是否重复 | 是否需要保留 |")
    print("| --- | --- | --- | --- | --- | --- |")
    for path, rel, _ in rows:
        if rel in dup_by_hash:
            duplicate = "是：内容哈希重复"
        elif rel in dup_by_name:
            duplicate = "可能：名称相近"
        else:
            duplicate = "否"
        print(
            f"| `{rel}` | {infer_kind(path, rel)} | {infer_year(rel)} | "
            f"{infer_subject(rel)} | {duplicate} | {keep_note(rel, duplicate)} |"
        )

    print("\n## 可能重复文件\n")
    exact = [group for group in hashes.values() if len(group) > 1]
    fuzzy = [group for group in norm_names.values() if len(group) > 1]
    if not exact and not fuzzy:
        print("\n暂无明确重复文件。")
    if exact:
        print("\n### 内容哈希完全一致\n")
        for group in exact:
            print("- " + "；".join(f"`{item}`" for item in group))
    if fuzzy:
        print("\n### 名称相近，需人工确认\n")
        for group in fuzzy:
            print("- " + "；".join(f"`{item}`" for item in group))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
