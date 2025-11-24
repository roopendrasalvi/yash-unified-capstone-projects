"""
Prompt Templates
Template management for prompts
"""

from typing import Dict, Any, Optional, List
from string import Template
import yaml
import logging

logger = logging.getLogger(__name__)


class PromptTemplate:
    """Prompt template with variable substitution"""
    
    def __init__(self, template: str, variables: Optional[List[str]] = None):
        """
        Initialize prompt template
        
        Args:
            template: Template string with ${variable} placeholders
            variables: List of required variables
        """
        self.template = Template(template)
        self.variables = variables or []
        self.raw_template = template
    
    def format(self, **kwargs) -> str:
        """
        Format template with variables
        
        Args:
            **kwargs: Variable values
            
        Returns:
            Formatted prompt
        """
        # Validate required variables
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        
        try:
            return self.template.safe_substitute(**kwargs)
        except Exception as e:
            logger.error(f"Template formatting error: {str(e)}")
            raise
    
    def get_variables(self) -> List[str]:
        """Get list of variables in template"""
        return self.variables


class PromptManager:
    """Manage multiple prompt templates"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize prompt manager
        
        Args:
            config_path: Path to YAML config file
        """
        self.templates: Dict[str, PromptTemplate] = {}
        
        if config_path:
            self.load_from_yaml(config_path)
    
    def add_template(self, name: str, template: str, variables: Optional[List[str]] = None):
        """
        Add a prompt template
        
        Args:
            name: Template name
            template: Template string
            variables: Required variables
        """
        self.templates[name] = PromptTemplate(template, variables)
        logger.info(f"Added template: {name}")
    
    def get_template(self, name: str) -> PromptTemplate:
        """
        Get a template by name
        
        Args:
            name: Template name
            
        Returns:
            PromptTemplate instance
        """
        if name not in self.templates:
            raise KeyError(f"Template '{name}' not found")
        
        return self.templates[name]
    
    def format(self, name: str, **kwargs) -> str:
        """
        Format a template by name
        
        Args:
            name: Template name
            **kwargs: Variable values
            
        Returns:
            Formatted prompt
        """
        template = self.get_template(name)
        return template.format(**kwargs)
    
    def load_from_yaml(self, config_path: str):
        """
        Load templates from YAML file
        
        Args:
            config_path: Path to YAML file
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            templates = config.get('templates', {})
            
            for name, template_config in templates.items():
                if isinstance(template_config, str):
                    self.add_template(name, template_config)
                elif isinstance(template_config, dict):
                    self.add_template(
                        name,
                        template_config.get('template', ''),
                        template_config.get('variables', [])
                    )
            
            logger.info(f"Loaded {len(templates)} templates from {config_path}")
            
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            raise
    
    def list_templates(self) -> List[str]:
        """Get list of template names"""
        return list(self.templates.keys())

