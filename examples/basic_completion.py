"""
Basic Completion Example
Simple text completion using LLM clients
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.openai_client import OpenAIClient
from src.llm.claude_client import ClaudeClient
from config.config_loader import get_model_config


def basic_openai_completion():
    """Example: Basic OpenAI completion"""
    config = get_model_config()
    azure_config = config.get("azure_openai", {})
    
    client = OpenAIClient(
        api_key=azure_config.get("api_key"),
        model=azure_config.get("chat_model", {}).get("deployment_name"),
        use_azure=True,
        azure_endpoint=azure_config.get("endpoint")
    )
    
    prompt = "Write a professional email greeting for a business meeting."
    response = client.generate(prompt, temperature=0.7, max_tokens=100)
    
    print("OpenAI Response:")
    print(response)
    print()


def basic_claude_completion():
    """Example: Basic Claude completion"""
    # Note: Add your Claude API key to config
    client = ClaudeClient(
        api_key="your-claude-api-key",
        model="claude-3-5-sonnet-20241022"
    )
    
    prompt = "Explain what an email classification system does in one sentence."
    response = client.generate(prompt, temperature=0.5, max_tokens=100)
    
    print("Claude Response:")
    print(response)
    print()


def streaming_example():
    """Example: Streaming completion"""
    config = get_model_config()
    azure_config = config.get("azure_openai", {})
    
    client = OpenAIClient(
        api_key=azure_config.get("api_key"),
        model=azure_config.get("chat_model", {}).get("deployment_name"),
        use_azure=True,
        azure_endpoint=azure_config.get("endpoint")
    )
    
    prompt = "Write a short poem about artificial intelligence."
    
    print("Streaming Response:")
    for chunk in client.stream(prompt, temperature=0.8, max_tokens=150):
        print(chunk, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    print("=== Basic Completion Examples ===\n")
    
    # Run OpenAI example
    try:
        basic_openai_completion()
    except Exception as e:
        print(f"OpenAI example error: {e}\n")
    
    # Run streaming example
    try:
        streaming_example()
    except Exception as e:
        print(f"Streaming example error: {e}\n")
    
    # Uncomment to run Claude example (requires API key)
    # try:
    #     basic_claude_completion()
    # except Exception as e:
    #     print(f"Claude example error: {e}\n")

