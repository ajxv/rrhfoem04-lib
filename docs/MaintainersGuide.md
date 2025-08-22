# Maintainers Guide

Comprehensive reference for maintaining `rrhfoem04-lib`. This document is modular: each top‑level section can be updated independently without impacting others. Keep sections concise; append new subsections rather than rewriting history.

> Tip: When you change behavior, update the relevant section and add a short dated note under "Revision Log" at the end.

## 1. Project Overview
- Purpose: Python interface for the RRHFOEM04 RFID/NFC reader (ISO15693, ISO14443A/Mifare operations).
- Design Goals: Reliability (timing + retries), clear errors, simple API surface, minimal external deps.
- Core Module: `src/rrhfoem04/core.py` — houses the `RRHFOEM04` class.
- Public Entry: `rrhfoem04/__init__.py` exports the class & exception types.

## 2. Package Layout
```
src/rrhfoem04/
  __init__.py          # Public exports
  core.py              # Main reader implementation
  constants.py         # Protocol constants, command bytes, timeouts
  exceptions.py        # Custom exception hierarchy
  utils.py             # Helper structures (e.g., RRHFOEM04Result)

docs/                  # Project documentation
  PublishingToPyPI.md  # Release steps
  MaintainersGuide.md  # (this file)

tests/                 # Basic test(s) & future test expansion
pyproject.toml         # Build & metadata
requirements.txt       # (Optional lock / dev syncing)
```

## 3. Public API Surface
Primary consumer‑facing calls (non-internal, stable-ish):
- Connection & lifecycle: `RRHFOEM04(auto_connect=True, log_to_file=False)`, `close()`, context manager `with RRHFOEM04() as r:`
- General device ops: `getReaderInfo()`, `buzzer_on()`, `buzzer_off()`, `buzzer_beep()`
- ISO15693: `ISO15693_singleSlotInventory()`, `ISO15693_16SlotInventory()`, block read/write single & multiple, `ISO15693_writeAFI()`
- ISO14443A/Mifare: inventory, select, authenticate, `ISO14443A_mifareRead()`, `ISO14443A_mifareWrite()`

Return Type: All high-level operations return `RRHFOEM04Result(success: bool, message: str, data: Any|None)` — prefer extending `data` rather than altering existing keys to preserve backward compatibility.

## 4. Logging Policy
- Default: Console (stderr) only at DEBUG for development clarity.
- Optional file logging: pass `log_to_file=True` to add `rrhfoem04.log` handler.
- Do not globally reconfigure logging beyond `basicConfig` once; per-instance file handlers only.
- When adding new operations, log:
  - DEBUG: inputs (sanitized), decision branches, retries
  - INFO: successful high-level operations
  - WARNING: recoverable anomalies
  - ERROR: operation failures (before raising / returning failure)

## 5. Error Handling Strategy
Custom exceptions in `exceptions.py` map to logical layers:
- `ConnectionError`: USB/HID open or lost connection
- `CommunicationError`: Transport issues (timeouts, malformed frames)
- `CommandError`: Device returned explicit failure status
- `ValidationError`: Parameter issues detected client-side
- `TagError`: Issues specific to card/tag presence or state
- `AuthenticationError`: Auth sequence failures

Guidelines:
- Validate parameters early; raise `ValidationError` or return failure result.
- Wrap low-level unexpected exceptions into the appropriate custom exception.
- Never leak raw stack traces to `RRHFOEM04Result.message`; keep messages concise.

## 6. Protocol & Command Encoding
Central constants live in `constants.py`:
- Command arrays (prefixed `CMD_...`) represent the bytes excluding CRC & HID report prefix (0x00 is prepended at send time).
- Timing constants: `COMMAND_INTERVAL`, `DEFAULT_TIMEOUT`, `RETRY_DELAY`, `MAX_RETRIES`, `BUFFER_SIZE`.
- Status codes: `STATUS_SUCCESS` etc.

For exhaustive frame formats, flag meanings, and full command tables, see `RRHFOEM04_ProtocolReference.md` (kept separate to avoid duplication here). When updating protocol behavior, modify that reference first, then adjust constants and this section if needed.

When adding a new command:
1. Add raw command definition + any new status codes in `constants.py`.
2. Implement wrapper method in `core.py` using `_send_command()`.
3. Parse response defensively: length, status, data boundaries.
4. Return `RRHFOEM04Result`.
5. Add tests (see Section 11).

