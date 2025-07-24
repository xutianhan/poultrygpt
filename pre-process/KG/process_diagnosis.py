import csv
import re
import uuid
from collections import defaultdict
import pandas as pd

def clean_text(text):
    """深度清洗并标准化文本"""
    if not text or text.strip() == "":
        return []
    
    # 处理特殊格式：引号内的内容保持完整
    text = re.sub(r'\"(.*?)\"', lambda m: m.group(1).replace('，', ';'), text)
    
    # 标准化分隔符（保留数字范围如"1-3周"）
    text = re.sub(r'([^0-9])-([^0-9])', r'\1;\2', text)
    text = text.replace('、', ',')
    
    # 按中文标点分割，但保持括号内的内容完整
    segments = []
    buffer = ""
    inside_parentheses = 0
    
    for char in text:
        if char in '([{（【「':
            inside_parentheses += 1
        elif char in ')]}）】」':
            inside_parentheses -= 1
        
        if inside_parentheses == 0 and char in '；。，,;':
            if buffer.strip():
                segments.append(buffer.strip())
                buffer = ""
            continue
        
        buffer += char
    
    if buffer.strip():
        segments.append(buffer.strip())
    
    # 进一步分割长段落
    final_segments = []
    for segment in segments:
        segment = re.sub(r'[,;，；]{2,}', ';', segment)
        
        if '和' in segment or '或' in segment or '以及' in segment:
            sub_segments = re.split(r'和|或|以及|同时', segment)
            final_segments.extend([s.strip() for s in sub_segments if s.strip()])
        else:
            final_segments.append(segment)
    
    return [s for s in final_segments if s and len(s) > 1]

def classify_feature(feature_text):
    """智能分类特征类型"""
    type_patterns = {
        'symptom': r'症状|表现|可见|出现|显示|肿胀|出血|流泪|呼吸困难|稀粪|腹泻|跛行|麻痹|瘫痪|震颤|抽搐',
        'pathology': r'剖检|病理|肝脏|肠道|心脏|肺|肾脏|法氏囊|肿瘤|结节|出血|坏死|溃疡|病变|气囊|腺胃|盲肠|脾脏|卵巢|输卵管',
        'age_feature': r'周龄|日龄|雏鸡|青年鸡|成年鸡|育成鸡|产蛋期|高峰期|雏鸭|雏鹅|母鸭|种鸡',
        'lab_feature': r'镜检|涂片|染色|检测|试验|诊断|PCR|分离|培养|药敏|凝集|电镜',
        'treatment': r'治疗|药物|剂量|方案|用药|注射|口服|饮水|拌料|疗程|抗生素|磺胺|疫苗|免疫|接种',
        'prevention': r'预防|免疫|疫苗|措施|管理|消毒|通风|温度|湿度|饲养|营养|饲料|净化|控制',
        'epidemiology': r'传播|感染|发病率|死亡率|高发|流行|暴发|传染|接触|空气|垂直|水平',
        'clinical_sign': r'触诊|听诊|叩诊|视诊|体温|剖检|解剖|观察|检查|诊断|鉴别'
    }
    
    for ftype, pattern in type_patterns.items():
        if re.search(pattern, feature_text):
            return ftype
    
    if re.search(r'\d+[~-]\d+周龄|\d+日龄|\d+周龄', feature_text):
        return 'age_feature'
    if re.search(r'\d+%|比例|浓度|ppm|mg/kg|ml/L', feature_text):
        return 'treatment'
    if re.search(r'病毒|细菌|寄生虫|支原体|霉菌|病原', feature_text):
        return 'pathology'
    
    return 'other'

