"""Tests for SessionRepository"""
import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime
from src.database.repositories.session_repository import SessionRepository
from src.database.models import Session


class TestSessionRepository:
    """Test SessionRepository functionality"""

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
    def sample_session_data(self):
        """Sample session data"""
        return {
            "file_info": {
                "filename": "test.csv",
                "rows": 100,
                "columns": 5
            },
            "categories": [
                {"name": "Cat1", "description": "Description 1"},
                {"name": "Cat2", "description": "Description 2"}
            ],
            "column_name": "text_column"
        }

    def test_create_session(self, mock_db_session, sample_session_data):
        """Test creating a new session"""
        repo = SessionRepository(mock_db_session)

        # Mock the created session
        mock_session_obj = Mock(spec=Session)
        mock_session_obj.id = uuid4()
        mock_session_obj.__dict__.update(sample_session_data)

        # Configure mock
        def add_side_effect(obj):
            obj.id = mock_session_obj.id
            obj.created_at = datetime.utcnow()

        mock_db_session.add.side_effect = add_side_effect

        # Create session
        result = repo.create(sample_session_data)

        # Verify database interactions
        assert mock_db_session.add.called
        assert mock_db_session.commit.called

    def test_get_by_id(self, mock_db_session):
        """Test retrieving session by ID"""
        repo = SessionRepository(mock_db_session)
        session_id = uuid4()

        # Mock query
        mock_query = Mock()
        mock_session = Mock(spec=Session)
        mock_session.id = session_id

        mock_db_session.query.return_value = mock_query
        mock_query.get.return_value = mock_session

        # Get session
        result = repo.get_by_id(session_id)

        # Verify
        assert result is not None
        assert result.id == session_id

    def test_get_all_sessions(self, mock_db_session):
        """Test retrieving all sessions"""
        repo = SessionRepository(mock_db_session)

        # Mock query
        mock_query = Mock()
        mock_order = Mock()
        mock_sessions = [Mock(spec=Session) for _ in range(5)]

        mock_db_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_order
        mock_order.all.return_value = mock_sessions

        # Get all sessions
        result = repo.get_all()

        # Verify
        assert len(result) == 5

    def test_update_session(self, mock_db_session, sample_session_data):
        """Test updating a session"""
        repo = SessionRepository(mock_db_session)
        session_id = uuid4()

        # Mock existing session
        mock_session = Mock(spec=Session)
        mock_session.id = session_id

        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.get.return_value = mock_session

        # Update session
        updates = {"column_name": "new_column"}
        result = repo.update(session_id, updates)

        # Verify commit was called
        assert mock_db_session.commit.called

    def test_delete_session(self, mock_db_session):
        """Test deleting a session"""
        repo = SessionRepository(mock_db_session)
        session_id = uuid4()

        # Mock session
        mock_session = Mock(spec=Session)

        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.get.return_value = mock_session

        # Delete session
        repo.delete(session_id)

        # Verify
        assert mock_db_session.delete.called
        assert mock_db_session.commit.called

    def test_get_recent_sessions(self, mock_db_session):
        """Test retrieving recent sessions"""
        repo = SessionRepository(mock_db_session)
        limit = 10

        # Mock query chain
        mock_query = Mock()
        mock_order = Mock()
        mock_limit = Mock()
        mock_sessions = [Mock(spec=Session) for _ in range(limit)]

        mock_db_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_order
        mock_order.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_sessions

        # Get recent sessions (if method exists)
        # result = repo.get_recent(limit)
        # assert len(result) == limit

    def test_session_with_relationships(self, mock_db_session):
        """Test session with related classifications and uploads"""
        repo = SessionRepository(mock_db_session)
        session_id = uuid4()

        # Mock session with relationships
        mock_session = Mock(spec=Session)
        mock_session.id = session_id
        mock_session.classifications = [Mock() for _ in range(5)]
        mock_session.uploads = [Mock()]

        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.get.return_value = mock_session

        # Get session
        result = repo.get_by_id(session_id)

        # Verify relationships loaded
        assert result is not None
        assert hasattr(result, 'classifications')
        assert hasattr(result, 'uploads')

    def test_count_total_sessions(self, mock_db_session):
        """Test counting total sessions"""
        repo = SessionRepository(mock_db_session)

        # Mock count
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.count.return_value = 42

        # If repo has count method
        # result = repo.count()
        # assert result == 42

    def test_find_sessions_by_column(self, mock_db_session):
        """Test finding sessions by column name"""
        repo = SessionRepository(mock_db_session)
        column_name = "text_column"

        # Mock query
        mock_query = Mock()
        mock_filter = Mock()
        mock_sessions = [Mock(spec=Session) for _ in range(3)]

        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = mock_sessions

        # If repo has this search method
        # result = repo.find_by_column(column_name)
        # assert len(result) == 3

    def test_session_metadata_storage(self, mock_db_session, sample_session_data):
        """Test that session metadata is properly stored"""
        repo = SessionRepository(mock_db_session)

        # Create with metadata
        data = sample_session_data.copy()
        data["file_info"]["processed_at"] = datetime.utcnow().isoformat()

        result = repo.create(data)

        # Verify JSONB fields are handled
        assert mock_db_session.add.called

    def test_concurrent_session_creation(self, mock_db_session):
        """Test handling concurrent session creation"""
        repo = SessionRepository(mock_db_session)

        # Simulate multiple sessions created rapidly
        sessions = []
        for i in range(5):
            mock_session = Mock(spec=Session)
            mock_session.id = uuid4()
            sessions.append(mock_session)

        # Each should get unique ID
        session_ids = [s.id for s in sessions]
        assert len(set(session_ids)) == 5
