import openai
import re
import json
from tenacity import retry, stop_after_attempt, wait_exponential

# 配置OpenAI
openai.api_key = "YOUR_API_KEY"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_qa_pairs(chunk, model="gpt-4-turbo"):
    """使用LLM生成QA对"""
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个农业技术文档专家，请根据技术文档内容生成高质量的QA对。要求："
                    "1. 生成3-5个用户最可能提出的问题"
                    "2. 答案必须严格来自文档内容"
                    "3. 包含操作步骤、参数数据、注意事项等关键信息"
                    "4. 问题形式多样：是什么/为什么/怎么做/参数要求等"
                    "输出格式：\n"
                    "Q1: 问题文本\nA1: 答案文本\n\n"
                    "Q2: 问题文本\nA2: 答案文本"
                )
            },
            {
                "role": "user",
                "content": f"技术文档内容：\n{chunk}"
            }
        ],
        temperature=0.3,
        max_tokens=1500
    )
    return response.choices[0].message['content'].strip()

def parse_qa_output(output):
    """解析LLM生成的QA文本"""
    qa_pairs = []
    current_q = None
    
    for line in output.split('\n'):
        if line.startswith('Q') and ':' in line:
            # 新问题开始
            if current_q:
                qa_pairs.append({"question": current_q, "answer": current_a})
            _, question = line.split(':', 1)
            current_q = question.strip()
            current_a = ""
        elif line.startswith('A') and ':' in line:
            # 答案行
            _, answer = line.split(':', 1)
            current_a = answer.strip()
        elif current_a is not None:
            # 多行答案
            current_a += "\n" + line.strip()
    
    if current_q and current_a:
        qa_pairs.append({"question": current_q, "answer": current_a})
    
    return qa_pairs

def chunk_markdown(md_content, max_chars=2000):
    """智能分块Markdown文档"""
    chunks = []
    
    # 优先按标题分块
    sections = re.split(r'(^#+ .+$)', md_content, flags=re.MULTILINE)
    sections = [s for s in sections if s.strip()]
    
    current_chunk = ""
    for i, section in enumerate(sections):
        if re.match(r'^#+ ', section):
            # 标题行 - 开始新块
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            current_chunk = section + "\n"
        else:
            # 内容部分
            if len(current_chunk + section) <= max_chars:
                current_chunk += section
            else:
                # 内容过长时按段落分割
                paragraphs = re.split(r'\n\n+', section)
                for para in paragraphs:
                    if len(current_chunk + para) > max_chars:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = para + "\n\n"
                    else:
                        current_chunk += para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def process_markdown(md_content):
    """处理Markdown生成QA pairs"""
    chunks = chunk_markdown(md_content)
    all_qa = []
    
    for i, chunk in enumerate(chunks):
        print(f"处理块 {i+1}/{len(chunks)}，长度: {len(chunk)}字符")
        try:
            qa_output = generate_qa_pairs(chunk)
            qa_pairs = parse_qa_output(qa_output)
            all_qa.extend(qa_pairs)
            print(f"✅ 生成 {len(qa_pairs)} 个QA对")
        except Exception as e:
            print(f"❌ 块 {i+1} 处理失败: {str(e)}")
    
    return all_qa

# 使用示例
if __name__ == "__main__":
    with open("incubation.md", "r", encoding="utf-8") as f:
        md_content = f.read()
    
    qa_pairs = process_markdown(md_content)
    
    # 保存结果
    with open("qa_pairs.json", "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
    
    print(f"共生成 {len(qa_pairs)} 个QA对")