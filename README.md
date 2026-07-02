# Distill Skill

Local workspace for building and versioning colleague-style Codex skills.

## Current Skill

- `colleagues/beet-yang/`: Beet Yang / 比特羊 skill
- `tools/crawl_beet_select.py`: resumable crawler for `beet.select`

## Public Release Notes

This repository does not include raw Telegram exports, crawled full-text JSON files, screenshots, or media assets.

The included skill files are distilled from private/source materials summarized in `meta.json`. They are intended as a reusable Codex skill profile, not as a complete archive of the original channel.

## License

See `LICENSE.md`. Tooling code is MIT licensed; skill/profile content is CC BY-NC 4.0.

## Versioning

Skill version metadata lives in each skill's `meta.json`.

For large future data exports, prefer keeping raw files outside git and recording source, date range, and sample counts in `meta.json`. Curated evidence files used by the current version can be committed when they are needed for reproducibility.
