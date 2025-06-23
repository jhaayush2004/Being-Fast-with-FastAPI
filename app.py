from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from time import time
from fastapi.middleware.cors import CORSMiddleware

# we use response model to strip out data we dont wanna diplay as output through our API
class BaseTodo(BaseModel):
    task : str

class Todo(BaseTodo):
    id: Optional[int] = None
    
    is_completed: bool = False

class ReturnTodo(BaseTodo):
    pass


app = FastAPI()

app.middleware(
    CORSMiddleware,
    allow_origin = ["*"],  #allow request fro every website, to make api to be accessedby only specific website like xyz.com, allow_origin = ["xyz.com"] to make it more secure
    allow_credentials = True, #to allow requests with credentials
    allow_methods = ["*"], # * is called y code operator
    allow_headers = ["*"], #to allow all headers in the request headers to posted to our API
)
todos = []


#middleware components are executed for each requests before the request reaches the load function and also before the response is returned
# most importnt. middleware is CORS middleware and it allows us to define from which origin we allow requests to our API and if we want to allow headers and special methods in our API, we can just import it from FastAPI.middleware.cors import CORSMiddleware
@app.middleware('http')
async def log_middleware(request, call_next):
    start_time = time()
    response = await call_next(request)
    end_time = time()
    process_time = end_time - start_time
    print(f"Request {request.url} processed in {process_time} in sec.")
    return response
'''

(venv) D:\Documents\MLOps\Being-Fast-with-FastAPI>uvicorn app:app --host 127.0.0.1 --port 5566
INFO:     Started server process [10848]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:5566 (Press CTRL+C to quit)
Request http://127.0.0.1:5566/docs processed in 0.0005295276641845703 in sec.
INFO:     127.0.0.1:62555 - "GET /docs HTTP/1.1" 200 OK
Request http://127.0.0.1:5566/openapi.json processed in 0.012750864028930664 in sec.These all are the reponse returned.
INFO:     127.0.0.1:62555 - "GET /openapi.json HTTP/1.1" 200 OK
Request http://127.0.0.1:5566/todos processed in 0.003963470458984375 in sec.
INFO:     127.0.0.1:62556 - "POST /todos HTTP/1.1" 200 OK
Request http://127.0.0.1:5566/todos processed in 0.0016040802001953125 in sec.
INFO:     127.0.0.1:62556 - "POST /todos HTTP/1.1" 200 OK
Request http://127.0.0.1:5566/todos processed in 0.001516580581665039 in sec.
INFO:     127.0.0.1:62556 - "POST /todos HTTP/1.1" 200 OK
Request http://127.0.0.1:5566/todos processed in 0.0014662742614746094 in sec.
INFO:     127.0.0.1:62556 - "POST /todos HTTP/1.1" 200 OK
Request http://127.0.0.1:5566/todos?completed=true processed in 0.0009646415710449219 in sec.
INFO:     127.0.0.1:62562 - "GET /todos?completed=true HTTP/1.1" 200 OK
Request http://127.0.0.1:5566/todos?completed=true processed in 0.0009121894836425781 in sec.
INFO:     127.0.0.1:62562 - "GET /todos?completed=true HTTP/1.1" 200 OK
Each and every request logged with processing time
'''
@app.post("/hello")
async def hello():
    return "hello"

async def send_email(todo:Todo):
    print(f"Email notification for todo {todo.id} sent!")

@app.post("/todos", response_model= ReturnTodo)
async def todo(todo: Todo, background_task:BackgroundTasks):
    todo.id = len(todos) + 1
    todos.append(todo)
    background_task.add_task(send_email, todo) # now send_email func. will be processed separateely from returning todo and thus even if its time taking, then also user will not get struck as other function will be executed separately from this and we use it only if the function(send email here) runs independent from the ouptut we wanna return like todo here.
    return todo
#query parameters
#http://127.0.0.1:5566/todos?completed=true, here completed is optional to give
@app.get("/todos")
async def read_todos(completed : Optional[bool] = None):
    if completed is None:
        return todos
    else:
        return[todo for todo in todos if todo.is_completed==completed]

# path parameters (here id) used to get a single todo on the basis of id
@app.get("/todos/{id}")
async def read_todo(id : int):
    for todo in todos:
        if todo.id == id:
            return todo
    raise HTTPException(status_code = 404, detail = "Item Not Found, Contact Supportat @AyushFoundation.org")

#To Update, we use Put
@app.put("/todos/{id}")
async def update_todos(id : int, new_todo : Todo):
    for index, todo in enumerate(todos):
        if todo.id == id :
            todos[index] = new_todo
            todos[index].id = id
            return
    HTTPException(status_code = 404, detail = "Item Not Found, Contact Supportat @AyushFoundation.org")

@app.delete("/todos/{id}")
async def delete_todo(id : int):
    for index, todo in enumerate(todos):
        if todo.id == id:
            del todos[index]
            return
    raise HTTPException(status = 404,  detail = "Item Not Found, Contact Supportat @AyushFoundation.org")