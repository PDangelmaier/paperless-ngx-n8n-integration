# Paperless-ngx and n8n Integration via Model Context Protocol

This guide provides detailed instructions for installing, configuring, and using the integration between Paperless-ngx and n8n via the Model Context Protocol (MCP).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the MCP Server](#running-the-mcp-server)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following requirements:

1. **Python 3.8+** installed on your system
2. **Paperless-ngx** instance up and running
   - You'll need admin access to your Paperless-ngx instance
   - You'll need to create an API token
3. **n8n** instance up and running
   - You'll need to be able to create and manage workflows
   - You'll need access to n8n API or webhook endpoints
4. Basic knowledge of the command line
5. An AI model that supports the Model Context Protocol (optional, needed for AI interactions)

## Installation

There are two ways to install the integration: using pip or setting up from the source code.

### Option 1: Install using pip (Recommended)

```bash
# Create and activate a virtual environment (recommended)
python -m venv mcp-integration
source mcp-integration/bin/activate  # On Windows, use: mcp-integration\Scripts\activate

# Install the package
pip install paperless-ngx-n8n-mcp

# Verify installation
paperless-n8n-mcp --version
```

### Option 2: Install from source

```bash
# Clone the repository
git clone https://github.com/PDangelmaier/paperless-ngx-n8n-integration.git
cd paperless-ngx-n8n-integration

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Configuration

After installation, you need to configure the integration by setting up environment variables.

1. **Create an environment file**:

   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Open .env file with your favorite text editor
   nano .env  # or use any other editor
   ```

2. **Configure Paperless-ngx connection**:

   In your `.env` file, update the following variables:
   
   ```
   # Paperless-ngx configuration
   PAPERLESS_URL=http://your-paperless-instance:8000
   PAPERLESS_API_TOKEN=your_api_token_from_paperless
   ```
   
   To get your API token:
   - Log in to your Paperless-ngx instance
   - Go to Profile settings (click on your username in the top-right corner)
   - Navigate to the "API Keys" section
   - Generate a new API key and copy it

3. **Configure n8n connection**:

   ```
   # n8n configuration
   N8N_URL=http://your-n8n-instance:5678
   N8N_API_TOKEN=your_n8n_api_token
   ```
   
   To get your n8n token:
   - Log in to your n8n instance
   - Go to Settings → API
   - Enable API and generate a token

4. **Configure MCP server settings**:

   ```
   # MCP server configuration
   MCP_PORT=3333
   MCP_HOST=0.0.0.0
   LOG_LEVEL=INFO
   ```

## Running the MCP Server

Once installation and configuration are complete, you can start the MCP server.

### Start the server

```bash
# If you installed via pip
paperless-n8n-mcp start

# If you installed from source
python src/mcp_server.py
```

You should see output similar to:
```
INFO:     Starting MCP server on http://0.0.0.0:3333
INFO:     Model Context Protocol server is ready!
INFO:     Exposing 3 resources and 4 tools for Paperless-ngx and n8n integration
```

### Register with AI models

To use the MCP server with AI models, you need to register the MCP server URL with your AI model provider. The process varies depending on the AI model you're using.

For Claude Desktop:
```bash
claude mcp install http://localhost:3333
```

## Usage Examples

Once your MCP server is running and registered with your AI model, you can use it to interact with Paperless-ngx and n8n. Here are some examples:

### 1. Query Document Information

You can ask your AI assistant questions about your documents:

- "List all documents with the tag 'Invoice'"
- "Find documents containing information about 'project X'"
- "What are all the document categories in my system?"

### 2. Automate Workflows

You can use natural language to trigger n8n workflows:

- "Process the latest invoice document and update its metadata"
- "Start the OCR workflow for documents uploaded today"
- "Trigger the email notification workflow for all documents with the tag 'Urgent'"

### 3. Analyze Documents

You can ask your AI to analyze documents:

- "Summarize the content of the latest tax document"
- "Extract action items from the meeting notes document"
- "Suggest appropriate tags for the document titled 'Q3 Financial Report'"

## Troubleshooting

### Common Issues and Solutions

1. **Connection Failed to Paperless-ngx**
   - Check that your Paperless-ngx URL is correct and accessible
   - Verify that your API token is valid and has the necessary permissions
   - Ensure that Paperless-ngx API is enabled

2. **Connection Failed to n8n**
   - Check that your n8n URL is correct and accessible
   - Verify that your API token is valid
   - Ensure that n8n API access is enabled in your n8n settings

3. **MCP Server Won't Start**
   - Check if another service is already using the configured port
   - Verify that you have the correct Python version
   - Check the log output for specific error messages

4. **AI Model Can't Connect to MCP Server**
   - Ensure the MCP server is running
   - Check that your firewall allows connections to the MCP port
   - Verify that the URL you provided to your AI model is correct and accessible

### Getting Help

If you encounter issues not covered in this guide:

1. Check the [GitHub Issues](https://github.com/PDangelmaier/paperless-ngx-n8n-integration/issues) for similar problems
2. Review the logs by running the server with increased verbosity:
   ```bash
   LOG_LEVEL=DEBUG paperless-n8n-mcp start
   ```
3. Open a new issue on GitHub with details about your problem and the steps to reproduce it

