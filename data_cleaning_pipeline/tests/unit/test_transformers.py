"""
Unit tests for transformer components.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timezone

from data_cleaning_pipeline.core.audit import AuditLogger
from data_cleaning_pipeline.transformers import (
    TimestampNormalizer,
    AmountCurrencyNormalizer,
    CategoricalCanonicalizer,
    DuplicateHandler,
    OutlierDetector,
    MissingnessHandler
)


class TestTimestampNormalizer:
    """Test cases for TimestampNormalizer."""

    @pytest.fixture
    def normalizer(self):
        """Create timestamp normalizer with audit logger."""
        audit_logger = AuditLogger()
        return TimestampNormalizer(audit_logger)

    def test_parse_timestamp_valid(self, normalizer):
        """Test parsing valid timestamps."""
        timestamp_str = "2024-01-01 10:00:00"
        parsed, confidence = normalizer.parse_timestamp(0, timestamp_str)
        
        assert parsed is not None
        assert confidence > 0.8
        assert isinstance(parsed, pd.Timestamp)

    def test_parse_timestamp_invalid(self, normalizer):
        """Test parsing invalid timestamps."""
        timestamp_str = "invalid_timestamp"
        parsed, confidence = normalizer.parse_timestamp(0, timestamp_str)
        
        assert parsed is None
        assert confidence == 0.0

    def test_normalize_timestamps(self, normalizer):
        """Test timestamp normalization on DataFrame."""
        df = pd.DataFrame({
            'timestamp': ['2024-01-01 10:00:00', '2024-01-01 11:00:00'],
            'other_col': [1, 2]
        })
        
        result = normalizer.normalize_timestamps(df)
        
        assert 'timestamp_confidence' in result.columns
        assert len(result) == len(df)


class TestAmountCurrencyNormalizer:
    """Test cases for AmountCurrencyNormalizer."""

    @pytest.fixture
    def normalizer(self):
        """Create amount normalizer with audit logger."""
        audit_logger = AuditLogger()
        return AmountCurrencyNormalizer(audit_logger)

    def test_parse_amount_numeric(self, normalizer):
        """Test parsing numeric amounts."""
        amount, confidence = normalizer.parse_amount(0, 100.50)
        
        assert amount == 100.50
        assert confidence == 1.0

    def test_parse_amount_string(self, normalizer):
        """Test parsing string amounts."""
        amount, confidence = normalizer.parse_amount(0, "$100.50")
        
        assert amount == 100.50
        assert confidence > 0.8

    def test_parse_currency_valid(self, normalizer):
        """Test parsing valid currencies."""
        currency, confidence = normalizer.parse_currency(0, "USD")
        
        assert currency == "USD"
        assert confidence == 1.0

    def test_parse_currency_symbol(self, normalizer):
        """Test parsing currency symbols."""
        currency, confidence = normalizer.parse_currency(0, "$")
        
        assert currency == "USD"
        assert confidence > 0.8


class TestCategoricalCanonicalizer:
    """Test cases for CategoricalCanonicalizer."""

    @pytest.fixture
    def canonicalizer(self):
        """Create categorical canonicalizer with audit logger."""
        audit_logger = AuditLogger()
        return CategoricalCanonicalizer(audit_logger)

    def test_build_canonical_mapping(self, canonicalizer):
        """Test building canonical mappings."""
        df = pd.DataFrame({
            'channel': ['online', 'Online', 'ONLINE', 'web', 'mobile']
        })
        
        mapping = canonicalizer.build_canonical_mapping(df, 'channel')
        
        assert isinstance(mapping, dict)
        assert len(mapping) > 0

    def test_apply_canonical_mapping(self, canonicalizer):
        """Test applying canonical mappings."""
        df = pd.DataFrame({
            'channel': ['online', 'Online', 'ONLINE']
        })
        
        # Build mapping first
        canonicalizer.build_canonical_mapping(df, 'channel')
        
        # Apply mapping
        result = canonicalizer.apply_canonical_mapping(df, 'channel')
        
        assert len(result) == len(df)


class TestDuplicateHandler:
    """Test cases for DuplicateHandler."""

    @pytest.fixture
    def handler(self):
        """Create duplicate handler with audit logger."""
        audit_logger = AuditLogger()
        return DuplicateHandler(audit_logger)

    def test_detect_exact_duplicates(self, handler):
        """Test exact duplicate detection."""
        df = pd.DataFrame({
            'col1': [1, 2, 1, 3],
            'col2': ['a', 'b', 'a', 'c']
        })
        
        result = handler.detect_exact_duplicates(df)
        
        assert 'is_exact_duplicate' in result.columns
        assert result['is_exact_duplicate'].sum() > 0

    def test_generate_row_signature(self, handler):
        """Test row signature generation."""
        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        signature = handler.generate_row_signature(row, ['col1', 'col2'])
        
        assert isinstance(signature, str)
        assert len(signature) > 0


class TestOutlierDetector:
    """Test cases for OutlierDetector."""

    @pytest.fixture
    def detector(self):
        """Create outlier detector with audit logger."""
        audit_logger = AuditLogger()
        return OutlierDetector(audit_logger)

    def test_detect_statistical_outliers(self, detector):
        """Test statistical outlier detection."""
        df = pd.DataFrame({
            'amount': [1, 2, 3, 4, 5, 100]  # 100 is an outlier
        })
        
        outliers = detector.detect_statistical_outliers(df, 'amount')
        
        assert isinstance(outliers, pd.Series)
        assert len(outliers) == len(df)

    def test_detect_ml_outliers(self, detector):
        """Test ML-based outlier detection."""
        df = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5, 100],
            'feature2': [1, 2, 3, 4, 5, 100]
        })
        
        outliers = detector.detect_ml_outliers(df, ['feature1', 'feature2'])
        
        assert isinstance(outliers, pd.Series)
        assert len(outliers) == len(df)


class TestMissingnessHandler:
    """Test cases for MissingnessHandler."""

    @pytest.fixture
    def handler(self):
        """Create missingness handler with audit logger."""
        audit_logger = AuditLogger()
        return MissingnessHandler(audit_logger)

    def test_analyze_missingness(self, handler):
        """Test missingness analysis."""
        df = pd.DataFrame({
            'col1': [1, 2, np.nan, 4],
            'col2': ['a', 'b', 'c', 'd']
        })
        
        analysis = handler.analyze_missingness(df)
        
        assert isinstance(analysis, dict)
        assert 'col1' in analysis

    def test_impute_column_median(self, handler):
        """Test median imputation."""
        df = pd.DataFrame({
            'amount': [1, 2, np.nan, 4, 5]
        })
        
        result = handler.impute_column(df, 'amount', strategy='median')
        
        assert not result['amount'].isna().any()
        assert len(result) == len(df)
