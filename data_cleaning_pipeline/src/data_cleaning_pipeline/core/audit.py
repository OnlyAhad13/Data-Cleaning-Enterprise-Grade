"""
Comprehensive audit trail for all data transformations.
Tracks: original value -> transformed value, rule applied, confidence, timestamps
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import pandas as pd


class AuditLogger:
    """Comprehensive audit trail for all data transformations."""

    def __init__(self):
        self.logs: List[Dict] = []
        self.logger = logging.getLogger(__name__)

    def log_transformation(
        self,
        row_id: Any,
        column: str,
        original_value: Any,
        new_value: Any,
        rule: str,
        confidence: float,
        metadata: Optional[Dict] = None
    ):
        """Log a single transformation"""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'row_id': row_id,
            'column': column,
            'original_value': str(original_value),
            'new_value': str(new_value),
            'rule': rule,
            'confidence': confidence,
            'metadata': metadata or {}
        }
        self.logs.append(log_entry)

    def get_audit_df(self) -> pd.DataFrame:
        """Return audit log as DataFrame"""
        return pd.DataFrame(self.logs)
    
    def save_audit_log(self, filepath: str):
        """Save audit log to CSV"""
        df = self.get_audit_df()
        df.to_parquet(filepath, index=False)
        self.logger.info(f"Audit log saved to {filepath}")

    def get_summary(self) -> Dict:
        """Get summary statistics of transformations"""
        if not self.logs:
            return {}
        
        df = self.get_audit_df()
        summary = {
            'total_transformations': len(df),
            'columns_affected': df['column'].nunique(),
            'avg_confidence': df['confidence'].mean(),
            'low_confidence_count': (df['confidence'] < 0.7).sum(),
            'rules_applied': df['rule'].value_counts().to_dict()
        }
        return summary
    