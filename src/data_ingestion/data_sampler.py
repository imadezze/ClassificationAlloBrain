"""Data Sampler - Smart sampling for LLM analysis with token management"""
import pandas as pd
import numpy as np
from typing import List, Optional
from src.config import Config


class DataSampler:
    """Handles smart sampling of data for LLM analysis"""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Rough estimation of token count
        Rule of thumb: ~4 characters per token
        """
        return len(text) // 4

    @staticmethod
    def stratified_sample(
        df: pd.DataFrame, column: str, sample_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Perform stratified random sampling on a column

        Args:
            df: DataFrame to sample from
            column: Column to stratify by
            sample_size: Number of samples (defaults to Config.SAMPLE_SIZE)

        Returns:
            Sampled DataFrame
        """
        if sample_size is None:
            sample_size = Config.SAMPLE_SIZE

        # If DataFrame is smaller than sample size, return all
        if len(df) <= sample_size:
            return df

        # Drop NA values for stratification
        df_clean = df.dropna(subset=[column])

        # Get value counts for stratification
        value_counts = df_clean[column].value_counts()

        # Calculate proportional samples per stratum
        proportions = value_counts / len(df_clean)
        samples_per_stratum = (proportions * sample_size).round().astype(int)

        # Ensure at least 1 sample per stratum if possible
        samples_per_stratum = samples_per_stratum.clip(lower=1)

        # Adjust if total exceeds sample_size
        if samples_per_stratum.sum() > sample_size:
            # Reduce from largest strata
            diff = samples_per_stratum.sum() - sample_size
            largest_strata = samples_per_stratum.nlargest(diff).index
            samples_per_stratum[largest_strata] -= 1

        # Perform stratified sampling
        sampled_dfs = []
        for value, n_samples in samples_per_stratum.items():
            stratum = df_clean[df_clean[column] == value]
            if len(stratum) > 0:
                sampled = stratum.sample(n=min(n_samples, len(stratum)), random_state=42)
                sampled_dfs.append(sampled)

        return pd.concat(sampled_dfs, ignore_index=True)

    @staticmethod
    def random_sample(df: pd.DataFrame, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Perform simple random sampling

        Args:
            df: DataFrame to sample from
            sample_size: Number of samples (defaults to Config.SAMPLE_SIZE)

        Returns:
            Sampled DataFrame
        """
        if sample_size is None:
            sample_size = Config.SAMPLE_SIZE

        # If DataFrame is smaller than sample size, return all
        if len(df) <= sample_size:
            return df

        return df.sample(n=sample_size, random_state=42)

    @staticmethod
    def sample_with_token_limit(
        df: pd.DataFrame,
        column: str,
        max_tokens: Optional[int] = None,
        strategy: str = "stratified",
    ) -> pd.DataFrame:
        """
        Sample data while respecting token limits

        Args:
            df: DataFrame to sample from
            column: Column to analyze
            max_tokens: Maximum tokens allowed (defaults to Config.MAX_TOKENS_FOR_SAMPLING)
            strategy: Sampling strategy ('stratified' or 'random')

        Returns:
            Sampled DataFrame that fits within token limit
        """
        if max_tokens is None:
            max_tokens = Config.MAX_TOKENS_FOR_SAMPLING

        # Start with configured sample size
        sample_size = Config.SAMPLE_SIZE

        while sample_size > 0:
            # Sample data
            if strategy == "stratified":
                sampled_df = DataSampler.stratified_sample(df, column, sample_size)
            else:
                sampled_df = DataSampler.random_sample(df, sample_size)

            # Estimate tokens
            sample_text = "\n".join(sampled_df[column].astype(str).tolist())
            estimated_tokens = DataSampler.estimate_tokens(sample_text)

            # Check if within limit
            if estimated_tokens <= max_tokens:
                return sampled_df

            # Reduce sample size
            sample_size = int(sample_size * 0.8)

        # If we can't fit anything, return minimal sample
        return df.head(1)

    @staticmethod
    def get_column_sample(
        df: pd.DataFrame, column: str, sample_size: Optional[int] = None
    ) -> List[str]:
        """
        Get a sample of unique values from a column

        Args:
            df: DataFrame
            column: Column name
            sample_size: Number of samples (defaults to Config.SAMPLE_SIZE)

        Returns:
            List of sampled values as strings
        """
        if sample_size is None:
            sample_size = Config.SAMPLE_SIZE

        # Get unique values
        unique_values = df[column].dropna().unique()

        # Sample if needed
        if len(unique_values) > sample_size:
            unique_values = np.random.choice(unique_values, size=sample_size, replace=False)

        return [str(val) for val in unique_values]
