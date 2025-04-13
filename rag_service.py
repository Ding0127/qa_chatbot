import os
from langchain_community.vectorstores import Chroma
from create_vectordb import BaiLianEmbeddings
from generate_data import get_answers_gpt, stream_response
from prompt import basic_prompt


class RagService:
    def __init__(self):
        # init
        # 加载已创建的向量数据库
        os.environ['DASHSCOPE_API_KEY'] = "sk-e3e79f4c089f4442a87facc3910f2e7c"
        self.persist_directory = "./chroma_db"
        self.NO_RESULTS_MSG = "This question is out of what we have taught in class. You may ask questions related to what we have learnt."
        # 添加相似度阈值
        self.similarity_threshold = 0.7

        # 使用与创建时相同的嵌入模型
        self.embeddings = BaiLianEmbeddings()

        # 加载向量数据库
        self.vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

    def retrieve(self, age_group, query):
        # 使用similarity_search_with_score来获取相似度分数
        results_with_scores = self.vector_db.similarity_search_with_score(
            query, 
            k=3,  # 返回前3个最相关的结果
        )

        # 显示搜索结果
        print("#---# Retrieve:")
        print(f"找到 {len(results_with_scores)} 个结果:")
        
        # 过滤掉相似度低于阈值的结果
        filtered_results = []
        for i, (doc, score) in enumerate(results_with_scores):
            # 注意：某些向量库的分数可能是距离而非相似度，需要转换
            # 这里假设score是距离（越小越好），转换为相似度（越大越好）
            similarity = 1.0 / (1.0 + score)  # 简单转换示例，根据实际情况调整
            
            print(f"-结果 {i+1}:")
            print(f"\t主题: {doc.metadata.get('topic', '未知')}")
            print(f"\t年龄段: {doc.metadata.get('age_group', '未知')}")
            print(f"\t问题: {doc.metadata.get('question', '未知')}")
            print(f"\t相似度: {similarity:.4f}")
            print(f"\t内容: {doc.page_content[:300]}...")
            
            if similarity >= self.similarity_threshold:
                filtered_results.append(doc)
        
        return filtered_results
    
    def generate(self, age_group, context, query):
        # 组合prompt
        context = basic_prompt.format(age_group=age_group, context=context, query=query)
        print("#---# Generate Context:\n", context)
        # call LLM
        print("#---# Generate:\n")
        return stream_response(context)

    
    def rag(self, age_group, query):
        retrieve_results = self.retrieve(age_group, query)
        if len(retrieve_results) == 0:
            yield self.NO_RESULTS_MSG
            return

        # the most related result
        context = retrieve_results[0].page_content
        for response in self.generate(age_group, context, query):    
            yield response
            



if __name__ == "__main__":
    rag = RagService()
    rag.rag("Kindergarten", "What is the process of plant growth?")