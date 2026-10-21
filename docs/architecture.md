# Architecture

How the launcher, the recompiled code and snesrecomp fit together.
Code: `src/main/main.c` (frame loop, modes), `src/recomp/` (hand-ported routines),
`ext/snesrecomp/` (hardware, see its `docs/architecture.md`).

```
┌─────────────────────────────────────────────────┐
│                 smk_launcher                      │
│  ┌──────────────────────────────────────────┐    │
│  │  src/recomp/ — 48 Recompiled functions   │    │
│  │  smk_boot.c  — NMI, state machine, input │    │
│  │  smk_init.c  — Init, transition dispatch │    │
│  │  smk_title.c — Decompressor, PPU, menus  │    │
│  └──────────────────────────────────────────┘    │
│                       │                           │
│              bus_read8 / bus_write8               │
│                       │                           │
│  ┌──────────────────────────────────────────┐    │
│  │  snesrecomp (ext/snesrecomp/)            │    │
│  │  ┌────────────────────────────────────┐  │    │
│  │  │  LakeSnes — Cycle-accurate SNES HW │  │    │
│  │  │  Real PPU (Mode 0-7, sprites, etc) │  │    │
│  │  │  Real SPC700 + DSP audio           │  │    │
│  │  │  Real DMA (GPDMA + HDMA)           │  │    │
│  │  │  Full memory bus routing            │  │    │
│  │  └────────────────────────────────────┘  │    │
│  │  SDL2 platform (window, audio, input)    │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

In the **recompiled-shell path** (`SMK_SHELLS=1`), recompiled game code acts as the CPU — it
calls `bus_read8(bank, addr)` / `bus_write8(bank, addr, val)`, which route through LakeSnes's
real memory bus to the actual PPU, APU, DMA, and cartridge hardware. In the **default
real-frame path**, LakeSnes's own CPU executes the genuine ROM each frame (`snes_runFrame`)
— identical to a cycle-accurate emulator — so the full game plays while the recompiled
functions are still being written. Either way, all PPU/APU/DMA behaviour is real.

## Project structure

```
├── include/smk/       functions.h (smk_XXXXXX forward declarations)
├── src/
│   ├── recomp/        Recompiled game functions (smk_boot.c, smk_init.c, smk_title.c)
│   └── main/          main.c — entry point, frame loop
├── ext/snesrecomp/    snesrecomp library (LakeSnes backend + SDL2 platform):
│                        recomp_patch.h    — RECOMP_PATCH auto-registration macro
│                        cpu_ops.h         — 65816 instruction helpers (op_lda_*, op_sta_*, …)
│                        menu_overlay.cpp  — Dear ImGui menu (File/Graphics/Sound/Controller/MP/Help)
│                        mp_session.c      — generic SNES lockstep netplay (TCP)
│                        third_party/imgui — vendored Dear ImGui
├── docs/
│   └── smk_flow_re.md  reverse-engineering of the menu→race flow
└── tools/
    ├── disasm/        65816 disassembler (M/X flag tracking, all addressing modes)
    ├── bizhawk/       headless BizHawk + snes9x-core ground-truth harness
    └── lakesnes_ref.c native LakeSnes runner (scripted input, snapshot/BMP dumps)
```

## The tile decompressor ($84:E09E)

The custom decompressor at `$84:E09E` handles SMK's tile/tilemap compression format:

| Mode | Encoding | Description |
|------|----------|-------------|
| `$00` | Raw | Copy N bytes from stream |
| `$20` | RLE | Repeat 1 byte N times |
| `$40` | Word fill | Alternate 2 bytes for N entries |
| `$60` | Inc fill | Store incrementing byte N times |
| `$80` | Backref | Copy from earlier in buffer (abs offset + base) |
| `$A0` | Inv backref | Copy with XOR $FF (inverted) |
| `$C0` | Byte backref | Copy from buf_pos - offset (1-byte offset) |

Commands `$E0`–`$FE` use extended 10-bit counts: 1 data byte + cmd bits 0-1 as high bits.

## ROM details

| Field | Value |
|-------|-------|
| Title | SUPER MARIO KART |
| System | Super Nintendo (SNES) |
| CPU | WDC 65C816 @ 3.58 MHz |
| Coprocessor | DSP-1 (math) + SPC700 (audio) |
| Mapping | HiROM FastROM |
| Size | 512 KB (8 × 64 KB banks, C0–C7) |
| SRAM | 2 KB |
| Region | USA |
| CRC32 | CD80DB86 |

## References

- [Yoshifanatic1/Super-Mario-Kart-Disassembly](https://github.com/Yoshifanatic1/Super-Mario-Kart-Disassembly) — Full 65816 + SPC700 disassembly (Asar)
- [jvipond/super_mario_kart_disassembly](https://github.com/jvipond/super_mario_kart_disassembly) — Trace-based disassembly with Python tooling
- [jvipond/super_mario_kart_recompilation](https://github.com/jvipond/super_mario_kart_recompilation) — Prior LLVM-based recomp attempt
- [MrL314/smk-spc700-disassembly](https://github.com/MrL314/smk-spc700-disassembly) — SPC700 audio driver disassembly
- [LakeSnes](https://github.com/elzo-d/LakeSnes) — Cycle-accurate SNES emulator in C (hardware backend)
