# Email Processing System - Complete Code Flow Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Main Code Flows](#main-code-flows)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)

---

## System Overview

This is an **AI-powered email processing and classification system** that:
- Extracts emails from Gmail and Outlook
- Classifies emails into categories (Birthday, Actionable, Promotional)
- Drafts automated responses using AI agents
- Stores email data and embeddings for semantic search
- Manages attachments via AWS S3

**Tech Stack:**
- **Backend:** FastAPI
- **AI Framework:** Autogen (multi-agent system)
- **LLM:** Azure OpenAI (GPT-4o), LiteLLM Router, Claude
- **Vector DBs:** Pinecone, Milvus
- **Storage:** PostgreSQL/Supabase, AWS S3
- **Email APIs:** Gmail API, Microsoft Graph API

---

## Architecture Layers

### 1. **API Layer** (FastAPI)
Entry points for all operations:
- `/extract_emails` - Extract emails from providers
- `/get_email` - Process and vectorize email content
- `/gmail/auth` - Gmail OAuth authentication
- `/outlook/auth` - Outlook OAuth authentication
- `/user_approval` - Get user approval for actions

### 2. **Service Layer**
Business logic orchestration:
- **EmailService** - Email classification and processing
- **VectorService** - Vector database operations
- **EmbeddingService** - Generate embeddings
- **S3Service** - Attachment storage

### 3. **Agent Layer** (Autogen)
AI agents for intelligent processing:
- **ClassificationAgent** - Categorizes emails
- **BirthdayAgent** - Drafts birthday/anniversary emails
- **ActionableAgent** - Handles approval/meeting/leave/asset emails
- **SelectorGroupChat** - Orchestrates multi-agent collaboration

### 4. **Extraction Layer**
Email provider integrations:
- **GmailExtractor** - Gmail OAuth + API
- **OutlookExtractor** - Outlook OAuth + Graph API

### 5. **LLM Layer**
Language model clients:
- **LiteLLM Router** - Multi-model routing
- **Azure OpenAI Client** - GPT-4o, embeddings
- **Claude Client** - Anthropic Claude
- **OpenAI Client** - Generic OpenAI

### 6. **Data Layer**
Persistent storage:
- **PostgreSQL/Supabase** - User credentials, email metadata
- **Pinecone** - Cloud vector database
- **Milvus** - Self-hosted vector database
- **AWS S3** - Email attachments

### 7. **Configuration Layer**
Centralized config management:
- **ConfigLoader** - Loads YAML configs with env var substitution
- **model_config.yaml** - LLM settings
- **prompt_template.yaml** - System prompts
- **vector_db.yaml** - Vector DB settings

### 8. **Utilities Layer**
Cross-cutting concerns:
- **RateLimiter** - API rate limiting
- **TokenCounter** - Track token usage
- **Cache** - LRU caching
- **Logger** - Logging
- **ErrorHandler** - Error handling

---

## Main Code Flows

### Flow 1: Email Extraction (Gmail/Outlook)

```
User Request → /extract_emails API
    ↓
Validate Request (user_email, provider, filters)
    ↓
Provider Selection (Gmail or Outlook)
    ↓
┌─────────────────────────────────┬─────────────────────────────────┐
│ GMAIL FLOW                      │ OUTLOOK FLOW                    │
├─────────────────────────────────┼─────────────────────────────────┤
│ 1. GmailExtractor.authenticate  │ 1. OutlookExtractor.authenticate│
│    - Load token_{email}.pickle  │    - MSAL authentication        │
│    - Refresh if expired         │    - Get access token           │
│    - OAuth flow if needed       │    - Store in database          │
│                                 │                                 │
│ 2. Build Gmail Service          │ 2. Microsoft Graph API client   │
│    - google.build('gmail')      │    - requests to graph.ms.com   │
│                                 │                                 │
│ 3. List Messages                │ 3. List Messages                │
│    - Apply filters (date,       │    - Apply filters              │
│      sender, subject)           │    - Query inbox/folders        │
│    - Query: "after:date         │                                 │
│      has:attachment"            │                                 │
│                                 │                                 │
│ 4. Get Message Details          │ 4. Get Message Details          │
│    - Parse headers              │    - Parse JSON response        │
│    - Extract body               │    - Extract body               │
│    - Process attachments        │    - Process attachments        │
│                                 │                                 │
│ 5. Download Attachments         │ 5. Download Attachments         │
│    - Base64 decode              │    - Download from Graph API    │
└─────────────────────────────────┴─────────────────────────────────┘
    ↓
S3Service.upload_attachment
    - Path: {user_email}/{provider}/{year}/{month}/{day}/{filename}
    - Return S3 URL
    ↓
Database.store_email_metadata
    - Store in PostgreSQL/Supabase
    - Fields: subject, sender, date, s3_urls, etc.
    ↓
Return EmailExtractionResponse
    - emails_processed count
    - attachments_extracted count
    - execution_time
```

