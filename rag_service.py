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

        # 使用与创建时相同的嵌入模型
        self.embeddings = BaiLianEmbeddings()

        # 加载向量数据库
        self.vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

    def retrieve(self, age_group, query):
        # 使用元数据过滤
        filter_dict = {"age_group": age_group}
        
        # 执行相似性搜索，带过滤
        results = self.vector_db.similarity_search(
            query, 
            k=3,  # 返回前3个最相关的结果
            filter=filter_dict
        )

        # 显示搜索结果
        print("#---# Retrieve:")
        print(f"找到 {len(results)} 个相关结果:")
        for i, doc in enumerate(results):
            print(f"-结果 {i+1}:")
            print(f"\t主题: {doc.metadata.get('topic', '未知')}")
            print(f"\t年龄段: {doc.metadata.get('age_group', '未知')}")
            print(f"\t问题: {doc.metadata.get('question', '未知')}")
            print(f"\t内容: {doc.page_content[:300]}...")
        
        return results
    
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
            return self.NO_RESULTS_MSG

        # the most related result
        context = retrieve_results[0].page_content
        for response in self.generate(age_group, context, query):    
            yield response
            
        print(response)
        yield response
        



if __name__ == "__main__":
    rag = RagService()
    rag.rag("Kindergarten", "What is the process of plant growth?")