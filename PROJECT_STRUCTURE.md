# Project Structure

```
yash-unified-capstone-projects/
│
├── config/                                    # Configuration files
│   ├── __init__.py
│   ├── model_config.yaml
│   ├── prompt_template.yaml
│   ├── vector_db.yaml
│   ├── gmail_extraction_config.yaml
│   ├── outlook_config.yaml
│   ├── s3_config.yaml
│   ├── database_config.yaml
│   ├── app_config.yaml
│   ├── config_loader.py
│   └── README.md
│
├── src/                                       # Core source code
│   ├── __init__.py
│   ├── README.md
│   ├── STRUCTURE.md
│   │
│   ├── llm/                                   # LLM client implementations
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── claude_client.py
│   │   ├── openai_client.py
│   │   └── utils.py
│   │
│   ├── agents/                                # AI agents
│   │   ├── __init__.py
│   │   ├── classification_agent.py
│   │   ├── birthday_agent.py
│   │   ├── actionable_agent.py
│   │   └── agent_factory.py
│   │
│   ├── extraction/                            # Email extraction
│   │   ├── __init__.py
│   │   └── email_extraction/
│   │       ├── __init__.py
│   │       ├── gmail_extraction.py
│   │       └── outlook_extraction.py
│   │
│   ├── models/                                # Data models
│   │   ├── __init__.py
│   │   ├── email_models.py
│   │   └── user_models.py
│   │
│   ├── services/                              # Business logic
│   │   ├── __init__.py
│   │   ├── email_service.py
│   │   ├── vector_service.py
│   │   ├── embedding_service.py
│   │   └── s3_service.py
│   │
│   ├── database/                              # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── crud.py
│   │
│   └── utils/                                 # Source utilities
│       ├── __init__.py
│       ├── logger.py
│       ├── helpers.py
│       └── validators.py
│
├── prompt_engineering/                        # Prompt engineering
│   ├── __init__.py
│   ├── templates.py
│   ├── few_shot.py
│   └── chain.py
│
├── utils/                                     # General utilities
│   ├── __init__.py
│   ├── rate_limiter.py
│   ├── token_counter.py
│   ├── cache.py
│   └── logger.py
│
├── handlers/                                  # Error handlers
│   ├── __init__.py
│   └── error_handler.py
│
├── data/                                      # Data storage
│   ├── cache/
│   ├── prompts/
│   ├── outputs/
│   └── embeddings/
│
├── examples/                                  # Example scripts
│   ├── basic_completion.py
│   ├── chat_session.py
│   └── chain_prompts.py
│
├── notebooks/                                 # Jupyter notebooks
│   ├── prompt_testing.ipynb
│   ├── response_analysis.ipynb
│   └── model_experimentation.ipynb
│
├── main.py                                    # FastAPI application
├── requirements.txt                           # Dependencies
├── setup.py                                   # Package setup
├── README.md                                  # Project documentation
└── Dockerfile                                 # Docker configuration
```

## Module Overview

### config/
Configuration files separate from code using YAML format

### src/llm/
Base LLM client implementations for OpenAI and Claude

### src/agents/
AI agents for email classification, birthday emails, and actionable emails

### src/extraction/
Email extraction from Gmail and Outlook with OAuth

### src/models/
Pydantic data models for validation

### src/services/
Business logic layer for email processing, embeddings, and vector operations

### src/database/
Database layer with SQLAlchemy ORM

### prompt_engineering/
Prompt templates, few-shot learning, and prompt chaining

### utils/
Rate limiting, token counting, caching, and logging utilities

### handlers/
Centralized error handling

### data/
Organized storage for different data types

### examples/
Implementation references and usage examples

### notebooks/
Experimentation and analysis notebooks

