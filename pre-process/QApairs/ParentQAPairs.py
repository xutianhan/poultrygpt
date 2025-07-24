import re
import json
import csv

def extract_title_qa(md_content):
    """
    提取Markdown中的标题作为问题(question)，标题后的内容作为答案(answer)
    返回格式: [{"question": "标题", "answer": "内容"}, ...]
    """
    qa_pairs = []
    sections = re.split(r'(^#+\s+.+?$)', md_content, flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip()]

    for i in range(0, len(sections), 2):
        if i + 1 < len(sections):
            header = sections[i]
            content = sections[i + 1]
            title_match = re.match(r'^#+\s*(\d+\.\s*)?(.+?)\??$', header)
            if title_match:
                question = title_match.group(2).strip()
                if not question.endswith('?'):
                    question += '？'
                qa_pairs.append({
                    "question": question,
                    "answer": content
                })
    return qa_pairs

def clean_text(text):
    """清理文本中的特殊字符"""
    text = text.replace("\t", " ").replace("\n", " ").replace("\r", " ").strip()
    return re.sub(r'\s+', ' ', text)

def save_as_txt(qa_pairs, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("question\tanswer\n")
        for qa in qa_pairs:
            q = clean_text(qa["question"])
            a = clean_text(qa["answer"])
            f.write(f"{q}\t{a}\n")
    print(f"QA对已保存为 TXT 格式: {filename}")

def save_as_json(qa_pairs, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
    print(f"QA对已保存为 JSON 格式: {filename}")

def save_as_csv(qa_pairs, filename):
    with open(filename, "w", encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["question", "answer"])
        for qa in qa_pairs:
            q = clean_text(qa["question"])
            a = clean_text(qa["answer"])
            writer.writerow([q, a])
    print(f"QA对已保存为 CSV 格式: {filename}")

if __name__ == "__main__":
    # 读取 Markdown 文件
    with open("PoultryFarmingQA2.md", "r", encoding="utf-8") as f:
        md_content = f.read()

    qa_pairs = extract_title_qa(md_content)

    # 分别保存为三种格式
    save_as_txt(qa_pairs, "qa_pairs_output_2.txt")
    save_as_json(qa_pairs, "qa_pairs_output_2.json")
    save_as_csv(qa_pairs, "qa_pairs_output_2.csv")
