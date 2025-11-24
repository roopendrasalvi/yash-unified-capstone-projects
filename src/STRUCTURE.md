# Source Code Structure

## Complete File Tree

```
src/
├── __init__.py                                    ✅ Package initialization
├── README.md                                      ✅ Documentation
│
├── agents/                                        ✅ AI Agents Module
│   ├── __init__.py                               ✅ Module exports
│   ├── classification_agent.py                   ✅ Email classification
│   ├── birthday_agent.py                         ✅ Birthday email drafting
│   ├── actionable_agent.py                       ✅ Actionable email handling
│   └── agent_factory.py                          ✅ Agent factory pattern
│
├── extraction/                                    ✅ Email Extraction Module
│   ├── __init__.py                               ✅ Module exports
│   └── email_extraction/
│       ├── __init__.py                           ✅ Submodule initialization
│       ├── gmail_extraction.py                   ✅ Gmail OAuth & extraction
│       └── outlook_extraction.py                 ✅ Outlook OAuth & extraction
│
├── models/                                        ✅ Data Models Module
│   ├── __init__.py                               ✅ Module exports
│   ├── email_models.py                           ✅ Email data models
│   └── user_models.py                            ✅ User data models
│
├── services/                                      ✅ Business Logic Module
│   ├── __init__.py                               ✅ Module exports
│   ├── email_service.py                          ✅ Email processing service
│   ├── vector_service.py                         ✅ Vector DB operations
│   ├── embedding_service.py                      ✅ Embedding generation
│   └── s3_service.py                             ✅ AWS S3 operations
│
├── database/                                      ✅ Database Module
│   ├── __init__.py                               ✅ Module exports
│   ├── connection.py                             ✅ DB connection management
│   ├── models.py                                 ✅ SQLAlchemy ORM models
│   └── crud.py                                   ✅ CRUD operations
│
└── utils/                                         ✅ Utilities Module
    ├── __init__.py                               ✅ Module exports
    ├── logger.py                                 ✅ Logging configuration
    ├── helpers.py                                ✅ Helper functions
    └── validators.py                             ✅ Input validation
```

## Files Created (Total: 28 files)

### Core Package (2 files)
1. `src/__init__.py` - Package initialization with version info
2. `src/README.md` - Comprehensive documentation

### Agents Module (5 files)
3. `src/agents/__init__.py`
4. `src/agents/classification_agent.py` - ClassificationAgent class
5. `src/agents/birthday_agent.py` - BirthdayAgent class
6. `src/agents/actionable_agent.py` - ActionableAgent class
7. `src/agents/agent_factory.py` - AgentFactory class

### Extraction Module (4 files)
8. `src/extraction/__init__.py`
9. `src/extraction/email_extraction/__init__.py`
10. `src/extraction/email_extraction/gmail_extraction.py` - GmailExtractor class
11. `src/extraction/email_extraction/outlook_extraction.py` - OutlookExtractor class

### Models Module (3 files)
12. `src/models/__init__.py`
13. `src/models/email_models.py` - 10+ Pydantic models
14. `src/models/user_models.py` - 4 Pydantic models

### Services Module (5 files)
15. `src/services/__init__.py`
16. `src/services/email_service.py` - EmailService class
17. `src/services/vector_service.py` - VectorService class (Pinecone & Milvus)
18. `src/services/embedding_service.py` - EmbeddingService class
19. `src/services/s3_service.py` - S3Service class

### Database Module (4 files)
20. `src/database/__init__.py`
21. `src/database/connection.py` - DatabaseConnection class
22. `src/database/models.py` - 5 SQLAlchemy ORM models
23. `src/database/crud.py` - DatabaseCRUD class with 20+ methods

### Utils Module (4 files)
24. `src/utils/__init__.py`
25. `src/utils/logger.py` - Logging setup
26. `src/utils/helpers.py` - 10+ helper functions
27. `src/utils/validators.py` - 7+ validation functions

### Documentation (1 file)
28. `src/STRUCTURE.md` - This file

## Key Classes and Functions

### Agents
- `ClassificationAgent` - Email classification with category extraction
- `BirthdayAgent` - Birthday email drafting and template customization
- `ActionableAgent` - Actionable email analysis and response drafting
- `AgentFactory` - Factory for creating and managing agents

### Extraction
- `GmailExtractor` - Gmail OAuth, authentication, email extraction
- `OutlookExtractor` - Outlook OAuth, authentication, email extraction

### Services
- `EmailService` - classify_email(), draft_birthday_email(), draft_actionable_response()
- `VectorService` - Pinecone and Milvus operations (create, insert, search)
- `EmbeddingService` - Azure OpenAI and Google AI embeddings
- `S3Service` - upload_file(), download_file(), generate_presigned_url()

### Database
- `DatabaseConnection` - Connection management, session factory
- `DatabaseCRUD` - 20+ CRUD methods for all models
- ORM Models: OAuthCredentials, EmailMetadata, Attachment, UserPreferences, EmailDraftHistory

### Models (Pydantic)
- EmailRequest, EmailResponse, EmailClassification, EmailDraft
- AttachmentInfo, EmailMetadata, EmailExtractionRequest, EmailExtractionResponse
- UserCredentials, UserPreferences, AuthenticationStatus

### Utils
- Helpers: format_email_date(), sanitize_filename(), generate_s3_key(), validate_email()
- Validators: validate_email_request(), validate_classification_result(), validate_file_size()

## Integration Points

### With Config Module
All modules use `config.config_loader` to load configurations:
- Model configurations (Azure OpenAI, Google AI, LiteLLM)
- Vector DB settings (Pinecone, Milvus)
- Email provider OAuth settings
- S3 storage configuration
- Database connection strings

### With Main API (main.py)
The source code integrates with `main.py` endpoints:
- `/categorize_email/` → EmailService.classify_email()
- `/actionable_email/` → ActionableAgent.draft_response()
- `/extract_emails` → GmailExtractor/OutlookExtractor
- `/email_status/{user_email}` → DatabaseCRUD.get_oauth_credentials()

## Technology Stack

- **AI Framework**: Autogen (multi-agent system)
- **LLM Abstraction**: LiteLLM
- **Web Framework**: FastAPI
- **Data Validation**: Pydantic
- **ORM**: SQLAlchemy
- **Vector DBs**: Pinecone, Milvus
- **Email APIs**: Google Gmail API, Microsoft Graph API
- **Cloud Storage**: AWS S3
- **Databases**: PostgreSQL/Supabase, SQLite
- **Text Processing**: LangChain

## Next Steps

1. **Testing**: Create unit tests for all modules
2. **Integration**: Connect with main.py endpoints
3. **Documentation**: Add docstring examples
4. **Deployment**: Set up production environment
5. **Monitoring**: Add logging and metrics

