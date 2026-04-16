# Copilot instructions for pythonbox

## Big picture
- This repository is a loose collection of standalone Python scripts under `src/main/python/`, not a packaged application. Keep changes local to the script you are editing unless the user explicitly asks for shared abstractions.
- The codebase has two main families:
	- `math/` and `physics/`: educational numerical visualizations that precompute arrays, animate with `matplotlib`, and usually save GIFs with `PillowWriter`.
	- `storage/`, `json/`, `files/`, `basic/`: small demos for AWS, HTTP, local files, JSON, and language features.
- The `docs/` folder is part of the product: long-form explanations mirror the simulations. Preserve docstring references such as `docs/06_fractals_julia_set.md` and `docs/07_non_relativistic_schrodinger_equation.md` when extending those scripts.

## Working style to preserve
- Prefer script-style entry points with `if __name__ == "__main__":` and direct `print()` status output. Many files are designed to be run manually rather than imported.
- Do not aggressively refactor modules into packages or shared utilities unless requested; several scripts intentionally duplicate setup to stay self-contained.
- Keep the existing educational tone in simulation docstrings, titles, and comments.

## Running code
- Environment setup is lightweight: create a venv and run `pip install -r requirements.txt` from the repo root.
- There is no discovered `tests/` directory or central test runner. Validate by running the specific script you changed.
- Common manual runs from the repo root:
	- `python src/main/python/math/fractal.py`
	- `python src/main/python/physics/non_relativistic_schrodinger_equation.py`
	- `python src/main/python/storage/write_to_dynamodb.py`
- Some filenames contain hyphens, for example `src/main/python/storage/amazon-storage.py` and `src/main/python/storage/scan-buckets.py`; run these as files, not with `python -m`.

## Project-specific patterns
- Simulation scripts often precompute all frames first, then render once. Follow the existing pattern in `math/fractal.py`, `physics/free_wave_packet.py`, and `physics/non_relativistic_schrodinger_equation.py` instead of introducing streaming or class-heavy designs.
- `physics/spacetime_curvature.py` contains a macOS-friendly `matplotlib` backend fallback chain. Preserve that pattern if you touch rendering startup code.
- Output-path handling is inconsistent by design: newer physics scripts save next to the script via `__file__`, while older scripts like `math/fractal.py` save to the current working directory. Preserve the behavior of the file you are editing unless asked to normalize it.
- Several utility scripts execute work at import time and depend on the current working directory. Examples: `json/csv_to_json.py`, `json/json_reader.py`, and `files/config.py`. Avoid changing relative-path assumptions unless the task is specifically about path robustness.

## Editing guidance for agents
- Prefer small, surgical fixes that keep each script runnable on its own.
- When adding dependencies for visualization output, remember GIF generation relies on `pillow` and many science scripts rely on `numpy` + `matplotlib`.
- If you change user-facing text, keep it beginner-friendly and explanatory rather than terse or framework-heavy.
