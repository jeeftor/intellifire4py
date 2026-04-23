# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.5.1] - 2026-04-23

### Fixed

- **Type checking**: Resolved all `ty` type errors across the codebase
  - Fixed `unified_fireplace.py`: replaced deprecated `.json()` with `model_dump_json()`, widened `async_validate_connectivity` timeout to `float`, fixed `.name` attribute access on `object` type, added `# type: ignore` for intentional dynamic mode assignment in `_switch_read_mode`
  - Fixed `cloud_api.py`: made `cookie_jar` parameter optional (`CookieJar | None = None`), replaced `hasattr(e, "response")` pattern with `getattr` to avoid unresolved-attribute errors
  - Fixed `udp.py`: widened `timeout` parameters to `float` throughout, typed `self.transport` as `asyncio.DatagramTransport | None`, added None guard before `transport.close()`
  - Fixed `model.py`: replaced `cookies.get(key, "UNSET").value` with explicit None checks to satisfy union-attr type errors
  - Fixed `cloud_interface.py`: replaced `inspect.currentframe().f_code` with a None-safe frame lookup, replaced `# type: ignore[union-attr]` on session calls with an explicit `None` guard, removed stale `# type: ignore` from commented-out code
  - Fixed `const.py`: removed now-unnecessary `# type: ignore` on `aenum` import and `MultiValueEnum` subclass
  - Fixed `local_api.py`: removed unnecessary `# type: ignore` on `challenge` keyword argument

- **Test fixes**: Updated tests to satisfy strict type checking
  - `test_cloud_api_extended.py`, `test_coverage_boost.py`: replaced `RequestInfo(url=str, headers={})` with properly typed `yarl.URL` and `CIMultiDictProxy` arguments; extracted `_make_request_info` helper
  - `test_local_api.py`, `conftest.py`: replaced `ClientResponseError(None, ...)` with a valid `RequestInfo` object
  - `test_unified.py`, `test_coverage_push.py`: added `# type: ignore` on intentional method monkey-patching
  - `test_model_dataclass.py`: switched from alias names (`temperature`, `setpoint`) to field names (`temperature_c`, `raw_thermostat_setpoint`) for Pydantic model construction
  - `test_cloud_api.py`: removed now-unnecessary `# type: ignore` directives from test function signatures
  - `test_coverage_push.py`: replaced fallback-path test for deprecated `.json()` with a test of the current `model_dump_json()` path

- **Pre-commit**: Switched `mypy` hook from `pre-commit/mirrors-mypy` (broken cached env due to `pathspec` incompatibility) to a local hook using the project's `.venv/bin/mypy`

## [4.5.0] - prior

See git history.
