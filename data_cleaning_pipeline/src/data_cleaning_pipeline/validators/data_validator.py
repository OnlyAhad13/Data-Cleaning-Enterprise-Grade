"""
Validate data against business rules and schema.
Implements Great Expectations-style validations.
"""

import pandas as pd
import json
from typing import Dict
from ..core.schema import DataSchema


class DataValidator:
    """Validate data against business rules and schema."""
    
    def __init__(self, schema: DataSchema):
        self.schema = schema
        self.validation_results = []
        
    def validate_all(self, df: pd.DataFrame) -> Dict:
        """Run all validations"""
        results = {
            'schema_validation': self.validate_schema(df),
            'business_rules': self.validate_business_rules(df),
            'data_quality': self.validate_data_quality(df),
            'summary': {}
        }
        
        # Aggregate results
        total_checks = sum(len(v['checks']) for v in results.values() if isinstance(v, dict) and 'checks' in v)
        passed_checks = sum(
            sum(1 for c in v['checks'] if c['passed']) 
            for v in results.values() 
            if isinstance(v, dict) and 'checks' in v
        )
        
        results['summary'] = {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'pass_rate': passed_checks / total_checks if total_checks > 0 else 0
        }
        
        return results
    
    def validate_schema(self, df: pd.DataFrame) -> Dict:
        """Validate schema requirements"""
        checks = []
        
        # Check required columns
        for col in self.schema.REQUIRED_COLUMNS:
            passed = col in df.columns
            checks.append({
                'check': f'column_exists_{col}',
                'passed': passed,
                'message': f'Column {col} exists' if passed else f'Missing column: {col}'
            })
        
        # Check data types
        for col, expected_dtype in self.schema.EXPECTED_DTYPES.items():
            if col in df.columns:
                actual_dtype = str(df[col].dtype)
                passed = expected_dtype in actual_dtype or actual_dtype in expected_dtype
                checks.append({
                    'check': f'dtype_{col}',
                    'passed': passed,
                    'message': f'{col} dtype: {actual_dtype} (expected: {expected_dtype})'
                })
        
        return {'checks': checks}
    
    def validate_business_rules(self, df: pd.DataFrame) -> Dict:
        """Validate business rules / invariants"""
        checks = []
        
        # Amount >= 0
        if 'amount' in df.columns:
            negative_count = (df['amount'] < 0).sum()
            passed = negative_count == 0
            checks.append({
                'check': 'amount_non_negative',
                'passed': passed,
                'message': f'{negative_count} negative amounts found' if not passed else 'All amounts non-negative'
            })
            
            # Amount within reasonable range
            max_amount = df['amount'].max()
            passed = max_amount <= self.schema.AMOUNT_MAX
            checks.append({
                'check': 'amount_within_max',
                'passed': passed,
                'message': f'Max amount: {max_amount}'
            })
        
        # Valid currencies
        if 'currency' in df.columns:
            invalid_currencies = df[~df['currency'].isin(self.schema.VALID_CURRENCIES)]['currency'].unique()
            passed = len(invalid_currencies) == 0
            checks.append({
                'check': 'valid_currencies',
                'passed': passed,
                'message': f'Invalid currencies: {invalid_currencies}' if not passed else 'All currencies valid'
            })
        
        # Valid channels
        if 'channel' in df.columns:
            invalid_channels = df[~df['channel'].isin(self.schema.VALID_CHANNELS)]['channel'].unique()
            passed = len(invalid_channels) == 0
            checks.append({
                'check': 'valid_channels',
                'passed': passed,
                'message': f'Invalid channels: {invalid_channels}' if not passed else 'All channels valid'
            })
        
        # Timestamp range
        if 'timestamp' in df.columns:
            min_ts = pd.Timestamp(self.schema.TIMESTAMP_MIN)
            max_ts = pd.Timestamp(self.schema.TIMESTAMP_MAX)
            out_of_range = ((df['timestamp'] < min_ts) | (df['timestamp'] > max_ts)).sum()
            passed = out_of_range == 0
            checks.append({
                'check': 'timestamp_range',
                'passed': passed,
                'message': f'{out_of_range} timestamps out of range' if not passed else 'All timestamps in range'
            })
        
        # Unique transaction IDs
        if 'transaction_id' in df.columns:
            duplicates = df['transaction_id'].duplicated().sum()
            passed = duplicates == 0
            checks.append({
                'check': 'unique_transaction_ids',
                'passed': passed,
                'message': f'{duplicates} duplicate transaction IDs' if not passed else 'All transaction IDs unique'
            })
        
        return {'checks': checks}
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict:
        """Validate overall data quality"""
        checks = []
        
        # Check for excessive missing values
        for col in df.columns:
            missing_pct = df[col].isna().mean() * 100
            passed = missing_pct < 50  # Arbitrary threshold
            if not passed:
                checks.append({
                    'check': f'missing_threshold_{col}',
                    'passed': passed,
                    'message': f'{col}: {missing_pct:.1f}% missing (>50%)'
                })
        
        # Check for low cardinality in expected high-cardinality columns
        high_card_cols = ['transaction_id', 'customer_id', 'merchant_name']
        for col in high_card_cols:
            if col in df.columns:
                unique_pct = df[col].nunique() / len(df) * 100
                passed = unique_pct > 10  # At least 10% unique
                checks.append({
                    'check': f'cardinality_{col}',
                    'passed': passed,
                    'message': f'{col}: {unique_pct:.1f}% unique'
                })
        
        return {'checks': checks}
    
    def save_validation_report(self, results: Dict, filepath: str):
        """Save validation results"""
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