---

### Flow 2: Email Processing & Vectorization

```
User Request → /get_email API (subject, body)
    ↓
1. Setup Pinecone
   - Initialize client with API key
   - Connect to cloud instance
    ↓
2. Split Text
   - RecursiveCharacterTextSplitter
   - chunk_size=100, chunk_overlap=20
   - Returns: text_splitter, chunks[]
    ↓
3. Create/Get Index
   - Check if index exists
   - Create if not: dimension=1536, metric=cosine
   - ServerlessSpec: AWS us-east-1
    ↓
4. Generate Embeddings
   - Model: azure/text-embedding-3-small
   - LiteLLM embedding() function
   - Input: text chunks
   - Output: 1536-dim vectors
    ↓
5. Store Vectors
   - Pinecone.from_documents()
   - Upsert vectors to index
   - Metadata: chunk text, source
    ↓
Return Success Response
```

---

### Flow 3: Email Classification & Response Generation

```
User Input → Email (subject, body)
    ↓
1. Configuration Loading
   - ConfigLoader loads all YAML configs
   - Replaces ${ENV_VAR} with actual values
   - Loads: model_config, prompt_template, vector_db
    ↓
2. Initialize Agents
   ┌─────────────────────────────────────────────────────────┐
   │ ClassificationAgent                                     │
   │ - Name: "EmailClassificationAgent"                      │
   │ - System Message: Classification rules                  │
   │ - Priority: Category 1 > Category 0 > Promotional      │
   │                                                         │
   │ BirthdayAgent                                           │
   │ - Name: "BirthdayEmailAssistant"                        │
   │ - System Message: Birthday email drafting rules         │
   │                                                         │
   │ ActionableAgent                                         │
   │ - Name: "ActionableEmailAssistant"                      │
   │ - System Message: Actionable email rules                │
   │ - Subcategories: Approval, Asset, Leave, Meeting        │
   │                                                         │
   │ UserProxyAgent                                          │
   │ - Name: "user_proxy"                                    │
   │ - Input function: input()                               │
   └─────────────────────────────────────────────────────────┘
    ↓
3. Create SelectorGroupChat Team
   - Agents: [classification, birthday, actionable, user_proxy]
   - Model: LiteLLM client
   - Termination: MaxMessageTermination(5)
    ↓
4. Receive Email Message
   - TextMessage(content=f"Subject: {subject}\nBody: {body}")
    ↓
5. Classification Agent Processes
   - Analyzes email content
   - Checks Category 1 (Actionable) first
   - Then Category 0 (Birthday/Anniversary)
   - Finally Promotional
   - Returns: category, confidence, reasoning
    ↓
6. Route to Appropriate Agent
   ┌──────────────┬──────────────────┬─────────────────┐
   │ Category 0   │ Category 1       │ Promotional     │
   ├──────────────┼──────────────────┼─────────────────┤
   │ Birthday     │ Actionable       │ Mark & Archive  │
   │ Agent        │ Agent            │                 │
   └──────────────┴──────────────────┴─────────────────┘
```

#### Category 0: Birthday/Anniversary Flow
```
BirthdayAgent.draft_email()
    ↓
Input:
- recipient_name
- occasion (birthday/anniversary)
- context (optional)
- tone (warm and professional)
    ↓
Prompt Construction:
"Draft a {occasion} email for {recipient_name}.
Tone: {tone}
Additional context: {context}"
    ↓
LLM Generation (via LiteLLM)
    ↓
Output:
{
  "subject": "Happy Birthday!",
  "body": "Dear {name}, ...",
  "tone": "warm and professional",
  "agent": "BirthdayEmailAssistant"
}
```

#### Category 1: Actionable Email Flow
```
ActionableAgent.analyze_and_respond()
    ↓
1. Subcategory Classification
   - Analyze email content
   - Determine: Approval | Asset | Leave | Meeting
    ↓
2. Extract Key Information
   - Action required
   - Deadline (if any)
   - Key details
    ↓
3. Ask User for Action
   - Display email summary
   - Prompt: "Do you want to approve or deny?"
   - UserProxyAgent.input_func() waits for input
    ↓
4. User Decision
   ┌─────────────┬─────────────┐
   │ Approve     │ Deny        │
   └─────────────┴─────────────┘
    ↓              ↓
5. Generate Response Email
   - Use appropriate template
   - Include user's decision
   - Professional tone
    ↓
Output:
{
  "subcategory": "Approval",
  "action_required": "approve/deny",
  "response_subject": "Re: ...",
  "response_body": "...",
  "agent": "ActionableEmailAssistant"
}
```

