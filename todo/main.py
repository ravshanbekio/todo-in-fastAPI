from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, schemas
from .models import Todo

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.get("/tasks/", status_code=status.HTTP_200_OK)
async def task(db:Session=Depends(get_db)):
    tasks = db.query(Todo).all()
    return tasks

@app.get("/tasks/{id}/",status_code=status.HTTP_200_OK, response_model=schemas.ShowTodo)
async def task_id(id, db:Session=Depends(get_db)):
    task_with_id = db.query(models.Todo).filter(models.Todo.id == id).first()
    if not task_with_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {id} not found")
    return task_with_id

@app.post("/tasks/new/", status_code=status.HTTP_201_CREATED)
async def new_task(request: schemas.Todo,db:Session=Depends(get_db)):
    task = models.Todo(title=request.title, text=request.text, date=request.date, status=request.status)
    db.add(task)
    db.commit()
    db.refresh(task)
    return f'Successfully added! {task.title}'

@app.put("/tasks/put/", status_code=status.HTTP_202_ACCEPTED)
async def update_task(id, request: schemas.Todo ,db:Session=Depends(get_db)):
    task = db.query(models.Todo).filter(models.Todo.id == id)
    task.update(request)
    db.commit()
    return f'Successfully updated {task.title}'

@app.delete("/tasks/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id, db:Session=Depends(get_db)):
    db.query(models.Todo).filter(models.Todo.id == id).delete(synchronize_session=False)
    db.commit()
    return 'Task successfully deleted'