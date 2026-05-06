# Code Quality & Lint Checklist
> Audio Identification System — automated evaluation readiness

---

## 0. Project Setup

- [ ] Project root has `pyproject.toml` or `ruff.toml` with all rules configured
- [ ] `.pre-commit-config.yaml` exists and is active (`pre-commit install` has been run)
- [ ] `requirements.txt` or `pyproject.toml` lists all dependencies with pinned versions
- [ ] `.gitignore` excludes `__pycache__`, `.mypy_cache`, `.ruff_cache`, `*.pyc`, `*.egg-info`
- [ ] Project runs with a single entry point command (e.g., `python main.py` or `python -m src.main`)
- [ ] All dependencies install cleanly with `pip install -r requirements.txt`

---

## 1. Ruff Configuration (`ruff.toml`)

Paste this exactly into your `ruff.toml` at the project root:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
src = ["src"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes — unused vars, imports
    "I",    # isort — import ordering
    "N",    # pep8 naming conventions
    "UP",   # pyupgrade — modern Python syntax
    "B",    # bugbear — common bug patterns
    "C4",   # flake8-comprehensions — cleaner list/dict comprehensions
    "SIM",  # simplify — removes redundant code patterns
    "ANN",  # type annotations on all functions
    "D",    # pydocstyle — docstrings
    "PT",   # pytest style
    "RET",  # return statement consistency
    "ERA",  # no commented-out code
    "PIE",  # misc cleanups
    "TRY",  # exception handling best practices
]
ignore = [
    "D203",   # conflicts with D211
    "D212",   # conflicts with D213
    "ANN101", # self annotation not required
    "ANN102", # cls annotation not required
    "TRY003", # allow long exception messages
]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.isort]
known-first-party = ["src"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"
```

- [ ] `ruff.toml` exists at project root with above config
- [ ] `ruff check .` returns zero errors
- [ ] `ruff format --check .` returns zero errors (no formatting changes needed)

---

## 2. Type Checking (`mypy`)

```toml
# add to pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
warn_return_any = true
warn_unused_configs = true
```

- [ ] `mypy src/` returns zero errors
- [ ] Every function has a return type annotation (`-> None`, `-> list[int]`, etc.)
- [ ] Every function parameter has a type annotation
- [ ] No use of `Any` type without an explicit `# type: ignore` comment with a reason
- [ ] No untyped `dict` or `list` — use `dict[str, int]`, `list[tuple[int, int]]`, etc.

---

## 3. Style & Readability

- [ ] All variable names are descriptive (`hash_value` not `h`, `time_offset` not `to`)
- [ ] All function names use `snake_case`
- [ ] All class names use `PascalCase`
- [ ] All module-level constants use `UPPER_SNAKE_CASE`
- [ ] No single-letter variable names except loop counters (`i`, `j`) and well-known math (`n`, `x`)
- [ ] Indentation is 4 spaces throughout — no tabs
- [ ] No trailing whitespace on any line
- [ ] Every file ends with a single newline
- [ ] No lines exceed 100 characters
- [ ] Imports are ordered: stdlib → third-party → local (enforced by ruff `I` rules)
- [ ] No wildcard imports (`from module import *`)
- [ ] No commented-out code left in the codebase (enforced by `ERA` rule)

---

## 4. Logic & Error Prevention

- [ ] No unused variables anywhere (enforced by `F841`)
- [ ] No unused imports anywhere (enforced by `F401`)
- [ ] No unreachable code after `return` or `raise` (enforced by `F`)
- [ ] No bare `except:` — always catch specific exceptions (`except ValueError:`, `except OSError:`)
- [ ] No empty `except` blocks — always log or re-raise
- [ ] No mutable default arguments (`def f(x=[])` → use `None` and assign inside)
- [ ] No `== None` — use `is None` / `is not None`
- [ ] No `== True` / `== False` — use truthiness directly
- [ ] All file handles use context managers (`with open(...) as f:`)
- [ ] No `print()` statements in library code — use `logging` module
- [ ] Logging is configured at the entry point only, not inside modules

---

## 5. Docstrings (Google style)

Every public symbol must have a docstring. Format:

```python
def fingerprint(pcm_array: np.ndarray, sample_rate: int = 11025) -> list[int]:
    """Generate combinatorial hashes from a PCM audio array.

    Args:
        pcm_array: Mono audio samples as a float32 numpy array.
        sample_rate: Sampling rate in Hz. Defaults to 11025.

    Returns:
        List of 32-bit integer hashes representing spectral fingerprints.

    Raises:
        ValueError: If pcm_array is empty or has fewer than 1024 samples.
    """
```

- [ ] Every module has a module-level docstring (one line minimum)
- [ ] Every public class has a class docstring
- [ ] Every public method/function has a docstring with Args, Returns, Raises sections
- [ ] Private functions (`_name`) have at least a one-line docstring
- [ ] No docstring says "TODO" or is a placeholder

---

## 6. Architecture & Modularity

- [ ] Project follows this structure (or equivalent):

```
src/
├── __init__.py
├── config.py          # all constants and configuration
├── models.py          # Song dataclass, result types
├── ingestor.py        # dataset loading and validation
├── fingerprinter.py   # STFT, peak picking, hash generation
├── indexer.py         # building and querying the hash index
├── matcher.py         # offset histogram, confidence scoring
├── query_pipeline.py  # end-to-end query orchestration
├── metrics.py         # latency tracking, accuracy evaluation
└── health.py          # health check / status reporting
main.py                # entry point only — no logic here
```

- [ ] No module exceeds 300 lines
- [ ] No function exceeds 40 lines
- [ ] No function has more than 4 parameters (use a config dataclass if needed)
- [ ] Feature extraction is behind an abstract interface / base class
- [ ] Swapping the fingerprinting strategy requires changing only one file
- [ ] The matcher has no knowledge of audio decoding
- [ ] The ingestor has no knowledge of fingerprinting
- [ ] No circular imports between modules

---

## 7. Configuration — No Magic Numbers

All tunable values must live in `config.py`, never inline:

```python
# config.py
SAMPLE_RATE: int = 11025
FFT_WINDOW_SIZE: int = 4096
FFT_OVERLAP: float = 0.5
PEAK_NEIGHBORHOOD_SIZE: int = 20
FAN_VALUE: int = 10
MIN_HASH_TIME_DELTA: int = 0
MAX_HASH_TIME_DELTA: int = 200
FINGERPRINT_REDUCTION: int = 20
CONFIDENCE_THRESHOLD: float = 0.4
MIN_QUERY_DURATION_SEC: float = 1.0
MIN_QUERY_RMS: float = 0.001
```

- [ ] `config.py` exists with all constants defined and type-annotated
- [ ] Zero raw numbers in `fingerprinter.py`, `matcher.py`, `indexer.py`
- [ ] Zero raw numbers in `query_pipeline.py`
- [ ] Constants are imported from `config.py` everywhere they are used

---

## 8. Tests (`pytest`)

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--strict-markers -v"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]

[tool.coverage.report]
fail_under = 80
```

- [ ] `tests/` directory exists at project root
- [ ] `pytest` runs with zero failures
- [ ] Test coverage is ≥ 80% (`pytest --cov=src --cov-fail-under=80`)
- [ ] `test_fingerprinter.py` — unit tests for hash generation with known inputs
- [ ] `test_matcher.py` — unit tests for offset histogram and confidence scoring
- [ ] `test_ingestor.py` — tests for corrupt/missing data handling
- [ ] `test_query_pipeline.py` — tests for invalid input rejection
- [ ] `test_integration.py` — one end-to-end test: fingerprint a file, query it, expect match
- [ ] No test uses `time.sleep()` — mock time-dependent code
- [ ] Test file names start with `test_`
- [ ] Every test function name starts with `test_`
- [ ] No test has bare `assert` without a message — use `assert x == y, "reason"`

---

## 9. Pre-commit Hooks (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [numpy, types-all]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements       # catches leftover breakpoint() / pdb
      - id: check-added-large-files
```

- [ ] `.pre-commit-config.yaml` exists at project root
- [ ] `pre-commit install` has been run (hooks fire on `git commit`)
- [ ] `pre-commit run --all-files` passes with zero failures

---

## 10. CI/CD (`github/workflows/ci.yml`)

```yaml
name: CI

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ruff mypy pytest pytest-cov pre-commit
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy src/
      - run: pytest --cov=src --cov-fail-under=80
```

- [ ] CI config exists and runs on every push
- [ ] CI runs `ruff check .` — must pass
- [ ] CI runs `ruff format --check .` — must pass
- [ ] CI runs `mypy src/` — must pass
- [ ] CI runs `pytest --cov=src --cov-fail-under=80` — must pass
- [ ] No step is marked `continue-on-error: true`

---

## 11. Final Automated Check — Run This Before Submitting

```bash
# 1. Auto-fix everything possible
ruff check . --fix
ruff format .

# 2. Verify zero remaining lint errors
ruff check .

# 3. Verify zero type errors
mypy src/

# 4. Verify all tests pass with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# 5. Verify all pre-commit hooks pass
pre-commit run --all-files
```

- [ ] All 5 commands above exit with code `0`
- [ ] No `# noqa` suppression comments unless accompanied by a written reason
- [ ] No `# type: ignore` comments unless accompanied by a written reason
- [ ] No `TODO` or `FIXME` comments in any file submitted for evaluation

---

## Quick Reference — Install Commands

```bash
pip install ruff mypy pytest pytest-cov pre-commit --break-system-packages
pre-commit install
ruff check . --fix && ruff format .
```