---

## Component Details

### 1. Configuration System

**ConfigLoader** (`config/config_loader.py`)
```python
class ConfigLoader:
    def __init__(self, config_dir="D://NIA/yash_unified_capstone_projects/config")

    def load_config(config_name: str) -> Dict
        # Loads YAML file
        # Replaces ${ENV_VAR} with os.getenv("ENV_VAR")
        # Caches in self._configs

    def _replace_env_vars(config: Any) -> Any
        # Recursively replaces environment variables
        # Pattern: ${VARIABLE_NAME}
```

**Usage:**
```python
from config.config_loader import get_model_config

config = get_model_config()
azure_config = config["azure_openai"]
api_key = azure_config["api_key"]  # Already replaced from ${AZURE_OPENAI_KEY}
```

---

### 2. Email Extraction Components

**GmailExtractor** (`src/extraction/email_extraction/gmail_extraction.py`)

Key Methods:
```python
def authenticate(user_email: str) -> bool
    # 1. Check for token_{user_email}.pickle
    # 2. Load existing credentials
    # 3. Refresh if expired
    # 4. Run OAuth flow if needed
    # 5. Save credentials
    # 6. Build Gmail service

def extract_emails(
    start_date: datetime,
    end_date: datetime,
    filters: Dict
) -> List[Dict]
    # 1. Build query string
    # 2. Call service.users().messages().list()
    # 3. For each message:
    #    - Get full message
    #    - Parse headers
    #    - Decode body
    #    - Extract attachments
    # 4. Return email list

def get_message_details(
    message_id: str,
    user_email: str,
    upload_to_s3: bool
) -> Dict
    # 1. Get message by ID
    # 2. Parse payload
    # 3. Extract parts (text, html, attachments)
    # 4. If upload_to_s3:
    #    - Download attachment
    #    - Upload to S3
    #    - Store S3 URL
    # 5. Return message details
```

**OutlookExtractor** (`src/extraction/email_extraction/outlook_extraction.py`)

Key Methods:
```python
def authenticate(user_email: str) -> bool
    # 1. MSAL (Microsoft Authentication Library)
    # 2. Get access token
    # 3. Store in database
    # 4. Return success

def extract_emails(
    start_date: datetime,
    end_date: datetime,
    filters: Dict
) -> List[Dict]
    # 1. Build Graph API query
    # 2. GET https://graph.microsoft.com/v1.0/me/messages
    # 3. Apply filters ($filter, $select)
    # 4. Parse JSON response
    # 5. Download attachments if needed
    # 6. Return email list
```

---

### 3. Agent System (Autogen)

**Agent Factory** (`src/agents/agent_factory.py`)
```python
class AgentFactory:
    def create_classification_agent() -> ClassificationAgent
    def create_birthday_agent() -> BirthdayAgent
    def create_actionable_agent() -> ActionableAgent
```

**Classification Agent** (`src/agents/classification_agent.py`)
```python
class ClassificationAgent:
    def __init__(model_client):
        # Load prompt config
        # Create AssistantAgent with system message

    async def classify(email_subject: str, email_body: str) -> Dict
        # 1. Create prompt
        # 2. Send to agent
        # 3. Parse response
        # 4. Extract category
        # 5. Return classification result
```

**System Message:**
```
You are an expert who classifies mails based on 3 categories:
1. Category 0: Birthday or Anniversary wishes
2. Category 1: Approvals (leaves, meetings, assets)
3. Promotional: Promotional advertisements

Priority: Category 1 > Category 0 > Promotional
```

**Birthday Agent** (`src/agents/birthday_agent.py`)
```python
class BirthdayAgent:
    async def draft_email(
        recipient_name: str,
        occasion: str,
        context: str,
        tone: str
    ) -> Dict
        # 1. Build prompt with parameters
        # 2. Send to LLM
        # 3. Generate personalized email
        # 4. Return draft
```

