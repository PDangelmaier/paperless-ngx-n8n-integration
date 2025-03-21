#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for Paperless-ngx and n8n Integration

This server implements the Model Context Protocol to expose Paperless-ngx documents
and metadata as resources, and provides tools to trigger n8n workflows and process
documents. It serves as a bridge between AI models, Paperless-ngx, and n8n.

Environment variables:
    PAPERLESS_API_URL: URL of the Paperless-ngx API (e.g., http://localhost:8000/api/)
    PAPERLESS_API_TOKEN: API token for Paperless-ngx
    N8N_API_URL: URL of the n8n API (e.g., http://localhost:5678/api/)
    N8N_API_TOKEN: API token for n8n
    MCP_SERVER_HOST: Host for the MCP server (default: localhost)
    MCP_SERVER_PORT: Port for the MCP server (default: 8080)
    LOG_LEVEL: Logging level (default: INFO)
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Optional, Any, Union

import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from mcp_api_adapter import Adapter, ResourceSpec, ToolSpec, Parameter

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# API configuration
PAPERLESS_API_URL = os.getenv("PAPERLESS_API_URL")
PAPERLESS_API_TOKEN = os.getenv("PAPERLESS_API_TOKEN")
N8N_API_URL = os.getenv("N8N_API_URL")
N8N_API_TOKEN = os.getenv("N8N_API_TOKEN")

# MCP server configuration
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))

# Validate required environment variables
if not PAPERLESS_API_URL:
    logger.error("PAPERLESS_API_URL environment variable is not set")
    raise ValueError("PAPERLESS_API_URL environment variable is not set")

if not PAPERLESS_API_TOKEN:
    logger.error("PAPERLESS_API_TOKEN environment variable is not set")
    raise ValueError("PAPERLESS_API_TOKEN environment variable is not set")

if not N8N_API_URL:
    logger.error("N8N_API_URL environment variable is not set")
    raise ValueError("N8N_API_URL environment variable is not set")

if not N8N_API_TOKEN:
    logger.error("N8N_API_TOKEN environment variable is not set")
    raise ValueError("N8N_API_TOKEN environment variable is not set")

# Create FastAPI app for the MCP server
app = FastAPI(title="Paperless-ngx and n8n MCP Server")

# Create MCP adapter
adapter = Adapter(app)

# Helper Functions for API Interactions

def get_paperless_headers() -> Dict[str, str]:
    """Generate headers for Paperless-ngx API requests."""
    return {
        "Authorization": f"Token {PAPERLESS_API_TOKEN}",
        "Content-Type": "application/json",
    }

def get_n8n_headers() -> Dict[str, str]:
    """Generate headers for n8n API requests."""
    return {
        "X-N8N-API-KEY": N8N_API_TOKEN,
        "Content-Type": "application/json",
    }

