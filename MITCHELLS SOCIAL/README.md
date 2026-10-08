# MITCHELLS SOCIAL

Social planning folder for Mitchell's Restaurant (Cocoa, FL), following `CLIENT-SOCIAL-PLAYBOOK.md`.

- `brand/brand-kit.md`: confirmed facts, contact line, choices, open items.
- `media/previous-posts/`: Frank's past branded posts go here.
- `media/holiday-posts/`: branded holiday images go here.
- `media/website/`: 93 photos downloaded from www.MitchellsCocoa.com.
- `media/catalog.json`: the 62 usable website photos with categories and alt text, plus 31 excluded with reasons.

The rest of the structure (config, scripts, hooks, skills) is copied from `MR SUSHI SOCIAL/` by the local Claude session; see `MITCHELLS-STARTER-PROMPT.md`.

## Month 1 (Oct 8 - Nov 7, 2026): drafted in the cloud session

- `content/weeks/2026-W41.json` ... `2026-W45.json`: 31 posts, 75 platform posts (IG + FB daily, GBP Mon/Wed/Fri), playbook week-file shape, `status: "draft"`.
- `media/rendered/`: 89 images with the logo plate, plus `manifest.json` (post id → platform → files).
- `content/review/mitchells-month.html`: approval page, published at https://claude.ai/artifact/AUJHeYDsRZPL3HXUM1QJjY
- `scripts/build_month.py` (captions + checks), `scripts/render_media.py` (renders), `scripts/build_review.py` (review page). Python + Pillow.

To schedule, on Frank's PC: copy `MR SUSHI SOCIAL/scripts/highlevel.mjs`, `hooks/` and `config/client.json` in, set Mitchell's locationId and account IDs, point `highlevel.mjs` at `media/rendered/manifest.json`, dry run each week, then Frank runs `--live`.
