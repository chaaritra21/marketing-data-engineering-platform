import logging
import pandas as pd 


def validate_processed_data(df: pd.DataFrame):
    """Run data quality checks on processed data."""

    logging.info("Starting data quality checks")

    # Check 1: Dataset must not be empty
    if df.empty:
        raise ValueError("Data quality failed: dataset is empty")

    # Check 2: Required columns must exist
    required_columns = {
        "userid",
        "id",
        "title",
        "body",
        "title_length",
        "body_length",
        "processed_at"
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Data quality failed: missing columns {missing_columns}"
        )

    # Check 3: ID must be unique
    if df["id"].duplicated().any():
        raise ValueError(
            "Data quality failed: duplicate IDs found"
        )

    # Check 4: Required fields must not be null
    required_fields = ["userid", "id", "title", "body"]

    if df[required_fields].isnull().any().any():
        raise ValueError(
            "Data quality failed: null values found"
        )

    # Check 5: Text fields should not be empty
    if (df["title"].str.strip() == "").any():
        raise ValueError(
            "Data quality failed: empty titles found"
        )

    if (df["body"].str.strip() == "").any():
        raise ValueError(
            "Data quality failed: empty body values found"
        )

    logging.info(
        "Data quality checks passed successfully"
    )

    return True