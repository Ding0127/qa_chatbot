import os
from langchain_community.vectorstores import Chroma
from create_vectordb import BaiLianEmbeddings

def test_vector_database_by_age(query, age_group=None):
    """
    测试向量数据库，可以指定年龄段进行过滤
    
    参数:
    query (str): 查询问题
    age_group (str, optional): 年龄段过滤，可选值: "Kindergarten", "P1-P3", "P4-P6"
    """
    print("开始测试向量数据库...")
    
    # 加载已创建的向量数据库
    persist_directory = "./chroma_db"
    
    # 使用与创建时相同的嵌入模型
    embeddings = BaiLianEmbeddings()
    
    # 加载向量数据库
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    # 获取数据库中的文档数量
    collection = vector_db.get()
    doc_count = len(collection['ids']) if 'ids' in collection else 0
    print(f"向量数据库中共有 {doc_count} 个文档")
    
    # 测试相似性搜索
    print(f"测试查询: '{query}'")
    
    # 如果指定了年龄段，添加过滤条件
    if age_group:
        print(f"过滤年龄段: {age_group}")
        # 使用元数据过滤
        filter_dict = {"age_group": age_group}
        
        # 执行相似性搜索，带过滤
        results = vector_db.similarity_search(
            query, 
            k=3,  # 返回前3个最相关的结果
            filter=filter_dict
        )
    else:
        # 不过滤，搜索所有文档
        results = vector_db.similarity_search(
            query, 
            k=3  # 返回前3个最相关的结果
        )
    
    # 显示搜索结果
    print(f"\n找到 {len(results)} 个相关结果:")
    
    for i, doc in enumerate(results):
        print(f"\n结果 {i+1}:")
        print(f"主题: {doc.metadata.get('topic', '未知')}")
        print(f"年龄段: {doc.metadata.get('age_group', '未知')}")
        print(f"问题: {doc.metadata.get('question', '未知')}")
        print(f"内容: {doc.page_content[:300]}...")
    
    print("\n向量数据库测试完成!")
    return results

if __name__ == "__main__":
    # 测试不同的查询和年龄段组合
    
    # 测试1: 科学问题，不指定年龄段
    print("\n===== 测试1: 科学问题，不指定年龄段 =====")
    test_vector_database_by_age("Why sky is blue?")
    
    # 测试2: 科学问题，指定幼儿园年龄段
    print("\n===== 测试2: 科学问题，指定幼儿园年龄段 =====")
    test_vector_database_by_age("How do plants grow?", age_group="Kindergarten")
    
    # 测试3: 科学问题，指定高年级年龄段
    print("\n===== 测试3: 科学问题，指定高年级年龄段 =====")
    test_vector_database_by_age("How do plants grow?", age_group="P4-P6")
    
    # 测试4: 技术问题，指定中年级年龄段
    print("\n===== 测试4: 技术问题，指定中年级年龄段 =====")
    test_vector_database_by_age("What is programming?", age_group="P1-P3")
    
    # 测试5: 自定义查询
    custom_query = input("\n请输入您想测试的问题: ")
    age_options = ["不过滤", "Kindergarten", "P1-P3", "P4-P6"]
    
    print("请选择年龄段过滤:")
    for i, option in enumerate(age_options):
        print(f"{i}. {option}")
    
    age_choice = int(input("请输入选项编号 (0-3): "))
    selected_age = None if age_choice == 0 else age_options[age_choice]
    
    print(f"\n===== 测试自定义查询: {custom_query} =====")
    test_vector_database_by_age(custom_query, age_group=selected_age) 