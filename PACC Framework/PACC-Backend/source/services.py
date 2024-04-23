import crud, models, schemas, forms
from sqlalchemy.orm import Session
import socket
import pickle
import time


def create_merged_info(db: Session, training_req: forms.TrainingRequest):
    training = schemas.Training(
        id=training_req.id,
        model=training_req.model,
        dataset=training_req.dataset
    )
    hyperparam = schemas.Hyperparam(
        id=training_req.id,
        lr=training_req.hyperparameters["learningRate"],
        bs=training_req.hyperparameters["batchSize"],
        epochs=training_req.hyperparameters["epochs"],
        optim=training_req.hyperparameters["optimizer"],
        lossfct=training_req.hyperparameters["lossFunction"],
    )
    nodes = list()
    for node_id in training_req.nodes:
        nodes.append(schemas.Node(
            id=training_req.id,
            node=node_id
        ))
    status = schemas.Status(
        id=training_req.id,
        progress=0.0,
        eta=0,
        epoch=0,
        accuracy='',
        loss='',
        mae='',
        current_state=0.0
    )
    request = schemas.Request(
        id=training_req.id,
        stop_req=0
    )

    try:
        crud.create_merged_info_by_training_req(db,training,hyperparam,nodes,status)
    except Exception as e:
        print(e)
        raise e


def get_merged_info(db: Session, id: int):
    joined_info = crud.get_merged_info(db, id)

    if len(joined_info) >= 1:
        nodes = list()
        for joined_row in joined_info:
            nodes.append(joined_row.Node.node)
        merged_info = schemas.MergedInfo(
            id=joined_info[0].Training.id,
            model=joined_info[0].Training.model,
            dataset=joined_info[0].Training.dataset,
            progress=joined_info[0].Status.progress,

            eta=joined_info[0].Status.eta,
            epoch=joined_info[0].Status.epoch,
            accuracy=joined_info[0].Status.accuracy,

            loss=joined_info[0].Status.loss,
            lr=joined_info[0].Hyperparam.lr,
            bs=joined_info[0].Hyperparam.bs,
            epochs=joined_info[0].Hyperparam.epochs,
            optim=joined_info[0].Hyperparam.optim,
            lossfct=joined_info[0].Hyperparam.lossfct,
            nodes=nodes
        )

        return merged_info

    return None


def put_status(db: Session, id: int, status_req: forms.StatusRequest):
    status = schemas.Status(
        id=id,
        progress=status_req.progress,
        eta=status_req.eta,
        epoch=status_req.epoch,
        accuracy=status_req.accuracy,
        loss=status_req.loss,
        mae=status_req.mae,
        current_state=status_req.current_state
    )
    crud.update_status_by_id(db,id,status)


def delete_merged_info(db: Session, id: int):
    crud.delete_merged_info_by_id(db, id)


def send_command_to_nodes(training_req: forms.TrainingRequest):
    nodes_with_port = list()
    start_port = 6000

    for nn in training_req.nodes:
        nodes_with_port.append(nn+f':{start_port}')
        start_port += 1

    parent_list, children_lists = make_bin_dep_list(nodes_with_port)
    req = forms.NodeRequest(
        id=training_req.id,
        command=0,
        model=training_req.model,
        dataset=training_req.dataset,
        hyperparameters=training_req.hyperparameters,
    )

    try: 
        start_port = 6000
        for idx, node in enumerate(training_req.nodes):
            req.parent_node = parent_list[idx]
            req.children_nodes = children_lists[idx]
            req.local_port = start_port
            print(training_req.status)
            req.status = training_req.status[idx]
            start_port += 1

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((node,22222))
                req_ser = pickle.dumps(req)
                sock.send(req_ser)
            except Exception as e:
                raise(e)
            finally:
                sock.close()
                if idx != len(training_req.nodes) - 1:
                    time.sleep(3)

    except Exception as e:
        raise e


def stop_training(db: Session, id: int):
    request = schemas.Request(
        id=id,
        stop_req=1
    )
    
    try: 
        crud.update_request_by_id(db, id, request)
    except Exception as e:
        raise e


def is_training_exist(db: Session, id: int):
    training = crud.get_training_by_id(db, id)
    if training != None:
        return True
    return False


def make_bin_dep_list(node_list: list) -> tuple[list]:
    parent_lists = list() # element type => str
    children_lists = list() # element type => list

    for i in range(len(node_list)):
        # Add parent
        if i == 0:
            parent_lists.append(None)
        else:
            parent_lists.append(node_list[(i - 1) // 2])

        # Add child
        children_list = list()
        
        first_child_idx = i * 2 + 1
        second_child_idx = i * 2 + 2
        
        if first_child_idx < len(node_list):
            children_list.append(node_list[first_child_idx])
        if second_child_idx < len(node_list):
            children_list.append(node_list[second_child_idx])

        children_lists.append(children_list)
            

    return (parent_lists, children_lists)

        