**Actionable Agent** (`src/agents/actionable_agent.py`)
```python
class ActionableAgent:
    SUBCATEGORIES = ["Approval", "Asset", "Leave", "Meeting"]

    async def analyze_and_respond(
        email_subject: str,
        email_body: str,
        user_action: str
    ) -> Dict
        # 1. Classify into subcategory
        # 2. Extract action required
        # 3. Ask user for decision
        # 4. Generate response based on decision
        # 5. Return response draft
```

---

### 4. Vector Database Operations

**Embedding Generation**
```python
def get_embeddings(text: str) -> List[float]:
    embeddings = embedding(
        model="azure/text-embedding-3-small",
        api_key=AZURE_OPENAI_KEY,
        api_base=AZURE_OPENAI_ENDPOINT,
        api_version=API_VERSION,
        input=text
    )
    return embeddings  # 1536-dimensional vector
```

**Pinecone Operations**
```python
# Setup
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# Create Index
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Store Vectors
index = pc.Index(host="https://...")
vectorstore = Pinecone.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name=index_name
)

# Query
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10}
)
results = retriever.get_relevant_documents(query)
```

**Milvus Operations** (Alternative)
```python
# Connect
connections.connect(host="localhost", port="19530")

# Create Collection
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535)
]
schema = CollectionSchema(fields)
collection = Collection(name="emails", schema=schema)

# Insert
collection.insert([ids, embeddings, texts])

# Search
results = collection.search(
    data=[query_embedding],
    anns_field="embedding",
    param={"metric_type": "L2", "params": {"nprobe": 10}},
    limit=10
)
```

---

### 5. LLM Integration

**LiteLLM Router** (main.py)
```python
# Model Configuration
llm_config = [
    {
        "model_name": "gpt-4o",
        "litellm_params": {
            "model": AZURE_DEPLOYMENT_NAME,
            "api_key": AZURE_OPENAI_KEY,
            "api_version": API_VERSION,
            "api_base": AZURE_OPENAI_ENDPOINT
        }
    }
]

# Create Router
litellm_router = Router(model_list=llm_config)
llm = ChatLiteLLMRouter(
    router=litellm_router,
    model_name="gpt-4o",
    temperature=0.1
)

# Use in Chain
chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)
result = chain.invoke(query)
```

**Agent Model Client**
```python
model_client = litellm.LiteLLM()

# Used by all agents
classification_agent = AssistantAgent(
    "EmailClassificationAgent",
    model_client=model_client,
    system_message="..."
)
```

---

### 6. S3 Storage

**S3Service** (`src/services/s3_service.py`)
```python
class S3Service:
    def upload_attachment(
        file_data: bytes,
        filename: str,
        user_email: str,
        provider: str,
        date: datetime
    ) -> str:
        # Path structure
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")

        s3_key = f"{user_email}/{provider}/{year}/{month}/{day}/{filename}"

        # Upload
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=file_data
        )

        # Return URL
        return f"s3://{bucket_name}/{s3_key}"
```

---

## Data Flow

### Complete Request-Response Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI ENDPOINT                             │
│  - Validate request                                             │
│  - Parse parameters                                             │
│  - Route to appropriate service                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                                │
│  - Load configuration                                           │
│  - Initialize required components                               │
│  - Orchestrate business logic                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        ↓                                           ↓
┌──────────────────┐                    ┌──────────────────────┐
│  AGENT LAYER     │                    │  EXTRACTION LAYER    │
│  - Classification│                    │  - OAuth Auth        │
│  - Birthday      │                    │  - API Calls         │
│  - Actionable    │                    │  - Parse Response    │
└──────────────────┘                    └──────────────────────┘
        ↓                                           ↓
┌──────────────────┐                    ┌──────────────────────┐
│  LLM LAYER       │                    │  STORAGE LAYER       │
│  - LiteLLM       │                    │  - S3 Upload         │
│  - Azure OpenAI  │                    │  - Database Insert   │
│  - Embeddings    │                    │  - Vector Store      │
└──────────────────┘                    └──────────────────────┘
        ↓                                           ↓
        └─────────────────────┬─────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE FORMATTING                          │
│  - Aggregate results                                            │
│  - Format as JSON                                               │
│  - Add metadata (timestamps, counts, etc.)                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    RETURN TO USER                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Design Patterns

### 1. **Factory Pattern**
- `AgentFactory` creates agent instances
- Centralizes agent initialization
- Manages dependencies

### 2. **Service Layer Pattern**
- Separates business logic from API layer
- `EmailService`, `VectorService`, `S3Service`
- Reusable across different endpoints

### 3. **Repository Pattern**
- Database CRUD operations in `src/database/crud.py`
- Abstracts data access
- Supports multiple databases (PostgreSQL, SQLite)