## 7. Internal Mechanics (`core.py`)
Key helpers:
- `_connect()` opens HID and sets non-blocking mode.
- `_calc_crc()` computes CCITT-16 (initial 0xFFFF, poly 0x1021, invert at end).
- `_send_command()` handles timing gap, CRC append, write, response polling with retries, and hex list response formatting.
- `_byte_list_to_hex_string()` utility for formatting.

State fields:
- `self.device`: HID device instance or `None`.
- `self._last_command_time`: enforces `COMMAND_INTERVAL`.
- `self._mifare_selected_uid` & `self._mifare_auth_blocks`: track selected Mifare card & authenticated blocks to optimize ops.

## 8. Adding Features / Extending Protocols
Checklist:
1. Identify command spec (datasheet/protocol doc).
2. Define constants (command header, flags, status codes).
3. Implement method with logging & validation.
4. Write parsing logic referencing spec offsets.
5. Add tests (success + failure path).
6. Update this guide (Sections 3 & 6) + README if user-visible.
7. Bump version (see Section 10) if public API changes.

## 9. Backward Compatibility Guidelines
- Avoid changing existing method signatures; add optional params with defaults.
- Deprecate by logging a WARNING once per process and documenting in README.
- Keep existing `RRHFOEM04Result.data` schema stable; add new keys nested if complex.

## 10. Release Process (Summary)
See `PublishingToPyPI.md` for full details.
Quick steps:
```bash
# bump version in pyproject.toml
python3 -m pip install --upgrade build twine
rm -rf dist build ./*.egg-info
python3 -m build
python3 -m twine upload dist/*
```
Tag:
```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

## 11. Testing Strategy
Current tests minimal — expand with:
- Unit tests for helpers (`_calc_crc`, parsing logic) using crafted frames.
- Integration tests that mock `hid.device` to simulate responses.
- Error condition tests (timeouts, bad status, invalid params).

Mocking HID:
- Patch `hid.device` with a fake object providing `open`, `set_nonblocking`, `write`, `read`, `close`.
- Preload a queue of responses for successive `read()` calls.

Test Naming & Layout:
- File-per-feature as growth occurs: `tests/test_iso15693.py`, `tests/test_iso14443a.py` etc.
- Use `pytest` (consider adding as a dev dependency).

## 12. Performance Considerations
- Minimize blocking: `_send_command()` already enforces minimal sleep + non-blocking reads.
- Drain stale responses before sending new commands to prevent frame mixing.
- Batch multi-block operations when reading/writing larger data.

Future Ideas:
- Optional async interface (asyncio) delegating to thread executor.
- Adaptive retry/backoff if noise detected.

## 13. Security & Safety Notes
- Mifare default keys are insecure; encourage users to supply real keys.
- Avoid logging full keys or sensitive data; mask except for last 2 bytes if needed.
- Watch for untrusted user input passed directly into command arrays; validate length & hex content.

## 14. Documentation Conventions
- Method docstrings: summary line, protocol context, argument details, returns, exceptions.
- Keep README user-focused; move deep implementation notes here.
- Use present tense (“Returns”, “Raises”).

## 15. Issue triage
Label suggestions:
- `bug`, `enhancement`, `question`, `protocol-update`, `good-first-issue`, `needs-info`.
Triage flow:
1. Reproduce.
2. Classify (bug/enhancement/question).
3. Add minimal failing test if bug.
4. Fix or tag `help-wanted`.

## 16. Coding Standards
- Python >= 3.12 features allowed (pattern matching if beneficial).
- Maintain readability: small methods, clear names.
- Prefer early returns over deep nesting.
- Type hints for public methods; internal helpers may omit if obvious.

## 17. Dependency Policy
Runtime deps kept minimal (`hidapi`, `setuptools`).
Add new runtime deps only if substantial benefit; prefer optional extras.
Document security implications of new deps.

## 18. Versioning
Semantic-ish: PATCH for fixes/internal, MINOR for new backward-compatible features, MAJOR for breaking changes (none yet).
If a user-visible behavior change occurs, bump accordingly and note in `PublishingToPyPI.md`.

## 19. Support Matrix
- OS: Linux primarily tested (hidapi). macOS may work; Windows unverified.
- Python: 3.12+ per `pyproject.toml`.

## 20. Roadmap (Editable)
- nothing planned

## 21. Revision Log
Add entries here (newest on top):
- 2025-08-22: Initial maintainer guide created.

---
Maintainers: Keep this file authoritative; link related docs instead of duplicating content.
