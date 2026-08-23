# Roadmap to a fully C-recompiled Super Mario Kart

This document distinguishes the playable emulator-backed launcher from the long-term
static-recompilation goal. "Fully C-recompiled" means that all reachable 65C816 game-code
paths execute as native C, while the original ROM is used only for data tables/assets and
LakeSnes remains the emulated SNES hardware backend. It does **not** mean rewriting the PPU,
SPC700, DSP-1, DMA, or SDL platform layers.

## Measured baseline (2026-08-23)

The standard 1,400-frame scripted route covers title, driver select, class/cup selection,
race initialization, and a short driving segment.

| Metric | Current value | Meaning |
|---|---:|---|
| Registered C entries | 81 | 49 hand-written plus 32 auto-generated; registration alone does not imply correctness |
| Default oracle-gated intercepts | 18 | Safe as one combined set on the standard route |
| Distinct direct JSR/JSL targets on the route | 361 | Excludes indirect calls, jumps, interrupt entries, and unvisited game modes |
| Registered direct targets reached | 56 / 361 (15.5%) | Potential C coverage if every registered body were enabled |
| Direct calls to registered targets | 86,972 / 150,979 (57.6%) | Call-weighted potential, boosted by the opt-in APU reader `$81:F56C`; not the default enabled share |
| Default execution mode | ROM interpreter | `snes_runFrame` still executes the original 65C816 code |

The percentages above are **route coverage**, not whole-game completion. Two-player modes,
all cups/tracks, battle mode, attract/demo paths, results/credits, exceptional input paths,
indirect dispatch targets, and interrupt/fallthrough entries are not fully represented.
Consequently the defensible whole-project statement is: infrastructure is established and a
small validated subset exists, but the project is still in an early static-recompilation phase.

## Current technical boundary

The generator now handles ordinary control flow, direct and computed calls/jumps, width-aware
stack/register operations, TSB/TRB, binary/decimal 8/16-bit ADC/SBC, all observed direct-page
indirect and stack-relative modes, `MVN`/`MVP`, and distinct `(PC,M,X)` CFG states. The profiler
exports exact multi-width entry variants and the generator selects the matching entry block from
the live CPU flags. On the standard route, all 305 not-yet-registered direct targets generate;
combined with 56 registered targets this is 361/361 observed-target generation coverage.
Important gaps remain:

- exact dynamic cycle accounting: taken branches, page/direct-page penalties, interrupt
  recognition points, DMA stalls, and nested call costs;
- complete discovery of indirect call-table targets and all entry flag variants;
- a C-owned reset/NMI/main-frame scheduler that can finish race initialization without
  falling back to `snes_runFrame`;
- scenario coverage for all game modes and long-running races.

One useful negative result is `$81:F638`: the function and all eight indirect JSR targets can
be generated as C, but their 2,715-call race-initialization burst diverges at frame 1040 because
the approximate cycle model reaches the NMI boundary at a different point. This closure remains
opt-in and is a regression target for the exact-timing milestone. `$85:96DC` similarly has two
transition-only divergence frames (1010 and 1030) and is not default-enabled.

## Milestones and acceptance gates

### M1 — Reproducible baseline and observability

- Keep ROM hashes, build instructions, deterministic input scripts, call profiles, and
  WRAM/VRAM/CGRAM snapshot comparison reproducible.
- Export the complete profile with `SMK_RECOMP_PROFILE_TOP=1000`.
- Gate every default-set change on the standard 1,400-frame comparison.

**Exit gate:** a clean checkout plus a user-supplied matching ROM can build and reproduce the
same profile and byte-identical reference snapshots.

### M2 — Generator instruction/addressing completeness

- Implement the missing indirect and stack-relative effective-address modes.
- Implement `MVN`/`MVP`, remaining control/stack instructions, and accurate emulation-mode
  behavior.
- Split CFGs by `(M,X)` state instead of rejecting multi-width re-entry.
- Add focused unit cases for every opcode/addressing/width rule.

**Exit gate (met 2026-08-23):** every direct-call target from the standard profile, including
multi-width entries, either already has C registered or generates successfully. The 1,400-frame
default-set regression remains byte-identical across all 140 sampled frames after the M2 changes.

### M3 — Exact timed native execution

- Move from aggregate instruction costs to bus-phase-accurate fetch/read/write/idle timing.
- Allow NMI/IRQ recognition at the same instruction boundaries as LakeSnes.
- Carry timing through nested native calls and indirect call closures.
- Use `$81:F638` plus its eight-target closure as the first hard regression.

**Exit gate:** all pure-logic and hardware-touching leaf closures on the standard route compose
without ignored divergences.

### M4 — Whole call-graph migration

- Generate/port functions by strongly connected call-graph component, not isolated entries.
- Discover indirect targets from runtime traces and ROM pointer tables.
- Keep the interpreter only as a diagnostic oracle; fail loudly if a production C path requests
  an unregistered code address.

**Exit gate:** title-to-race driving completes with zero interpreter-dispatched opcodes while
WRAM/VRAM/CGRAM remain oracle-identical.

### M5 — C-owned frame scheduler

- Replace the default `snes_runFrame` CPU execution with the recompiled reset, main, NMI, IRQ,
  DMA/HDMA coordination, and wait-state model.
- Keep LakeSnes only for hardware devices and bus routing.

**Exit gate:** the default launcher boots and drives a race with the LakeSnes 65C816 CPU disabled.

### M6 — Whole-game coverage and ROM-code independence

- Add deterministic scripts/save-state seeds for every cup/track, 50/100/150cc, battle,
  two-player, results, credits, demo/attract, pause, retry, and save-data paths.
- Classify every ROM byte used as code versus data; prohibit execution from ROM in release mode.
- Run long-duration and randomized-input differential tests.

**Exit gate:** no reachable 65C816 ROM code executes across the scenario matrix; the ROM remains
required only for legal user-supplied data/assets, with all compared state and rendered output
matching the oracle.
