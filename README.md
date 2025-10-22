# Music Assistant Niconico Fixtures

Fixture generation and maintenance tools for [Music Assistant](https://github.com/music-assistant/server)'s Niconico provider.

## Overview

This repository contains tools to generate and maintain test fixtures for the Niconico music provider in Music Assistant. These fixtures are JSON snapshots of actual API responses used for testing the provider's converters and business logic.

## Why a Separate Repository?

This tooling is kept separate from both:
- **niconico.py** - Pure API client library, should remain dependency-free
- **Music Assistant server** - Production code repository, shouldn't include fixture generation infrastructure

## Structure

```
.
├── scripts/           # Fixture generation scripts
├── fixtures/          # Generated fixture JSON files
├── pyproject.toml     # Project dependencies
└── README.md
```

## Usage

### Prerequisites

1. A Niconico test account (do NOT use your personal account)
2. Python 3.12+
3. Session token from your test account

### Setup

```bash
# Clone the repository
git clone https://github.com/Shi-553/music-assistant-nicovideo-fixtures.git
cd music-assistant-nicovideo-fixtures

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install this package
pip install -e .

# Install Music Assistant server in editable mode (required dependency)
# This assumes you have the Music Assistant server repository cloned
pip install -e /path/to/music-assistant/server
```

**Note:** This tool requires the Music Assistant server to be installed as it uses the provider's service managers and converters for fixture generation.

### Generate Fixtures

```bash
# Set your test account session token
export NICONICO_SESSION='your_test_account_session_token'

# Run fixture generation
python scripts/main.py
```

### Update Fixtures in Music Assistant

After generating fixtures, copy them to the Music Assistant repository:

```bash
# From this repository root
cp -r fixtures/* /path/to/music-assistant/server/tests/providers/nicovideo/fixtures/
```

## Security Note

**NEVER commit fixtures containing real user data!**

- Always use a dedicated test account
- Review generated fixtures before committing
- The `NICONICO_SESSION` environment variable prevents accidental credential commits

## License

Apache-2.0 - Same as Music Assistant
