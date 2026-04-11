# Python Best Practices for pythonbox Project

## Project Information
- **Language**: Python 3.8+
- **Package Manager**: pip
- **Virtual Environment**: venv
- **Main Source Directory**: `src/main/python/`

## Code Style and Formatting

### PEP 8 Compliance
- Follow PEP 8 style guide for Python code
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 79 characters for code, 72 for docstrings
- Use snake_case for functions and variables
- Use PascalCase for class names
- Use UPPER_CASE for constants

### Imports
- Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
- Use absolute imports when possible
- Avoid wildcard imports (`from module import *`)

### Naming Conventions
- **Variables**: `lowercase_with_underscores`
- **Functions**: `lowercase_with_underscores()`
- **Classes**: `CapitalizedWords`
- **Constants**: `UPPER_CASE_WITH_UNDERSCORES`
- **Private methods/attributes**: `_leading_underscore`

## Type Hints and Documentation

### Type Hints
Use type hints for function signatures:
```python
def query_by_city(city: str) -> int:
    """Query DynamoDB table by city name."""
    count: int = 0
    # implementation
    return count
```

### Logging
Use Python's logging module instead of print statements:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Processing started")
logger.warning("Resource not found")
logger.error("Operation failed", exc_info=True)
```

## File Structure

### Module Organization
- Keep related functionality together in modules
- Use `__init__.py` files to expose public APIs
- Use `if __name__ == '__main__':` for script entry points

### Configuration
- Store configuration in separate files (e.g., `config.py` or `.ini` files)
- Use environment variables for sensitive data
- Never commit credentials to version control

## Testing

### Unit Tests
- Ignore tests since i am only playing around.

## Virtual Environment

### Always Use Virtual Environments
```bash
# Create
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Deactivate
deactivate
```

### Requirements Management
- Keep `requirements.txt` updated
- Pin versions for production: `boto3==1.26.0`
- Use ranges for development: `boto3>=1.26.0`
- Consider using `requirements-dev.txt` for development dependencies

## Code Quality Tools

### Black (Code Formatter)
```bash
black src/main/python/
```

### Flake8 (Linter)
```bash
flake8 src/main/python/ --max-line-length=88
```

### MyPy (Type Checker)
```bash
mypy src/main/python/ --ignore-missing-imports
```

### Pre-commit Hooks
Consider using pre-commit hooks:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

## Performance Considerations

### List Comprehensions
Prefer list comprehensions over map/filter when readable:
```python
# Good
squares = [x**2 for x in range(10)]

# Also good for readability
result = [process(item) for item in items if item.is_valid()]
```

### Generators
Use generators for large datasets:
```python
def read_large_file(file_path):
    with open(file_path) as f:
        for line in f:
            yield line.strip()
```

### Context Managers
Use context managers for resource management:
```python
class DynamoDBConnection:
    def __enter__(self):
        self.client = boto3.client('dynamodb')
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        # cleanup
        pass
```

### Dataclasses
Use dataclasses for simple data structures (Python 3.7+):
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CustomerOrder:
    order_id: int
    customer_id: str
    item_name: str
    quantity: int = 1
    status: Optional[str] = None
```

### Path Handling
Use `pathlib` for path operations:
```python
from pathlib import Path

file_path = Path('src/main/python/data.csv')
if file_path.exists():
    data = file_path.read_text()
```

### String Formatting
Use f-strings (Python 3.6+):
```python
# Good
message = f"Processing {count} items from {city}"

# Avoid
message = "Processing {} items from {}".format(count, city)
message = "Processing " + str(count) + " items from " + city
```

## Simulations and Visualizations

When asked to create a simulation, **always**:

1. **Use `matplotlib` for visualization** — animate with `matplotlib.animation.FuncAnimation` and render with `PillowWriter`.
2. **Save a GIF output** next to the script via `Path(__file__).parent / "<name>.gif"`.
3. **Show the animation in the UI** — after `anim.save(...)`, always call `plt.show()` so the live window opens, then `plt.close(fig)`:
   ```python
   anim.save(str(out_path), writer=animation.PillowWriter(fps=FPS))
   print(f"Saved → {out_path}")
   print("Displaying animation in UI window …")
   plt.show()
   plt.close(fig)
   ```
3. **Precompute all frames first**, then render once — follow the pattern in `physics/qualia_modality.py`, `physics/free_wave_packet.py`, and `math/fractal.py`.
4. **Use the macOS-friendly backend fallback** at the top of every new simulation file:
   ```python
   import matplotlib
   for _backend in ("MacOSX", "TkAgg", "Qt5Agg", "Agg"):
       try:
           matplotlib.use(_backend)
           import matplotlib.pyplot as _probe  # noqa: F401
           break
       except Exception:
           continue
   ```
5. **Print progress** with `print()` so the user can follow along (e.g. "Pre-computing …", "Rendering N frames to GIF …", "Saved → <path>").
6. **Place all work at module level** (not inside `__main__`) to match the repo convention; keep `if __name__ == "__main__": pass` at the bottom.
7. **Dependencies**: use `numpy` + `matplotlib` + `pillow` (already in `requirements.txt`); add any new dependency to `requirements.txt`.

## When Editing Code

1. **Read existing code style** and match it
2. **Add type hints** to new functions
4. **Handle exceptions** appropriately
5. **Use logging** instead of print statements
6. **Update requirements.txt** if adding new dependencies
