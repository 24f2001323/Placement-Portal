from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, DateTime
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # hashed in real apps
    created_at = Column(DateTime, default=datetime.utcnow)


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    website = Column(String)
    email = Column(String)
    jobs = relationship("JobPosition", back_populates="company") 


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    resume_link = Column(String)
    applications = relationship("Application", back_populates="student")  


class JobPosition(Base):
    __tablename__ = "job_positions"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    location = Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job") 


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    job_id = Column(Integer, ForeignKey("job_positions.id"))
    applied_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Pending")  

    student = relationship("Student", back_populates="applications")
    job = relationship("JobPosition", back_populates="applications")
    placement = relationship("Placement", back_populates="application", uselist=False)  


class Placement(Base):
    __tablename__ = "placements"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True)
    placed_at = Column(DateTime, default=datetime.utcnow)
    package_offer = Column(String)

    application = relationship("Application", back_populates="placement")


def init_db(db_url="sqlite:///placement_portal.db", echo=True):
    """
    Initialize the SQLite database and create all tables.
    Returns a SQLAlchemy session object.
    """
    engine = create_engine(db_url, echo=echo)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
