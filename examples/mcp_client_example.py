#!/usr/bin/env python3
"""
MCP Client Example for Paperless-ngx and n8n Integration

This script demonstrates how to use the Model Context Protocol (MCP) client to interact
with Paperless-ngx documents and trigger n8n workflows through the MCP server.

Prerequisites:
- The MCP server (src/mcp_server.py) must be running
- You must have configured the environment variables for the MCP server
- Paperless-ngx and n8n must be properly configured and running

Usage:
1. Install the required dependencies:
   pip install mcp-python requests python-dotenv

2. Update the MCP_SERVER_URL variable below or set it as an environment variable

3. Run the script with one of the following commands:
   - List all documents:        python mcp_client_example.py list
   - Get document details:      python mcp_client_example.py get <document_id>
   - Chat with a document:      python mcp_client_example.py chat <document_id> "<your question>"
   - Update document tags:      python mcp_client_example.py tag <document_id>
   - Run all examples:          python mcp_client_example.py all

Example:
   python mcp_client_example.py chat 123 "What are the key points in this document?"
"""

import argparse
import os
import sys
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import MCP client library
try:
    from mcp import MCPClient
except ImportError:
    print("Error: MCP client library not found. Please install it using:")
    print("pip install mcp-python")
    sys.exit(1)

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")


def create_mcp_client() -> MCPClient:
    """
    Create and configure an MCP client connection to the server.
    
    Returns:
        MCPClient: Configured MCP client instance
    """
    print(f"Connecting to MCP server at {MCP_SERVER_URL}...")
    
    try:
        # Initialize the MCP client with our server URL
        client = MCPClient(base_url=MCP_SERVER_URL)
        
        # Verify the connection by retrieving the server resources and tools
        resources = client.list_resources()
        tools = client.list_tools()
        
        print(f"Successfully connected to MCP server!")
        print(f"Available resources: {', '.join([r.name for r in resources])}")
        print(f"Available tools: {', '.join([t.name for t in tools])}\n")
        
        return client
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        sys.exit(1)


def list_documents(client: MCPClient) -> None:
    """
    List all documents from Paperless-ngx through the MCP server.
    
    Args:
        client: The MCP client instance
    """
    print("\n=== Listing Documents ===")
    
    try:
        # Fetch the documents resource
        documents = client.get_resource("documents")
        
        # Process and display the documents
        print(f"Found {len(documents)} documents:")
        for i, doc in enumerate(documents[:10], 1):  # Show first 10 documents
            created_date = datetime.fromisoformat(doc.get('created_date', '').replace('Z', '+00:00'))
            print(f"{i}. ID: {doc['id']} - {doc['title']} ({created_date.strftime('%Y-%m-%d')})")
        
        if len(documents) > 10:
            print(f"... and {len(documents) - 10} more")
            
        return documents
    except Exception as e:
        print(f"Error listing documents: {e}")
        return []


def get_document_details(client: MCPClient, document_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific document.
    
    Args:
        client: The MCP client instance
        document_id: The ID of the document to retrieve
        
    Returns:
        Dict containing document details or None if an error occurred
    """
    print(f"\n=== Getting Document Details for ID: {document_id} ===")
    
    try:
        # Fetch specific document by ID
        document = client.get_resource("document", {"id": document_id})
        
        # Display document details
        print(f"Title: {document['title']}")
        print(f"Created: {document.get('created_date', 'Unknown')}")
        print(f"File Type: {document.get('document_type', {}).get('name', 'Unknown')}")
        
        # Show tags if available
        if 'tags' in document and document['tags']:
            tag_names = [tag.get('name', str(tag.get('id', 'Unknown'))) for tag in document['tags']]
            print(f"Tags: {', '.join(tag_names)}")
        else:
            print("Tags: None")
            
        # Show content snippet if available
        if 'content' in document and document['content']:
            content_preview = document['content'][:200] + "..." if len(document['content']) > 200 else document['content']
            print(f"\nContent Preview:\n{content_preview}")
        
        return document
    except Exception as e:
        print(f"Error getting document details: {e}")
        return None


def chat_with_document(client: MCPClient, document_id: int, question: str) -> None:
    """
    Trigger the document chat workflow in n8n and display the response.
    
    Args:
        client: The MCP client instance
        document_id: The ID of the document to chat with
        question: The user's question about the document
    """
    print(f"\n=== Chatting with Document ID: {document_id} ===")
    print(f"Question: {question}")
    
    try:
        # Call the MCP tool to trigger the n8n workflow
        result = client.use_tool("trigger_document_chat", {
            "document_id": document_id,
            "query": question
        })
        
        # Display the AI response
        print("\nAI Response:")
        print(f"{result.get('response', 'No response received')}")
        
        return result
    except Exception as e:
        print(f"Error chatting with document: {e}")
        return None


def update_document_tags(client: MCPClient, document_id: int) -> None:
    """
    Update document tags based on AI analysis of the document content.
    
    Args:
        client: The MCP client instance
        document_id: The ID of the document to analyze and tag
    """
    print(f"\n=== Updating Tags for Document ID: {document_id} ===")
    
    try:
        # First get current tags
        document = client.get_resource("document", {"id": document_id})
        current_tags = []
        if 'tags' in document and document['tags']:
            current_tags = [tag.get('name', str(tag.get('id', 'Unknown'))) for tag in document['tags']]
            print(f"Current tags: {', '.join(current_tags)}")
        else:
            print("Current tags: None")
        
        # Call the MCP tool to analyze and update tags
        result = client.use_tool("update_document_tags", {
            "document_id": document_id,
            "analyze_content": True
        })
        
        # Display the updated tags
        if result and 'updated_tags' in result:
            print(f"Updated tags: {', '.join(result['updated_tags'])}")
            
            # Show which tags were added
            added_tags = [tag for tag in result['updated_tags'] if tag not in current_tags]
            if added_tags:
                print(f"Added tags: {', '.join(added_tags)}")
        else:
            print("No tag updates were made")
        
        return result
    except Exception as e:
        print(f"Error updating document tags: {e}")
        return None


def main():
    """Main function to handle command line arguments and execute examples."""
    parser = argparse.ArgumentParser(
        description="Example script for interacting with Paperless-ngx through MCP"
    )
    
    # Define commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List documents command
    subparsers.add_parser("list", help="List all documents")
    
    # Get document details command
    get_parser = subparsers.add_parser("get", help="Get document details")
    get_parser.add_argument("document_id", type=int, help="ID of the document")
    
    # Chat with document command
    chat_parser = subparsers.add_parser("chat", help="Chat with a document")
    chat_parser.add_argument("document_id", type=int, help="ID of the document")
    chat_parser.add_argument("question", type=str, help="Question to ask about the document")
    
    # Update document tags command
    tag_parser = subparsers.add_parser("tag", help="Update document tags using AI")
    tag_parser.add_argument("document_id", type=int, help="ID of the document")
    
    # Run all examples command
    subparsers.add_parser("all", help="Run all examples sequentially")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create MCP client
    client = create_mcp_client()
    
    # Execute requested command
    if args.command == "list" or args.command == "all":
        documents = list_documents(client)
        
        # If running all examples and we have documents, use the first one for other commands
        if args.command == "all" and documents:
            document_id = documents[0]['id']
            get_document_details(client, document_id)
            chat_with_document(client, document_id, "What is this document about?")
            update_document_tags(client, document_id)
    
    elif args.command == "get":
        get_document_details(client, args.document_id)
    
    elif args.command == "chat":
        chat_with_document(client, args.document_id, args.question)
    
    elif args.command == "tag":
        update_document_tags(client, args.document_id)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

