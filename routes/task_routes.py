from fastapi import APIRouter, HTTPException
from models import Task
from database import task_collection
from bson import ObjectId
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# ✅ Serializer to convert MongoDB document to JSON-friendly format
def task_serializer(task) -> dict:
    return {
        "id": str(task["_id"]),  # Convert ObjectId to string
        "title": task.get("title"),
        "description": task.get("description"),
        "status": task.get("status"),
        "start_date": str(task.get("start_date")),  # Ensure dates are strings
        "end_date": str(task.get("end_date")),
        "assigned_to": task.get("assigned_to")
    }

def task_helper(task) -> dict:
    return {
        "_id": str(task["_id"]),
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "start_date": str(task["start_date"]),
        "end_date": str(task["end_date"]),
        "assigned_to": task["assigned_to"]
    }

# ✅ GET /tasks - Fetch all tasks
@router.get("/tasks")
async def get_tasks():
    try:
        tasks = []
        async for task in task_collection.find():
            tasks.append(task_helper(task))
        logger.info(f"Retrieved {len(tasks)} tasks")
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ POST /tasks - Create a new task
@router.post("/tasks")
async def create_task(task: Task):
    try:
        logger.info(f"Received task data: {task.dict()}")
        task_dict = task.dict()
        # Convert dates to ISO format string
        task_dict["start_date"] = task_dict["start_date"].isoformat()
        task_dict["end_date"] = task_dict["end_date"].isoformat()
        
        result = await task_collection.insert_one(task_dict)
        logger.info(f"Task created with ID: {result.inserted_id}")
        
        # Fetch the created task
        created_task = await task_collection.find_one({"_id": result.inserted_id})
        if created_task:
            logger.info(f"Returning created task: {task_helper(created_task)}")
            return task_helper(created_task)
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ GET /tasks/{id} - Fetch a single task by ID
@router.get("/tasks/{id}")
async def get_task(id: str):
    try:
        logger.info(f"Fetching task with ID: {id}")
        task = await task_collection.find_one({"_id": ObjectId(id)})
        if task:
            logger.info(f"Found task: {task_helper(task)}")
            return task_helper(task)
        logger.warning(f"Task not found with ID: {id}")
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        logger.error(f"Error fetching task {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ PUT /tasks/{id} - Update task by ID
@router.put("/tasks/{id}")
async def update_task(id: str, task: Task):
    try:
        logger.info(f"Updating task {id} with data: {task.dict()}")
        task_dict = task.dict()
        task_dict["start_date"] = task_dict["start_date"].isoformat()
        task_dict["end_date"] = task_dict["end_date"].isoformat()
        
        update_result = await task_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": task_dict}
        )
        
        if update_result.modified_count == 1:
            updated_task = await task_collection.find_one({"_id": ObjectId(id)})
            logger.info(f"Successfully updated task: {task_helper(updated_task)}")
            return task_helper(updated_task)
        logger.warning(f"Task not found with ID: {id}")
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        logger.error(f"Error updating task {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ DELETE /tasks/{id} - Delete task by ID
@router.delete("/tasks/{id}")
async def delete_task(id: str):
    try:
        logger.info(f"Attempting to delete task with ID: {id}")
        delete_result = await task_collection.delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 1:
            logger.info(f"Successfully deleted task with ID: {id}")
            return {"message": "Task deleted successfully"}
        logger.warning(f"Task not found with ID: {id}")
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        logger.error(f"Error deleting task {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
