# Preview validation

The patched manuscript was compiled from upstream commit `5025cc8e8f2f8ca015dff2066f08f81ad5715a51` with Tectonic 0.16.9. `validation.json` records the patch/apply and compile checks; `build.log` is sanitized so temporary paths do not leak into the artifact. The validator fixes `SOURCE_DATE_EPOCH` to the pinned commit time; two consecutive builds produced SHA-256 `0a43360e59fdbbc4002e2190479871896688b3b4ef640d219313cd9d2ed5acb9`.

Visual QA on 2026-07-20 rendered all 30 pages at 110 DPI with Poppler. Pages 1, 6, 7, 21, 22, and 30 were inspected at full resolution, covering the title/keywords, renamed framework section, institutional matrix, research-program insertion and transition, and bibliography. No clipping, overlap, broken table rules, blank pages, or unreadable glyphs were observed. Compiler warnings are retained in `build.log`; the inspected additions render cleanly.
