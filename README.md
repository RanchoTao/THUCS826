# THUCS826

THUCS826 is a long-term knowledge base for preparing for Tsinghua University computer science graduate entrance exam materials, with emphasis on current THUCS826 preparation and historical 清华计算机 912 materials.

This repository is currently in a **cleanup and indexing stage**. Materials are preserved conservatively; historical 912 files are useful references but should not be treated as an official or complete 826 syllabus.

## Directory structure

```text
THUCS826/
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── index.md
│   ├── roadmap.md
│   ├── syllabus.md
│   ├── resources.md
│   └── notes/
├── exams/
│   ├── 2017/
│   ├── 2018/
│   ├── 2019/
│   └── 2020/
├── references/
├── raw/
│   ├── legacy-before-2025-11/
│   ├── legacy-after-2026-01/
│   └── duplicates/
├── scripts/
└── outputs/
```

## How to use this repository

1. Start from [`docs/index.md`](docs/index.md) for navigation.
2. Read [`docs/syllabus.md`](docs/syllabus.md) as an inferred subject map, not an official syllabus.
3. Use [`docs/roadmap.md`](docs/roadmap.md) to plan preparation phases.
4. Check [`docs/resources.md`](docs/resources.md) to locate available materials.
5. Review [`outputs/material_inventory.md`](outputs/material_inventory.md) before moving or editing raw materials.
6. Use [`outputs/exam_analysis.md`](outputs/exam_analysis.md) to understand which past 912 recall files are currently available.

## Current material coverage

- Historical 清华计算机 912 recall files for 2017, 2018, 2019, and 2020.
- A legacy archive collected before 2025-11, including subject notes, course materials, older exam documents, English and math materials, and miscellaneous files.
- A small post-2026-01 legacy archive.
- A Tsinghua CS undergraduate reference book list PDF.
- Previous generated THUCS826 planning notes preserved under `docs/notes/previous-826-layout/`.

## Important cautions

- This repository does not provide official admissions or exam policy guarantees.
- Always verify exam subjects, scores, and admissions requirements against official Tsinghua University graduate admissions sources.
- Historical 912 materials are not equivalent to current 826 materials.
- Some PDF/DOC/DOCX contents have not been parsed; classification may rely on filenames and folder context.

## Current status

- Root directory has been cleaned.
- Past 912 recall files have been moved into year-based `exams/` folders.
- Root reference materials have been moved into `references/`.
- Old time-based folders have been archived under `raw/`.
- Generated reports live under `outputs/`.

## Next steps

1. Manually review files marked `needs manual review` in the inventory.
2. Extract metadata from PDF/DOC/DOCX files where possible.
3. Build a verified 826-specific resource list from official sources.
4. Expand year-by-year exam analysis without inventing unavailable content.
