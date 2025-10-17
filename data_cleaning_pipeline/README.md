# Data Cleaning Pipeline

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Enterprise-grade data cleaning and validation framework for production data pipelines.

## 🚀 Features

- **Comprehensive Data Profiling**: Deep analysis of data quality, distributions, and patterns
- **Robust Timestamp Normalization**: Handles multiple formats, timezones, and ambiguous dates
- **Smart Amount & Currency Parsing**: Supports symbols, formats, and automatic USD conversion
- **Advanced Duplicate Detection**: Both exact and fuzzy duplicate identification
- **Multi-Method Outlier Detection**: Statistical (MAD, IQR, Z-score) and ML-based (Isolation Forest)
- **Strategic Missing Value Handling**: Context-aware imputation strategies
- **Categorical Canonicalization**: Fuzzy matching and learned embeddings for text normalization
- **Complete Audit Trail**: Every transformation is logged with confidence scores
- **Great Expectations-Style Validation**: Comprehensive business rule validation
- **Gold Test Set Generation**: Quality measurement through synthetic corruption testing
- **Production Ready**: Reversible, auditable, and scalable

## 📦 Installation

### From Source

```bash
git clone https://github.com/your-org/data-cleaning-pipeline.git
cd data-cleaning-pipeline
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/your-org/data-cleaning-pipeline.git
cd data-cleaning-pipeline
pip install -e ".[dev,docs]"
```

## 🚀 Quick Start

```python
import pandas as pd
from data_cleaning_pipeline import DataCleaningPipeline

# Load your data
df = pd.read_csv('your_data.csv')

# Initialize and run the pipeline
pipeline = DataCleaningPipeline()
cleaned_df = pipeline.fit_transform(df)

# Generate comprehensive report
print(pipeline.generate_report())

# Save all artifacts
pipeline.save_artifacts('output/')
```

## 📊 Pipeline Components

### Core Components

- **`DataCleaningPipeline`**: Main orchestration class
- **`DataSchema`**: Business rules and schema definitions
- **`AuditLogger`**: Complete transformation audit trail
- **`DataProfiler`**: Comprehensive data analysis

### Transformers

- **`TimestampNormalizer`**: Multi-format timestamp parsing
- **`AmountCurrencyNormalizer`**: Amount and currency standardization
- **`CategoricalCanonicalizer`**: Text field normalization
- **`DuplicateHandler`**: Advanced duplicate detection
- **`OutlierDetector`**: Statistical and ML-based outlier detection
- **`MissingnessHandler`**: Strategic missing value imputation

### Validators

- **`DataValidator`**: Business rule and schema validation

### Utilities

- **`GoldTestSetGenerator`**: Quality measurement tools

## 🔧 Configuration

The pipeline can be configured through the `DataSchema` class:

```python
from data_cleaning_pipeline import DataSchema

# Customize business rules
schema = DataSchema()
schema.AMOUNT_MAX = 5000000.0  # Increase max amount
schema.VALID_CURRENCIES.add('BTC')  # Add new currency
```

## 📈 Advanced Usage

### Custom Transformations

```python
from data_cleaning_pipeline import DataCleaningPipeline
from data_cleaning_pipeline.transformers import TimestampNormalizer

# Use individual components
normalizer = TimestampNormalizer(audit_logger)
df_normalized = normalizer.normalize_timestamps(df)
```

### Quality Measurement

```python
from data_cleaning_pipeline.utils import GoldTestSetGenerator

# Generate gold test set
generator = GoldTestSetGenerator()
corrupted_df, ground_truth = generator.create_from_corruptions(clean_df)

# Evaluate cleaning quality
metrics = generator.evaluate_cleaning_pipeline(cleaned_df, ground_truth)
print(f"Overall accuracy: {metrics['overall']['accuracy']:.2%}")
```

### Audit Trail

```python
# Get detailed audit information
audit_summary = pipeline.get_audit_summary()
print(f"Total transformations: {audit_summary['total_transformations']}")
print(f"Average confidence: {audit_summary['avg_confidence']:.2%}")
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/data_cleaning_pipeline

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests
```

## 📚 Documentation

- [API Reference](docs/api_reference.md)
- [User Guide](docs/user_guide.md)
- [Developer Guide](docs/developer_guide.md)
- [Examples](examples/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of pandas, scikit-learn, and scipy
- Inspired by Great Expectations validation framework
- Designed for enterprise data science workflows

## 📞 Support

- 📧 Email: support@datacleaningpipeline.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/data-cleaning-pipeline/issues)
- 📖 Documentation: [Read the Docs](https://data-cleaning-pipeline.readthedocs.io/)

---

**Made with ❤️ for the data science community**
