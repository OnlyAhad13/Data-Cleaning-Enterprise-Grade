"""
Sophisticated duplicate detection using multiple strategies
"""

import pandas as pd
import hashlib
from typing import List, Optional
from ..core.audit import AuditLogger


class DuplicateHandler:
    """Sophisticated duplicate detection using multiple strategies"""

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
    
    def generate_row_signature(self, row: pd.Series, key_columns: List[str]) -> str:
        """Generate hash signature for duplicate detection"""
        values = [str(row[col]) for col in key_columns if col in row.index]
        signature_str = '|'.join(values)
        return hashlib.md5(signature_str.encode()).hexdigest()
        
    def detect_exact_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """Detect exact duplicate rows"""

        df = df.copy()
        df['is_exact_duplicate'] = df.duplicated(subset=subset, keep='first')
        
        # log duplicates
        dup_indices = df[df['is_exact_duplicate']].index
        for idx in dup_indices:
            self.audit_logger.log_transformation(
                row_id=idx,
                column='_row',
                original_value='keep',
                new_value='duplicate',
                rule='exact_duplicate_detection',
                confidence=1.0
            )
        return df
    
    def detect_fuzzy_duplicates(
        self,
        df: pd.DataFrame, 
        key_columns: List[str],
        time_window_seconds: int = 60
    ) -> pd.DataFrame:
        """
        Detect fuzzy duplicates: same key fields within time window
        Common in fraud detection - same transaction submitted multiple times
        """

        df = df.copy()
        df['signature'] = df.apply(
            lambda row: self.generate_row_signature(row, key_columns),
            axis=1
        )
        
        # Sort by timestamp and signature
        if 'timestamp' in df.columns:
            df = df.sort_values(['signature', 'timestamp'])

            # Identify fuzzy duplicates
            df['is_fuzzy_duplicate'] = False
            for sig in df['signature'].unique():
                sig_mask = df['signature'] == sig
                sig_df = df[sig_mask].copy()

                if len(sig_df) > 1:
                    # Check time windows
                    for i in range(1, len(sig_df)):
                        time_diff = (sig_df.iloc[i]['timestamp'] - sig_df.iloc[i-1]['timestamp']).total_seconds()
                        if abs(time_diff) <= time_window_seconds:
                            df.loc[sig_df.iloc[i].name, 'is_fuzzy_duplicate'] = True
        
        return df
    
    def resolve_duplicates(
        self,
        df: pd.DataFrame,
        strategy: str = 'keep_first'
    ) -> pd.DataFrame:
        """
        Resolve duplicates based on strategy.
        """
        df = df.copy()
        # Mark duplicates for removal
        duplicate_cols = [c for c in df.columns if 'duplicate' in c.lower()]
        if duplicate_cols:
            mask = df[duplicate_cols].any(axis=1)
            df['_to_remove'] = mask
        
        return df
