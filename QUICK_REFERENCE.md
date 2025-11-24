# Quick Reference Guide - Email Processing System

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/.env.template .env
# Edit .env with your API keys

# Run application
uvicorn main:app --reload
```

### 2. API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/extract_emails` | POST | Extract emails from Gmail/Outlook |
| `/get_email` | POST | Process and vectorize email |
| `/gmail/auth` | GET | Gmail OAuth authentication |
| `/outlook/auth` | GET | Outlook OAuth authentication |
| `/user_approval` | GET | Get user approval status |

---

## 📊 Code Flow Summary

### Email Extraction Flow
```
User → API → GmailExtractor/OutlookExtractor → OAuth → List Messages → 
Get Details → Download Attachments → S3 Upload → Database Store → Response
```

### Email Classification Flow
```
User → API → EmailService → ConfigLoader → AgentFactory → 
ClassificationAgent → SelectorGroupChat → Route to Specialized Agent → 
LLM Generation → Response
```

### Vector Storage Flow
```
User → API → Split Text → Generate Embeddings → Create/Get Index → 
Store Vectors → Pinecone/Milvus → Response
```

---

## 🏗️ Architecture Layers

1. **API Layer** - FastAPI endpoints
2. **Service Layer** - Business logic (EmailService, VectorService, S3Service)
3. **Agent Layer** - AI agents (Classification, Birthday, Actionable)
4. **Extraction Layer** - Email providers (Gmail, Outlook)
5. **LLM Layer** - Language models (Azure OpenAI, LiteLLM, Claude)
6. **Data Layer** - Storage (PostgreSQL, Pinecone, Milvus, S3)
7. **Config Layer** - Configuration management
8. **Utils Layer** - Cross-cutting concerns

---

## 🤖 AI Agents

### Classification Agent
- **Purpose:** Categorize emails
- **Categories:** Category 0 (Birthday), Category 1 (Actionable), Promotional
- **Priority:** Category 1 > Category 0 > Promotional

### Birthday Agent
- **Purpose:** Draft birthday/anniversary emails
- **Inputs:** recipient_name, occasion, context, tone
- **Output:** Personalized email draft

### Actionable Agent
- **Purpose:** Handle actionable emails
- **Subcategories:** Approval, Asset, Leave, Meeting
- **Flow:** Classify → Ask User → Generate Response

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application, all endpoints |
| `config/config_loader.py` | Load YAML configs with env vars |
| `src/services/email_service.py` | Email processing business logic |
| `src/agents/classification_agent.py` | Email classification |
| `src/agents/birthday_agent.py` | Birthday email drafting |
| `src/agents/actionable_agent.py` | Actionable email handling |
| `src/extraction/email_extraction/gmail_extraction.py` | Gmail integration |
| `src/extraction/email_extraction/outlook_extraction.py` | Outlook integration |
| `src/llm/openai_client.py` | OpenAI/Azure client |
| `src/llm/claude_client.py` | Claude client |
| `prompt_engineering/templates.py` | Prompt management |
| `utils/rate_limiter.py` | API rate limiting |
| `utils/token_counter.py` | Token usage tracking |

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `config/model_config.yaml` | LLM settings (Azure, Google, LiteLLM) |
| `config/prompt_template.yaml` | System prompts for agents |
| `config/vector_db.yaml` | Pinecone and Milvus settings |
| `config/gmail_extraction_config.yaml` | Gmail OAuth config |
| `config/outlook_config.yaml` | Outlook OAuth config |
| `config/s3_config.yaml` | AWS S3 settings |
| `config/database_config.yaml` | Database connection |

---

## 🔑 Environment Variables

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
DEPLOYMENT_NAME=gpt-4o

# Pinecone
PINECONE_API_KEY=your-pinecone-key

# Gmail
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-client-secret

# Outlook
OUTLOOK_CLIENT_ID=your-client-id
OUTLOOK_CLIENT_SECRET=your-client-secret

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=your-bucket

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
```

---

## 📦 Key Dependencies

- **fastapi** - Web framework
- **autogen-agentchat** - Multi-agent system
- **litellm** - LLM routing
- **langchain** - LLM orchestration
- **pinecone-client** - Vector database
- **pymilvus** - Vector database
- **google-api-python-client** - Gmail API
- **msal** - Outlook authentication
- **boto3** - AWS S3
- **sqlalchemy** - Database ORM
- **pydantic** - Data validation

---

## 🎯 Common Use Cases

### 1. Extract Gmail Emails
```python
POST /extract_emails
{
  "user_email": "user@gmail.com",
  "provider": "gmail",
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-01-31T23:59:59"
}
```

### 2. Classify Email
```python
from src.services.email_service import EmailService

service = EmailService()
result = await service.classify_email(
    subject="Happy Birthday!",
    body="Wishing you a wonderful day!"
)
# Returns: EmailClassification(category="Category 0", ...)
```

### 3. Draft Birthday Email
```python
result = await service.draft_birthday_email(
    recipient_name="John",
    occasion="birthday",
    tone="warm and professional"
)
# Returns: EmailDraft(subject="...", body="...")
```

---

## 🐛 Debugging Tips

1. **Check logs:** `logger.info()` statements throughout code
2. **Enable LiteLLM debug:** `litellm._turn_on_debug()`
3. **Verify configs:** Ensure all `${ENV_VAR}` are replaced
4. **Test OAuth:** Check token files exist (`token_*.pickle`)
5. **Monitor tokens:** Use `TokenCounter` to track usage
6. **Check rate limits:** `RateLimiter` prevents quota issues

---

## 📚 Additional Resources

- **Full Documentation:** `CODE_FLOW_DOCUMENTATION.md`
- **Project Structure:** `PROJECT_STRUCTURE.md`
- **Examples:** `examples/` directory
- **Notebooks:** `notebooks/` directory
- **Config README:** `config/README.md`