async def fetch_paperless_documents(
    query: Optional[str] = None, 
    tag_id: Optional[int] = None,
    correspondent_id: Optional[int] = None,
    document_type_id: Optional[int] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Fetch documents from Paperless-ngx API with optional filtering.
    
    Args:
        query: Search query string
        tag_id: Filter by tag ID
        correspondent_id: Filter by correspondent ID
        document_type_id: Filter by document type ID
        created_after: Filter by creation date (ISO format)
        created_before: Filter by creation date (ISO format)
        limit: Maximum number of documents to return
        
    Returns:
        List of document objects
    """
    url = f"{PAPERLESS_API_URL.rstrip('/')}/documents/"
    params = {"page_size": limit}
    
    # Add optional filters
    if query:
        params["query"] = query
    if tag_id:
        params["tags__id"] = tag_id
    if correspondent_id:
        params["correspondent__id"] = correspondent_id
    if document_type_id:
        params["document_type__id"] = document_type_id
    if created_after:
        params["created__gte"] = created_after
    if created_before:
        params["created__lte"] = created_before
    
    try:
        response = requests.get(url, headers=get_paperless_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except RequestException as e:
        logger.error(f"Error fetching documents from Paperless-ngx: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {str(e)}")

async def fetch_paperless_document(document_id: int) -> Dict[str, Any]:
    """
    Fetch a specific document from Paperless-ngx API.
    
    Args:
        document_id: The ID of the document to fetch
        
    Returns:
        Document object
    """
    url = f"{PAPERLESS_API_URL.rstrip('/')}/documents/{document_id}/"
    
    try:
        response = requests.get(url, headers=get_paperless_headers())
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(f"Error fetching document {document_id} from Paperless-ngx: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching document: {str(e)}")

async def fetch_paperless_tags() -> List[Dict[str, Any]]:
    """
    Fetch all tags from Paperless-ngx API.
    
    Returns:
        List of tag objects
    """
    url = f"{PAPERLESS_API_URL.rstrip('/')}/tags/"
    
    try:
        response = requests.get(url, headers=get_paperless_headers())
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except RequestException as e:
        logger.error(f"Error fetching tags from Paperless-ngx: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching tags: {str(e)}")

async def fetch_paperless_correspondents() -> List[Dict[str, Any]]:
    """
    Fetch all correspondents from Paperless-ngx API.
    
    Returns:
        List of correspondent objects
    """
    url = f"{PAPERLESS_API_URL.rstrip('/')}/correspondents/"
    
    try:
        response = requests.get(url, headers=get_paperless_headers())
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except RequestException as e:
        logger.error(f"Error fetching correspondents from Paperless-ngx: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching correspondents: {str(e)}")

async def fetch_paperless_document_types() -> List[Dict[str, Any]]:
    """
    Fetch all document types from Paperless-ngx API.
    
    Returns:
        List of document type objects
    """
    url = f"{PAPERLESS_API_URL.rstrip('/')}/document_types/"
    
    try:
        response = requests.get(url, headers=get_paperless_headers())
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except RequestException as e:
        logger.error(f"Error fetching document types from Paperless-ngx: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching document types: {str(e)}")

async def trigger_n8n_workflow(
    workflow_id: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Trigger an n8n workflow with the given data.
    
    Args:
        workflow_id: The ID of the workflow to trigger
        data: The data to pass to the workflow
        
    Returns:
        Workflow execution result
    """
    url = f"{N8N_API_URL.rstrip('/')}/workflows/{workflow_id}/trigger"
    
    try:
        response = requests.post(
            url, 
            headers=get_n8n_headers(), 
            json=data
        )
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(f"Error triggering n8n workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error triggering workflow: {str(e)}")

async def fetch_n8n_workflows() -> List[Dict[str, Any]]:
    """
    Fetch all workflows from n8n API.
    
    Returns:
        List of workflow objects
    """
    url = f"{N8N_API_URL.rstrip('/')}/workflows"
    
    try:
        response = requests.get(url, headers=get_n8n_headers())
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(f"Error fetching workflows from n8n: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching workflows: {str(e)}")

async def update_paperless_document(
    document_id: int,
    update_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update a document in Paperless-ngx.
    
    Args:
        document_id: The ID of the document to update
        update_data: The data to update on the document
        
    Returns:
        Updated document object
    """
    url = f"{PAPERLESS_API_URL.rstrip('/')}/documents/{document_id}/"
    
    try:
        # First get the current document to avoid partial updates
        current_doc = await fetch_paperless_document(document_id)
        
        # Merge the update data with the current document data
        updated_doc = {**current_doc, **update_data}
        
        # Send the update request
        response = requests.put(
            url, 
            headers=get_paperless_headers(), 
            json=updated_doc
        )
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(f"Error updating document {document_id} in Paperless-ngx: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating document: {str(e)}")

# Define MCP Resources

@adapter.resource(
    name="documents",
    description="List and search for documents in Paperless-ngx",
)
async def get_documents(
    query: Optional[str] = None,
    tag_id: Optional[int] = None,
    correspondent_id: Optional[int] = None, 
    document_type_id: Optional[int] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """Resource to get documents with optional filtering."""
    try:
        documents = await fetch_paperless_documents(
            query=query,
            tag_id=tag_id,
            correspondent_id=correspondent_id,
            document_type_id=document_type_id,
            created_after=created_after,
            created_before=created_before,
            limit=limit
        )
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Error in get_documents resource: {e}")
        return {"error": str(e), "documents": []}

@adapter.resource(
    name="document",
    description="Get a specific document by ID from Paperless-ngx",
)
async def get_document(document_id: int) -> Dict[str, Any]:
    """Resource to get a specific document by ID."""
    try:
        document = await fetch_paperless_document(document_id)
        return {"document": document}
    except Exception as e:
        logger.error(f"Error in get_document resource: {e}")
        return {"error": str(e), "document": None}

@adapter.resource(
    name="tags",
    description="Get all tags from Paperless-ngx",
)
async def get_tags() -> Dict[str, Any]:
    """Resource to get all tags."""
    try:
        tags = await fetch_paperless_tags()
        return {"tags": tags}
    except Exception as e:
        logger.error(f"Error in get_tags resource: {e}")
        return {"error": str(e), "tags": []}

@adapter.resource(
    name="correspondents",
    description="Get all correspondents from Paperless-ngx",
)
async def get_correspondents() -> Dict[str, Any]:
    """Resource to get all correspondents."""
    try:
        correspondents = await fetch_paperless_correspondents()
        return {"correspondents": correspondents}
    except Exception as e:
        logger.error(f"Error in get_correspondents resource: {e}")
        return {"error": str(e), "correspondents": []}

@adapter.resource(
    name="document_types",
    description="Get all document types from Paperless-ngx",
)
async def get_document_types() -> Dict[str, Any]:
    """Resource to get all document types."""
    try:
        document_types = await fetch_paperless_document_types()
        return {"document_types": document_types}
    except Exception as e:
        logger.error(f"Error in get_document_types resource: {e}")
        return {"error": str(e), "document_types": []}

@adapter.resource(
    name="workflows",
    description="Get all workflows from n8n",
)
async def get_workflows() -> Dict[str, Any]:
    """Resource to get all n8n workflows."""
    try:
        workflows = await fetch_n8n_workflows()
        return {"workflows": workflows}
    except Exception as e:
        logger.error(f"Error in get_workflows resource: {e}")
        return {"error": str(e), "workflows": []}

# Define MCP Tools

@adapter.tool(
    name="trigger_workflow",
    description="Trigger an n8n workflow with document data",
    parameters=[
        Parameter(name="workflow_id", description="ID of the workflow to trigger"),
        Parameter(name="document_id", description="ID of the document to process"),
        Parameter(name="additional_data", description="Additional data to pass to the workflow (optional)", required=False),
    ]
)
async def tool_trigger_workflow(
    workflow_id: str,
    document_id: int,
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Tool to trigger an n8n workflow with document data.
    
    Args:
        workflow_id: ID of the workflow to trigger
        document_id: ID of the document to process
        additional_data: Additional data to pass to the workflow (optional)
        
    Returns:
        Result of the workflow execution
    """
    try:
        # Fetch document data
        document = await fetch_paperless_document(document_id)
        
        # Prepare payload for the workflow
        payload = {
            "document": document,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        
        # Add any additional data
        if additional_data:
            payload["additional_data"] = additional_data
            
        # Trigger the workflow
        result = await trigger_n8n_workflow(workflow_id, payload)
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "document_id": document_id,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error in tool_trigger_workflow: {e}")
        return {
            "success": False,
            "error": str(e),
            "workflow_id": workflow_id,
            "document_id": document_id
        }

@adapter.tool(
    name="update_document_tags",
    description="Update tags for a document in Paperless-ngx",
    parameters=[
        Parameter(name="document_id", description="ID of the document to update"),
        Parameter(name="add_tags", description="List of tag IDs to add to the document (optional)", required=False),
        Parameter(name="remove_tags", description="List of tag IDs to remove from the document (optional)", required=False),
    ]
)
async def tool_update_document_tags(
    document_id: int,
    add_tags: Optional[List[int]] = None,
    remove_tags: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Tool to update the tags of a document in Paperless-ngx.
    
    Args:
        document_id: ID of the document to update
        add_tags: List of tag IDs to add to the document
        remove_tags: List of tag IDs to remove from the document
        
    Returns:
        Result of the update operation
    """
    try:
        # Get current document data
        document = await fetch_paperless_document(document_id)
        current_tags = document.get("tags", [])
        
        # Add new tags
        if add_tags:
            for tag_id in add_tags:
                if tag_id not in current_tags:
                    current_tags.append(tag_id)
        
        # Remove tags
        if remove_tags:
            current_tags = [tag_id for tag_id in current_tags if tag_id not in remove_tags]
        
        # Update the document
        update_data = {"tags": current_tags}
        updated_doc = await update_paperless_document(document_id, update_data)
        
        return {
            "success": True,
            "document_id": document_id,
            "updated_tags": updated_doc.get("tags", []),
            "message": "Tags updated successfully"
        }
    except Exception as e:
        logger.error(f"Error in tool_update_document_tags: {e}")
        return {
            "success": False,
            "error": str(e),
            "document_id": document_id
        }

@adapter.tool(
    name="analyze_document",
    description="Analyze a document and suggest tags and metadata",
    parameters=[
        Parameter(name="document_id", description="ID of the document to analyze"),
        Parameter(name="update_automatically", description="Whether to apply suggested tags automatically", required=False),
    ]
)
async def tool_analyze_document(
    document_id: int,
    update_automatically: bool = False
) -> Dict[str, Any]:
    """
    Tool to analyze a document and suggest tags and metadata.
    This is a simplified analysis that could be expanded with more advanced NLP.
    
    Args:
        document_id: ID of the document to analyze
        update_automatically: Whether to apply suggested tags automatically
        
    Returns:
        Analysis results and suggested metadata
    """
    try:
        # Fetch document data
        document = await fetch_paperless_document(document_id)
        document_title = document.get("title", "")
        document_content = document.get("content", "")
        
        # Fetch all available tags for matching
        all_tags = await fetch_paperless_tags()
        tag_mapping = {tag["name"].lower(): tag["id"] for tag in all_tags}
        
        # Simple keyword matching for tag suggestions
        # This is a placeholder for more sophisticated analysis
        suggested_tag_ids = []
        
        # Check document title and content for keyword matches with existing tags
        for tag_name, tag_id in tag_mapping.items():
            if tag_name in document_title.lower() or tag_name in document_content.lower():
                suggested_tag_ids.append(tag_id)
        
        # If update_automatically is True, update the document with suggested tags
        if update_automatically and suggested_tag_ids:
            current_tags = document.get("tags", [])
            new_tags = list(set(current_tags + suggested_tag_ids))
            update_data = {"tags": new_tags}
            await update_paperless_document(document_id, update_data)
            
        # Get tag names for the response
        suggested_tag_names = [
            tag["name"] for tag in all_tags 
            if tag["id"] in suggested_tag_ids
        ]
        
        return {
            "success": True,
            "document_id": document_id,
            "document_title": document_title,
            "suggested_tags": suggested_tag_names,
            "suggested_tag_ids": suggested_tag_ids,
            "tags_updated": update_automatically,
            "message": "Document analyzed successfully"
        }
    except Exception as e:
        logger.error(f"Error in tool_analyze_document: {e}")
        return {
            "success": False,
            "error": str(e),
            "document_id": document_id
        }

@adapter.tool(
    name="search_similar_documents",
    description="Find documents similar to a specific document",
    parameters=[
        Parameter(name="document_id", description="ID of the reference document"),
        Parameter(name="max_results", description="Maximum number of similar documents to return", required=False),
    ]
)
async def tool_search_similar_documents(
    document_id: int,
    max_results: int = 5
) -> Dict[str, Any]:
    """
    Tool to find documents similar to a reference document.
    
    Args:
        document_id: ID of the reference document
        max_results: Maximum number of similar documents to return
        
    Returns:
        List of similar documents
    """
    try:
        # Fetch the reference document
        reference_doc = await fetch_paperless_document(document_id)
        
        # Extract key information
        correspondent_id = reference_doc.get("correspondent")
        document_type = reference_doc.get("document_type")
        tags = reference_doc.get("tags", [])
        
        # Fetch similar documents based on shared metadata
        similar_docs = await fetch_paperless_documents(
            correspondent_id=correspondent_id,
            document_type_id=document_type,
            limit=max_results + 1  # +1 to account for the reference document
        )
        
        # Remove the reference document from results and limit results
        similar_docs = [doc for doc in similar_docs if doc["id"] != document_id][:max_results]
        
        return {
            "success": True,
            "reference_document_id": document_id,
            "similar_documents": similar_docs,
            "similarity_criteria": {
                "correspondent_id": correspondent_id,
                "document_type": document_type,
                "tags": tags
            }
        }
    except Exception as e:
        logger.error(f"Error in tool_search_similar_documents: {e}")
        return {
            "success": False,
            "error": str(e),
            "reference_document_id": document_id
        }

# Main function to run the server
def main():
    """Main function to run the MCP server."""
    try:
        import uvicorn
        
        # Log server configuration
        logger.info(f"Starting Paperless-ngx and n8n MCP Server on {MCP_SERVER_HOST}:{MCP_SERVER_PORT}")
        logger.info(f"Paperless-ngx API URL: {PAPERLESS_API_URL}")
        logger.info(f"n8n API URL: {N8N_API_URL}")
        
        # Register the server with MCP
        adapter.register_mcp_server(
            name="paperless-n8n-mcp",
            description="Model Context Protocol server for Paperless-ngx and n8n integration"
        )
        
        # Run the server
        uvicorn.run(
            app,
            host=MCP_SERVER_HOST,
            port=MCP_SERVER_PORT
        )
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        raise

# Server startup with error handling
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
