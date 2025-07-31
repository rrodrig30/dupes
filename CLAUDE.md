# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a duplicate file detection project designed to identify duplicate files in directories. The project is in early planning stages, with only a design document (`dupes.md`) currently present.

## Architecture

Based on the design document, the planned architecture includes:

- **Flask Web Application**: Web-based interface for duplicate file detection
- **File Processing Module**: Handles directory scanning, file hashing (SHA-256), and metadata extraction
- **Duplicate Detection Module**: Compares file hashes to identify duplicates
- **Web Interface**: HTML templates for user interaction

### Planned File Structure
```
dupes/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   └── models.py
├── utils/
│   ├── file_processor.py
│   └── duplicate_manager.py
├── templates/
│   ├── index.html
│   └── results.html
├── static/
├── config.py
├── requirements.txt
└── run.py
```

## Development Commands

Since this is a new Python project with no implementation yet, standard Python development commands would be:

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt

# Run the application (when implemented)
python run.py

# Run tests (when implemented)
python -m pytest

# Code quality checks
python -m flake8
python -m black .
```

## Key Design Decisions

- **Hashing Algorithm**: SHA-256 for file duplicate detection
- **Web Framework**: Flask for the web interface
- **Development Approach**: Agile with Test-Driven Development (TDD)
- **File Processing**: Recursive directory scanning with metadata extraction

## Current Status

- Project is in planning phase
- Only design document exists (`dupes.md`)
- No implementation files present yet
- Git repository initialized but empty of source code