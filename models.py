#region imports
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
#endregion 

# ------------------------
#   DB TABLE DEFINITIONS
# ------------------------

Base = declarative_base()

utcnow = lambda: datetime.now(timezone.utc)  

class Form(Base):
    __tablename__ = "forms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(12), nullable=False)
    url_id = Column(String(12), nullable=False)
    form_name = Column(String(255), nullable=False)
    
    submissions = Column(MutableList.as_mutable(JSON), default=list)
    created_on = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    delete_on = Column(DateTime(timezone=True), nullable=True)

    fields = relationship("FormField", back_populates="form", cascade="all, delete-orphan", lazy="joined")


class FormField(Base):
    __tablename__ = "form_fields"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(UUID(as_uuid=True), ForeignKey("forms.id", ondelete="CASCADE"), nullable=False)

    field_id = Column(String(255), nullable=False)
    field_type = Column(String(50), nullable=False)
    label = Column(String(255), nullable=False)
    required = Column(Boolean, default=False)

    form = relationship("Form", back_populates="fields")
