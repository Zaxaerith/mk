# Contributing

Contributions are welcome, especially translations of 65816 routines and fixes to
existing ones. A recompiled function is right when it matches the genuine ROM:
check it against the oracle (`tools/lakesnes_ref.c` + `tools/diff_snapshots.py`, or
snesrecomp's lockstep validation) and say how you checked it.

## What never goes in a PR

- ROMs, dumps, or anything extracted from one (graphics, audio, tables).
- Recompiler output (`src/recomp/smk_autogen.c`, anything else `autogen.py` writes),
  disassembly listings, or symbol maps generated from the ROM. The tools ship; their
  output stays on your machine.
- Code from proprietary SDKs or leaked material.

## Where your code comes from

This project is MIT. Contributions must be your own work or under an MIT-compatible
licence. The usual way that goes wrong is porting a fix you saw in a GPL project —
bsnes, higan, Mesen — or in snes9x (non-commercial licence), which relicenses it by
accident and is very hard to untangle later. This repo runs BizHawk (snes9x core),
snes9x and Mesen only as black-box references to compare output against; reading
their source to write ours is not allowed. Hardware documentation (fullsnes, the
SNESdev wiki) is fine. If a change came from somewhere, say where in the PR.

## AI-assisted contributions

Welcome, provided a human understood and verified the change.

## Toolkit changes

Anything hardware-level, harness-level or useful to other titles belongs in
[snesrecomp](https://github.com/sp00nznet/snesrecomp), not here. Open the PR there and
reference it from the game-side change (`needs snesrecomp#N`).

## Before you open a PR

1. Build (README, Getting Started) and check the title → race flow still runs.
2. Keep PRs to one logical change each, so they can be reviewed line by line.
3. If you touched a screen, attach a before/after (`--headless` with
   `SNESRECOMP_SHOT_FRAMES`).
