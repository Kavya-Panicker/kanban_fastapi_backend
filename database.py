from motor.motor_asyncio import AsyncIOMotorClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_DETAILS = "mongodb://localhost:27017"

# MongoDB connection
try:
    client = AsyncIOMotorClient(MONGO_DETAILS)
    database = client.kanaban_board  # make sure this matches your Compass DB
    task_collection = database.get_collection("task")
    project_collection = database.get_collection("projects")
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise
