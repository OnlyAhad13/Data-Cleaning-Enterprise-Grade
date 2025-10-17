"""
Robust timestamp parsing and normalization.
Handles multiple formats, timezones and ambiguous dates.
"""

import pandas as pd
from datetime import datetime, timezone
from typing import Any, Optional, Tuple
from ..core.audit import AuditLogger


class TimestampNormalizer:
    """Robust timestamp parsing and normalization."""

    COMMON_FORMATS = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y/%m/%d %H:%M:%S',
        '%d-%m-%Y %H:%M:%S',
        '%m-%d-%Y %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%d/%m/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
    ]

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger

    def parse_timestamp(
        self,
        row_id: Any, 
        timestamp_str: Any,
        default_tz: timezone = timezone.utc
    ) -> Tuple[Optional[pd.Timestamp], float]:
        """
        Parse timestamp with confidence scoring
        Returns: (parsed_timestamp, confidence)
        """

        if pd.isna(timestamp_str):
            return None, 0.0
        
        if isinstance(timestamp_str, (pd.Timestamp, datetime)):
            return pd.Timestamp(timestamp_str, tz=default_tz), 1.0
        timestamp_str = str(timestamp_str).strip()
        
        # Try common formats
        for fmt in self.COMMON_FORMATS:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                # Add timezone if naive
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=default_tz)
                confidence = 0.95
                return pd.Timestamp(dt), confidence
            except:
                continue
        
        # Try pandas flexible parsing
        try:
            dt = pd.to_datetime(timestamp_str)
            if dt.tzinfo is None:
                dt = dt.tz_localize(default_tz)
            confidence = 0.8
            return dt, confidence
        except:
            pass

        return None, 0.0 
    
    def normalize_timestamps(
        self,
        df: pd.DataFrame,
        timestamp_col: str = 'timestamp',
    ) -> pd.DataFrame:
        """Normalize all timestamps in the dataframe"""

        df = df.copy()
        parsed_timestamps = []
        confidences = []

        for idx, val in df[timestamp_col].items():
            parsed, conf = self.parse_timestamp(idx, val)
            parsed_timestamps.append(parsed)
            confidences.append(conf)

            # log transformation
            if parsed is not None and str(val) != str(parsed):
                self.audit_logger.log_transformation(
                    row_id=idx,
                    column=timestamp_col,
                    original_value=val,
                    new_value=parsed,
                    rule='timestamp_parsing',
                    confidence=conf
                )
        df[timestamp_col] = parsed_timestamps
        df[f'{timestamp_col}_confidence'] = confidences

        return df
