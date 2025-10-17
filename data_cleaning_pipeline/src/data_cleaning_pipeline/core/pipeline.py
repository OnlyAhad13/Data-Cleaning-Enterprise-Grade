"""
Main orchestration pipeline that ties all components together.
Implements reversible, auditable, production-grade data cleaning.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

from .schema import DataSchema
from .audit import AuditLogger
from .profiler import DataProfiler
from ..transformers.timestamp_normalizer import TimestampNormalizer
from ..transformers.amount_normalizer import AmountCurrencyNormalizer
from ..transformers.categorical_canonicalizer import CategoricalCanonicalizer
from ..transformers.duplicate_handler import DuplicateHandler
from ..transformers.outlier_detector import OutlierDetector
from ..transformers.missingness_handler import MissingnessHandler
from ..validators.data_validator import DataValidator


class DataCleaningPipeline:
    """Main orchestration pipeline that ties all components together."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.audit_logger = AuditLogger()
        self.schema = DataSchema()
        
        # Initialize components
        self.profiler = None
        self.timestamp_normalizer = TimestampNormalizer(self.audit_logger)
        self.amount_normalizer = AmountCurrencyNormalizer(self.audit_logger)
        self.categorical_canonicalizer = CategoricalCanonicalizer(self.audit_logger)
        self.duplicate_handler = DuplicateHandler(self.audit_logger)
        self.outlier_detector = OutlierDetector(self.audit_logger)
        self.missingness_handler = MissingnessHandler(self.audit_logger)
        self.validator = DataValidator(self.schema)
        
        # Store original data
        self.original_df = None
        self.cleaned_df = None
        self.profile_results = None
        self.validation_results = None
        
    def fit(self, df: pd.DataFrame) -> 'DataCleaningPipeline':
        """
        Fit the pipeline on training data.
        Learns mappings, imputation values, etc.
        """
        logging.info("Starting pipeline fitting...")
        
        # Store original
        self.original_df = df.copy()
        
        # Profile data
        logging.info("Step 1/10: Profiling data...")
        self.profiler = DataProfiler(df)
        self.profile_results = self.profiler.generate_profile()
        
        # Build canonical mappings
        logging.info("Step 2/10: Building canonical mappings...")
        if 'channel' in df.columns:
            self.categorical_canonicalizer.build_canonical_mapping(
                df, 'channel', valid_values=self.schema.VALID_CHANNELS
            )
        
        if 'merchant_name' in df.columns:
            self.categorical_canonicalizer.build_canonical_mapping(
                df, 'merchant_name'
            )
        
        logging.info("Pipeline fitting complete.")
        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data through the cleaning pipeline.
        All operations are logged and reversible.
        """
        logging.info("Starting data transformation...")
        
        df_clean = df.copy()
        
        # Step 1: Normalize timestamps
        logging.info("Step 3/10: Normalizing timestamps...")
        if 'timestamp' in df_clean.columns:
            df_clean = self.timestamp_normalizer.normalize_timestamps(df_clean)
        
        # Step 2: Normalize amounts and currencies
        logging.info("Step 4/10: Normalizing amounts and currencies...")
        if 'amount' in df_clean.columns and 'currency' in df_clean.columns:
            df_clean = self.amount_normalizer.normalize_amounts_currencies(df_clean)
        
        # Step 3: Canonicalize categorical fields
        logging.info("Step 5/10: Canonicalizing categorical fields...")
        for col in ['channel', 'merchant_name']:
            if col in df_clean.columns:
                df_clean = self.categorical_canonicalizer.apply_canonical_mapping(df_clean, col)
        
        # Step 4: Detect duplicates
        logging.info("Step 6/10: Detecting duplicates...")
        df_clean = self.duplicate_handler.detect_exact_duplicates(df_clean)
        if 'timestamp' in df_clean.columns:
            df_clean = self.duplicate_handler.detect_fuzzy_duplicates(
                df_clean,
                key_columns=['customer_id', 'amount', 'merchant_name']
            )
        
        # Step 5: Detect outliers
        logging.info("Step 7/10: Detecting outliers...")
        numeric_cols = ['amount', 'amount_usd'] if 'amount_usd' in df_clean.columns else ['amount']
        df_clean = self.outlier_detector.detect_all_outliers(df_clean, numeric_cols)
        
        # Step 6: Handle missing values
        logging.info("Step 8/10: Handling missing values...")
        missing_analysis = self.missingness_handler.analyze_missingness(df_clean)
        for col, analysis in missing_analysis.items():
            if analysis['percentage'] > 0 and analysis['percentage'] < 80:
                df_clean = self.missingness_handler.impute_column(df_clean, col)
        
        # Step 7: Validate
        logging.info("Step 9/10: Validating cleaned data...")
        self.validation_results = self.validator.validate_all(df_clean)
        
        self.cleaned_df = df_clean
        logging.info("Step 10/10: Transformation complete.")
        
        return df_clean
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform in one step"""
        self.fit(df)
        return self.transform(df)
    
    def get_audit_summary(self) -> Dict:
        """Get summary of all transformations"""
        return self.audit_logger.get_summary()
    
    def save_artifacts(self, output_dir: str):
        """Save all pipeline artifacts"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save cleaned data
        if self.cleaned_df is not None:
            self.cleaned_df.to_parquet(output_path / 'cleaned_data.parquet', index=False)
        
        # Save audit log
        self.audit_logger.save_audit_log(str(output_path / 'audit_log.parquet'))
        
        # Save profile
        if self.profile_results:
            with open(output_path / 'data_profile.json', 'w') as f:
                json.dump(self.profile_results, f, indent=2, default=str)
        
        # Save validation results
        if self.validation_results:
            with open(output_path / 'validation_results.json', 'w') as f:
                json.dump(self.validation_results, f, indent=2, default=str)
        
        # Save audit summary
        audit_summary = self.get_audit_summary()
        with open(output_path / 'audit_summary.json', 'w') as f:
            json.dump(audit_summary, f, indent=2)
        
        logging.info(f"All artifacts saved to {output_dir}")
    
    def generate_report(self) -> str:
        """Generate human-readable cleaning report"""
        report = []
        report.append("=" * 80)
        report.append("DATA CLEANING PIPELINE REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Dataset info
        if self.original_df is not None:
            report.append(f"Original Dataset: {self.original_df.shape[0]:,} rows × {self.original_df.shape[1]} columns")
        if self.cleaned_df is not None:
            report.append(f"Cleaned Dataset: {self.cleaned_df.shape[0]:,} rows × {self.cleaned_df.shape[1]} columns")
        report.append("")
        
        # Audit summary
        audit_summary = self.get_audit_summary()
        report.append("TRANSFORMATION SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Transformations: {audit_summary.get('total_transformations', 0):,}")
        report.append(f"Columns Affected: {audit_summary.get('columns_affected', 0)}")
        report.append(f"Average Confidence: {audit_summary.get('avg_confidence', 0):.2%}")
        report.append(f"Low Confidence (<0.7): {audit_summary.get('low_confidence_count', 0):,}")
        report.append("")
        
        # Rules applied
        if 'rules_applied' in audit_summary:
            report.append("RULES APPLIED")
            report.append("-" * 80)
            for rule, count in sorted(audit_summary['rules_applied'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {rule}: {count:,}")
            report.append("")
        
        # Validation results
        if self.validation_results:
            summary = self.validation_results.get('summary', {})
            report.append("VALIDATION RESULTS")
            report.append("-" * 80)
            report.append(f"Total Checks: {summary.get('total_checks', 0)}")
            report.append(f"Passed: {summary.get('passed_checks', 0)}")
            report.append(f"Failed: {summary.get('failed_checks', 0)}")
            report.append(f"Pass Rate: {summary.get('pass_rate', 0):.1%}")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
