"""
Advanced usage example of the Data Cleaning Pipeline.

This example demonstrates advanced features like custom configuration,
individual component usage, and quality measurement.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
import logging

from data_cleaning_pipeline import DataCleaningPipeline, DataSchema
from data_cleaning_pipeline.utils import GoldTestSetGenerator
from data_cleaning_pipeline.transformers import TimestampNormalizer, AmountCurrencyNormalizer
from data_cleaning_pipeline.core.audit import AuditLogger


def create_advanced_sample_data():
    """Create sample data with more complex quality issues."""
    np.random.seed(42)
    
    # Create base data
    data = {
        'transaction_id': [f'TXN{i:04d}' for i in range(500)],
        'timestamp': pd.date_range('2024-01-01', periods=500, freq='1H'),
        'amount': np.random.lognormal(4, 1, 500),
        'currency': np.random.choice(['USD', 'EUR', 'GBP', 'JPY'], 500),
        'merchant_name': np.random.choice([
            'Amazon', 'Walmart', 'Target', 'BestBuy', 'Starbucks',
            'McDonalds', 'Shell', 'Exxon', 'CVS', 'Walgreens'
        ], 500),
        'customer_id': [f'CUST{i:03d}' for i in range(500)],
        'channel': np.random.choice(['online', 'in-store', 'mobile', 'atm'], 500),
        'is_fraud': np.random.choice([0, 1], 500, p=[0.95, 0.05])
    }
    
    df = pd.DataFrame(data)
    
    # Introduce complex quality issues
    print("Introducing complex data quality issues...")
    
    # 1. Multiple timestamp formats
    formats = [
        '%d/%m/%Y %H:%M:%S',
        '%m-%d-%Y %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%d-%m-%Y %H:%M:%S'
    ]
    
    for i, fmt in enumerate(formats):
        corrupt_idx = np.random.choice(df.index, size=10, replace=False)
        for idx in corrupt_idx:
            df.at[idx, 'timestamp'] = df.at[idx, 'timestamp'].strftime(fmt)
    
    # 2. Various amount formats
    amount_formats = [
        lambda x: f"${x:.2f}",
        lambda x: f"€{x:.2f}",
        lambda x: f"£{x:.2f}",
        lambda x: f"{x:,.2f}",
        lambda x: f"USD {x:.2f}"
    ]
    
    for fmt_func in amount_formats:
        corrupt_idx = np.random.choice(df.index, size=8, replace=False)
        for idx in corrupt_idx:
            df.at[idx, 'amount'] = fmt_func(df.at[idx, 'amount'])
    
    # 3. Currency symbol variations
    currency_symbols = {
        'USD': ['$', 'US$', 'USD'],
        'EUR': ['€', 'EUR', 'EURO'],
        'GBP': ['£', 'GBP', 'POUND'],
        'JPY': ['¥', 'JPY', 'YEN']
    }
    
    for currency, symbols in currency_symbols.items():
        mask = df['currency'] == currency
        for symbol in symbols:
            corrupt_idx = np.random.choice(df[mask].index, size=5, replace=False)
            for idx in corrupt_idx:
                df.at[idx, 'currency'] = symbol
    
    # 4. Merchant name variations
    merchant_variations = {
        'Amazon': ['amazon', 'AMAZON', 'Amazon.com', 'Amazon Inc'],
        'Walmart': ['walmart', 'WALMART', 'Walmart Inc', 'Walmart Stores'],
        'Target': ['target', 'TARGET', 'Target Corp', 'Target Stores']
    }
    
    for merchant, variations in merchant_variations.items():
        mask = df['merchant_name'] == merchant
        for variation in variations:
            corrupt_idx = np.random.choice(df[mask].index, size=3, replace=False)
            for idx in corrupt_idx:
                df.at[idx, 'merchant_name'] = variation
    
    # 5. Channel variations
    channel_variations = {
        'online': ['web', 'internet', 'ecommerce', 'Online'],
        'in-store': ['store', 'retail', 'brick-mortar', 'In-Store'],
        'mobile': ['app', 'smartphone', 'Mobile App', 'Mobile']
    }
    
    for channel, variations in channel_variations.items():
        mask = df['channel'] == channel
        for variation in variations:
            corrupt_idx = np.random.choice(df[mask].index, size=2, replace=False)
            for idx in corrupt_idx:
                df.at[idx, 'channel'] = variation
    
    # 6. Introduce missing values with patterns
    for col in ['merchant_name', 'channel', 'currency']:
        missing_idx = np.random.choice(df.index, size=10, replace=False)
        df.loc[missing_idx, col] = np.nan
    
    # 7. Create various types of duplicates
    # Exact duplicates
    dup_idx = np.random.choice(df.index, size=10, replace=False)
    df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)
    
    # Near duplicates (same customer, amount, merchant but different time)
    near_dup_idx = np.random.choice(df.index, size=5, replace=False)
    for idx in near_dup_idx:
        new_row = df.loc[idx].copy()
        new_row['timestamp'] = df.loc[idx, 'timestamp'] + pd.Timedelta(minutes=1)
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
    
    return df


def demonstrate_individual_components():
    """Demonstrate usage of individual pipeline components."""
    print("\n" + "=" * 60)
    print("INDIVIDUAL COMPONENT USAGE")
    print("=" * 60)
    
    # Create sample data
    df = pd.DataFrame({
        'timestamp': ['2024-01-01 10:00:00', '01/01/2024 11:00:00', '2024-01-01T12:00:00'],
        'amount': [100.0, '$200.50', '€300.75'],
        'currency': ['USD', '$', '€'],
        'merchant': ['Amazon', 'amazon', 'AMAZON']
    })
    
    print("Original data:")
    print(df)
    
    # Use individual components
    audit_logger = AuditLogger()
    
    # Timestamp normalization
    print("\n1. Timestamp Normalization:")
    timestamp_normalizer = TimestampNormalizer(audit_logger)
    df_timestamp = timestamp_normalizer.normalize_timestamps(df)
    print(df_timestamp[['timestamp', 'timestamp_confidence']])
    
    # Amount and currency normalization
    print("\n2. Amount and Currency Normalization:")
    amount_normalizer = AmountCurrencyNormalizer(audit_logger)
    df_amount = amount_normalizer.normalize_amounts_currencies(df_timestamp)
    print(df_amount[['amount', 'currency', 'amount_usd']])
    
    # Show audit log
    print("\n3. Audit Log:")
    audit_df = audit_logger.get_audit_df()
    print(audit_df[['column', 'original_value', 'new_value', 'rule', 'confidence']])


def demonstrate_quality_measurement():
    """Demonstrate quality measurement using gold test sets."""
    print("\n" + "=" * 60)
    print("QUALITY MEASUREMENT")
    print("=" * 60)
    
    # Create clean data
    clean_data = pd.DataFrame({
        'transaction_id': [f'TXN{i:04d}' for i in range(100)],
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='1H'),
        'amount': np.random.uniform(10, 1000, 100),
        'currency': ['USD'] * 100,
        'merchant_name': ['Amazon'] * 100,
        'customer_id': [f'CUST{i:03d}' for i in range(100)],
        'channel': ['online'] * 100,
        'is_fraud': [0] * 100
    })
    
    # Generate gold test set
    generator = GoldTestSetGenerator()
    corrupted_df, ground_truth = generator.create_from_corruptions(
        clean_data, n_samples=50, corruption_rate=0.4
    )
    
    print(f"Generated gold test set:")
    print(f"  Corrupted data: {len(corrupted_df)} rows")
    print(f"  Ground truth: {len(ground_truth)} rows")
    
    # Clean the corrupted data
    pipeline = DataCleaningPipeline()
    cleaned_df = pipeline.fit_transform(corrupted_df)
    
    # Evaluate quality
    metrics = generator.evaluate_cleaning_pipeline(cleaned_df, ground_truth)
    
    print(f"\nQuality Metrics:")
    for col, metric in metrics.items():
        if col != 'overall':
            print(f"  {col}: {metric['accuracy']:.2%} accuracy")
    
    print(f"\nOverall Quality: {metrics['overall']['accuracy']:.2%}")


def demonstrate_custom_configuration():
    """Demonstrate custom pipeline configuration."""
    print("\n" + "=" * 60)
    print("CUSTOM CONFIGURATION")
    print("=" * 60)
    
    # Create custom schema
    custom_schema = DataSchema()
    custom_schema.AMOUNT_MAX = 5000000.0  # Increase max amount
    custom_schema.VALID_CURRENCIES.add('BTC')  # Add Bitcoin
    custom_schema.VALID_CHANNELS.add('crypto')  # Add crypto channel
    
    print("Custom schema configuration:")
    print(f"  Max amount: {custom_schema.AMOUNT_MAX:,}")
    print(f"  Valid currencies: {custom_schema.VALID_CURRENCIES}")
    print(f"  Valid channels: {custom_schema.VALID_CHANNELS}")
    
    # Create data with custom values
    df = pd.DataFrame({
        'transaction_id': ['TXN001', 'TXN002'],
        'timestamp': ['2024-01-01 10:00:00', '2024-01-01 11:00:00'],
        'amount': [1000000.0, 2000000.0],  # Large amounts
        'currency': ['USD', 'BTC'],  # Including Bitcoin
        'merchant_name': ['Amazon', 'CryptoExchange'],
        'customer_id': ['CUST001', 'CUST002'],
        'channel': ['online', 'crypto'],  # Including crypto channel
        'is_fraud': [0, 0]
    })
    
    print(f"\nTest data with custom values:")
    print(df)
    
    # Use custom configuration
    pipeline = DataCleaningPipeline({'schema': custom_schema})
    cleaned_df = pipeline.fit_transform(df)
    
    print(f"\nCleaned data:")
    print(cleaned_df)


def main():
    """Main advanced example function."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 80)
    print("DATA CLEANING PIPELINE - ADVANCED USAGE EXAMPLE")
    print("=" * 80)
    
    # 1. Create complex sample data
    print("\n1. Creating complex sample data...")
    df_raw = create_advanced_sample_data()
    print(f"   Created dataset with {len(df_raw):,} rows")
    print(f"   Data quality issues: {df_raw.isnull().sum().sum()} missing values")
    
    # 2. Run full pipeline
    print("\n2. Running full data cleaning pipeline...")
    pipeline = DataCleaningPipeline()
    df_cleaned = pipeline.fit_transform(df_raw)
    
    print(f"   Pipeline completed!")
    print(f"   Original shape: {df_raw.shape}")
    print(f"   Cleaned shape: {df_cleaned.shape}")
    
    # 3. Generate comprehensive report
    print("\n3. Generating comprehensive report...")
    report = pipeline.generate_report()
    print(report)
    
    # 4. Demonstrate individual components
    demonstrate_individual_components()
    
    # 5. Demonstrate quality measurement
    demonstrate_quality_measurement()
    
    # 6. Demonstrate custom configuration
    demonstrate_custom_configuration()
    
    # 7. Save all artifacts
    print("\n7. Saving all artifacts...")
    output_dir = 'advanced_cleaning_artifacts'
    pipeline.save_artifacts(output_dir)
    print(f"   Artifacts saved to: {output_dir}/")
    
    print("\n" + "=" * 80)
    print("ADVANCED EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
