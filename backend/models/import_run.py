import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from backend.database import Base


class ImportRun(Base):
    __tablename__ = "import_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    broker = Column(String, nullable=False)
    imported_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    trades_added = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="success")  # success | partial | failed
    errors = Column(String, nullable=True)  # JSON string

    def set_errors(self, errors: list):
        self.errors = json.dumps(errors)

    def get_errors(self) -> list:
        return json.loads(self.errors) if self.errors else []
