# Python Development Environment Setup

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### 1. Install Python

**macOS:**
```bash
brew update
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

### 2. Create Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies:

```bash
# Navigate to project directory
cd /path/to/pythonbox

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Or install specific packages
pip install boto3 requests matplotlib
```

## Running Code

### Check Python Version

```bash
python --version
# Should output: Python 3.x.x
```

### Install Modules (Gradle-style monorepo)

This repo is split into independent Python modules under `modules/`,
each with its own `pyproject.toml` (like Gradle subprojects).

```bash
# Install every module in editable mode
make install

# Or with uv workspace support
uv sync

# Or via requirements (editable installs)
pip install -r requirements.txt
```

### Run Individual Scripts

```bash
# From project root
python modules/core/src/pythonbox_core/Shipping.py

# Math / physics simulations
python modules/math/src/pythonbox_math/fractal.py
python modules/physics/src/pythonbox_physics/non_relativistic_schrodinger_equation.py

# AWS storage demos
python modules/storage/src/pythonbox_storage/query_dynamodb.py
```

### Run with Arguments

```bash
# Pass arguments to scripts
python modules/storage/src/pythonbox_storage/query_dynamodb.py
```

## AWS Configuration

For AWS-related scripts (boto3), configure your credentials:

```bash
# Configure AWS credentials
aws configure

# Or manually create ~/.aws/credentials
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY

[aws-federated]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
EOF

# Set default region in ~/.aws/config
cat > ~/.aws/config << EOF
[default]
region = us-west-2
output = json
EOF
```

## Project Structure

```
pythonbox/                        # root workspace (pyproject.toml)
├── Makefile                      # Gradle-style tasks: install, format, lint
├── pyproject.toml                # workspace coordinator (uv)
├── requirements.txt              # aggregated editable installs
└── modules/                      # subprojects (each has pyproject.toml)
    ├── basic/src/pythonbox_basic/
    ├── core/src/pythonbox_core/
    ├── files/src/pythonbox_files/
    ├── json/src/pythonbox_json/
    ├── math/src/pythonbox_math/
    ├── oo/src/pythonbox_oo/
    ├── physics/src/pythonbox_physics/
    └── storage/src/pythonbox_storage/
```

## Development

### Code Formatting

```bash
make format    # black all modules
make lint      # flake8 all modules
make typecheck # mypy all modules
```

### Testing

```bash
# Run tests with pytest
pytest tests/
```

## Deactivating Virtual Environment

```bash
deactivate
```


## Example: Using Python Requests Library

```bash
$ python3
Python 3.x.x (default, ...)
>>> import requests
>>> r = requests.get('http://api.github.com')
>>> print(r)
<Response [200]>
>>> r.text
# JSON response output
```

## Environment Variables

If needed, set custom Python path:

```bash
# macOS/Linux
export PYTHONPATH="${PYTHONPATH}:/path/to/your/modules"

# Or in virtual environment (preferred method)
source venv/bin/activate
```

## Additional Resources

- [Python Documentation](https://docs.python.org/3/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Requests Documentation](https://requests.readthedocs.io/)