def process_diagnosis_data(input_file):
    # 存储处理后的数据
    diseases = {}  # diseaseName: diseaseID
    features = {}  # featureName: featureID
    disease_data = []
    feature_data = []
    relation_data = []
    
    # 生成疾病ID映射
    disease_id_map = {}
    feature_id_map = {}
    
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            disease_name = row['病名'].strip()
            if not disease_name:
                continue
                
            # 为疾病生成唯一ID（如果不存在）
            if disease_name not in disease_id_map:
                disease_id = f"disease_{str(uuid.uuid4())[:8]}"
                disease_id_map[disease_name] = disease_id
                # 疾病属性（可扩展）
                disease_data.append({
                    'diseaseID': disease_id,
                    'diseaseName': disease_name,
                    'diseaseProperty': '禽病实体'
                })
            
            # 处理相似点
            similar_points = clean_text(row.get('相似点', ''))
            for point in similar_points:
                if point not in feature_id_map:
                    feature_id = f"feature_{str(uuid.uuid4())[:8]}"
                    feature_id_map[point] = feature_id
                    feature_type = classify_feature(point)
                    feature_data.append({
                        'featureID': feature_id,
                        'featureName': point,
                        'featureProperty': feature_type
                    })
                
                relation_data.append({
                    'diseaseID': disease_id_map[disease_name],
                    'featureID': feature_id_map[point],
                    'operation': 'diagnose',
                    'groupType': 'similar'
                })
            
            # 处理区别点
            different_points = clean_text(row.get('区别点', ''))
            for point in different_points:
                if point not in feature_id_map:
                    feature_id = f"feature_{str(uuid.uuid4())[:8]}"
                    feature_id_map[point] = feature_id
                    feature_type = classify_feature(point)
                    feature_data.append({
                        'featureID': feature_id,
                        'featureName': point,
                        'featureProperty': feature_type
                    })
                
                relation_data.append({
                    'diseaseID': disease_id_map[disease_name],
                    'featureID': feature_id_map[point],
                    'operation': 'diagnose',
                    'groupType': 'different'
                })
    
    return disease_data, feature_data, relation_data

def save_to_csv(data, filename, fieldnames):
    """保存数据到CSV文件"""
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"已保存 {len(data)} 条记录到 {filename}")

# 执行处理
if __name__ == "__main__":
    input_csv = "鸡病鉴别诊断.csv"
    
    # 处理数据
    disease_data, feature_data, relation_data = process_diagnosis_data(input_csv)
    
    # 保存疾病实体文件
    save_to_csv(disease_data, "disease.csv", 
                ['diseaseID', 'diseaseName', 'diseaseProperty'])
    
    # 保存特征实体文件
    save_to_csv(feature_data, "feature.csv", 
                ['featureID', 'featureName', 'featureProperty'])
    
    # 保存关系文件
    save_to_csv(relation_data, "relation.csv", 
                ['diseaseID', 'featureID', 'operation', 'groupType'])
    
    # 生成统计报告
    print("\n数据处理统计:")
    print("=" * 60)
    print(f"疾病数量: {len(disease_data)}")
    print(f"特征数量: {len(feature_data)}")
    print(f"关系数量: {len(relation_data)}")
    
    # 特征类型分布
    feature_types = defaultdict(int)
    for feature in feature_data:
        feature_types[feature['featureProperty']] += 1
    
    print("\n特征类型分布:")
    for ftype, count in sorted(feature_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ftype.upper():<15}: {count} 条")
    
    # 关系类型分布
    group_types = defaultdict(int)
    for relation in relation_data:
        group_types[relation['groupType']] += 1
    
    print("\n关系类型分布:")
    for gtype, count in group_types.items():
        print(f"  {gtype.upper():<15}: {count} 条")
    
    # 每个疾病的特征数量
    disease_features = defaultdict(int)
    for relation in relation_data:
        disease_features[relation['diseaseID']] += 1
    
    print("\n疾病特征数量TOP5:")
    sorted_diseases = sorted(disease_features.items(), key=lambda x: x[1], reverse=True)[:5]
    for disease_id, count in sorted_diseases:
        disease_name = next(d['diseaseName'] for d in disease_data if d['diseaseID'] == disease_id)
        print(f"  {disease_name:<20}: {count} 个特征")