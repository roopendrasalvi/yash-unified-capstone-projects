# Source Code Documentation

This directory contains the core source code for the Email Processing and Classification System.

## Directory Structure

```
src/
├── agents/                 # AI Agent implementations
│   ├── __init__.py
│   ├── classification_agent.py    # Email classification agent
│   ├── birthday_agent.py          # Birthday email drafting agent
│   ├── actionable_agent.py        # Actionable email handling agent
│   └── agent_factory.py           # Factory for creating agents
│
├── extraction/            # Email extraction modules
│   ├── __init__.py
│   └── email_extraction/
│       ├── __init__.py
│       ├── gmail_extraction.py    # Gmail OAuth and extraction
│       └── outlook_extraction.py  # Outlook OAuth and extraction
│
├── models/                # Pydantic data models
│   ├── __init__.py
│   ├── email_models.py           # Email-related models
│   └── user_models.py            # User-related models
│
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── email_service.py          # Email processing service
│   ├── vector_service.py         # Vector database operations
│   ├── embedding_service.py      # Text embedding generation
│   └── s3_service.py             # AWS S3 operations
│
├── database/              # Database layer
│   ├── __init__.py
│   ├── connection.py             # Database connection management
│   ├── models.py                 # SQLAlchemy ORM models
│   └── crud.py                   # CRUD operations
│
└── utils/                 # Utility functions
    ├── __init__.py
    ├── logger.py                 # Logging configuration
    ├── helpers.py                # Helper functions
    └── validators.py             # Input validation
```

## Module Descriptions

### 1. Agents (`agents/`)

AI agents powered by Autogen framework for email processing:

- **ClassificationAgent**: Classifies emails into categories (Birthday, Actionable, Promotional)
- **BirthdayAgent**: Drafts personalized birthday and anniversary emails
- **ActionableAgent**: Handles actionable emails (approvals, meetings, assets, leaves)
- **AgentFactory**: Factory pattern for creating and managing agents

**Usage Example:**
```python
from src.agents.agent_factory import AgentFactory

factory = AgentFactory()
classification_agent = factory.create_classification_agent()
result = await classification_agent.classify(subject, body)
```

### 2. Extraction (`extraction/`)

Email extraction from various providers:

- **GmailExtractor**: Gmail OAuth authentication and email extraction
- **OutlookExtractor**: Outlook OAuth authentication and email extraction

**Usage Example:**
```python
from src.extraction.email_extraction.gmail_extraction import gmail_manager

gmail_manager.authenticate(user_email)
emails = gmail_manager.extract_emails(user_email, max_results=50)
```

### 3. Models (`models/`)

Pydantic models for data validation:

- **email_models.py**: EmailRequest, EmailResponse, EmailClassification, EmailDraft, AttachmentInfo
- **user_models.py**: UserCredentials, UserPreferences, AuthenticationStatus

**Usage Example:**
```python
from src.models.email_models import EmailRequest

email_request = EmailRequest(
    subject="Meeting Request",
    body="Let's schedule a meeting...",
    sender="user@example.com"
)
```

### 4. Services (`services/`)

Business logic and service layer:

- **EmailService**: Email processing, classification, and drafting
- **VectorService**: Pinecone and Milvus vector database operations
- **EmbeddingService**: Text embedding generation (Azure OpenAI, Google AI)
- **S3Service**: AWS S3 file upload/download operations

**Usage Example:**
```python
from src.services.email_service import EmailService

email_service = EmailService()
classification = await email_service.classify_email(subject, body)
```

### 5. Database (`database/`)

Database layer with SQLAlchemy:

- **connection.py**: Database connection management (PostgreSQL/SQLite)
- **models.py**: ORM models (OAuthCredentials, EmailMetadata, Attachment, UserPreferences)
- **crud.py**: CRUD operations for all models

**Usage Example:**
```python
from src.database.connection import DatabaseConnection
from src.database.crud import DatabaseCRUD

db_conn = DatabaseConnection()
db = db_conn.get_session()
credentials = DatabaseCRUD.get_oauth_credentials(db, user_email)
```

### 6. Utils (`utils/`)

Utility functions and helpers:

- **logger.py**: Logging configuration
- **helpers.py**: Common helper functions (date formatting, filename sanitization, S3 key generation)
- **validators.py**: Input validation functions

**Usage Example:**
```python
from src.utils.helpers import sanitize_filename, generate_s3_key
from src.utils.validators import validate_email_request

safe_filename = sanitize_filename("my file (1).pdf")
s3_key = generate_s3_key(user_email, "gmail", safe_filename)
```

## Key Features

### Multi-Agent System
- Uses Autogen framework for intelligent email processing
- Specialized agents for different email types
- LiteLLM for model routing and abstraction

### Email Provider Support
- Gmail with OAuth 2.0 authentication
- Outlook/Microsoft 365 with MSAL authentication
- Attachment extraction and S3 storage

### Vector Database Integration
- Pinecone for cloud-based vector storage
- Milvus for self-hosted vector storage
- Semantic search capabilities

### Database Support
- PostgreSQL/Supabase for production
- SQLite for local development
- Complete ORM with SQLAlchemy

## Configuration

All modules use centralized configuration from the `config/` folder:
- Model configurations (Azure OpenAI, Google AI, LiteLLM)
- Vector database settings (Pinecone, Milvus)
- Email provider OAuth settings
- S3 storage configuration
- Database connection strings

## Dependencies

Key dependencies:
- `autogen-agentchat`: Multi-agent framework
- `litellm`: LLM abstraction layer
- `fastapi`: Web framework
- `pydantic`: Data validation
- `sqlalchemy`: ORM
- `google-api-python-client`: Gmail API
- `msal`: Microsoft authentication
- `boto3`: AWS S3
- `pinecone-client`: Pinecone vector DB
- `pymilvus`: Milvus vector DB
- `langchain`: Text processing and retrieval

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables (see `config/.env.template`)

3. Initialize database:
   ```python
   from src.database.connection import DatabaseConnection
   db_conn = DatabaseConnection()
   db_conn.create_tables()
   ```

4. Use in your application:
   ```python
   from src.services.email_service import EmailService
   
   email_service = EmailService()
   result = await email_service.classify_email(subject, body)
   ```

