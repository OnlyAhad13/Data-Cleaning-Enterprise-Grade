"""
Integration tests for the complete data cleaning pipeline.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timezone

from data_cleaning_pipeline import DataCleaningPipeline


class TestFullPipeline:
    """Integration tests for the complete pipeline."""

    @pytest.fixture
    def synthetic_data(self):
        """Create synthetic data with various quality issues."""
        np.random.seed(42)
        
        data = {
            'transaction_id': [f'TXN{i:04d}' for i in range(100)],
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='1H'),
            'amount': np.random.lognormal(4, 1, 100),
            'currency': np.random.choice(['USD', 'EUR', 'GBP'], 100),
            'merchant_name': np.random.choice(['Amazon', 'Walmart', 'Target'], 100),
            'customer_id': [f'CUST{i:03d}' for i in range(100)],
            'channel': np.random.choice(['online', 'in-store', 'mobile'], 100),
            'is_fraud': np.random.choice([0, 1], 100, p=[0.9, 0.1])
        }
        
        df = pd.DataFrame(data)
        
        # Introduce quality issues
        # 1. Corrupt some timestamps
        corrupt_idx = np.random.choice(df.index, size=10, replace=False)
        for idx in corrupt_idx:
            df.at[idx, 'timestamp'] = df.at[idx, 'timestamp'].strftime('%d/%m/%Y %H:%M:%S')
        
        # 2. Add currency symbols to amounts
        corrupt_idx = np.random.choice(df.index, size=15, replace=False)
        for idx in corrupt_idx:
            df.at[idx, 'amount'] = f"${df.at[idx, 'amount']:.2f}"
        
        # 3. Add typos to merchant names
        corrupt_idx = np.random.choice(df.index, size=5, replace=False)
        for idx in corrupt_idx:
            merchant = df.at[idx, 'merchant_name']
            df.at[idx, 'merchant_name'] = merchant + ' Inc'
        
        # 4. Introduce missing values
        for col in ['merchant_name', 'channel']:
            missing_idx = np.random.choice(df.index, size=3, replace=False)
            df.loc[missing_idx, col] = np.nan
        
        # 5. Create some duplicates
        dup_idx = np.random.choice(df.index, size=5, replace=False)
        df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)
        
        return df

    def test_full_pipeline_execution(self, synthetic_data):
        """Test complete pipeline execution."""
        pipeline = DataCleaningPipeline()
        
        # Run the pipeline
        cleaned_df = pipeline.fit_transform(synthetic_data)
        
        # Basic assertions
        assert cleaned_df is not None
        assert len(cleaned_df) >= len(synthetic_data)  # May have added columns
        assert pipeline.original_df is not None
        assert pipeline.cleaned_df is not None
        assert pipeline.profile_results is not None
        assert pipeline.validation_results is not None

    def test_pipeline_audit_trail(self, synthetic_data):
        """Test that audit trail is properly maintained."""
        pipeline = DataCleaningPipeline()
        pipeline.fit_transform(synthetic_data)
        
        # Check audit summary
        summary = pipeline.get_audit_summary()
        assert isinstance(summary, dict)
        assert 'total_transformations' in summary
        assert 'columns_affected' in summary
        assert 'avg_confidence' in summary

    def test_pipeline_artifacts(self, synthetic_data, tmp_path):
        """Test that all artifacts are saved correctly."""
        pipeline = DataCleaningPipeline()
        pipeline.fit_transform(synthetic_data)
        
        output_dir = str(tmp_path / "artifacts")
        pipeline.save_artifacts(output_dir)
        
        # Check that all expected files exist
        import os
        expected_files = [
            'cleaned_data.parquet',
            'audit_log.parquet',
            'data_profile.json',
            'validation_results.json',
            'audit_summary.json'
        ]
        
        for file in expected_files:
            assert os.path.exists(os.path.join(output_dir, file))

    def test_pipeline_report_generation(self, synthetic_data):
        """Test report generation."""
        pipeline = DataCleaningPipeline()
        pipeline.fit_transform(synthetic_data)
        
        report = pipeline.generate_report()
        
        # Check report content
        assert isinstance(report, str)
        assert "DATA CLEANING PIPELINE REPORT" in report
        assert "TRANSFORMATION SUMMARY" in report
        assert "VALIDATION RESULTS" in report

    def test_pipeline_with_clean_data(self):
        """Test pipeline with already clean data."""
        # Create clean data
        clean_data = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
            'timestamp': pd.to_datetime(['2024-01-01 10:00:00', '2024-01-01 11:00:00', '2024-01-01 12:00:00']),
            'amount': [100.0, 200.0, 300.0],
            'currency': ['USD', 'USD', 'USD'],
            'merchant_name': ['Amazon', 'Walmart', 'Target'],
            'customer_id': ['CUST001', 'CUST002', 'CUST003'],
            'channel': ['online', 'in-store', 'mobile'],
            'is_fraud': [0, 0, 1]
        })
        
        pipeline = DataCleaningPipeline()
        cleaned_df = pipeline.fit_transform(clean_data)
        
        # Should still work with clean data
        assert cleaned_df is not None
        assert len(cleaned_df) == len(clean_data)

    @pytest.mark.slow
    def test_pipeline_performance(self):
        """Test pipeline performance with larger dataset."""
        # Create larger dataset
        n_rows = 10000
        np.random.seed(42)
        
        data = {
            'transaction_id': [f'TXN{i:06d}' for i in range(n_rows)],
            'timestamp': pd.date_range('2024-01-01', periods=n_rows, freq='1min'),
            'amount': np.random.lognormal(4, 1, n_rows),
            'currency': np.random.choice(['USD', 'EUR', 'GBP'], n_rows),
            'merchant_name': np.random.choice(['Amazon', 'Walmart', 'Target'], n_rows),
            'customer_id': [f'CUST{i:04d}' for i in range(n_rows)],
            'channel': np.random.choice(['online', 'in-store', 'mobile'], n_rows),
            'is_fraud': np.random.choice([0, 1], n_rows, p=[0.95, 0.05])
        }
        
        df = pd.DataFrame(data)
        
        pipeline = DataCleaningPipeline()
        
        # Time the execution
        import time
        start_time = time.time()
        cleaned_df = pipeline.fit_transform(df)
        execution_time = time.time() - start_time
        
        # Basic performance assertions
        assert cleaned_df is not None
        assert execution_time < 60  # Should complete within 60 seconds
        assert len(cleaned_df) == len(df)
