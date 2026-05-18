from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime
from app.api.session import Base

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(String(255), primary_key=True, index=True)
    task_type = Column(String(50))
    status = Column(String(50))
    input_text = Column(Text)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
