# To-Do API — Learning Notes

A beginner backend project built with FastAPI, done stage by stage before starting the personal website.

## Setting up on a new computer

```powershell
git clone https://github.com/eboves/personal_site.git
cd personal_site
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install sqlmodel          # needed from Stage 5 on (add it to requirements.txt)
cd todo-api
fastapi dev main2.py
```

Then open http://127.0.0.1:8000/docs

- Never copy a `.venv` folder between projects or computers. Always create a new one; it stores the full path to Python and breaks if moved.
- If `fastapi` isn't recognized, the venv isn't active. Run `.venv\Scripts\activate` from the `personal_site` folder.
- If a file "does not exist", check which folder the terminal is in (shown in the `PS C:\...>` prompt).

## Progress

| Stage | Topic | Status |
|---|---|---|
| 1 | CRUD with an in-memory list | ✅ Done |
| 2 | Pydantic models and validation | ✅ Done |
| 3 | Status codes and `HTTPException` | ✅ Done, including the `find_task()` helper |
| 4 | Query parameters (`done` filter, `limit`) | ✅ Done |
| 5 | SQLite database with SQLModel | ⏳ **Next: start with 5a** |
| 6 | Tests with pytest | Not started |
| Bonus | User accounts and login | Not started |

Optional extras still open from Stage 4:
- Validate `limit` with `Query(default=None, ge=1)` so `limit=-1` gets a 422.
- Add a `search: str | None = None` filter (hint: `"milk" in "Buy milk"` is `True`).

## What I've learned so far

**Routes.** The decorator sets the method and path: `@app.get`, `@app.post`, `@app.put`, `@app.delete`.

**Where FastAPI gets data from:**
- A name in `{curly braces}` in the path is a **path parameter**: `/tasks/{task_id}`.
- A Pydantic model parameter is the **request body** (JSON).
- Any other simple type (`str`, `int`, `bool`) is a **query parameter**: `/tasks?done=true`. Give it `= None` to make it optional.

**Models are forms with blanks.** A model lists the fields the client must send and the rules for each. FastAPI checks the input before the function runs and returns `422` if it's wrong. Use separate models for different actions: `CreateTask` has only `title`, while `UpdateTask` has `title` and `done`.

**Status codes:**
- Success code: set in the decorator, only when it isn't 200, e.g. `@app.post("/tasks", status_code=201)`.
- Errors: `raise HTTPException(status_code=404, detail="task not found")`. Use `raise`, not `return`; it stops the function immediately.

**Optional filters:** start `result` with everything, then narrow it down with each filter that `is not None`. Use `is not None`, not `if done:`, because `False` is a real value.

**Refactoring:** when the same lines repeat, move them into a function, give it parameters for what changes, and call it from each place. Each route then becomes "find, then act":
```python
task = find_task(task_id)   # search (shared, raises 404 if missing)
tasks.remove(task)          # action (different per route)
```

**async vs def:** use `async def` only when the function `await`s an async library. Never call blocking code (like `time.sleep` or `requests`) inside `async def`, because it freezes the whole server. If unsure, use plain `def`.

**Git:** create `.gitignore` *before* the first `git add .`. To untrack files that were added by mistake:
```powershell
git rm -r --cached .     # add -f if git complains; --cached keeps the files on disk
git add .
git status               # check before committing
```

## Stage 5: Database (SQLite + SQLModel)

**The stack:**
```
FastAPI code → SQLModel → SQLAlchemy → SQLite (now) / PostgreSQL (later)
```
- **SQLite:** the database is a single file (`tasks.db`). No server needed. Good for learning.
- **PostgreSQL:** a database server. Used for real production apps.
- **SQLAlchemy:** translates Python into SQL and works with both databases.
- **SQLModel:** built on SQLAlchemy and Pydantic; one class can be both a model and a table.

**New concepts:**

| Concept | What it is |
|---|---|
| Table model | A class with `table=True` that describes a table |
| Engine | The connection to the database file |
| Session | One conversation with the database (open, change, save, close) |
| Commit | Actually saving the changes |

**Before starting:** add `sqlmodel` to `requirements.txt` and `*.db` to `.gitignore`.

### 5a: Setup, create, and list

Reference (books example, map it to tasks):

```python
from sqlmodel import SQLModel, Field, Session, create_engine, select

class Book(SQLModel, table=True):          # table=True makes it a real table
    id: int | None = Field(default=None, primary_key=True)   # the database assigns ids
    title: str
    read: bool = False

class CreateBook(SQLModel):                # an input form, not a table
    title: str = Field(min_length=1, max_length=100)

engine = create_engine("sqlite:///books.db")
SQLModel.metadata.create_all(engine)       # creates the table if it doesn't exist


@app.post("/books", status_code=201)
def create_book(new_book: CreateBook):
    with Session(engine) as session:
        book = Book(title=new_book.title)
        session.add(book)
        session.commit()                   # save; the database assigns the id
        session.refresh(book)              # reload so book.id is filled in
        return book


@app.get("/books")
def list_books():
    with Session(engine) as session:
        return session.exec(select(Book)).all()
```

Things to remember:
- `next_id` and `global` go away; the database creates the ids.
- Rows are objects now: `task.title`, not `task["title"]`.
- Import `Field` from `sqlmodel`, not `pydantic`.
- Only the `Task` table gets `table=True`. `CreateTask` and `UpdateTask` don't.

Tasks:
1. Create a `Task` table model (`id`, `title`, `done`).
2. Make `CreateTask` and `UpdateTask` inherit from `SQLModel`.
3. Add the engine and `create_all`.
4. Rewrite **create** and **list** (leave the filters out for now).
5. Get, update, and delete will break for now; that's expected.

Test: create tasks, save the file to restart the server, and run `GET /tasks` again. The tasks should still be there.

### 5b: Get, update, and delete

- Find one row by id: `session.get(Task, task_id)` returns the task, or `None` if it doesn't exist. Use it in `find_task` and raise a 404 when it's `None`.
- Update: change the fields on the object, then `session.add(task)`, `session.commit()`, `session.refresh(task)`.
- Delete: `session.delete(task)`, then `session.commit()`.
- Think about how `find_task` gets a session: the route opens one and passes it in, e.g. `find_task(session, task_id)`.

### 5c: Filters in the database

Instead of looping in Python, ask the database to filter:
```python
query = select(Task)
if done is not None:
    query = query.where(Task.done == done)
if limit is not None:
    query = query.limit(limit)
tasks = session.exec(query).all()
```
It's the same "start with everything, then narrow down" idea as in Stage 4.

## After this project

1. Stage 6: tests with `pytest` and FastAPI's `TestClient`.
2. Bonus: user accounts and login.
3. Personal website: Jinja2 templates (`templates/` folder) and static files (`static/` for CSS), then a shared base template, styling, dynamic content, and deployment (Render, Railway, or Fly.io), switching to PostgreSQL there.
