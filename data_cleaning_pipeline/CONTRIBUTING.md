# Contributing to Data Cleaning Pipeline

Thank you for your interest in contributing to the Data Cleaning Pipeline! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/data-cleaning-pipeline.git
   cd data-cleaning-pipeline
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev,docs]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 🧪 Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pre-commit**: Automated checks

Run all checks before committing:
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Testing

Write tests for new features and bug fixes:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/data_cleaning_pipeline

# Run specific tests
pytest tests/unit/test_pipeline.py
```

### Documentation

Update documentation for new features:

- API documentation in docstrings
- User guide updates in `docs/`
- Example notebooks in `examples/`

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment information**:
   - Python version
   - Operating system
   - Package versions

2. **Reproducible example**:
   - Minimal code to reproduce the issue
   - Expected vs actual behavior
   - Error messages and stack traces

3. **Additional context**:
   - Steps to reproduce
   - Any workarounds you've found

## ✨ Feature Requests

For new features, please:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and expected behavior
3. **Provide examples** of how the feature would be used
4. **Consider implementation complexity** and maintenance burden

## 🔧 Pull Request Process

### Before Submitting

1. **Ensure tests pass**: `pytest`
2. **Check code style**: `black src/ tests/ && flake8 src/ tests/`
3. **Update documentation** for new features
4. **Add tests** for new functionality
5. **Update CHANGELOG.md** with your changes

### PR Guidelines

1. **Use descriptive titles** and descriptions
2. **Link related issues** using keywords (e.g., "Fixes #123")
3. **Keep PRs focused** - one feature/fix per PR
4. **Request reviews** from maintainers
5. **Respond to feedback** promptly

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] All existing tests pass

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 🏗️ Architecture Guidelines

### Adding New Transformers

1. **Create transformer class** in `src/data_cleaning_pipeline/transformers/`
2. **Inherit from base patterns** used by existing transformers
3. **Include audit logging** for all transformations
4. **Add comprehensive tests**
5. **Update pipeline integration**

### Adding New Validators

1. **Create validator class** in `src/data_cleaning_pipeline/validators/`
2. **Follow Great Expectations patterns**
3. **Include detailed error messages**
4. **Add validation tests**

### Performance Considerations

- **Use vectorized operations** where possible
- **Consider memory usage** for large datasets
- **Add performance benchmarks** for critical paths
- **Document performance characteristics**

## 📋 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update version numbers** in `setup.py` and `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Run full test suite**
4. **Update documentation**
5. **Create GitHub release**

## 🎯 Areas for Contribution

### High Priority

- **Performance optimizations** for large datasets
- **Additional data sources** (JSON, XML, etc.)
- **Enhanced validation rules**
- **Better error handling and recovery**

### Medium Priority

- **New outlier detection methods**
- **Advanced imputation strategies**
- **Integration with popular ML frameworks**
- **Cloud deployment examples**

### Low Priority

- **Additional language support**
- **GUI interface**
- **Real-time processing capabilities**

## 📞 Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bug reports and feature requests
- **Email**: dev@datacleaningpipeline.com for private matters

## 🏆 Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **Project documentation** for major features

Thank you for contributing to the Data Cleaning Pipeline! 🎉
