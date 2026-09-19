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

## Checkpoint 2 — hardware-divider byte direction

Recovered $81:F722 as `smk_vector_direction8`. The ROM CPU gate routes divider
accesses into LakeSnes's actual register implementation and passes 6,489,603
cases; vector and cell gates remain green. The zero-divisor boundary at a
reduced magnitude of 256, overlapping scratch-word read and differing axis
convention are preserved. See `binary_direction.md` for the timing/API limits.

## Next investigation

Checkpoint 3 recovered $80:86A0 as `smk_project_coordinates`; all 4,194,304
ROM tests pass, including skipped paths with no destination writes. See
`binary_projection.md`. Its ROL sequence simplifies to extracting bits 14..29.

Study $80:A027 next: it compares adjacent object keys, conditionally exchanges
two order entries, updates each object's reverse slot reference, then walks
backward. Check zero sentinels, equal keys and predecessor flag bit $20 before
describing it as an insertion-order repair operation.

Continue after that with callers or other bounded game algorithms. Keep data
tables caller-supplied, distinguish inferred gameplay purpose from established
math, and report actual test coverage rather than a whole-game percentage.
