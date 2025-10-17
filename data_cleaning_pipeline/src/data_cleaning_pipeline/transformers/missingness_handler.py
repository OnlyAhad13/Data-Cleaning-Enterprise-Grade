"""
Strategic imputation based on data type and patterns
"""

import pandas as pd
import numpy as np
from typing import Dict
from ..core.audit import AuditLogger


class MissingnessHandler:
    """Strategic imputation based on data type and patterns"""

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.imputation_values = {}
    
    def analyze_missingness(self, df: pd.DataFrame) -> Dict:
        """Analyze missingness patterns"""
        missing_analysis = {}

        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_analysis[col] = {
                    'count': int(missing_count),
                    'percentage': float(missing_count/len(df)*100),
                    'pattern': self._detect_missing_pattern(df, col)
                }
        return missing_analysis
    
    def _detect_missing_pattern(self, df: pd.DataFrame, col: str) -> str:
        """
        Detects is missingness is random or not
        """
        missing_mask = df[col].isnull()

        # Simple heuristic: if >80% missing, likely systematic
        missing_pct = missing_mask.mean()
        if missing_pct > 0.8:
            return 'systematic'
        elif missing_pct < 0.05:
            return 'random'
        else:
            return 'mixed'
        
    def impute_column(
        self, 
        df: pd.DataFrame,
        column: str,
        strategy: str = 'auto'
    ) -> pd.DataFrame:
        """
        Impute missing values with appropriate strategy
        Strategies: auto, median, mode, forward_fill, flag
        """

        df = df.copy()

        if column not in df.columns:
            return df
        
        missing_mask = df[column].isnull()
        if not missing_mask.any():
            return df
        
        if strategy == 'auto':
            if pd.api.types.is_numeric_dtype(df[column]):
                strategy = 'median'
            else:
                strategy = 'mode'
        
        # Apply imputation
        if strategy == 'median':
            fill_value = df[column].median()
            df.loc[missing_mask, column] = fill_value
            self.imputation_values[column] = fill_value
            confidence = 0.7
        
        elif strategy == 'mode':
            fill_value = df[column].mode()[0] if not df[column].mode().empty else 'UNKNOWN'
            df.loc[missing_mask, column] = fill_value
            self.imputation_values[column] = fill_value
            confidence = 0.6
        
        elif strategy == 'forward_fill':
            df[column] = df[column].fillna(method='ffill')
            confidence = 0.8
        
        elif strategy == 'flag':
            # Create missing indicator
            df[f'{column}_was_missing'] = missing_mask
            df[column] = df[column].fillna('MISSING')
            confidence = 0.8
        
        imputed_indices = missing_mask[missing_mask].index
        for idx in imputed_indices:
            self.audit_logger.log_transformation(
                row_id=idx,
                column=column,
                original_value=None,
                new_value=df.at[idx, column],
                rule=f'imputation_{strategy}',
                confidence=confidence
            )

        return df
