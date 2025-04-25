import requests
import json
from typing import Dict, Any, List

def classify_query(query: str) -> str:
    """
    Classifies a user query into one of five categories: health, history, life_skills, science, or technology.
    
    Args:
        query: The user's question or query text
        
    Returns:
        The category classification as a string
    """
    # API configuration
    url = "https://api.ohmygpt.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    
    # Construct the prompt for classification
    prompt = f"""You are a classifier that categorizes educational questions into exactly one of these five categories:
- health: Questions about physical or mental health, wellness, medical topics, or the human body
- history: Questions about historical events, figures, civilizations, or time periods
- life_skills: Questions about practical skills, social interactions, personal development, or daily life
- science: Questions about scientific principles, natural phenomena, biology, chemistry, physics, or the universe
- technology: Questions about computers, internet, digital devices, programming, or technological innovations

The question is: "{query}"

Respond with only one word - the category name.
"""
    
    # Prepare the API request
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful classification assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 10  # We only need a short response
    }
    
    # Make the API call
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Extract the classification from the response
        classification = result["choices"][0]["message"]["content"].strip().lower()
        
        # Validate the classification is one of the expected categories
        valid_categories = ["health", "history", "life_skills", "science", "technology"]
        if classification in valid_categories:
            return classification
        else:
            # If response doesn't match expected categories, make a best effort match
            for category in valid_categories:
                if category in classification:
                    return category
            return "science"  # Default fallback
            
    except Exception as e:
        print(f"Error classifying query: {e}")
        return "science"  # Default category if classification fails

def main():
    """Test the classification function with sample queries"""
    test_queries = [
        "How does the heart pump blood?",
        "Who was the first emperor of China?",
        "How do I create a budget for my monthly expenses?",
        "Why is the sky blue?",
        "How does a computer processor work?"
    ]
    
    for query in test_queries:
        category = classify_query(query)
        print(f"Query: {query}")
        print(f"Category: {category}")
        print("-" * 50)

if __name__ == "__main__":
    main() 