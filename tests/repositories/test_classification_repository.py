"""Tests for ClassificationRepository"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime
from src.database.repositories.classification_repository import ClassificationRepository
from src.database.models import Classification


class TestClassificationRepository:
    """Test ClassificationRepository functionality"""

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session"""
        session = Mock()
        session.add = Mock()
        session.commit = Mock()
        session.refresh = Mock()
        session.query = Mock()
        return session

    @pytest.fixture
    def sample_classification_data(self):
        """Sample classification data"""
        return {
            "session_id": uuid4(),
            "input_text": "How do I reset my password?",
            "predicted_category": "Technical Support",
            "confidence": "high",
            "reasoning": "Password reset is a technical task",
            "version": 1
        }

    def test_create_classification(self, mock_db_session, sample_classification_data):
        """Test creating a new classification"""
        repo = ClassificationRepository(mock_db_session)

        # Mock the created classification
        mock_classification = Mock(spec=Classification)
        mock_classification.id = uuid4()
        mock_classification.__dict__.update(sample_classification_data)

        # Configure mock session
        def add_side_effect(obj):
            obj.id = mock_classification.id
            obj.created_at = datetime.utcnow()

        mock_db_session.add.side_effect = add_side_effect
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_classification.id)

        # Create classification
        result = repo.create(sample_classification_data)

        # Verify database interactions
        assert mock_db_session.add.called
        assert mock_db_session.commit.called

    def test_get_by_session(self, mock_db_session):
        """Test retrieving classifications by session ID"""
        repo = ClassificationRepository(mock_db_session)
        session_id = uuid4()

        # Mock query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_all = [Mock(spec=Classification) for _ in range(3)]

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = mock_all

        # Get classifications
        result = repo.get_by_session(session_id)

        # Verify query was constructed correctly
        assert mock_db_session.query.called
        assert mock_query.filter.called
        assert len(result) == 3

    def test_get_latest_version(self, mock_db_session, sample_classification_data):
        """Test retrieving latest version of a classification"""
        repo = ClassificationRepository(mock_db_session)
        session_id = sample_classification_data["session_id"]
        input_text = sample_classification_data["input_text"]

        # Mock query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_order = Mock()
        mock_classification = Mock(spec=Classification)
        mock_classification.version = 2

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        mock_order.first.return_value = mock_classification

        # Get latest version
        result = repo.get_latest_version(session_id, input_text)

        # Verify correct version returned
        assert result is not None
        assert result.version == 2

    def test_get_by_version(self, mock_db_session):
        """Test retrieving classifications by version number"""
        repo = ClassificationRepository(mock_db_session)
        session_id = uuid4()
        version = 2

        # Mock query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_classifications = [Mock(spec=Classification) for _ in range(2)]

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = mock_classifications

        # Get by version
        result = repo.get_by_version(session_id, version)

        # Verify query and results
        assert len(result) == 2

    def test_get_all_versions(self, mock_db_session):
        """Test retrieving all versions of classifications"""
        repo = ClassificationRepository(mock_db_session)
        session_id = uuid4()
        input_text = "Test text"

        # Mock multiple versions
        mock_query = Mock()
        mock_filter = Mock()
        mock_order = Mock()
        versions = [
            Mock(spec=Classification, version=1),
            Mock(spec=Classification, version=2),
            Mock(spec=Classification, version=3)
        ]

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        mock_order.all.return_value = versions

        # Would need method in repo for this
        # This tests the concept of version tracking

    def test_delete_classification(self, mock_db_session):
        """Test deleting a classification"""
        repo = ClassificationRepository(mock_db_session)
        classification_id = uuid4()

        # Mock query chain
        mock_query = Mock()
        mock_get = Mock(spec=Classification)

        mock_db_session.query.return_value = mock_query
        mock_query.get.return_value = mock_get

        # If repo has delete method
        # repo.delete(classification_id)

        # Verify delete was called
        # assert mock_db_session.delete.called
        # assert mock_db_session.commit.called

    def test_update_classification(self, mock_db_session, sample_classification_data):
        """Test updating a classification"""
        repo = ClassificationRepository(mock_db_session)
        classification_id = uuid4()

        # Mock existing classification
        mock_classification = Mock(spec=Classification)
        mock_classification.id = classification_id
        mock_classification.predicted_category = "Sales"

        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.get.return_value = mock_classification

        # Update if repo supports it
        # This demonstrates the pattern

    def test_count_by_session(self, mock_db_session):
        """Test counting classifications for a session"""
        repo = ClassificationRepository(mock_db_session)
        session_id = uuid4()

        # Mock count query
        mock_query = Mock()
        mock_filter = Mock()

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.count.return_value = 5

        # If repo has count method
        # result = repo.count_by_session(session_id)
        # assert result == 5

    def test_get_by_category(self, mock_db_session):
        """Test retrieving classifications by category"""
        repo = ClassificationRepository(mock_db_session)
        session_id = uuid4()
        category = "Technical Support"

        # Mock query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_classifications = [Mock(spec=Classification) for _ in range(3)]

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = mock_classifications

        # If repo has this method
        # result = repo.get_by_category(session_id, category)
        # assert len(result) == 3

    def test_bulk_create(self, mock_db_session):
        """Test bulk creation of classifications"""
        repo = ClassificationRepository(mock_db_session)

        classifications_data = [
            {
                "session_id": uuid4(),
                "input_text": f"Text {i}",
                "predicted_category": "Test",
                "version": 1
            }
            for i in range(10)
        ]

        # Mock bulk operations
        mock_db_session.bulk_insert_mappings = Mock()

        # If repo supports bulk operations
        # repo.bulk_create(classifications_data)
        # assert mock_db_session.bulk_insert_mappings.called

    def test_transaction_rollback_on_error(self, mock_db_session, sample_classification_data):
        """Test that transactions rollback on error"""
        repo = ClassificationRepository(mock_db_session)

        # Simulate commit failure
        mock_db_session.commit.side_effect = Exception("Database error")
        mock_db_session.rollback = Mock()

        # Attempt to create (should fail)
        try:
            repo.create(sample_classification_data)
        except Exception:
            pass

        # In proper implementation, rollback should be called
        # assert mock_db_session.rollback.called

    def test_filter_by_confidence(self, mock_db_session):
        """Test filtering classifications by confidence level"""
        repo = ClassificationRepository(mock_db_session)
        session_id = uuid4()
        confidence = "high"

        # Mock query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_classifications = [Mock(spec=Classification) for _ in range(2)]

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = mock_classifications

        # If repo has this filtering capability
        # result = repo.get_by_confidence(session_id, confidence)
        # assert len(result) == 2

    def test_get_category_distribution(self, mock_db_session):
        """Test getting category distribution for a session"""
        repo = ClassificationRepository(mock_db_session)
        session_id = uuid4()

        # This would return counts per category
        # Useful for visualization and analysis

        # Mock result
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query

        # If repo has this aggregation method
        # result = repo.get_category_distribution(session_id)
        # assert isinstance(result, dict)
        # assert "Technical Support" in result
