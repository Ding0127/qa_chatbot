import requests
import json
import time
import re
from typing import Iterator


def get_answers_gpt(context, temperature=0.7):
    model = "gpt-4o-mini"
    url = "https://api.ohmygpt.com/v1/chat/completions"
    
    # IMPORTANT: You should use environment variables for API keys in production
    # This is just for demonstration purposes
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    
    if isinstance(context, list):
        messages = []
        for i, c in enumerate(context):
            role = "user" if i % 2 == 0 else "assistant"
            
            if isinstance(c, str):
                content = [{"type": "text", "text": c}]
            else:
                content = [{"type": "text", "text": c["text"]}]
                
            messages.append({"role": role, "content": content})
            
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
    elif isinstance(context, str):
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": context
                        }
                    ]
                }
            ],
            "temperature": temperature
        }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_json = response.json()
        # Fix: Correctly retrieve the reply content
        if isinstance(response_json["choices"][0]["message"]["content"], list):
            assistant_reply = response_json["choices"][0]["message"]["content"][0]["text"]
        else:
            assistant_reply = response_json["choices"][0]["message"]["content"]
        return assistant_reply
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(e.response.text)
        raise ValueError("Error in the API request")

def stream_response(context: str, temperature: float = 0.7) -> Iterator[str]:
    """流式响应生成器函数"""
    model = "gpt-4o-mini"
    url = "https://api.ohmygpt.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": [{"type": "text", "text": context}]}],
        "temperature": temperature,
        "stream": True  # 启用流式响应
    }
    
    try:
        with requests.post(url, headers=headers, json=data, stream=True) as response:
            response.raise_for_status()
            
            # 处理流式响应
            accumulated_text = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        event_data = decoded_line[6:]  # 去掉"data: "前缀
                        if event_data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(event_data)
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content = delta["content"]
                                    accumulated_text += content
                                    yield accumulated_text
                        except json.JSONDecodeError:
                            continue
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(e.response.text)
        yield "Error in the API request"

def chat_interface(message: str, history: list) -> Iterator[str]:
    """Gradio聊天接口函数"""
    for response in stream_response(message):
        yield response


def clean_json_response(response):
    """Clean JSON string returned by GPT, remove Markdown code block markers"""
    # Remove possible code block markers
    cleaned = re.sub(r'```json\s*', '', response)
    cleaned = re.sub(r'```\s*', '', cleaned)
    return cleaned.strip()

def generate_educational_content():
    topics = ["Science", "Technology", "History", "Life Skills", "Health"]
    age_groups = ["Kindergarten", "P1-P3", "P4-P6"]
    
    all_content = []
    
    for topic in topics:
        print(f"Generating questions for {topic} topic...")
        
        # Generate 10 questions about this topic
        questions_prompt = f"""
        Generate 10 educational questions about {topic} suitable for children.
        Questions should be interesting and appropriate for elementary school children.
        Return only a JSON formatted list of 10 questions, as follows:
        [
            "Why is the sky blue?",
            "How do plants grow?",
            ...
        ]
        Do not include any other text or explanations, just return the JSON array.
        """
        
        questions_response = get_answers_gpt(questions_prompt, temperature=0.8)
        
        try:
            # Clean and parse the response to get questions
            cleaned_response = clean_json_response(questions_response)
            print(f"Cleaned response: {cleaned_response[:100]}...")
            questions_list = json.loads(cleaned_response)
            
            # Ensure we have 10 questions
            questions_list = questions_list[:10]
            
            topic_data = {
                "topic": topic,
                "questions": []
            }
            
            for question in questions_list:
                print(f"  Processing question: {question}")
                question_data = {
                    "question": question,
                    "answers": {}
                }
                
                # Generate answers for each age group
                for age_group in age_groups:
                    age_description = {
                        "Kindergarten": "Ages 3-6: Simple, fun language, basic concepts",
                        "P1-P3": "Ages 6-9: Short explanations and simple analogies",
                        "P4-P6": "Ages 9-12: More detailed answers, appropriate use of technical terms"
                    }
                    
                    answer_prompt = f"""
                    Question: {question}
                    
                    Please provide an educational answer for {age_group} students ({age_description[age_group]}).
                    The answer should be appropriate for their age level in terms of language, complexity, and content.
                    Provide only the answer without any introduction or explanation about the age group.
                    """
                    
                    answer = get_answers_gpt(answer_prompt, temperature=0.7)
                    question_data["answers"][age_group] = answer.strip()
                    
                    # Add a small delay to avoid rate limits
                    time.sleep(1)
                
                topic_data["questions"].append(question_data)
            
            all_content.append(topic_data)
            
            # Save progress after each topic is completed
            with open(f"educational_content_{topic.lower()}.json", "w", encoding="utf-8") as f:
                json.dump(topic_data, f, ensure_ascii=False, indent=2)
                
        except json.JSONDecodeError as e:
            print(f"Error parsing questions for {topic}. Error: {e}")
            print(f"Original response: {questions_response}")
            continue
    
    # Save the complete dataset
    with open("educational_content_complete.json", "w", encoding="utf-8") as f:
        json.dump(all_content, f, ensure_ascii=False, indent=2)
    
    return all_content

if __name__ == "__main__":
    content = generate_educational_content()
    print(f"Generated content for {len(content)} topics")
    print("Data has been saved to educational_content_complete.json")