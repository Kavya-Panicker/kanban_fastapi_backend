from fastapi import APIRouter, HTTPException
from models import Project
from database import project_collection
from bson import ObjectId
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Helper function to serialize project for JSON response
def project_helper(project) -> dict:
    return {
        "_id": str(project["_id"]),
        "name": project["name"],
        "description": project["description"],
        "status": project["status"],
        "progress": project["progress"],
        "team": project["team"],
        "dueDate": str(project["dueDate"]),
        "priority": project["priority"]
    }

# POST /projects - Create a new project
@router.post("/projects")
async def create_project(project: Project):
    try:
        logger.info(f"Received project data: {project.dict()}")
        project_dict = project.dict()
        # Convert date to ISO format string
        project_dict["dueDate"] = project_dict["dueDate"].isoformat()
        
        result = await project_collection.insert_one(project_dict)
        logger.info(f"Project created with ID: {result.inserted_id}")
        
        # Fetch the created project
        created_project = await project_collection.find_one({"_id": result.inserted_id})
        logger.info(f"Returning created project: {project_helper(created_project)}")
        return project_helper(created_project)
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# GET /projects - Fetch all projects
@router.get("/projects")
async def get_projects():
    try:
        projects = []
        async for project in project_collection.find():
            projects.append(project_helper(project))
        logger.info(f"Retrieved {len(projects)} projects")
        return projects
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# GET /projects/{id} - Fetch a single project by ID
@router.get("/projects/{id}")
async def get_project(id: str):
    try:
        logger.info(f"Fetching project with ID: {id}")
        project = await project_collection.find_one({"_id": ObjectId(id)})
        if project:
            logger.info(f"Found project: {project_helper(project)}")
            return project_helper(project)
        logger.warning(f"Project not found with ID: {id}")
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logger.error(f"Error fetching project {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# PUT /projects/{id} - Update a project
@router.put("/projects/{id}")
async def update_project(id: str, project: Project):
    try:
        logger.info(f"Updating project {id} with data: {project.dict()}")
        project_dict = project.dict()
        project_dict["dueDate"] = project_dict["dueDate"].isoformat()
        
        update_result = await project_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": project_dict}
        )
        
        if update_result.modified_count == 1:
            updated_project = await project_collection.find_one({"_id": ObjectId(id)})
            logger.info(f"Successfully updated project: {project_helper(updated_project)}")
            return project_helper(updated_project)
        logger.warning(f"Project not found with ID: {id}")
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logger.error(f"Error updating project {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# DELETE /projects/{id} - Delete a project
@router.delete("/projects/{id}")
async def delete_project(id: str):
    try:
        logger.info(f"Attempting to delete project with ID: {id}")
        delete_result = await project_collection.delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 1:
            logger.info(f"Successfully deleted project with ID: {id}")
            return {"message": "Project deleted successfully"}
        logger.warning(f"Project not found with ID: {id}")
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logger.error(f"Error deleting project {id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 