import json
import csv
import os

def read_qa_from_csv(csv_file):
    """
    从CSV文件读取QA对
    格式：第一列为question, 第二列为answer
    跳过第一行（标题行）
    """
    qa_pairs = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        
        # 跳过第一行（标题行）
        next(reader, None)
        
        for row in reader:
            # 跳过空行和列数不足的行
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

def generate_dify_csv(csv_file, synonyms_file, output_file="dify_knowledge.csv", category="家禽养殖"):
    """
    生成Dify支持的CSV格式知识库文件
    """
    # 1. 从CSV读取QA对
    qa_pairs = read_qa_from_csv(csv_file)
    if not qa_pairs:
        print("未读取到有效的QA对")
        return
        
    print(f"成功读取 {len(qa_pairs)} 个QA对")
    
    # 2. 加载同义词表
    synonyms_dict = load_synonyms(synonyms_file)
    
    # 3. 创建CSV文件
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        
        # 写入CSV表头（Dify要求的格式）
        writer.writerow(["question", "answer", "metadata"])
        
        for idx, qa in enumerate(qa_pairs):
            # 获取问题的同义词
            synonyms = get_synonyms_for_question(qa["question"], synonyms_dict)
            
            # 构建元数据（JSON字符串）
            metadata = {
                "doc_id": f"doc_{idx}",
                "doc_type": "parent",
                "source": "家禽养殖知识库",
                "category": category,
                "synonyms": synonyms
            }
            metadata_str = json.dumps(metadata, ensure_ascii=False)
            
            # 写入行
            writer.writerow([
                qa["question"],  # 问题
                qa["answer"],    # 答案
                metadata_str     # 元数据（JSON格式）
            ])
    
    print(f"已生成Dify知识库文件: {output_file} (CSV格式)")
    print(f"共包含 {len(qa_pairs)} 个QA对")
    print(f"使用同义词表: {synonyms_file} (包含 {len(synonyms_dict)} 组同义词)")
    return output_file

def generate_qa_txt(csv_file, output_file="qa_pairs.txt"):
    """
    生成简单的QA对文本文件（备选方案）
    """
    qa_pairs = read_qa_from_csv(csv_file)
    if not qa_pairs:
        print("未读取到有效的QA对")
        return
        
    with open(output_file, "w", encoding="utf-8") as f:
        for qa in qa_pairs:
            f.write(f"Q: {qa['question']}\n")
            f.write(f"A: {qa['answer']}\n")
            f.write("\n")  # 添加空行分隔
    
    print(f"已生成QA对文本文件: {output_file}")
    return output_file

if __name__ == "__main__":
    # 配置参数
    CSV_FILE = "qa_pairs_output.csv"  # 输入的CSV文件
    SYNONYMS_FILE = "poultry_synonyms.txt"  # 同义词表文件
    OUTPUT_CSV = "qa_pairs_knowledge.csv"  # 输出文件（CSV格式）
    OUTPUT_TXT = "qa_pairs_knowledge.txt"  # 输出文件（TXT格式）
    CATEGORY = "饲料知识"  # 知识分类
    
    print("请选择生成格式（Dify Cloud支持）：")
    print("1. CSV格式（推荐，支持元数据）")
    print("2. TXT格式（简单QA对）")
    choice = input("请输入选项编号 (1/2): ")
    
    if choice == "1":
        # 生成CSV格式知识库
        csv_file = generate_dify_csv(
            csv_file=CSV_FILE,
            synonyms_file=SYNONYMS_FILE,
            output_file=OUTPUT_CSV,
            category=CATEGORY
        )
        
        # 打印下一步操作指南
        print("\n下一步操作:")
        print(f"1. 登录 cloud.dify.ai")
        print(f"2. 创建或选择知识库")
        print(f"3. 点击'上传文件'，选择 {csv_file}")
        print("4. 在导入设置中选择:")
        print("   - 文件类型: CSV")
        print("   - 列映射:")
        print("       问题 -> question")
        print("       答案 -> answer")
        print("       元数据 -> metadata")
        print("5. 点击'确认导入'")
        
    elif choice == "2":
        # 生成TXT格式知识库
        txt_file = generate_qa_txt(
            csv_file=CSV_FILE,
            output_file=OUTPUT_TXT
        )
        
        # 打印下一步操作指南
        print("\n下一步操作:")
        print(f"1. 登录 cloud.dify.ai")
        print(f"2. 创建或选择知识库")
        print(f"3. 点击'上传文件'，选择 {txt_file}")
        print("4. 在导入设置中选择:")
        print("   - 文件类型: 纯文本")
        print("   - 分段规则: 按段落分割（默认）")
        print("5. 点击'确认导入'")
        
    else:
        print("无效选择，程序退出")