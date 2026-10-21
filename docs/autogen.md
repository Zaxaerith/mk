# Generating smk_autogen.c

`src/recomp/smk_autogen.c` holds routines lifted from the ROM by
`tools/recomp/autogen.py`: per-instruction C with `recomp_tick()` cycle costs,
each gated byte-identical to the emulation oracle through a race. They only run
with `SMK_RECOMP_CYCLEACCURATE=1`; the default real-frame path never needs them.

Because the file is generated from the ROM, it is never committed (section 3 of
the house rules: the tool ships, the output never does). It is gitignored, and
`CMakeLists.txt` builds it in only when it exists (`SMK_HAVE_AUTOGEN`).

## Generate it

```
py tools/recomp/gen_set.py "Super Mario Kart (USA).sfc" tools/recomp/profiles/default_set.prof src/recomp/smk_autogen.c
```

Expected output:

```
wrote 19 functions -> src/recomp/smk_autogen.c
```

Then re-run CMake (`cmake -B build ...`) so it picks the file up. Checked
2026-10-20: this regenerates the copy that used to be committed byte for byte.

`tools/recomp/profiles/default_set.prof` is the input: `PROF <addr> <calls> <P>`
lines from a profiled run (addresses and entry flags, no ROM bytes).
`tools/recomp/regen_inplace.py <rom> src/recomp/smk_autogen.c` regenerates an
existing file's own function list after an `autogen.py` change.
