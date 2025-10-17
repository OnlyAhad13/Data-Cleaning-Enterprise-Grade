"""
Data Cleaning Pipeline - Enterprise-grade data cleaning and validation framework.

A comprehensive, production-ready data cleaning pipeline that provides:
- Robust data profiling and analysis
- Multi-format timestamp normalization
- Amount and currency parsing with exchange rate conversion
- Categorical field canonicalization with fuzzy matching
- Advanced duplicate detection (exact and fuzzy)
- Statistical and ML-based outlier detection
- Strategic missing value imputation
- Comprehensive data validation
- Complete audit trail and reversibility
- Gold test set generation for quality measurement

Main Components:
- DataCleaningPipeline: Main orchestration class
- DataSchema: Business rules and schema definitions
- AuditLogger: Complete transformation audit trail
- Various transformers for specific data cleaning tasks
- DataValidator: Great Expectations-style validation
"""

from .core.pipeline import DataCleaningPipeline
from .core.schema import DataSchema
from .core.audit import AuditLogger
from .core.profiler import DataProfiler

__version__ = "1.0.0"
__author__ = "Data Cleaning Pipeline Team"

__all__ = [
    "DataCleaningPipeline",
    "DataSchema", 
    "AuditLogger",
    "DataProfiler"
]
