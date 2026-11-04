from fastapi import FastAPI

#this create the app server using fastapi
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "hello EB!"}

@app.get("/about")
def about():
    return {"message": "This is the ABOUT me page!"}