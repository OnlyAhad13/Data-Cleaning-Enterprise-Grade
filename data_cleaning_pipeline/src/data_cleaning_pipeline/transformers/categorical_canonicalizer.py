"""
Canonicalize categorical text fields(merchants, channels, etc)
Uses fuzzy matching and learned embeddings
"""

import pandas as pd
from typing import Dict, List, Optional, Set
from ..core.audit import AuditLogger


class CategoricalCanonicalizer:
    """Canonicalize categorical text fields"""

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.canonical_mappings = {}
    
    def build_canonical_mapping(
        self, 
        df: pd.DataFrame,
        column: str,
        valid_values: Optional[set] = None,
        min_frequency: int = 5
    ) -> Dict[str, str]:
        """
        Build canonical mapping for a categorical column.
        Groups similar values and maps to most common variant
        """

        if column not in df.columns:
            return {}
        
        # Get value counts
        value_counts = df[column].dropna().value_counts()

        # Filter by frequency
        frequent_values = value_counts[value_counts >= min_frequency].index.tolist()

        mappings = {}

        if valid_values:
            # Map to valid values
            for val in frequent_values:
                canonical = self._find_best_match(val, valid_values)
                mappings[val] = canonical
        else:
            # Group similar values
            groups = self._group_similar_values(frequent_values)
            for group in groups:
                canonical = max(group, key=lambda x: value_counts.get(x, 0))
                for val in group:
                    mappings[val] = canonical
        
        self.canonical_mappings[column] = mappings
        return mappings
    
    def _find_best_match(self, value: str, valid_values: set) -> str:
        """Finding the best match valid value"""

        value_clean = str(value).lower().strip()
        # Exact match
        for valid in valid_values:
            if value_clean == str(valid).lower().strip():
                return valid
        
        # Fuzzy match
        for valid in valid_values:
            if value_clean in str(valid).lower().strip() or str(valid).lower().strip() in value_clean:
                return valid
        
        # Return original value if no match
        return value
    
    def _group_similar_values(self, values: List[str], threshold: float = 0.85) -> List[List[str]]:
        """Group similar values using simple similarity"""

        # Simplified grouping
        groups = []
        processed = set()

        for val in values:
            if val in processed:
                continue

            group = [val]
            val_clean = str(val).lower().strip()

            for other in values:
                if other == val or other in processed:
                    continue

                other_clean = str(other).lower().strip()

                # Simple similarity check
                if (val_clean in other_clean or other_clean in val_clean or
                    self._simple_similarity(val_clean, other_clean) > threshold):
                    group.append(other)
                    processed.add(other)
            
            groups.append(group)
            processed.add(val)
        
        return groups
    
    def _simple_similarity(self, s1: str, s2: str) -> float:
        """Simple character-based similarity"""

        if not s1 or not s2:
            return 0.0
        
        s1_chars = set(s1)
        s2_chars = set(s2)
        intersection = len(s1_chars & s2_chars)
        union = len(s1_chars | s2_chars)
        return intersection / union if union > 0 else 0.0

    def apply_canonical_mapping(
        self,
        df: pd.DataFrame,
        column: str
    ) -> pd.DataFrame:
        """Apply canonical mapping to column"""
        if column not in self.canonical_mappings:
            return df
        
        df = df.copy()
        mapping = self.canonical_mappings[column]

        for idx, val in df[column].items():
            if pd.notna(val) and val in mapping:
                new_val = mapping[val]
                if new_val != val:
                    self.audit_logger.log_transformation(
                        row_id=idx,
                        column=column,
                        original_value=val,
                        new_value=new_val,
                        rule='canonical_mapping',
                        confidence=0.9
                    )
                    df.at[idx, column] = new_val
        
        return df
