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
src
├── fixture_generator/   # Fixture generation scripts
│   └── main.py          # Entry point
└── fixture_data/        # Generated fixture data
    ├── fixtures/        # JSON fixture files by category
    ├── fixture_type_mappings.py  # Auto-generated type mappings
    └── shared_types.py  # Custom fixture types
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

# Install dependencies
pip install -e .
```

### Generate Fixtures

```bash
# Set your test account session token
export NICONICO_SESSION='your_test_account_session_token'

# Run fixture generation
python src/fixture_generator/main.py
```

### Update Fixtures in Music Assistant

After generating fixtures, copy them to the Music Assistant repository:

```bash
# Copy entire fixture_data directory
cp -r src/fixture_data /path/to/music-assistant/server/tests/providers/nicovideo/
```

The generated files include:
- `src/fixture_data/fixtures/**/*.json` - API response fixtures organized by category
- `src/fixture_data/fixture_type_mappings.py` - Auto-generated type mappings for deserialization

## Security Note

**NEVER commit fixtures containing real user data!**

- Always use a dedicated test account
- Review generated fixtures before committing
- The `NICONICO_SESSION` environment variable prevents accidental credential commits

## License

Apache-2.0 - Same as Music Assistant
