# Roadmap

## Next

- **Grow the recompiled-shell path** (`SMK_SHELLS=1`) to drive gameplay. The shells
  render the menus, but the Mode-7 race's multi-frame init/fade-in needs the real
  frame. See `docs/smk_flow_re.md`.
- **More recompiled functions**: the long-term goal is replacing real-frame with
  recompiled C. `autogen.py` (now in snesrecomp) plus lockstep validation is the path.
- **Conformance harness** with a pass count in the README and a regression gate,
  built on snesrecomp's lockstep validation (Mario Paint's `tools/conformance.py`
  is the model). Today the oracle diffs (`tools/diff_snapshots.py`) are run by hand.
- **Quick-start `Setup.cmd`** per the house rules: prerequisite checks, ROM prompt,
  build, launcher shortcut. Players will get the recomp-launcher installer; that is
  being added repo by repo.
- **Netplay polish**: rollback or over-the-wire desync detection; drop straight into
  2-player on connect.

## Deferred

- Contributor PR #1 (recompiler correctness work) is under review; see the PR thread.

## Out of scope

- Distributing the ROM, anything extracted from it, or generated source.
