from fastapi.testclient import TestClient
from main2 import app

client = TestClient(app)

def test_get_missing_task():
    response = client.get("/tasks/99999")
    assert response.status_code == 404

def test_create_task_with_empty_title():
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422

def test_delete_missing_task():
    response = client.delete("/tasks/99999")
    assert response.status_code == 404

def test_update_missing_task():
    response = client.put("/tasks/99999", json={"title": "a", "done": True})
    assert response.status_code == 404

def test_list_task_with_limit():
    response = client.get("/tasks?limit=0")
    assert response.status_code == 422

def test_title_too_long():
    response = client.post("/tasks", json={"title": "a"*101})
    assert response.status_code == 422

def test_list_all_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200

