# Configuration Files

This directory contains all configuration files for the Email Processing and Classification application.

## Configuration Files Overview

### 1. **app_config.yaml**
Main application configuration including:
- FastAPI settings (host, port, CORS)
- Streamlit frontend settings
- Logging configuration
- Rate limiting
- Email processing settings
- MCP (Model Context Protocol) configuration
- Cache settings
- Feature flags
- Security settings

### 2. **model_config.yaml**
AI/ML model configurations:
- Azure OpenAI settings (endpoint, API key, deployment)
- Embedding model configuration
- Chat model configuration
- Google AI settings
- LiteLLM router configuration
- Agent configurations (classification, birthday, actionable)

### 3. **prompt_template.yaml**
Prompt templates and system messages:
- Custom prompts for MCP tools
- Classification agent system message
- Birthday agent system message
- Actionable agent system message
- Email categories definitions
- Email templates (birthday, approval, meeting)

### 4. **vector_db.yaml**
Vector database configurations:
- **Pinecone**: Index settings, text splitter, retriever configuration
- **Milvus**: Connection settings, collection schema, index configuration
- Sample email data for testing

### 5. **gmail_extraction_config.yaml**
Gmail OAuth and extraction settings:
- Google OAuth credentials
- Scopes and permissions
- Database connection for storing credentials
- Redirect URIs

### 6. **outlook_config.yaml**
Outlook/Microsoft Graph API settings:
- Microsoft OAuth credentials
- Graph API endpoints
- Email extraction settings
- S3 storage configuration
- Database settings

### 7. **s3_config.yaml**
AWS S3 configuration for attachment storage:
- AWS credentials
- Bucket settings
- Folder structure
- Upload settings (ACL, encryption, storage class)
- File settings (size limits, allowed/blocked extensions)
- Lifecycle rules
- CloudFront CDN configuration (optional)

### 8. **database_config.yaml**
Database configurations:
- PostgreSQL/Supabase connection settings
- Table schemas (oauth_credentials, email_metadata, attachments, user_preferences)
- SQLite configuration for local development
- Migration settings
- Backup settings

### 9. **.env.template**
Template for environment variables:
- Copy this to `.env` and fill in your actual values
- Contains placeholders for all required API keys and credentials

## Usage

### Using the Configuration Loader

```python
from config.config_loader import config_loader, get_model_config, get_vector_db_config

# Load a specific configuration
model_config = get_model_config()

# Access nested values
azure_endpoint = config_loader.get("model_config", "azure_openai", "endpoint")

# Load with default value
pinecone_key = config_loader.get("vector_db", "pinecone", "api_key", default="")
```

### Environment Variables

All sensitive information (API keys, passwords, etc.) should be stored in environment variables.
The configuration files use the `${VARIABLE_NAME}` syntax to reference environment variables.

1. Copy `.env.template` to `.env`:
   ```bash
   cp config/.env.template .env
   ```

2. Fill in your actual values in the `.env` file

3. The `config_loader.py` will automatically replace `${VARIABLE_NAME}` with the actual values from environment variables

## Configuration File Format

All configuration files use YAML format with the following features:

- **Environment Variable Substitution**: Use `${VAR_NAME}` to reference environment variables
- **Nested Structure**: Organize related settings hierarchically
- **Comments**: Use `#` for inline documentation
- **Type Safety**: YAML supports strings, numbers, booleans, lists, and dictionaries

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use `.env.template`** to document required environment variables
3. **Rotate credentials regularly**
4. **Use different credentials** for development, staging, and production
5. **Limit access** to configuration files containing sensitive data

## Adding New Configurations

To add a new configuration file:

1. Create a new YAML file in the `config/` directory
2. Add environment variable placeholders using `${VAR_NAME}` syntax
3. Update `.env.template` with new required variables
4. Add a convenience function in `config_loader.py` if needed
5. Document the new configuration in this README

## Configuration Validation

The application validates configurations on startup. If required values are missing or invalid, the application will fail to start with a descriptive error message.

## Troubleshooting

### Common Issues

1. **Missing environment variables**: Check that all variables in `.env.template` are set in your `.env` file
2. **YAML syntax errors**: Validate your YAML files using a YAML linter
3. **File not found**: Ensure configuration files are in the correct directory
4. **Permission errors**: Check file permissions on configuration files

### Debug Mode

Enable debug mode in `app_config.yaml` to see detailed configuration loading logs:

```yaml
app:
  debug: true
```

## Configuration Hierarchy

The application loads configurations in the following order:

1. Environment variables (`.env` file)
2. Configuration files (`.yaml` files)
3. Default values (hardcoded in the application)

Later sources override earlier ones.

