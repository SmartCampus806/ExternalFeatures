from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    bookingGroupId = Column(String, index=True)
    room = Column(Integer, index=True)
    owner = Column(Integer, index=True)
    startTime = Column(DateTime)
    endTime = Column(DateTime)
    title = Column(String)
    description = Column(String)
    status = Column(String)


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    size = Column(Integer)
    specialty = Column(String)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    roomName = Column(String)
    capacity = Column(Integer)
    has_computers = Column(Boolean, default=False)
    has_projector = Column(Boolean, default=False)
    is_cathedral = Column(Boolean, default=False)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    fullName = Column(String)
    shortName = Column(String)
    color = Column(String)


class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    phone_number = Column(String, nullable=True)
    role = Column(String)
