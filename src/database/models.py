"""Database models for the Semantic Classifier application"""
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class Session(Base):
    """
    User sessions for file uploads and classification workflows
    Tracks the entire workflow from file upload to classification
    """

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(
        String(50),
        nullable=False,
        default="pending_upload",
        comment="pending_upload | file_uploaded | categories_discovered | classification_in_progress | completed",
    )

    # File metadata
    original_filename = Column(String(255), nullable=True)
    file_type = Column(String(20), nullable=True, comment="csv | excel")
    selected_sheet = Column(String(100), nullable=True, comment="For Excel files")
    selected_column = Column(String(100), nullable=True, comment="Column to classify")
    total_rows = Column(Integer, nullable=True)
    total_columns = Column(Integer, nullable=True)

    # Column detection metadata
    column_metadata = Column(
        JSONB,
        nullable=True,
        comment="All detected columns with stats and text analysis",
    )

    # Categories (discovered by LLM)
    categories = Column(
        JSONB,
        nullable=True,
        comment="Array of category definitions with name, description, boundary, examples",
    )
    num_categories = Column(Integer, nullable=True)

    # LLM settings used
    llm_model = Column(String(100), nullable=True)
    llm_temperature = Column(Float, nullable=True)

    # Classification metadata
    classification_sample_size = Column(Integer, nullable=True)
    classification_mode = Column(
        String(50), nullable=True, comment="sample | full_dataset"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    uploads = relationship("Upload", back_populates="session", cascade="all, delete-orphan")
    classifications = relationship(
        "Classification", back_populates="session", cascade="all, delete-orphan"
    )


class Upload(Base):
    """
    Tracks uploaded files and their processing status
    """

    __tablename__ = "uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)

    # File details
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(512), nullable=True, comment="Path in Supabase Storage (session_id/filename)")
    file_type = Column(String(20), nullable=False, comment="csv | excel")
    file_size_bytes = Column(BigInteger, nullable=False)
    file_hash = Column(String(64), nullable=True, comment="MD5 hash for deduplication")

    # Parsing metadata
    encoding = Column(String(50), nullable=True, comment="For CSV files")
    sheets = Column(JSONB, nullable=True, comment="List of sheet names for Excel")
    row_count = Column(Integer, nullable=False)
    column_count = Column(Integer, nullable=False)
    column_metadata = Column(JSONB, nullable=True, comment="Column statistics")

    # Processing status
    status = Column(
        String(50),
        nullable=False,
        default="uploaded",
        comment="uploaded | processing | processed | error",
    )
    error_message = Column(Text, nullable=True)

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    session = relationship("Session", back_populates="uploads")


class Classification(Base):
    """
    Individual classification results for each value
    """

    __tablename__ = "classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)

    # Input data
    input_text = Column(Text, nullable=False, comment="Original text that was classified")
    row_index = Column(Integer, nullable=True, comment="Row number in original dataset")

    # Classification result
    predicted_category = Column(String(255), nullable=False)
    confidence = Column(
        String(20), nullable=True, comment="high | medium | low (from LLM)"
    )
    version = Column(Integer, nullable=False, default=1, comment="Classification version (increments on retry)")

    # LLM metadata
    llm_model = Column(String(100), nullable=True)
    llm_temperature = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)

    # Success/error tracking
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)

    # Additional metadata
    extra_data = Column(JSONB, nullable=True, comment="Any additional classification data")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("Session", back_populates="classifications")
    feedback = relationship(
        "Feedback", back_populates="classification", uselist=False, cascade="all, delete-orphan"
    )


class Feedback(Base):
    """
    User feedback on classifications (for future improvement)
    """

    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    classification_id = Column(
        UUID(as_uuid=True), ForeignKey("classifications.id"), nullable=False, unique=True
    )

    # Feedback data
    original_prediction = Column(String(255), nullable=False)
    user_correction = Column(String(255), nullable=True, comment="User's suggested category")
    is_correct = Column(Boolean, nullable=True, comment="Was the prediction correct?")
    is_helpful = Column(Boolean, nullable=True, comment="Was the classification helpful?")

    # User comments
    reason_text = Column(Text, nullable=True, comment="Why user disagreed")
    user_confidence = Column(String(20), nullable=True, comment="User's confidence level")

    # Extracted signals (for future ML)
    signals = Column(
        JSONB,
        nullable=True,
        comment="Keywords, sentiment, error_type extracted from feedback",
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    classification = relationship("Classification", back_populates="feedback")


class CategoryHistory(Base):
    """
    Tracks category modifications and refinements
    """

    __tablename__ = "category_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)

    # Category version
    version = Column(Integer, nullable=False, default=1)

    # Category data
    categories = Column(
        JSONB,
        nullable=False,
        comment="Snapshot of categories at this version",
    )

    # Change metadata
    change_type = Column(
        String(50),
        nullable=False,
        comment="initial_discovery | user_edit | llm_refinement",
    )
    change_description = Column(Text, nullable=True, comment="What changed")
    user_feedback = Column(Text, nullable=True, comment="User's feedback that triggered change")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Create indexes
from sqlalchemy import Index

# Session indexes
Index("idx_sessions_status_created", Session.status, Session.created_at)
Index("idx_sessions_expires", Session.expires_at)

# Upload indexes
Index("idx_uploads_session", Upload.session_id)
Index("idx_uploads_hash", Upload.file_hash)
Index("idx_uploads_uploaded_at", Upload.uploaded_at)

# Classification indexes
Index("idx_classifications_session", Classification.session_id)
Index("idx_classifications_category", Classification.predicted_category)
Index("idx_classifications_created", Classification.created_at)

# Feedback indexes
Index("idx_feedback_classification", Feedback.classification_id)

# Category history indexes
Index("idx_category_history_session", CategoryHistory.session_id)
Index("idx_category_history_version", CategoryHistory.session_id, CategoryHistory.version)
