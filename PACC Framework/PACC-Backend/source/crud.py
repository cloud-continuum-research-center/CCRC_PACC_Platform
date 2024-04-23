from sqlalchemy import insert, update, delete
from sqlalchemy.orm import Session

import models, schemas

def create_training(db: Session, training: schemas.Training):
    db_training = models.Training(
        id=training.id,
        model=training.model,
        dataset=training.dataset
    )
    db.add(db_training)
    db.commit()
    db.refresh(db_training)
    return db_training

def get_training_by_id(db: Session, id: int) -> schemas.Training:
    return db.query(models.Training).filter(models.Training.id == id).first()

def update_training_by_id(db: Session, training: schemas.Training):
    update_stmt = (
        update(models.Training).
        where(models.Training.id == id).
        values({
            "model": training.model,
            "dataset": training.dataset,
        })
    )
    db.execute(update_stmt)
    db.commit()
    return None

def delete_training_by_id(db: Session, id: int):
    delete_stmt = (
        delete(models.Training).
        where(models.Training.id == id)
    )
    db.execute(delete_stmt)
    db.commit()
    return None

def create_hyperparam(db: Session, hyperparam: schemas.Hyperparam):
    db_hyperparam = models.Hyperparam(
        id=hyperparam.id,
        lr=hyperparam.lr,
        bs=hyperparam.bs,
        epochs=hyperparam.epochs,
        optim=hyperparam.optim,
        lossfct=hyperparam.lossfct
    )
    db.add(db_hyperparam)
    db.commit()
    db.refresh(db_hyperparam)
    return db_hyperparam

def get_hyperparam_by_id(db: Session, id: int):
    return db.query(models.Hyperparam).filter(models.Hyperparam.id == id).first()

def update_hyperparam_by_id(db: Session, hyperparam: schemas.Hyperparam):
    update_stmt = (
        update(models.Training).
        where(models.Training.id == id).
        values({
            "lr": hyperparam.lr,
            "bs": hyperparam.bs,
            "epochs": hyperparam.epochs,
            "optim": hyperparam.optim,
            "lossfct": hyperparam.lossfct
        })
    )
    db.execute(update_stmt)
    db.commit()
    return None

def delete_hyperparam_by_id(db: Session, id: int):
    delete_stmt = (
        delete(models.Hyperparam).
        where(models.Hyperparam.id == id)
    )
    db.execute(delete_stmt)
    db.commit()
    return None

def create_node(db: Session, node: schemas.Node):
    db_node = models.Node(
        id=node.id,
        node=node.node
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

def get_node_by_id(db: Session, id: int):
    return db.query(models.Node).filter(models.Node.id == id).all()

def update_node_by_id(db: Session, node: schemas.Node):
    update_stmt = (
        update(models.Node).
        where(models.Node.id == id).
        values({
            "id": node.id,
            "node": node.node
        })
    )
    db.execute(update_stmt)
    db.commit()
    return None

def delete_node_by_id(db: Session, id: int):
    delete_stmt = (
        delete(models.Node).
        where(models.Node.id == id)
    )
    db.execute(delete_stmt)
    db.commit()
    return None

def create_status(db: Session, status: schemas.Status):
    db_status = models.Status(
        id=status.id,
        progress=status.progress,
        eta=status.eta,
        epoch=status.epoch,
        accuracy=status.accuracy,
        loss=status.loss,
        mae=status.mae,
        current_state=status.current_state
    )
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status

def get_status_by_id(db: Session, id: int):
    return db.query(models.Status).filter(models.Status.id == id).first()

def update_status_by_id(db: Session, id: int, status: schemas.Status):
    update_stmt = (
        update(models.Status).
        where(models.Status.id == id).
        values({
            "id": status.id,
            "progress" : status.progress,
            "eta": status.eta,
            "epoch": status.epoch,
            "accuracy": status.accuracy,
            "loss": status.loss,
            "mae": status.mae,
            "current_state": status.current_state
        })
    )
    db.execute(update_stmt)
    db.commit()
    return None

def delete_status_by_id(db: Session, id: int):
    delete_stmt = (
        delete(models.Status).
        where(models.Status.id == id)
    )
    db.execute(delete_stmt)
    db.commit()
    return None

def delete_all_trainings(db: Session):
    delete_stmt = (
        delete(models.Training)
    )
    db.execute(delete_stmt)
    db.commit()
    return None

def delete_all_hyperparams(db: Session):
    delete_stmt = (
        delete(models.Hyperparam)
    )
    db.execute(delete_stmt)
    db.commit()
    return None

def delete_all_nodes(db: Session):
    delete_stmt = (
        delete(models.Node)
    )
    db.execute(delete_stmt)
    db.commit()
    return None
    
def delete_all_status(db: Session):
    delete_stmt = (
        delete(models.Status)
    )
    db.execute(delete_stmt)
    db.commit()
    return None

def create_merged_info_by_training_req(db: Session, training: schemas.Training, hyperparam: schemas.Hyperparam, nodes: list[schemas.Node], status: schemas.Status):
    training_model = models.Training(
        id=training.id,
        model=training.model,
        dataset=training.dataset
    )
    hyperparam_model = models.Hyperparam(
        id=training.id,
        lr=hyperparam.lr,
        bs=hyperparam.bs,
        epochs=hyperparam.epochs,
        optim=hyperparam.optim,
        lossfct=hyperparam.lossfct
    )
    nodes_param = list()
    status_model = models.Status(
        id=training.id,
        progress=0.0,
        eta=0,
        epoch=0,
        accuracy='',
        loss='',
        mae='',
        current_state=0
    )

    for node in nodes:
        nodes_param.append(
            {
                "id": node.id,
                "node": node.node
            }
        )

    request_model = models.Request(
        id=training.id,
        stop_req=0
    )

    # 최적화?
    db.add(training_model)
    db.add(hyperparam_model)
    db.execute(insert(models.Node), nodes_param) # Bulk insert
    db.add(status_model)
    db.add(request_model)
    db.commit()
    return None
    
def get_merged_info(db: Session, id: int):
    return db.query(models.Training,models.Hyperparam,models.Node,models.Status).join(models.Hyperparam).join(models.Node).join(models.Status).filter(models.Training.id == id).all()

def delete_merged_info_by_id(db :Session, id: int):
    # 최적화
    db.execute(delete(models.Training).where(models.Training.id == id))
    db.execute(delete(models.Hyperparam).where(models.Hyperparam.id == id))
    db.execute(delete(models.Node).where(models.Node.id == id))
    db.execute(delete(models.Status).where(models.Status.id == id))
    db.commit()

def create_request_by_id(db: Session, request: schemas.Request):
    db_request = models.Request(
        id=request.id,
        stop_req=request.stop_req
    )
    db.add(db_request)
    db.commit
    return None

def get_request_by_id(db: Session, id: int):
    return db.query(models.Request).filter(models.Request.id == id).first()

def update_request_by_id(db: Session, id: int, request: schemas.Request):
    update_stmt = (
        update(models.Request).
        where(models.Request.id == id).
        values({
            "stop_req": request.stop_req
        })
    )
    db.execute(update_stmt)
    db.commit()
    return None

def delete_all_requests(db: Session):
    delete_stmt = (
        delete(models.Request)
    )
    db.execute(delete_stmt)
    db.commit()
    return None

