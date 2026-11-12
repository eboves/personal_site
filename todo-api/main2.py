from fastapi import FastAPI, HTTPException, Query, Depends
from sqlmodel import Field, SQLModel, create_engine, Session, select

app = FastAPI()

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

def get_session():
    with Session(engine) as session:
        yield session


def find_task(session, task_id: int):
    get_task = session.get(Task, task_id)
    if get_task is None:
        raise HTTPException(status_code=404, detail="task not found")
    
    return get_task


@app.post("/tasks", status_code=201)
def create_task(new_task: CreateTask, session: Session = Depends(get_session)):
    task = Task(title=new_task.title)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks")
def list_tasks(done: bool | None = None, limit: int | None= Query(default=None, ge=1), session: Session = Depends(get_session)):
    query = select(Task)
    if done is not None:
        query = query.where(Task.done == done)
    if limit is not None:
        query = query.limit(limit)
    tasks = session.exec(query).all()
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = find_task(session, task_id)
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, update_task: UpdateTask, session: Session = Depends(get_session)):
    task = find_task(session, task_id)
    task.title = update_task.title
    task.done = update_task.done
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = find_task(session, task_id)
    session.delete(task)
    session.commit()
    return task

   