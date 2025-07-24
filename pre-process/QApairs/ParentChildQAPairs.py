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

def generate_qa_txt(csv_file, output_file="qa_pairs.txt"):
    """
    生成指定格式的QA对文本文件
    
    格式：
    [question]问题文本
    [answer]答案文本
    
    [question]下一个问题
    [answer]下一个答案
    """
    qa_pairs = read_qa_from_csv(csv_file)
    if not qa_pairs:
        print("未读取到有效的QA对")
        return
        
    with open(output_file, "w", encoding="utf-8") as f:
        for i, qa in enumerate(qa_pairs):
            # 写入问题
            f.write(f"[question]{qa['question']}\n")
            
            # 写入答案
            f.write(f"[answer]{qa['answer']}\n")
            
            # 在每对QA之间添加空行（除了最后一个）
            if i < len(qa_pairs) - 1:
                f.write("\n")
    
    print(f"已生成QA对文本文件: {output_file}")
    print(f"共包含 {len(qa_pairs)} 个QA对")
    return output_file

def clean_text(text):
    """
    清理文本中的特殊格式
    """
    # 替换Markdown公式标记
    text = text.replace("$", "")
    text = text.replace("\\%", "%")
    text = text.replace("\\sim", "~")
    text = text.replace("^{\\circ}C", "°C")
    
    # 替换特殊符号
    text = text.replace("\\times", "×")
    
    # 删除多余的空白
    text = ' '.join(text.split())
    return text

if __name__ == "__main__":
    # 配置参数
    CSV_FILE = "qa_pairs_output_2.csv"  # 输入的CSV文件
    OUTPUT_FILE = "qa_pairs_knowledge_2.txt"  # 输出文件
    
    # 生成TXT格式知识库
    txt_file = generate_qa_txt(
        csv_file=CSV_FILE,
        output_file=OUTPUT_FILE
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