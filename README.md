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

# Windows:
venv\Scripts\activate
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

### Run Individual Scripts

```bash
# From project root
python src/main/python/Shipping.py

# Or navigate to the script directory
cd src/main/python
python Shipping.py

# Run specific modules
python -m storage.amazon-storage
python -m basic.arrays
python -m json.csv_to_json
```

### Run with Arguments

```bash
# Pass arguments to scripts
python src/main/python/storage/query_dynamodb.py
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
pythonbox/
├── requirements.txt          # Python dependencies
├── src/main/python/         # Main source code
│   ├── basic/              # Basic Python examples
│   ├── storage/            # AWS S3 and DynamoDB examples
│   ├── json/               # JSON processing
│   ├── oo/                 # Object-oriented examples
│   └── files/              # File handling examples
```

## Development

### Code Formatting

```bash
# Format code with black
black src/main/python/

# Check code style with flake8
flake8 src/main/python/
```

### Type Checking

```bash
# Run mypy for type checking
mypy src/main/python/
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


