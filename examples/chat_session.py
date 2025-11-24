"""
Chat Session Example
Multi-turn conversation with LLM
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.openai_client import OpenAIClient
from src.llm.utils import format_messages, count_messages_tokens
from config.config_loader import get_model_config


def chat_session_example():
    """Example: Multi-turn chat session"""
    config = get_model_config()
    azure_config = config.get("azure_openai", {})
    
    client = OpenAIClient(
        api_key=azure_config.get("api_key"),
        model=azure_config.get("chat_model", {}).get("deployment_name"),
        use_azure=True,
        azure_endpoint=azure_config.get("endpoint")
    )
    
    # System prompt
    system_prompt = "You are a helpful email assistant that helps classify and draft emails."
    
    # Conversation history
    conversation = []
    
    # Turn 1
    messages = format_messages(
        system_prompt=system_prompt,
        user_message="What categories of emails can you help me with?",
        history=conversation
    )
    
    response1 = client.chat(messages, temperature=0.7, max_tokens=200)
    print("User: What categories of emails can you help me with?")
    print(f"Assistant: {response1}\n")
    
    # Add to history
    conversation.append({"role": "user", "content": "What categories of emails can you help me with?"})
    conversation.append({"role": "assistant", "content": response1})
    
    # Turn 2
    messages = format_messages(
        system_prompt=system_prompt,
        user_message="Can you draft a birthday email for my colleague John?",
        history=conversation
    )
    
    response2 = client.chat(messages, temperature=0.8, max_tokens=300)
    print("User: Can you draft a birthday email for my colleague John?")
    print(f"Assistant: {response2}\n")
    
    # Add to history
    conversation.append({"role": "user", "content": "Can you draft a birthday email for my colleague John?"})
    conversation.append({"role": "assistant", "content": response2})
    
    # Turn 3
    messages = format_messages(
        system_prompt=system_prompt,
        user_message="Make it more casual and friendly.",
        history=conversation
    )
    
    response3 = client.chat(messages, temperature=0.8, max_tokens=300)
    print("User: Make it more casual and friendly.")
    print(f"Assistant: {response3}\n")
    
    # Token usage
    final_messages = format_messages(
        system_prompt=system_prompt,
        history=conversation
    )
    total_tokens = count_messages_tokens(final_messages, model="gpt-4")
    print(f"Total tokens used in conversation: {total_tokens}")


def contextual_chat_example():
    """Example: Chat with context from previous emails"""
    config = get_model_config()
    azure_config = config.get("azure_openai", {})
    
    client = OpenAIClient(
        api_key=azure_config.get("api_key"),
        model=azure_config.get("chat_model", {}).get("deployment_name"),
        use_azure=True,
        azure_endpoint=azure_config.get("endpoint")
    )
    
    # Context from email
    email_context = """
    Previous Email:
    From: manager@company.com
    Subject: Project Update Required
    Body: Please provide an update on the Q4 project status by end of week.
    """
    
    system_prompt = f"You are an email assistant. Here's the context:\n{email_context}"
    
    messages = format_messages(
        system_prompt=system_prompt,
        user_message="Help me draft a response to this email."
    )
    
    response = client.chat(messages, temperature=0.7, max_tokens=300)
    
    print("=== Contextual Chat Example ===")
    print(f"Context: {email_context}")
    print(f"\nUser: Help me draft a response to this email.")
    print(f"\nAssistant: {response}\n")


if __name__ == "__main__":
    print("=== Chat Session Examples ===\n")
    
    try:
        chat_session_example()
        print("\n" + "="*50 + "\n")
        contextual_chat_example()
    except Exception as e:
        print(f"Error: {e}")

