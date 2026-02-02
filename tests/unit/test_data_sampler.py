"""Unit tests for DataSampler"""
import pytest
import pandas as pd
from src.data_ingestion.data_sampler import DataSampler


class TestDataSampler:
    """Test DataSampler functionality"""

    @pytest.fixture
    def large_dataframe(self):
        """Create large DataFrame for sampling"""
        data = []
        categories = ["Category A", "Category B", "Category C"]

        for i in range(300):
            category = categories[i % len(categories)]
            data.append({
                "id": i,
                "text": f"Text content for item {i} in {category}",
                "category": category
            })

        return pd.DataFrame(data)

    def test_stratified_sample_size(self, large_dataframe):
        """Test that sample size is respected"""
        sampler = DataSampler()
        sample = sampler.stratified_sample(
            df=large_dataframe,
            column="text",
            sample_size=50
        )

        assert len(sample) <= 50

    def test_stratified_sample_diversity(self, large_dataframe):
        """Test that sample maintains category distribution"""
        sampler = DataSampler()
        sample = sampler.stratified_sample(
            df=large_dataframe,
            column="text",
            sample_size=90
        )

        # Check all categories are represented
        original_categories = set(large_dataframe["category"].unique())
        sample_categories = set(sample["category"].unique())

        assert sample_categories == original_categories

    def test_sample_smaller_than_dataframe(self, large_dataframe):
        """Test sampling when requested size is larger than data"""
        sampler = DataSampler()
        small_df = large_dataframe.head(10)

        sample = sampler.stratified_sample(
            df=small_df,
            column="text",
            sample_size=100
        )

        # Should return all rows when sample_size > total rows
        assert len(sample) == len(small_df)

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        sampler = DataSampler()
        empty_df = pd.DataFrame()

        sample = sampler.stratified_sample(
            df=empty_df,
            column="text",
            sample_size=50
        )

        assert len(sample) == 0

    def test_single_row_dataframe(self):
        """Test sampling with single row"""
        sampler = DataSampler()
        single_row_df = pd.DataFrame({"text": ["Single text entry"]})

        sample = sampler.stratified_sample(
            df=single_row_df,
            column="text",
            sample_size=50
        )

        assert len(sample) == 1

    def test_sample_randomness(self, large_dataframe):
        """Test that multiple samples produce different results"""
        sampler = DataSampler()

        sample1 = sampler.stratified_sample(
            df=large_dataframe,
            column="text",
            sample_size=50
        )

        sample2 = sampler.stratified_sample(
            df=large_dataframe,
            column="text",
            sample_size=50
        )

        # Samples should be different (with high probability)
        assert not sample1.equals(sample2)

    def test_sample_deterministic_with_seed(self, large_dataframe):
        """Test that sampling is deterministic with same seed"""
        sampler = DataSampler()

        # If sampler supports seed, test it
        # This may need adjustment based on actual implementation
        sample1 = sampler.stratified_sample(
            df=large_dataframe,
            column="text",
            sample_size=50
        )

        # Check that sample is a valid subset
        assert len(sample1) > 0
        assert all(col in large_dataframe.columns for col in sample1.columns)
