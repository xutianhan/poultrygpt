import json
import csv
import os

def read_qa_from_csv(csv_file):
    """
    从CSV文件读取QA对
    格式：第一列为question, 第二列为answer
    """
    qa_pairs = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        # 跳过第一行（标题行）
        next(reader, None)
        for row in reader:
            # 跳过空行
            if len(row) < 2 or not row[0].strip() or not row[1].strip():
                continue
                
            qa_pairs.append({
                "question": row[0].strip(),
                "answer": row[1].strip()
            })
    return qa_pairs

def load_synonyms(synonyms_file):
    """
    从TXT文件加载同义词表
    格式：每行用制表符(\t)分隔同义词
    """
    synonyms_dict = {}
    if not os.path.exists(synonyms_file):
        print(f"同义词文件不存在: {synonyms_file}")
        return synonyms_dict
        
    with open(synonyms_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  # 跳过空行和注释行
                continue
                
            terms = line.split("\t")
            if len(terms) < 2:  # 至少需要两个词
                continue
                
            # 以第一个词为主键，所有词为值
            primary_term = terms[0]
            synonyms_dict[primary_term] = terms
    
    return synonyms_dict

def get_synonyms_for_question(question, synonyms_dict):
    """
    为问题生成同义词列表
    """
    synonyms = []
    for primary_term, term_list in synonyms_dict.items():
        # 如果主键词出现在问题中，添加所有同义词
        if primary_term in question:
            # 添加除主键词外的其他同义词
            synonyms.extend([term for term in term_list if term != primary_term])
            
            # 添加同义词组合（可选）
            if len(term_list) > 1:
                for term in term_list[1:]:
                    # 用同义词替换主键词生成新的问题变体
                    new_question = question.replace(primary_term, term)
                    if new_question != question:
                        synonyms.append(new_question)
    return list(set(synonyms))  # 去重

def generate_parent_child_docs(csv_file, synonyms_file, output_file="dify_knowledge.jsonl", category="家禽养殖"):
    """
    生成父子文档模式的JSONL文件
    """
    # 1. 从CSV读取QA对
    qa_pairs = read_qa_from_csv(csv_file)
    if not qa_pairs:
        print("未读取到有效的QA对")
        return
        
    # 2. 加载同义词表
    synonyms_dict = load_synonyms(synonyms_file)
    
    # 3. 生成知识库文件
    with open(output_file, "w", encoding="utf-8") as f:
        for idx, qa in enumerate(qa_pairs):
            # 为每对QA生成唯一ID前缀
            doc_id_prefix = f"doc_{idx}"
            
            # 获取问题的同义词
            synonyms = get_synonyms_for_question(qa["question"], synonyms_dict)
            
            # ===== 父文档（问题） =====
            parent_doc = {
                "content": qa["question"],
                "metadata": {
                    "doc_id": f"{doc_id_prefix}_parent",
                    "doc_type": "parent",
                    "child_id": f"{doc_id_prefix}_child",
                    "source": "家禽养殖知识库",
                    "category": category,
                    "synonyms": synonyms
                }
            }
            f.write(json.dumps(parent_doc, ensure_ascii=False) + "\n")
            
            # ===== 子文档（答案） =====
            child_doc = {
                "content": qa["answer"],
                "metadata": {
                    "doc_id": f"{doc_id_prefix}_child",
                    "doc_type": "child",
                    "parent_id": f"{doc_id_prefix}_parent",
                    "source": "家禽养殖知识库",
                    "category": category,
                    "answer_length": len(qa["answer"])
                }
            }
            f.write(json.dumps(child_doc, ensure_ascii=False) + "\n")
    
    print(f"已生成父子文档知识库文件: {output_file}")
    print(f"共包含 {len(qa_pairs)} 个问题 和 {len(qa_pairs)} 个答案")
    print(f"使用同义词表: {synonyms_file} (包含 {len(synonyms_dict)} 组同义词)")
    return output_file

if __name__ == "__main__":
    # 配置参数
    CSV_FILE = "qa_pairs_output.csv"  # 输入的CSV文件
    SYNONYMS_FILE = "poultry_synonyms.txt"  # 同义词表文件
    OUTPUT_FILE = "poultry_qa_knowledge.jsonl"  # 输出文件
    CATEGORY = "饲料知识"  # 知识分类
    
    # 生成知识库
    jsonl_file = generate_parent_child_docs(
        csv_file=CSV_FILE,
        synonyms_file=SYNONYMS_FILE,
        output_file=OUTPUT_FILE,
        category=CATEGORY
    )
    
    # 打印下一步操作指南
    print("\n下一步操作:")
    print(f"1. 登录Dify控制台，创建知识库")
    print(f"2. 上传 {jsonl_file} 文件")
    print(f"3. 在知识库设置中启用父子文档模式")
    print("4. 配置父子关系字段:")
    print("   - 父文档ID字段: metadata.doc_id")
    print("   - 子文档ID字段: metadata.doc_id")
    print("   - 父→子关联字段: metadata.child_id")
    print("   - 子→父关联字段: metadata.parent_id")
