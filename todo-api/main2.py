from fastapi import FastAPI, HTTPException, Query
# from pydantic import BaseModel, Field
from sqlmodel import Field, SQLModel, create_engine, Session, select

app = FastAPI()

tasks = []
next_id = 0

class CreateTask(SQLModel):
    title: str = Field(min_length = 1, max_length= 100)
   

class UpdateTask(SQLModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = False

engine = create_engine("sqlite:///tasks.db")
SQLModel.metadata.create_all(engine)

def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="task not found")


@app.post("/tasks", status_code=201)
def create_task(new_task: CreateTask):
    with Session(engine) as session:
        task = Task(title=new_task.title)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

@app.get("/tasks")
def list_tasks(done: bool | None = None, limit: int | None= Query(default=None, ge=1)):
    with Session(engine) as session:
        return session.exec(select(Task)).all()
    # result = tasks
    # if done is not None: 
    #     result = []
    #     for task in tasks:
    #         if task["done"] == done:
    #             result.append(task)
    # if limit is not None:
    #     result = result[:limit]

    # return result


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = find_task(task_id)
    return task

    

@app.put("/tasks/{task_id}")
def update_task(task_id: int, update_task: UpdateTask):

    task = find_task(task_id)   
    task['title'] = update_task.title
    task['done'] = update_task.done
    return task
   
    

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    
    task = find_task(task_id)
    tasks.remove(task)
    return {"message": "Task deleted."}
   