from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI()

tasks = []
next_id = 0

class CreateTask(BaseModel):
    title: str = Field(min_length = 1, max_length= 100)
   

class UpdateTask(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool

def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="task not found")


@app.post("/tasks", status_code=201)
def create_task(new_task: CreateTask):
    global next_id 
    next_id = next_id + 1
    task = {"id": next_id, "title": new_task.title, "done": False}
    tasks.append(task)
    
    return task


@app.get("/tasks")
def list_tasks(done: bool | None = None, limit: int | None= Query(default=None, ge=1)):
    result = tasks
    if done is not None: 
        result = []
        for task in tasks:
            if task["done"] == done:
                result.append(task)
    if limit is not None:
        result = result[:limit]

    return result


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
   