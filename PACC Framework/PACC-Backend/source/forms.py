from pydantic import BaseModel

class TrainingRequest(BaseModel):
    id: int
    model: int
    dataset: int
    hyperparameters: dict
    nodes: list[str]
    status: list[list]

class StatusRequest(BaseModel):
    progress: float
    eta: int
    epoch: int
    accuracy: str
    loss: str
    mae: str
    current_state: int

class TrainingResponse(BaseModel):
    success: bool
    code: int
    id: int
    message: str

class TrainingStatusResponse(TrainingResponse):
    progress: float
    eta: int 
    epoch: int
    total_epoch: int
    accuracy: list
    loss: list
    current_state: int


class TrainingRequestResponse(TrainingResponse):
    stop_req: int

class NodeRequest():
    id: int
    command: int
    model: int
    dataset: int
    hyperparameters: dict
    parent_node: str
    children_nodes: list
    local_port: int
    status: list

    def __init__(self, id=0, command=0, model=0, dataset=0, hyperparameters={}, parent_node="", children_nodes=[]) -> None:
        self.id = id
        self.command = command
        self.model = model
        self.dataset = dataset
        self.hyperparameters = hyperparameters
        self.parent_node = parent_node
        self.children_nodes = children_nodes
