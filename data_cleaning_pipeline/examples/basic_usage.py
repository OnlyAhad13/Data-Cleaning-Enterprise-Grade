"""
Basic usage example of the Data Cleaning Pipeline.

This example demonstrates how to use the pipeline with a simple dataset.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
import logging

from data_cleaning_pipeline import DataCleaningPipeline


def create_sample_data():
    """Create sample data with various quality issues."""
    np.random.seed(42)
    
    # Create base data
    data = {
        'transaction_id': [f'TXN{i:04d}' for i in range(100)],
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='1H'),
        'amount': np.random.lognormal(4, 1, 100),
        'currency': np.random.choice(['USD', 'EUR', 'GBP'], 100),
        'merchant_name': np.random.choice(['Amazon', 'Walmart', 'Target', 'BestBuy'], 100),
        'customer_id': [f'CUST{i:03d}' for i in range(100)],
        'channel': np.random.choice(['online', 'in-store', 'mobile'], 100),
        'is_fraud': np.random.choice([0, 1], 100, p=[0.9, 0.1])
    }
    
    df = pd.DataFrame(data)
    
    # Introduce quality issues
    print("Introducing data quality issues...")
    
    # 1. Corrupt some timestamps
    corrupt_idx = np.random.choice(df.index, size=10, replace=False)
    for idx in corrupt_idx:
        df.at[idx, 'timestamp'] = df.at[idx, 'timestamp'].strftime('%d/%m/%Y %H:%M:%S')
    
    # 2. Add currency symbols to amounts
    corrupt_idx = np.random.choice(df.index, size=15, replace=False)
    for idx in corrupt_idx:
        df.at[idx, 'amount'] = f"${df.at[idx, 'amount']:.2f}"
    
    # 3. Add typos to merchant names
    corrupt_idx = np.random.choice(df.index, size=5, replace=False)
    for idx in corrupt_idx:
        merchant = df.at[idx, 'merchant_name']
        df.at[idx, 'merchant_name'] = merchant + ' Inc'
    
    # 4. Introduce missing values
    for col in ['merchant_name', 'channel']:
        missing_idx = np.random.choice(df.index, size=3, replace=False)
        df.loc[missing_idx, col] = np.nan
    
    # 5. Create some duplicates
    dup_idx = np.random.choice(df.index, size=5, replace=False)
    df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)
    
    return df


def main():
    """Main example function."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 80)
    print("DATA CLEANING PIPELINE - BASIC USAGE EXAMPLE")
    print("=" * 80)
    
    # Create sample data
    print("\n1. Creating sample data with quality issues...")
    df_raw = create_sample_data()
    print(f"   Created dataset with {len(df_raw):,} rows")
    print(f"   Columns: {list(df_raw.columns)}")
    
    # Show some data quality issues
    print(f"\n   Data quality issues introduced:")
    print(f"   - Corrupted timestamps: {df_raw['timestamp'].dtype}")
    print(f"   - Mixed amount formats: {df_raw['amount'].dtype}")
    print(f"   - Missing values: {df_raw.isnull().sum().sum()} total")
    print(f"   - Duplicate rows: {df_raw.duplicated().sum()}")
    
    # Initialize pipeline
    print("\n2. Initializing data cleaning pipeline...")
    pipeline = DataCleaningPipeline()
    
    # Run the pipeline
    print("\n3. Running data cleaning pipeline...")
    df_cleaned = pipeline.fit_transform(df_raw)
    
    print(f"   Pipeline completed successfully!")
    print(f"   Original shape: {df_raw.shape}")
    print(f"   Cleaned shape: {df_cleaned.shape}")
    
    # Generate and display report
    print("\n4. Generating cleaning report...")
    report = pipeline.generate_report()
    print(report)
    
    # Show audit summary
    print("\n5. Audit Summary:")
    audit_summary = pipeline.get_audit_summary()
    print(f"   Total transformations: {audit_summary.get('total_transformations', 0):,}")
    print(f"   Columns affected: {audit_summary.get('columns_affected', 0)}")
    print(f"   Average confidence: {audit_summary.get('avg_confidence', 0):.2%}")
    
    # Save artifacts
    print("\n6. Saving artifacts...")
    output_dir = 'cleaning_artifacts'
    pipeline.save_artifacts(output_dir)
    print(f"   Artifacts saved to: {output_dir}/")
    
    # Show some cleaned data
    print("\n7. Sample of cleaned data:")
    print(df_cleaned.head())
    
    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
