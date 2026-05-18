from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.api.session import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(String(36), unique=True, index=True)

    task_type = Column(String(50))

    status = Column(String(20))

    input_text = Column(Text)

    result = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)