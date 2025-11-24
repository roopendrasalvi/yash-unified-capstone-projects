"""
Prompt Chain
Chain multiple prompts together
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChainStep:
    """Single step in prompt chain"""
    name: str
    prompt_template: str
    processor: Optional[Callable] = None
    variables: Optional[List[str]] = None


class PromptChain:
    """Chain multiple prompts together"""
    
    def __init__(self, name: str):
        """
        Initialize prompt chain
        
        Args:
            name: Chain name
        """
        self.name = name
        self.steps: List[ChainStep] = []
        self.results: Dict[str, Any] = {}
    
    def add_step(
        self,
        name: str,
        prompt_template: str,
        processor: Optional[Callable] = None,
        variables: Optional[List[str]] = None
    ):
        """
        Add a step to the chain
        
        Args:
            name: Step name
            prompt_template: Prompt template
            processor: Optional result processor
            variables: Required variables
        """
        step = ChainStep(name, prompt_template, processor, variables)
        self.steps.append(step)
        logger.debug(f"Added step '{name}' to chain '{self.name}'")
    
    def execute(
        self,
        llm_client: Any,
        initial_input: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the prompt chain
        
        Args:
            llm_client: LLM client instance
            initial_input: Initial input variables
            **kwargs: Additional parameters for LLM
            
        Returns:
            Results from all steps
        """
        context = initial_input.copy()
        self.results = {}
        
        for step in self.steps:
            logger.info(f"Executing step: {step.name}")
            
            # Format prompt with current context
            try:
                from string import Template
                prompt = Template(step.prompt_template).safe_substitute(**context)
            except Exception as e:
                logger.error(f"Error formatting prompt for step '{step.name}': {str(e)}")
                raise
            
            # Generate response
            try:
                response = llm_client.generate(prompt, **kwargs)
            except Exception as e:
                logger.error(f"Error generating response for step '{step.name}': {str(e)}")
                raise
            
            # Process response if processor provided
            if step.processor:
                try:
                    processed = step.processor(response)
                    self.results[step.name] = processed
                    context[step.name] = processed
                except Exception as e:
                    logger.error(f"Error processing response for step '{step.name}': {str(e)}")
                    raise
            else:
                self.results[step.name] = response
                context[step.name] = response
            
            logger.debug(f"Step '{step.name}' completed")
        
        return self.results
    
    def get_step_result(self, step_name: str) -> Any:
        """
        Get result from a specific step
        
        Args:
            step_name: Name of the step
            
        Returns:
            Step result
        """
        if step_name not in self.results:
            raise KeyError(f"Step '{step_name}' not found in results")
        
        return self.results[step_name]
    
    def get_final_result(self) -> Any:
        """Get result from the last step"""
        if not self.results:
            raise ValueError("Chain has not been executed yet")
        
        last_step = self.steps[-1].name
        return self.results[last_step]
    
    def clear_results(self):
        """Clear all results"""
        self.results = {}
        logger.debug(f"Cleared results for chain '{self.name}'")


class ChainManager:
    """Manage multiple prompt chains"""
    
    def __init__(self):
        """Initialize chain manager"""
        self.chains: Dict[str, PromptChain] = {}
    
    def create_chain(self, name: str) -> PromptChain:
        """
        Create a new chain
        
        Args:
            name: Chain name
            
        Returns:
            PromptChain instance
        """
        chain = PromptChain(name)
        self.chains[name] = chain
        logger.info(f"Created chain: {name}")
        return chain
    
    def get_chain(self, name: str) -> PromptChain:
        """
        Get a chain by name
        
        Args:
            name: Chain name
            
        Returns:
            PromptChain instance
        """
        if name not in self.chains:
            raise KeyError(f"Chain '{name}' not found")
        
        return self.chains[name]

