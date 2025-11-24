"""
Chain Prompts Example
Chaining multiple prompts together
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.openai_client import OpenAIClient
from prompt_engineering.chain import PromptChain
from config.config_loader import get_model_config
import json


def email_processing_chain():
    """Example: Chain for processing an email"""
    config = get_model_config()
    azure_config = config.get("azure_openai", {})
    
    client = OpenAIClient(
        api_key=azure_config.get("api_key"),
        model=azure_config.get("chat_model", {}).get("deployment_name"),
        use_azure=True,
        azure_endpoint=azure_config.get("endpoint")
    )
    
    # Create chain
    chain = PromptChain("email_processing")
    
    # Step 1: Classify email
    chain.add_step(
        name="classification",
        prompt_template="""
        Classify the following email into one of these categories: Birthday, Actionable, Promotional.
        
        Email Subject: ${subject}
        Email Body: ${body}
        
        Respond with only the category name.
        """,
        processor=lambda x: x.strip()
    )
    
    # Step 2: Extract key information
    chain.add_step(
        name="extraction",
        prompt_template="""
        From the following email, extract key information in JSON format.
        
        Email Subject: ${subject}
        Email Body: ${body}
        Category: ${classification}
        
        Extract: sender intent, action required, deadline (if any).
        Respond with only valid JSON.
        """,
        processor=lambda x: json.loads(x) if x.strip().startswith('{') else {}
    )
    
    # Step 3: Generate response
    chain.add_step(
        name="response",
        prompt_template="""
        Draft a professional response to this email.
        
        Original Email:
        Subject: ${subject}
        Body: ${body}
        
        Category: ${classification}
        Key Info: ${extraction}
        
        Write a brief, professional response.
        """
    )
    
    # Execute chain
    email_data = {
        "subject": "Meeting Request - Q4 Planning",
        "body": "Hi, I'd like to schedule a meeting next week to discuss Q4 planning. Are you available on Tuesday or Wednesday afternoon?"
    }
    
    print("=== Email Processing Chain ===\n")
    print(f"Input Email:")
    print(f"Subject: {email_data['subject']}")
    print(f"Body: {email_data['body']}\n")
    
    results = chain.execute(client, email_data, temperature=0.7, max_tokens=300)
    
    print(f"Step 1 - Classification: {results['classification']}")
    print(f"Step 2 - Extraction: {results['extraction']}")
    print(f"Step 3 - Response:\n{results['response']}")


def multi_step_analysis_chain():
    """Example: Multi-step email analysis"""
    config = get_model_config()
    azure_config = config.get("azure_openai", {})
    
    client = OpenAIClient(
        api_key=azure_config.get("api_key"),
        model=azure_config.get("chat_model", {}).get("deployment_name"),
        use_azure=True,
        azure_endpoint=azure_config.get("endpoint")
    )
    
    chain = PromptChain("analysis")
    
    # Step 1: Sentiment analysis
    chain.add_step(
        name="sentiment",
        prompt_template="Analyze the sentiment of this text in one word (Positive/Negative/Neutral): ${text}"
    )
    
    # Step 2: Urgency detection
    chain.add_step(
        name="urgency",
        prompt_template="Rate the urgency of this text (Low/Medium/High): ${text}"
    )
    
    # Step 3: Summary
    chain.add_step(
        name="summary",
        prompt_template="""
        Summarize this text in one sentence:
        ${text}
        
        Sentiment: ${sentiment}
        Urgency: ${urgency}
        """
    )
    
    text = "URGENT: The server is down and customers are unable to access the application. We need immediate action to resolve this issue."
    
    print("\n=== Multi-Step Analysis Chain ===\n")
    print(f"Input Text: {text}\n")
    
    results = chain.execute(client, {"text": text}, temperature=0.5, max_tokens=100)
    
    print(f"Sentiment: {results['sentiment']}")
    print(f"Urgency: {results['urgency']}")
    print(f"Summary: {results['summary']}")


if __name__ == "__main__":
    try:
        email_processing_chain()
        print("\n" + "="*50 + "\n")
        multi_step_analysis_chain()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

