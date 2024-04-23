from sqlalchemy import Integer, String, Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Training(Base):
    __tablename__ = "trainings"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False) 
    model: Mapped[int] = mapped_column(Integer())
    dataset: Mapped[int] = mapped_column(Integer())


class Hyperparam(Base):
    __tablename__ = "hyperparams"

    id: Mapped[int] = mapped_column(ForeignKey("trainings.id"), primary_key=True) 
    lr: Mapped[float] = mapped_column(Float())
    bs: Mapped[int] = mapped_column(Integer())
    epochs: Mapped[int] = mapped_column(Integer())
    optim: Mapped[int] = mapped_column(Integer())
    lossfct: Mapped[int] = mapped_column(Integer())


class Node(Base):
    __tablename__ = "nodes"
    
    record_id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    id: Mapped[int] = mapped_column(ForeignKey("trainings.id"))
    node: Mapped[str] = mapped_column(String())


# Put 할 필요 없이 바로 insert
# Get 할 때는 record 루프돌면서 list append
class Status(Base):
    __tablename__ = "status"

    id: Mapped[int] = mapped_column(ForeignKey("trainings.id"), primary_key=True)
    progress: Mapped[float] = mapped_column(Float())
    eta: Mapped[int] = mapped_column(Integer())
    epoch: Mapped[int] = mapped_column(Integer())
    accuracy: Mapped[str] = mapped_column(String())
    loss: Mapped[str] = mapped_column(String()) # Loss
    mae: Mapped[str] = mapped_column(String()) # mae list
    current_state: Mapped[int] = mapped_column(Integer())

class Request(Base):
    __tablename__ = "request"

    id: Mapped[int] = mapped_column(ForeignKey("trainings.id"), primary_key=True)
    stop_req: Mapped[int] = mapped_column(Integer())