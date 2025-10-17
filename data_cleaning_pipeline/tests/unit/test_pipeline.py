"""
Unit tests for the main DataCleaningPipeline class.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timezone

from data_cleaning_pipeline import DataCleaningPipeline, DataSchema


class TestDataCleaningPipeline:
    """Test cases for the main pipeline class."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'timestamp': ['2024-01-01 10:00:00', '2024-01-01 11:00:00', '2024-01-01 12:00:00'],
            'amount': [100.0, 200.0, 300.0],
            'currency': ['USD', 'EUR', 'GBP'],
            'merchant_name': ['Amazon', 'Walmart', 'Target'],
            'customer_id': ['CUST001', 'CUST002', 'CUST003'],
            'channel': ['online', 'in-store', 'mobile'],
            'is_fraud': [0, 0, 1]
        })

    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = DataCleaningPipeline()
        assert pipeline.original_df is None
        assert pipeline.cleaned_df is None
        assert pipeline.profile_results is None
        assert pipeline.validation_results is None

    def test_pipeline_fit(self, sample_data):
        """Test pipeline fitting."""
        pipeline = DataCleaningPipeline()
        pipeline.fit(sample_data)
        
        assert pipeline.original_df is not None
        assert pipeline.profile_results is not None
        assert pipeline.profiler is not None

    def test_pipeline_transform(self, sample_data):
        """Test pipeline transformation."""
        pipeline = DataCleaningPipeline()
        pipeline.fit(sample_data)
        cleaned_df = pipeline.transform(sample_data)
        
        assert cleaned_df is not None
        assert len(cleaned_df) == len(sample_data)
        assert pipeline.cleaned_df is not None

    def test_pipeline_fit_transform(self, sample_data):
        """Test combined fit and transform."""
        pipeline = DataCleaningPipeline()
        cleaned_df = pipeline.fit_transform(sample_data)
        
        assert cleaned_df is not None
        assert len(cleaned_df) == len(sample_data)
        assert pipeline.original_df is not None
        assert pipeline.cleaned_df is not None

    def test_audit_summary(self, sample_data):
        """Test audit summary generation."""
        pipeline = DataCleaningPipeline()
        pipeline.fit_transform(sample_data)
        
        summary = pipeline.get_audit_summary()
        assert isinstance(summary, dict)
        assert 'total_transformations' in summary

    def test_report_generation(self, sample_data):
        """Test report generation."""
        pipeline = DataCleaningPipeline()
        pipeline.fit_transform(sample_data)
        
        report = pipeline.generate_report()
        assert isinstance(report, str)
        assert "DATA CLEANING PIPELINE REPORT" in report
        assert "TRANSFORMATION SUMMARY" in report

    def test_save_artifacts(self, sample_data, tmp_path):
        """Test artifact saving."""
        pipeline = DataCleaningPipeline()
        pipeline.fit_transform(sample_data)
        
        output_dir = str(tmp_path / "artifacts")
        pipeline.save_artifacts(output_dir)
        
        # Check that files were created
        import os
        assert os.path.exists(output_dir)
        assert os.path.exists(os.path.join(output_dir, "cleaned_data.parquet"))
        assert os.path.exists(os.path.join(output_dir, "audit_log.parquet"))
        assert os.path.exists(os.path.join(output_dir, "data_profile.json"))
        assert os.path.exists(os.path.join(output_dir, "validation_results.json"))
        assert os.path.exists(os.path.join(output_dir, "audit_summary.json"))


class TestDataSchema:
    """Test cases for the DataSchema class."""

    def test_schema_initialization(self):
        """Test schema initialization."""
        schema = DataSchema()
        assert isinstance(schema.REQUIRED_COLUMNS, list)
        assert isinstance(schema.EXPECTED_DTYPES, dict)
        assert isinstance(schema.VALID_CURRENCIES, set)
        assert isinstance(schema.VALID_CHANNELS, set)

    def test_required_columns(self):
        """Test required columns definition."""
        schema = DataSchema()
        expected_columns = [
            'transaction_id', 'timestamp', 'amount', 'currency',
            'merchant_name', 'customer_id', 'channel', 'is_fraud'
        ]
        assert schema.REQUIRED_COLUMNS == expected_columns

    def test_business_rules(self):
        """Test business rule definitions."""
        schema = DataSchema()
        assert schema.AMOUNT_MIN == 0.0
        assert schema.AMOUNT_MAX == 1000000.0
        assert 'USD' in schema.VALID_CURRENCIES
        assert 'online' in schema.VALID_CHANNELS
