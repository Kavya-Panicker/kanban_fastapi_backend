from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.task_routes import router as TaskRouter
from routes.project_routes import router as ProjectRouter
from database import client  # your MongoDB client
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Add CORS middleware to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods like GET, POST, PUT, DELETE
    allow_headers=["*"],  # Allow all headers
)

# Register routes
app.include_router(TaskRouter)
app.include_router(ProjectRouter)

# Root route to check API
@app.get("/")
async def root():
    logger.info("API health check endpoint called")
    return {"message": "Kanban API is running"}

# Connection check route (pings MongoDB)
@app.get("/check-connection")
async def check_connection():
    try:
        await client.admin.command("ping")  # ping MongoDB
        return {"connected": True}
    except Exception as e:
        return {"connected": False, "error": str(e)}