### 4. **Strategy Pattern**
- Different extraction strategies for Gmail vs Outlook
- Pluggable LLM clients (Azure, Claude, OpenAI)
- Multiple vector databases (Pinecone, Milvus)

### 5. **Chain of Responsibility**
- Agent team processes emails sequentially
- Classification → Routing → Specialized Agent
- Each agent handles specific category

---

## Configuration Management

### Environment Variables
```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_KEY=sk-...
DEPLOYMENT_NAME=gpt-4o

# Pinecone
PINECONE_API_KEY=...

# Gmail OAuth
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...

# Outlook OAuth
OUTLOOK_CLIENT_ID=...
OUTLOOK_CLIENT_SECRET=...

# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=...

# Database
DATABASE_URL=postgresql://...
```

### YAML Configuration Files

**model_config.yaml**
```yaml
azure_openai:
  endpoint: ${AZURE_OPENAI_ENDPOINT}
  api_key: ${AZURE_OPENAI_KEY}
  embedding_model:
    deployment_name: text-embedding-3-small
    dimension: 1536
  chat_model:
    deployment_name: ${DEPLOYMENT_NAME}
    temperature: 0.7
```

**prompt_template.yaml**
```yaml
classification_agent_system_message: |
  You are an expert who classifies mails...

birthday_agent_system_message: |
  You are an expert birthday email assistant...

actionable_agent_system_message: |
  You are an expert actionable email assistant...
```

---

## Error Handling

### Error Handler (`handlers/error_handler.py`)
```python
class ErrorHandler:
    def handle_error(error: Exception, context: Dict) -> Dict:
        # 1. Log error
        # 2. Track error count
        # 3. Return formatted error response

@handle_errors(default_response=None, raise_on_error=False)
def some_function():
    # Function logic
    pass
```

### API Error Responses
```json
{
  "error": "Error message",
  "error_type": "ValueError",
  "status_code": 400,
  "context": {
    "function": "classify_email",
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

---

## Performance Optimizations

### 1. **Caching**
- LRU cache for LLM responses
- Config caching in ConfigLoader
- Token caching for OAuth

### 2. **Rate Limiting**
- Token bucket algorithm
- Prevents API quota exhaustion
- Configurable limits per model

### 3. **Batch Processing**
- Process multiple emails in parallel
- Batch embedding generation
- Bulk vector upserts

### 4. **Async Operations**
- Async agent methods
- Concurrent API calls
- Non-blocking I/O

---

## Security Considerations

### 1. **OAuth 2.0**
- Secure token storage
- Automatic token refresh
- Encrypted credentials in database

### 2. **Environment Variables**
- Sensitive data not in code
- `.env` file not committed
- Config loader replaces placeholders

### 3. **API Key Management**
- Stored in environment
- Rotated regularly
- Access logging

### 4. **Data Privacy**
- Email data encrypted at rest (S3)
- Secure database connections
- HTTPS for all API calls

---

## Monitoring & Logging

### Token Counter
```python
token_counter = TokenCounter()
token_counter.add_request("gpt-4", input_tokens=100, output_tokens=50)
stats = token_counter.get_stats()
# {
#   "total_requests": 1,
#   "total_input_tokens": 100,
#   "total_output_tokens": 50,
#   "total_cost": 0.0015
# }
```

### Logger
```python
logger.info("Email classified successfully")
logger.error("Failed to extract emails", exc_info=True)
logger.warning("Rate limit approaching")
```

---

## Testing

### Example Scripts (`examples/`)
- `basic_completion.py` - Test LLM clients
- `chat_session.py` - Test multi-turn conversations
- `chain_prompts.py` - Test prompt chaining

### Notebooks (`notebooks/`)
- `prompt_testing.ipynb` - Iterate on prompts
- `response_analysis.ipynb` - Analyze LLM outputs
- `model_experimentation.ipynb` - Compare models

---

## Deployment

### Docker
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Run
```bash
# Build
docker build -t email-assistant .

# Run
docker run -p 8000:8000 --env-file .env email-assistant
```

---

## Summary

This email processing system demonstrates:
- **Multi-agent AI architecture** using Autogen
- **Hybrid vector search** with Pinecone and Milvus
- **OAuth integration** with Gmail and Outlook
- **Scalable storage** with S3 and PostgreSQL
- **Flexible LLM routing** with LiteLLM
- **Production-ready** error handling, logging, and monitoring

The modular design allows easy extension with new:
- Email providers
- AI agents
- Vector databases
- LLM models
- Storage backends

