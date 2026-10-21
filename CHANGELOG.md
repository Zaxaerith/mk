# Changelog

All notable changes to this project. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow SemVer once the first one is tagged (none yet). Earlier milestones:
[docs/history.md](docs/history.md).

## [Unreleased]

### Added
- `--headless` and `--record out.mp4` (snesrecomp's shared flags): no window, audio or
  pacing; frames piped to ffmpeg. Headless runs lock live input like `SMK_HEADLESS`.
- CI build on every push and PR (Windows, MSVC + vcpkg SDL2).
- `CHANGELOG.md`, `ROADMAP.md`, `CONTRIBUTING.md`, `CONTRIBUTORS.md`,
  `docs/architecture.md`, `docs/autogen.md`, `docs/history.md`.

### Changed
- snesrecomp bumped 41c5603 → b73fdcd (snesrecomp #1–#6: headless/record, lockstep
  validation, `autogen.py` in the toolkit, LakeSnes mouse fix). Checked headless:
  title screen at frame 600 as before.
- README reorganised to the house layout; reference sections moved to `docs/`,
  screenshots to `docs/screenshots/`.

### Fixed
- The launcher did not link with SDL2main on mingw (no `SDL_main`): `main.c`
  now includes `<SDL.h>`.

### Removed
- `src/recomp/smk_autogen.c` is no longer tracked: it is `autogen.py` output
  generated from the ROM. Generate it locally ([docs/autogen.md](docs/autogen.md));
  the build works without it.
