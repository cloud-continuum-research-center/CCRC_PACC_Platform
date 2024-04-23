from app import db
from app.models import User, Model, Dataset, Node, Project

def drop_user_table():
    User.__table__.drop(db.engine)
    db.session.commit()

def drop_model_table():
    Model.__table__.drop(db.engine)
    db.session.commit()

def drop_dataset_table():
    Dataset.__table__.drop(db.engine)
    db.session.commit()

def drop_node_table():
    Node.__table__.drop(db.engine)
    db.session.commit()

def drop_project_table():
    Project.__table__.drop(db.engine)
    db.session.commit()
    
# Functions to delete all data from tables
def delete_all_users():
    db.session.query(User).delete()
    db.session.commit()

def delete_all_models():
    db.session.query(Model).delete()
    db.session.commit()

def delete_all_datasets():
    db.session.query(Dataset).delete()
    db.session.commit()

def delete_all_nodes():
    db.session.query(Node).delete()
    db.session.commit()

def delete_all_projects():
    db.session.query(Project).delete()
    db.session.commit()
