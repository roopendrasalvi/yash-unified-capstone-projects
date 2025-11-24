"""
Configuration Loader Utility
Loads and manages all configuration files for the application
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class ConfigLoader:
    """Utility class to load and manage configuration files"""
    
    def __init__(self, config_dir: str = "D://NIA/yash_unified_capstone_projects/config"):
        """
        Initialize the configuration loader
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self._configs = {}
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """
        Load a specific configuration file
        
        Args:
            config_name: Name of the config file (without .yaml extension)
            
        Returns:
            Dictionary containing the configuration
        """
        if config_name in self._configs:
            return self._configs[config_name]
        
        config_path = self.config_dir / f"{config_name}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Replace environment variables
        config = self._replace_env_vars(config)
        
        self._configs[config_name] = config
        return config
    
    def _replace_env_vars(self, config: Any) -> Any:
        """
        Recursively replace environment variable placeholders with actual values
        
        Args:
            config: Configuration object (dict, list, or string)
            
        Returns:
            Configuration with environment variables replaced
        """
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable value
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, config)
            
            for match in matches:
                env_value = os.getenv(match, '')
                config = config.replace(f'${{{match}}}', env_value)
            
            return config
        else:
            return config
    
    def get(self, config_name: str, *keys: str, default: Any = None) -> Any:
        """
        Get a specific value from a configuration file
        
        Args:
            config_name: Name of the config file
            *keys: Nested keys to access the value
            default: Default value if key not found
            
        Returns:
            The configuration value or default
        """
        config = self.load_config(config_name)
        
        for key in keys:
            if isinstance(config, dict) and key in config:
                config = config[key]
            else:
                return default
        
        return config
    
    def reload(self, config_name: Optional[str] = None):
        """
        Reload configuration files
        
        Args:
            config_name: Specific config to reload, or None to reload all
        """
        if config_name:
            if config_name in self._configs:
                del self._configs[config_name]
        else:
            self._configs.clear()


# Global configuration loader instance
config_loader = ConfigLoader()

# Convenience functions for accessing specific configurations
def get_model_config() -> Dict[str, Any]:
    """Get model configuration"""
    return config_loader.load_config("model_config")

def get_vector_db_config() -> Dict[str, Any]:
    """Get vector database configuration"""
    return config_loader.load_config("vector_db")

def get_prompt_config() -> Dict[str, Any]:
    """Get prompt template configuration"""
    return config_loader.load_config("prompt_template")

def get_gmail_config() -> Dict[str, Any]:
    """Get Gmail extraction configuration"""
    return config_loader.load_config("gmail_extraction_config")

def get_outlook_config() -> Dict[str, Any]:
    """Get Outlook configuration"""
    return config_loader.load_config("outlook_config")

def get_app_config() -> Dict[str, Any]:
    """Get application configuration"""
    return config_loader.load_config("app_config")

def get_s3_config() -> Dict[str, Any]:
    """Get S3 configuration"""
    return config_loader.load_config("s3_config")

def get_database_config() -> Dict[str, Any]:
    """Get database configuration"""
    return config_loader.load_config("database_config")

