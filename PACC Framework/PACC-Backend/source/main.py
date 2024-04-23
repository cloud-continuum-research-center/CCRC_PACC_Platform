# Fastapi
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse, JSONResponse
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from os import environ
import math

# Sqlalchemy
from sqlalchemy.orm import Session
import crud, models, schemas, services, forms
from database import SessionLocal, engine
from sqlalchemy.exc import IntegrityError, NoResultFound

FASTAPI_IP = environ['FASTAPI_IP']
FASTAPI_PORT = int(environ['FASTAPI_PORT'])
FASTAPI_LOG_LEVEL = environ['FASTAPI_LOG_LEVEL']


# Create all database tables
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()


@app.get("/", response_class=RedirectResponse)
def read_root():
    return "/docs"


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    resp = forms.TrainingResponse(
        success=False,
        code=400,
        id=-1,
        message="Invalid form."
    )
    print(resp.__dict__)
    return JSONResponse(resp.__dict__)

# 안정화 노드 연결 실패하고 데이터에비스으 만들경우
@app.post("/training")
def submit_training(training_req: forms.TrainingRequest, db: Session = Depends(get_db)):
    resp = forms.TrainingResponse(
        success=True,
        code=201,
        id=training_req.id,
        message="Received a model training request."
    )

    try:
        services.create_merged_info(db, training_req)
        services.send_command_to_nodes(training_req)
    except IntegrityError as e:
        resp.success = False
        resp.code = 500
        resp.message = 'Integrity error: The data integrity of the system has been compromised. Please contact the system administrator for assistance.'

    except Exception as e:
        resp.success = False
        resp.code = 500
        resp.message = 'Internal server error: Please contact the system administrator for assistance.'
        print(e)


    return resp


@app.get("/status/{id}")
def get_training(id: int, db: Session = Depends(get_db)):
    training = crud.get_training_by_id(db, id)
    hyperparam = crud.get_hyperparam_by_id(db, id)
    status = crud.get_status_by_id(db, id)
    if training == None:
        return forms.TrainingResponse(
            success=False,
            code=404,
            id=-1,
            message="Invalid ID.",
        )
    else:
        resp = forms.TrainingStatusResponse(
            success=True,
            code=202,
            id=id,
            message="Valid ID.",
            progress=round((status.epoch / hyperparam.epochs) * 100, 2),
            eta=status.eta,
            epoch=status.epoch,
            total_epoch=hyperparam.epochs,
            accuracy=eval(status.accuracy),
            loss=eval(status.loss),
            current_state=status.current_state
        )
        if len(resp.accuracy) < 1:
            resp.accuracy = eval(status.mae)

    if resp.progress < 100:
        resp.message = "Training in progress."
    else:
        resp.message = "Training has been completed."
    return resp


@app.get("/request/{id}")
def get_request(id: int, db: Session = Depends(get_db)):
    request = crud.get_request_by_id(db, id)
    if request == None:
        return forms.TrainingResponse(
            success=False,
            code=404,
            id=-1,
            message="Invalid ID.",
        )
    else:
        resp = forms.TrainingRequestResponse(
            success=True,
            code=200,
            id=id,
            message="Valid ID.",
            stop_req=request.stop_req
        )
    return resp


@app.put("/status/{id}")
def put_training(id: int, status_req: forms.StatusRequest, db: Session = Depends(get_db)):

    resp = forms.TrainingResponse(
       success=True,
       code=204,
       id=id,
       message="Status recoreded successfully."
    )

    try:
        if not services.is_training_exist(db, id):
            raise NoResultFound()
        services.put_status(db, id, status_req)
    except NoResultFound as e:
        resp.success=False
        resp.code=404
        resp.id=id
        resp.message="Invalid ID."
    except Exception as e:
        resp.success=False
        resp.code=500
        resp.id=id
        resp.message="Modification failed."
        print(e)

    return resp


@app.delete("/training/{id}")
def delete_training(id: int, db: Session = Depends(get_db)):
    resp = forms.TrainingResponse(
       success=True,
       code=205,
       id=id,
       message="Deletion completed."
    )

    try:
        if not services.is_training_exist(db, id):
            raise NoResultFound()

        services.stop_training(db, id)
    except NoResultFound as e:
        resp.success=False
        resp.code=404
        resp.id=id
        resp.message="Invalid id."
    # for debugging
    except Exception as e:
        resp.success=True
        resp.code=200
        resp.id=id
        resp.message="Deletion completed."
        print(e)

    return resp


@app.delete("/")
def del_dbs(db: Session = Depends(get_db)):
    crud.delete_all_trainings(db)
    crud.delete_all_hyperparams(db)
    crud.delete_all_nodes(db)
    crud.delete_all_status(db)
    crud.delete_all_requests(db)

    resp = forms.TrainingResponse(
       success=True,
       code=1,
       id=-1,
       message="Test용: 모든 테이블의 레코드를 삭제했습니다."
    )
    return resp


if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'

    uvicorn.run("main:app",host=FASTAPI_IP,port=FASTAPI_PORT,log_level=FASTAPI_LOG_LEVEL, reload=True)