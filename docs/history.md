# History

Milestones before the CHANGELOG existed (2026-10-20). Newer changes are in
[CHANGELOG.md](../CHANGELOG.md).

## June 2026
- **Cracked the menu→race flow** — root-caused the long-standing menu blocker to a power-on
  WRAM fill (`$2E` game-mode read as 2-player on a zero-filled RAM); fixed with a `0x55` fill
  matching hardware/snes9x. Full RE writeup in [`docs/smk_flow_re.md`](docs/smk_flow_re.md),
  cracked headlessly via a BizHawk + snes9x-core harness (`tools/bizhawk/`).
- **Real-frame mode** — runs the genuine ROM via LakeSnes's full frame so the whole game plays now.
- **ImGui menu, save-states, 2-player input, and lockstep netplay** added to snesrecomp (generic).
- **Fixed a real `s_pixel_buf` overflow** (478 vs 480 rows) that silently zeroed adjacent statics.

## Earlier
- **Auto-registered dispatch** via `RECOMP_PATCH(name, snes_addr) { ... }` — linker-priority static
  constructors, no central list. Pattern inspired by N64Recomp's `RECOMP_PATCH`.
- **Public 65816 op kit** — `<snesrecomp/cpu_ops.h>` (`op_lda_*`, `op_sta_*`, `op_rep`, …).
