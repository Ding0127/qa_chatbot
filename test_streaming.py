import requests
import gradio as gr
from typing import Iterator

import json

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

# 创建Gradio界面
demo = gr.ChatInterface(
    fn=chat_interface,
    title="GPT-4o-mini 聊天演示",
    description="与GPT-4o-mini进行流式对话",
    theme="soft"
)

if __name__ == "__main__":
    demo.queue().launch()