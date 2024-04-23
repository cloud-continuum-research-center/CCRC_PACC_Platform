from pydantic import BaseModel


class TrainingBase(BaseModel):
    id: int
    model:int
    dataset: int

class TrainingCreate(TrainingBase):
    pass

class Training(TrainingBase):
    pass


class HyperparamBase(BaseModel):
    id: int
    lr: float
    bs: int
    epochs: int
    optim: int
    lossfct: int

class HyperparamCreate(HyperparamBase):
    pass

class Hyperparam(HyperparamBase):
    pass


class NodeBase(BaseModel):
    id: int
    node: str

class NodeCreate(NodeBase):
    pass

class Node(NodeBase):
    pass


# 현재 epoch 추가
# 전체 epoch 추가 <= request할 때 updator thead에서 저장하고 매 업데이트마다 함께 보냄
class StatusBase(BaseModel):
    id: int
    progress: float
    eta: int
    epoch: int
    # total_epoch
    accuracy: str # acc list
    loss: str# loss list
    mae: str # mae list
    current_state: int

class StatusCreate(StatusBase):
    pass

class Status(StatusBase):
    pass


class RequestBase(BaseModel):
    id: int
    stop_req: int

class RequestCreate(RequestBase):
    pass

class Request(RequestBase):
    pass



class MergedInfo(BaseModel):
    # training
    id: int
    model:int
    dataset: int

    # hyperparams
    lr: float
    bs: int
    epochs: int
    optim: int
    lossfct: int

    # node list
    nodes: list

    # status
    progress: float
    eta: int
    epoch: int
    accuracy: float
    loss: float