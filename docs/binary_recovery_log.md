# Ongoing binary recovery

Goal started 2026-09-19: continue recovering readable C algorithms from the
locally supplied ROM, verify against actual CPU execution, and save incremental
local checkpoints until the user stops work or usage/runtime limits intervene.
This is an ongoing goal; the entries below are checkpoints, not completion of
the full recompilation project.

## Checkpoint 1 — vector direction and packed-cell direction

Added `smk_vector_direction` ($81:F638 plus eight child branches) and
`smk_direction_from_cell` ($81:FD22) to the semantic algorithm library. Their
ROM differential gate passes 6,489,603 and 1,572,864 cases respectively.
Existing word-mixer and generator regressions pass. See `binary_direction.md`
for evidence, preconditions and limitations. No timed game routine was replaced.

## Next investigation

Study $81:F722, another direction calculation. It uses the hardware divider
($4204/$4206, $4214), an 8-bit runtime table at $7F:0000, and ROM octant tables
at $81:F7C3/$81:F7CB. Its axis convention differs from F638. Preserve the
divisor-low-byte behavior when the reduced magnitude equals 256; do not assume
ordinary mathematical division by 256. Inspect the LakeSnes divider behavior
and test with hardware-backed reference accesses before claiming equivalence.

Continue after that with callers or other bounded game algorithms. Keep data
tables caller-supplied, distinguish inferred gameplay purpose from established
math, and report actual test coverage rather than a whole-game percentage.
