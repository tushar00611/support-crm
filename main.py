import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes.tickets import router as ticket_router

app = FastAPI(
    title="Support CRM API",
    description="Datastraw CRM System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(
    ticket_router,
    prefix="/api/tickets",
    tags=["tickets"]
)

@app.get("/")
def root():
    return {
        "message": "CRM API is running!",
        "docs": "http://localhost:8000/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0",
                port=8000, reload=True)
