

"""
Data schema definitions and business rules for the data cleaning pipeline.
"""

from dataclasses import dataclass
from typing import Set


@dataclass
class DataSchema:
    """Define expected schema and business rules"""

    # Column Definitions
    REQUIRED_COLUMNS = [
        'transaction_id', 'timestamp', 'amount', 'currency',
        'merchant_name', 'customer_id', 'channel', 'is_fraud'
    ]

    # Data types
    EXPECTED_DTYPES = {
        'transaction_id': 'object',
        'amount': 'float64',
        'is_fraud': 'int64'
    }

    # Business rules
    AMOUNT_MIN = 0.0
    AMOUNT_MAX = 1000000.0
    VALID_CURRENCIES = {'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'INR', 'AUD', 'CAD'}
    VALID_CHANNELS = {'online', 'in-store', 'mobile', 'atm', 'phone'}
    TIMESTAMP_MIN = '2020-01-01'
    TIMESTAMP_MAX = '2025-12-31'
    
    # Duplicate Detection
    DUPLICATE_WINDOW_SECONDS = 60

    # Outlier Detection
    OUTLIER_CONTAMINATION = 0.05
