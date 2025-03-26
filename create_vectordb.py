import os
import json
import time
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.embeddings.base import Embeddings
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables (for API keys)
load_dotenv()

# 创建自定义嵌入类
class BaiLianEmbeddings(Embeddings):
    def __init__(self, api_key=None, model="text-embedding-v3"):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set DASHSCOPE_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        print(f"初始化 BaiLianEmbeddings 类，使用模型: {self.model}")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
    def embed_documents(self, texts):
        """嵌入文档列表"""
        print(f"开始嵌入 {len(texts)} 个文档...")
        embeddings = []
        
        # 批量处理以提高效率，但每批次限制数量
        batch_size = 5
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            print(f"处理批次 {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}，包含 {len(batch_texts)} 个文档")
            
            for j, text in enumerate(batch_texts):
                try:
                    print(f"  嵌入文档 {i+j+1}/{len(texts)}, 长度: {len(text)} 字符")
                    print(f"  文档预览: {text[:100]}...")
                    
                    response = self.client.embeddings.create(
                        model=self.model,
                        input=text,
                        encoding_format="float"
                    )
                    
                    # 验证响应
                    if not hasattr(response, 'data') or not response.data:
                        print(f"  警告: API 响应中没有 data 字段: {response}")
                        continue
                        
                    embedding = response.data[0].embedding
                    
                    # 验证嵌入向量
                    if not embedding or not isinstance(embedding, list):
                        print(f"  警告: 无效的嵌入向量: {embedding}")
                        continue
                        
                    # 保持1024维度
                    if len(embedding) != 1024:
                        if len(embedding) > 1024:
                            embedding = embedding[:1024]
                        else:
                            embedding.extend([0.0] * (1024 - len(embedding)))
                        
                    print(f"  成功获取嵌入向量，维度: {len(embedding)}")
                    embeddings.append(embedding)
                    
                except Exception as e:
                    print(f"  错误: 嵌入文档时出错: {str(e)}")
                    # 添加一个空向量以保持索引一致性
                    embeddings.append([0.0] * 1024)  # 使用1024维
                
                # 添加短暂延迟以避免API限制
                time.sleep(0.5)
        
        print(f"文档嵌入完成，共生成 {len(embeddings)} 个嵌入向量")
        return embeddings
    
    def embed_query(self, text):
        """嵌入单个查询文本"""
        print(f"嵌入查询: '{text[:100]}...'")
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text,
                    encoding_format="float"
                )
                
                embedding = response.data[0].embedding
                
                # 确保向量维度为1024
                if len(embedding) != 1024:
                    print(f"警告：获取到的向量维度为 {len(embedding)}，需要调整到1024维")
                    # 如果维度大于1024，截断
                    if len(embedding) > 1024:
                        embedding = embedding[:1024]
                    # 如果维度小于1024，填充零
                    else:
                        embedding.extend([0.0] * (1024 - len(embedding)))
                    
                print(f"查询嵌入成功，维度: {len(embedding)}")
                return embedding
                
            except Exception as e:
                print(f"嵌入查询时出错 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    print("达到最大重试次数，返回零向量")
                    return [0.0] * 1024  # 返回1024维的零向量

def create_vector_database(processed_data_path=None, documents=None, test_mode=False):
    """
    Create a vector database from preprocessed documents
    Can directly pass a list of documents or specify the path to preprocessed data
    """
    if documents is None and processed_data_path is not None:
        print(f"Loading preprocessed data from file: {processed_data_path}")
        try:
            with open(processed_data_path, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
            
            print(f"成功加载数据，包含 {len(doc_data)} 个项目")
            
            # 在测试模式下只使用少量文档
            if test_mode:
                doc_data = doc_data[:5]
                print(f"测试模式: 仅使用前 5 个文档")
            
            # Convert JSON data to LangChain Document objects
            documents = []
            for item in doc_data:
                doc = Document(
                    page_content=item["content"],
                    metadata=item["metadata"]
                )
                documents.append(doc)
                
        except Exception as e:
            print(f"加载数据时出错: {str(e)}")
            return None, None
    
    if not documents:
        print("错误: 未提供文档数据")
        return None, None
    
    print(f"Starting to create vector database, document count: {len(documents)}")
    
    # 打印一些文档示例
    for i in range(min(2, len(documents))):
        print(f"\n文档 {i+1} 示例:")
        print(f"内容: {documents[i].page_content[:200]}...")
        print(f"元数据: {documents[i].metadata}")
    
    try:
        # 使用自定义的百炼嵌入类
        print("\n初始化嵌入模型...")
        embeddings = BaiLianEmbeddings()
        
        # 创建向量存储
        persist_directory = "./chroma_db"
        print(f"\n开始创建向量数据库，保存目录: {persist_directory}")
        
        # 如果目录已存在，先删除
        if os.path.exists(persist_directory):
            import shutil
            print(f"删除现有数据库目录: {persist_directory}")
            shutil.rmtree(persist_directory)
        
        print("创建 Chroma 向量数据库...")
        vector_db = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        
        # 持久化数据库
        print("持久化向量数据库...")
        vector_db.persist()
        
        print(f"Vector database created and saved to: {persist_directory}")
        return vector_db, persist_directory
        
    except Exception as e:
        print(f"创建向量数据库时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    processed_data_path = "processed_data/processed_documents.json"
    
    # 设置为 False 以处理所有文档
    test_mode = False
    create_vector_database(processed_data_path=processed_data_path, test_mode=test_mode)