"""
Parse and normalize amounts and currencies
Handles: symbols ($, €, £), word amounts, different formats.
"""

import pandas as pd
import re
from typing import Any, Optional, Tuple
from ..core.audit import AuditLogger
from ..core.schema import DataSchema


class AmountCurrencyNormalizer:
    """Parse and normalize amounts and currencies"""

    CURRENCY_SYMBOLS = {
        '$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY',
        '₹': 'INR', 'A$': 'AUD', 'C$': 'CAD'
    }

    # Simplified exchange rates
    EXCHANGE_RATES = {
        'USD': 1.0, 'EUR': 1.08, 'GBP': 1.27, 'JPY': 0.0067,
        'CNY': 0.14, 'INR': 0.012, 'AUD': 0.65, 'CAD': 0.73
    }

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
    
    def parse_amount(
        self,
        row_id: Any,
        amount_str: Any,
    ) -> Tuple[Optional[float], float]:
        """
        Parse amount with confidence scoring
        Returns: (parsed_amount, confidence)
        """

        if pd.isnull(amount_str):
            return None, 0.0
        
        # Already numeric
        if isinstance(amount_str, (int, float)):
            return float(amount_str), 1.0
        
        amount_str = str(amount_str).strip()

        # Remove currency symbols
        cleaned = re.sub(r'[,$£€¥₹]', '', amount_str)
        cleaned = cleaned.replace(' ', '')

        try:
            amount = float(cleaned)
            confidence = 0.95 if amount >= 0 else 0.5
            return amount, confidence
        except:
            pass

        # Try to extract numbers
        numbers = re.findall(r'\d+\.?\d*', amount_str)
        if numbers:
            try:
                amount = float(numbers[0])
                return amount, 0.7
            except:
                pass
        
        return None, 0.0
    
    def parse_currency(
        self,
        row_id: Any,
        currency_str: Any
    ) -> Tuple[Optional[str], float]:
        """
        Parse currency with confidence scoring
        Returns: (parsed_currency, confidence)
        """

        if pd.isnull(currency_str):
            return None, 0.0
        
        currency_str = str(currency_str).strip().upper()

        # Direct match
        if currency_str in DataSchema.VALID_CURRENCIES:
            return currency_str, 1.0

        # Symbol match
        for symbol, code in self.CURRENCY_SYMBOLS.items():
            if symbol in str(currency_str):
                return code, 0.9
        
        # Fuzzy match
        for valid_curr in DataSchema.VALID_CURRENCIES:
            if valid_curr in currency_str or currency_str in valid_curr:
                return valid_curr, 0.7
        
        return None, 0.0
    
    def normalize_amounts_currencies(
        self,
        df: pd.DataFrame,
        amount_col: str = 'amount',
        currency_col: str = 'currency'
    ) -> pd.DataFrame:
        """Normalize amounts and currencies"""
        df = df.copy()

        # Parse amounts
        parsed_amounts = []
        amount_confidences = []
        for idx, val in df[amount_col].items():
            parsed, conf = self.parse_amount(idx, val)
            parsed_amounts.append(parsed)
            amount_confidences.append(conf)

            if parsed is not None and val != parsed:
                self.audit_logger.log_transformation(
                    row_id=idx,
                    column=amount_col,
                    original_value=val,
                    new_value=parsed,
                    rule='amount_parsing',
                    confidence=conf
                )
        
        df[amount_col] = parsed_amounts
        df[f'{amount_col}_confidence'] = amount_confidences

        # Parse currencies
        parsed_currencies = []
        currency_confidences = []
        for idx, val in df[currency_col].items():
            parsed, conf = self.parse_currency(idx, val)
            parsed_currencies.append(parsed)
            currency_confidences.append(conf)
            if parsed is not None and val != parsed:
                self.audit_logger.log_transformation(
                    row_id=idx,
                    column=currency_col,
                    original_value=val,
                    new_value=parsed,
                    rule='currency_parsing',
                    confidence=conf
                )
        
        df[currency_col] = parsed_currencies
        df[f'{currency_col}_confidence'] = currency_confidences

        # Convert to USD
        df['amount_usd'] = df.apply(
            lambda row: self._convert_to_usd(row[amount_col], row[currency_col]),
            axis=1
        )

        return df
    
    def _convert_to_usd(
        self,
        amount: Optional[float],
        currency: Optional[str]
    ) -> Optional[float]:
        """Convert amount to USD"""

        if pd.isnull(amount) or pd.isnull(currency):
            return None
        if currency not in self.EXCHANGE_RATES:
            return None
        
        return amount * self.EXCHANGE_RATES[currency]
