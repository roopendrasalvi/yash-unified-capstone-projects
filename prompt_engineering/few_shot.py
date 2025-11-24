"""
Few-Shot Prompting
Few-shot learning prompt construction
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class FewShotExample:
    """Single few-shot example"""
    input: str
    output: str
    explanation: Optional[str] = None


class FewShotPrompt:
    """Few-shot prompt builder"""
    
    def __init__(
        self,
        instruction: str,
        examples: Optional[List[FewShotExample]] = None,
        input_prefix: str = "Input:",
        output_prefix: str = "Output:",
        separator: str = "\n\n"
    ):
        """
        Initialize few-shot prompt
        
        Args:
            instruction: Task instruction
            examples: List of examples
            input_prefix: Prefix for input
            output_prefix: Prefix for output
            separator: Separator between examples
        """
        self.instruction = instruction
        self.examples = examples or []
        self.input_prefix = input_prefix
        self.output_prefix = output_prefix
        self.separator = separator
    
    def add_example(
        self,
        input_text: str,
        output_text: str,
        explanation: Optional[str] = None
    ):
        """
        Add an example
        
        Args:
            input_text: Example input
            output_text: Example output
            explanation: Optional explanation
        """
        example = FewShotExample(input_text, output_text, explanation)
        self.examples.append(example)
        logger.debug(f"Added example: {input_text[:50]}...")
    
    def build(self, query: str) -> str:
        """
        Build complete few-shot prompt
        
        Args:
            query: User query/input
            
        Returns:
            Complete prompt with examples
        """
        parts = [self.instruction]
        
        # Add examples
        for example in self.examples:
            example_text = f"{self.input_prefix} {example.input}\n{self.output_prefix} {example.output}"
            
            if example.explanation:
                example_text += f"\nExplanation: {example.explanation}"
            
            parts.append(example_text)
        
        # Add query
        parts.append(f"{self.input_prefix} {query}\n{self.output_prefix}")
        
        return self.separator.join(parts)
    
    def get_examples_count(self) -> int:
        """Get number of examples"""
        return len(self.examples)
    
    def clear_examples(self):
        """Clear all examples"""
        self.examples = []
        logger.debug("Cleared all examples")


class FewShotManager:
    """Manage multiple few-shot prompts"""
    
    def __init__(self):
        """Initialize few-shot manager"""
        self.prompts: Dict[str, FewShotPrompt] = {}
    
    def create_prompt(
        self,
        name: str,
        instruction: str,
        examples: Optional[List[FewShotExample]] = None
    ) -> FewShotPrompt:
        """
        Create and register a few-shot prompt
        
        Args:
            name: Prompt name
            instruction: Task instruction
            examples: Initial examples
            
        Returns:
            FewShotPrompt instance
        """
        prompt = FewShotPrompt(instruction, examples)
        self.prompts[name] = prompt
        logger.info(f"Created few-shot prompt: {name}")
        return prompt
    
    def get_prompt(self, name: str) -> FewShotPrompt:
        """
        Get a prompt by name
        
        Args:
            name: Prompt name
            
        Returns:
            FewShotPrompt instance
        """
        if name not in self.prompts:
            raise KeyError(f"Few-shot prompt '{name}' not found")
        
        return self.prompts[name]
    
    def build(self, name: str, query: str) -> str:
        """
        Build a prompt by name
        
        Args:
            name: Prompt name
            query: User query
            
        Returns:
            Complete prompt
        """
        prompt = self.get_prompt(name)
        return prompt.build(query)

