"""
Generate gold test for measuring cleaning quality.
Two modes: manual correction storage and synthetic corruption
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class GoldTestSetGenerator:
    """Generate gold test for measuring cleaning quality."""

    def __init__(self):
        self.gold_data = []
    
    def create_from_corruptions(
        self,
        clean_df: pd.DataFrame,
        n_samples: int = 1000,
        corruption_rate: float = 0.3
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Create gold test set by corrupting clean data.
        Returns: (corrupted_df, ground_truth_df)
        """
        # Sample rows
        if len(clean_df) < n_samples:
            n_samples = len(clean_df)
        
        sample_df = clean_df.sample(n=n_samples, random_state=42).copy()
        ground_truth = sample_df.copy()
        corrupted = sample_df.copy()
        
        # Apply corruptions
        n_corruptions = int(len(sample_df) * corruption_rate)
        corruption_indices = np.random.choice(sample_df.index, size=n_corruptions, replace=False)
        
        for idx in corruption_indices:
            corruption_type = np.random.choice([
                'timestamp_format', 'amount_format', 'currency_symbol',
                'merchant_typo', 'missing_value'
            ])
            
            if corruption_type == 'timestamp_format':
                # Corrupt timestamp format
                if 'timestamp' in corrupted.columns:
                    ts = corrupted.at[idx, 'timestamp']
                    # Random format corruption
                    corrupted.at[idx, 'timestamp'] = ts.strftime('%d/%m/%Y %H:%M:%S')
            
            elif corruption_type == 'amount_format':
                # Add currency symbol to amount
                if 'amount' in corrupted.columns:
                    amount = corrupted.at[idx, 'amount']
                    corrupted.at[idx, 'amount'] = f'${amount:,.2f}'
            
            elif corruption_type == 'currency_symbol':
                # Replace currency code with symbol
                if 'currency' in corrupted.columns:
                    currency = corrupted.at[idx, 'currency']
                    symbol_map = {'USD': '$', 'EUR': '€', 'GBP': '£'}
                    if currency in symbol_map:
                        corrupted.at[idx, 'currency'] = symbol_map[currency]
            
            elif corruption_type == 'merchant_typo':
                # Add typo to merchant name
                if 'merchant_name' in corrupted.columns:
                    merchant = str(corrupted.at[idx, 'merchant_name'])
                    if len(merchant) > 3:
                        pos = np.random.randint(0, len(merchant))
                        merchant_list = list(merchant)
                        merchant_list[pos] = 'X'
                        corrupted.at[idx, 'merchant_name'] = ''.join(merchant_list)
            
            elif corruption_type == 'missing_value':
                # Introduce missing value
                cols = ['merchant_name', 'channel', 'currency']
                col = np.random.choice([c for c in cols if c in corrupted.columns])
                corrupted.at[idx, col] = np.nan
        
        return corrupted, ground_truth
    
    def evaluate_cleaning_pipeline(
        self,
        cleaned_df: pd.DataFrame,
        ground_truth_df: pd.DataFrame,
        columns_to_check: Optional[List[str]] = None
    ) -> Dict:
        """
        Evaluate cleaning quality against ground truth.
        Returns metrics: accuracy, precision, recall
        """

        if columns_to_check is None:
            columns_to_check = ground_truth_df.columns.tolist()
        
        metrics = {}

        for col in columns_to_check:
            if col not in cleaned_df.columns or col not in ground_truth_df.columns:
                continue

            # Align indices
            common_idx = cleaned_df.index.intersection(ground_truth_df.index)
            if len(common_idx) == 0:
                continue
            
            cleaned_vals = cleaned_df.loc[common_idx, col]
            truth_vals = ground_truth_df.loc[common_idx, col]

            # Calculate accuracy
            matches = (cleaned_vals == truth_vals) | (cleaned_vals.isna() & truth_vals.isna())
            accuracy = matches.mean()

            metrics[col] = {
                'accuracy': float(accuracy),
                'total_values': len(common_idx),
                'correct_values': int(matches.sum())
            }
        
        # Overall metrics
        overall_accuracy = np.mean([m['accuracy'] for m in metrics.values()])
        metrics['overall'] = {
            'accuracy': float(overall_accuracy),
            'columns_evaluated': len(metrics)-1
        }

        return metrics
