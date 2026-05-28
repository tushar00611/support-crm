import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import init_db
from routes.tickets import router as ticket_router

app = FastAPI(title="Support CRM API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

init_db()

app.include_router(ticket_router, prefix="/api/tickets", tags=["tickets"])

@app.get("/")
def home():
    return FileResponse("index.html")

@app.get("/create")
def create():
    return FileResponse("create.html")

@app.get("/detail/{ticket_id}")
def detail(ticket_id: str):
    return FileResponse("detail.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
