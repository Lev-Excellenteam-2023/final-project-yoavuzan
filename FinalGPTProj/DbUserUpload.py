# DbUserUpload.py

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import create_engine

UPLOADS_FOLDER = "uploads"
OUTPUTS_FOLDER = "outputs"
DB_FILE = "db/explainer.db"

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False)
    uploads = relationship("Upload", back_populates="user", cascade="all, delete-orphan")

class Upload(Base):
    __tablename__ = 'uploads'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(300), nullable=False, unique=True)
    filename = Column(String, nullable=False)
    upload_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    finish_time = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)  # Use String type for compatibility with all databases

    # Additional upload statuses
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_DONE = "done"
    STATUS_FAILED = "failed"

    # Constraints
    __table_args__ = (
        UniqueConstraint('uid'),
        UniqueConstraint('filename'),
    )

    # Cascades for user deletion
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    user = relationship("User", back_populates="uploads")

    def set_finish_time(self):
        self.finish_time = datetime.utcnow()

    def upload_path(self):
        # Implement this method to compute the path of the uploaded file based on the metadata in the DB
        pass

    def set_status(self, status):
        if status not in [Upload.STATUS_PENDING, Upload.STATUS_PROCESSING, Upload.STATUS_DONE, Upload.STATUS_FAILED]:
            raise ValueError("Invalid status value.")
        self.status = status

    def set_failed(self):
        self.status = Upload.STATUS_FAILED

    def set_processing(self):
        self.status = Upload.STATUS_PROCESSING

    def set_done(self):
        self.status = Upload.STATUS_DONE

    def get_error_message(self):
        # Implement this method to get error messages for failed uploads
        pass



# Database configuration
def create_database_engine():
    engine = create_engine(f'sqlite:///{DB_FILE}')
    Base.metadata.create_all(engine)
    return engine
    #pull request test