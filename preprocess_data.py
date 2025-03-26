import json
import os

def preprocess_educational_content(json_file_path):
    """
    预处理教育内容 JSON 数据，为 RAG 系统准备文档
    """
    print(f"正在预处理文件: {json_file_path}")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建向量数据库文档
    documents = []
    
    for topic_data in data:
        topic = topic_data["topic"]
        print(f"处理主题: {topic}")
        
        for question_data in topic_data["questions"]:
            question = question_data["question"]
            
            for age_group, answer in question_data["answers"].items():
                # 为每个问题-答案对创建一个文档，包含元数据
                doc = {
                    "content": f"Question: {question}\nAnswer: {answer}",
                    "metadata": {
                        "topic": topic,
                        "question": question,
                        "age_group": age_group
                    }
                }
                documents.append(doc)
    
    print(f"预处理完成，共生成 {len(documents)} 个文档")
    
    # 保存预处理后的文档
    output_dir = "processed_data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "processed_documents.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    
    print(f"预处理数据已保存至: {output_path}")
    return documents, output_path

if __name__ == "__main__":
    # 如果直接运行此脚本，则处理完整的教育内容数据
    json_file_path = "data/educational_content_complete.json"
    preprocess_educational_content(json_file_path) 