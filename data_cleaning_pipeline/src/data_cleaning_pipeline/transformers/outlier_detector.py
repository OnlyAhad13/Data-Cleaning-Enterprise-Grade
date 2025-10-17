"""
Multi-method outlier detection: Statistical + ML based
"""

import pandas as pd
import numpy as np
from typing import List, Optional
from sklearn.ensemble import IsolationForest
from scipy import stats
from ..core.audit import AuditLogger


class OutlierDetector:
    """Multi-method outlier detection: Statistical + ML based"""

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
    
    def detect_statistical_outliers(
        self,
        df: pd.DataFrame,
        column: str,
        method: str = 'mad',
        threshold: float = 3.5
    ) -> pd.Series:
        """
        Detect outliers using statistical methods
        Methods: MAD(Median Absolute Deviation), IQR, Z-score
        """

        if column not in df.columns or df[column].isnull().all():
            return pd.Series([False]*len(df), index=df.index)
        
        values = df[column].dropna()

        if method.lower().strip() == 'mad':
            median = values.median()
            mad = np.median(np.abs(values - median))
            if mad == 0:
                return pd.Series([False]*len(df), index=df.index)
            modified_z_scores = 0.6745 * (df[column] - median) / mad
            return np.abs(modified_z_scores) > threshold
        
        elif method.lower().strip() == 'iqr':
            Q1 = values.quantile(0.25)
            Q3 = values.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            return (df[column] < lower) | (df[column] > upper)
        
        elif method.lower().strip() == 'z-score':
            z_scores = np.abs(stats.zscore(values, nan_policy='omit'))
            outlier_mask = pd.Series([False]*len(df), index=df.index)
            outlier_mask.loc[values.index] = z_scores > threshold
            return outlier_mask       

        return pd.Series([False]*len(df), index=df.index)
    
    def detect_ml_outliers(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        contamination: float = 0.05
    ) -> pd.Series:
        """Detect outliers using Isolation Forest"""
        # Select numerical features
        features = df[feature_columns].select_dtypes(include=[np.number])

        if features.empty or features.shape[1] == 0:
            return pd.Series([False]*len(df), index=df.index)
        
        # Handle missing values
        features_filled = features.fillna(features.median())

        # Fit isolation forest
        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )

        predictions = iso_forest.fit_predict(features_filled)
        outlier_mask = predictions == -1

        return pd.Series(outlier_mask, index=df.index)
    
    def detect_all_outliers(
        self,
        df: pd.DataFrame,
        numeric_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Detect outliers using multiple methods"""
        df = df.copy()

        if numeric_columns is None:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Statistical outliers per column
        for col in numeric_columns:
            if col in df.columns:
                outlier_mask = self.detect_statistical_outliers(df, col, method='mad')
                df[f'{col}_is_outlier'] = outlier_mask

                # Log outliers
                outlier_indices = df[outlier_mask].index
                for idx in outlier_indices:
                    self.audit_logger.log_transformation(
                        row_id=idx,
                        column=col,
                        original_value=df.at[idx, col],
                        new_value='OUTLIER_DETECTED',
                        rule='mad_outlier_detection',
                        confidence=0.85
                    )
        
        # ML-based outliers
        if len(numeric_columns) > 1:
            ml_outliers = self.detect_ml_outliers(df, numeric_columns)
            df['ml_outliers'] = ml_outliers
        
        return df
