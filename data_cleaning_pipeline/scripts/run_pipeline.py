#!/usr/bin/env python3
"""
Command-line script for running the data cleaning pipeline.

Usage:
    python scripts/run_pipeline.py --input data.csv --output cleaned_data.parquet
    python scripts/run_pipeline.py --input data.csv --output-dir artifacts/
    python scripts/run_pipeline.py --input data.csv --config config.json
"""

import argparse
import sys
import os
import json
import logging
from pathlib import Path

import pandas as pd

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_cleaning_pipeline import DataCleaningPipeline, DataSchema


def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('pipeline.log')
        ]
    )


def load_config(config_path):
    """Load configuration from JSON file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)


def load_data(input_path):
    """Load data from various formats."""
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Determine file format and load accordingly
    if input_path.suffix.lower() == '.csv':
        return pd.read_csv(input_path)
    elif input_path.suffix.lower() == '.parquet':
        return pd.read_parquet(input_path)
    elif input_path.suffix.lower() == '.json':
        return pd.read_json(input_path)
    elif input_path.suffix.lower() == '.xlsx':
        return pd.read_excel(input_path)
    else:
        # Try to read as CSV by default
        return pd.read_csv(input_path)


def save_data(df, output_path):
    """Save data to various formats."""
    output_path = Path(output_path)
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine file format and save accordingly
    if output_path.suffix.lower() == '.csv':
        df.to_csv(output_path, index=False)
    elif output_path.suffix.lower() == '.parquet':
        df.to_parquet(output_path, index=False)
    elif output_path.suffix.lower() == '.json':
        df.to_json(output_path, orient='records', indent=2)
    elif output_path.suffix.lower() == '.xlsx':
        df.to_excel(output_path, index=False)
    else:
        # Default to CSV
        df.to_csv(output_path, index=False)


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description='Data Cleaning Pipeline - Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_pipeline.py --input data.csv --output cleaned_data.parquet
  python scripts/run_pipeline.py --input data.csv --output-dir artifacts/
  python scripts/run_pipeline.py --input data.csv --config config.json --verbose
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input data file path (CSV, Parquet, JSON, Excel)'
    )
    
    # Output options (mutually exclusive)
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument(
        '--output', '-o',
        help='Output cleaned data file path'
    )
    output_group.add_argument(
        '--output-dir', '-d',
        help='Output directory for all artifacts'
    )
    
    # Optional arguments
    parser.add_argument(
        '--config', '-c',
        help='Configuration file path (JSON)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate and display cleaning report'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate data without cleaning'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Load data
        logger.info(f"Loading data from: {args.input}")
        df = load_data(args.input)
        logger.info(f"Loaded data shape: {df.shape}")
        
        # Load configuration if provided
        config = {}
        if args.config:
            logger.info(f"Loading configuration from: {args.config}")
            config = load_config(args.config)
        
        # Initialize pipeline
        logger.info("Initializing data cleaning pipeline...")
        pipeline = DataCleaningPipeline(config)
        
        if args.validate_only:
            # Only validate data
            logger.info("Running validation only...")
            pipeline.fit(df)
            validation_results = pipeline.validator.validate_all(df)
            
            print("\nValidation Results:")
            print("=" * 50)
            for category, results in validation_results.items():
                if isinstance(results, dict) and 'checks' in results:
                    print(f"\n{category.upper()}:")
                    for check in results['checks']:
                        status = "✓" if check['passed'] else "✗"
                        print(f"  {status} {check['check']}: {check['message']}")
            
            summary = validation_results.get('summary', {})
            print(f"\nSummary:")
            print(f"  Total checks: {summary.get('total_checks', 0)}")
            print(f"  Passed: {summary.get('passed_checks', 0)}")
            print(f"  Failed: {summary.get('failed_checks', 0)}")
            print(f"  Pass rate: {summary.get('pass_rate', 0):.1%}")
            
        else:
            # Run full pipeline
            logger.info("Running data cleaning pipeline...")
            df_cleaned = pipeline.fit_transform(df)
            logger.info(f"Pipeline completed. Cleaned data shape: {df_cleaned.shape}")
            
            # Generate report if requested
            if args.report:
                logger.info("Generating cleaning report...")
                report = pipeline.generate_report()
                print("\n" + report)
            
            # Save results
            if args.output:
                logger.info(f"Saving cleaned data to: {args.output}")
                save_data(df_cleaned, args.output)
            
            if args.output_dir:
                logger.info(f"Saving all artifacts to: {args.output_dir}")
                pipeline.save_artifacts(args.output_dir)
                
                # Also save cleaned data in the output directory
                cleaned_data_path = Path(args.output_dir) / 'cleaned_data.parquet'
                save_data(df_cleaned, cleaned_data_path)
        
        logger.info("Pipeline execution completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()