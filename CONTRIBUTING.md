# Contributing to DeepSeek-OCR-SDK

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/deepseek-ocr-sdk.git
cd deepseek-ocr-sdk
```

### 2. Set Up Development Environment

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write clear, concise code
- Add type hints to all functions
- Include docstrings (Google style)
- Update tests as needed

### 3. Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=deepseek_ocr --cov-report=html

# Run specific test
uv run pytest tests/test_client.py::test_parse
```

### 4. Check Code Quality

```bash
# Format code
uv run black deepseek_ocr/
uv run isort deepseek_ocr/

# Check linting
uv run flake8 deepseek_ocr/ --max-line-length=88 --extend-ignore=E203,W503

# Type checking
uv run mypy deepseek_ocr/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
# or
git commit -m "fix: resolve bug in parse method"
```

Commit message format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Build/tooling changes

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Standards

### Python Style

- Follow PEP 8
- Use black for formatting (line length: 88)
- Use isort for import sorting
- Maximum line length: 88 characters

### Type Hints

All public functions must have type hints:

```python
from typing import Union, Optional, List
from pathlib import Path

def parse_document(
    file_path: Union[str, Path],
    mode: Optional[str] = None
) -> str:
    """Parse document and return text."""
    ...
```

### Docstrings

Use Google style docstrings:

```python
def parse_document(file_path: str, mode: str = "free_ocr") -> str:
    """
    Parse document and extract text.

    Args:
        file_path: Path to document file.
        mode: OCR mode to use.

    Returns:
        Extracted text in Markdown format.

    Raises:
        FileProcessingError: If file cannot be processed.

    Example:
        >>> client = DeepSeekOCR(api_key="xxx")
        >>> text = client.parse("document.pdf")
    """
    ...
```

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Use pytest fixtures for common setup
- Test both success and error cases
- Aim for >80% coverage

```python
import pytest
from deepseek_ocr import DeepSeekOCR, APIError

def test_parse_success():
    """Test successful document parsing."""
    client = DeepSeekOCR(api_key="test_key")
    # Test implementation
    ...

def test_parse_invalid_file():
    """Test parsing with invalid file."""
    client = DeepSeekOCR(api_key="test_key")
    with pytest.raises(FileProcessingError):
        client.parse("nonexistent.pdf")
```

## Documentation

### Update Documentation

When adding features:

1. Update README.md if user-facing
2. Add/update docstrings
3. Update API_REFERENCE.md if API changes
4. Add examples if applicable

### Documentation Standards

- Use clear, concise language
- Include code examples
- Use Mermaid for flowcharts/diagrams
- Maintain bilingual docs (EN + CN)

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass (`uv run pytest`)
- [ ] Code is formatted (`black`, `isort`)
- [ ] Type checking passes (`mypy`)
- [ ] Linting passes (`flake8`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass
- [ ] Code formatted
- [ ] Documentation updated
- [ ] CHANGELOG updated
```

## Code Review Process

1. Maintainer reviews PR
2. Feedback provided if needed
3. Author addresses feedback
4. PR approved and merged

## Questions?

- Open an issue for bugs
- Start a discussion for questions
- Join our community chat

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
