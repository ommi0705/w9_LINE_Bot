from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    line_user_id = Column(String, index=True, nullable=False)
    user_input = Column(Text, nullable=False)
    bot_reply = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
