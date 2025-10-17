"""
Comprehensive data profiling before any transformations.
Quantifies missingness, distributions, cardinality, patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import json


class DataProfiler:
    """Comprehensive data profiling before any transformations."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.profile = {}
    
    def generate_profile(self) -> Dict:
        """Generate comprehensive data profile"""
        self.profile = {
            'shape': self.df.shape,
            'memory_usage_mb': self.df.memory_usage(deep=True).sum()/1024**2,
            'columns': self._profile_columns(),
            'duplicates': self._profile_duplicates(),
            'correlations': self._profile_correlations()
        }
        return self.profile
    
    def _profile_columns(self) -> Dict:
        """Profile each column"""
        column_profile = {}

        for col in self.df.columns:
            column_profile[col] = {
                'dtype': str(self.df[col].dtype),
                'missing_count': int(self.df[col].isnull().sum()),
                'missing_pct': float(self.df[col].isnull().mean()*100),
                'unique_count': int(self.df[col].nunique()),
                'unique_pct': float(self.df[col].nunique()/len(self.df)*100),
                'most_common': self._get_most_common(col)
            }
        
        # Numeric Columns
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                column_profile[col].update({
                    'min': float(self.df[col].min()) if not self.df[col].isnull().all() else None,
                    'max': float(self.df[col].max()) if not self.df[col].isnull().all() else None,
                    'mean': float(self.df[col].mean()) if not self.df[col].isnull().all() else None,
                    'median': float(self.df[col].median()) if not self.df[col].isnull().all() else None,
                    'std': float(self.df[col].std()) if not self.df[col].isnull().all() else None,
                    'zeros_count': int((self.df[col] == 0).sum()),
                    'negative_count': int((self.df[col] < 0).sum()) if not self.df[col].isnull().all() else None
                })

        return column_profile
    
    def _get_most_common(self, series: pd.Series, n: int = 5) -> List:
        """Get most common values"""
        try:
            return series.value_counts().head(n).to_dict()
        except:
            return {}
    
    def _profile_duplicates(self) -> Dict:
        """Profile duplicate rows"""
        return {
            'duplicate_rows': int(self.df.duplicated().sum()),
            'duplicate_pct': float(self.df.duplicated().mean()*100)
        }
    
    def _profile_correlations(self) -> Dict:
        """Profile numeric correlations"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = self.df[numeric_cols].corr()
            return {
                'high_correlations': self._find_high_correlations(corr_matrix)
            }
        
        return {}
    
    def _find_high_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.8) -> List:
        """Find highly correlated pairs"""
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > threshold:
                    high_corr.append({
                        'col1': corr_matrix.columns[i],
                        'col2': corr_matrix.columns[j],
                        'correlation': float(corr_matrix.iloc[i, j])
                    })
        return high_corr
    
    def save_profile(self, filepath: str):
        """Save profile to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.profile, f, indent=2)
