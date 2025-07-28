import requests
import time

# 更新后的API路径
url = "http://175.27.253.234:8000/api/chat/diagnose"

# 初始化用户和会话ID
user_id = "test_user_123"
session_id = "test_session_456"

# 第一轮对话
data1 = {
    "user_id": user_id,
    "session_id": session_id,
    "query": "鸡出现咳嗽和流鼻涕的症状",
    "intent": "diagnose",
    "entities": ["咳嗽", "流鼻涕"]
}

# 第二轮对话
data2 = {
    "user_id": user_id,
    "session_id": session_id,
    "query": "眼睑水肿和流泪",
    "intent": "diagnose",
    "entities": ["眼睑水肿", "流泪"]
}

# 第三轮对话
data3 = {
    "user_id": user_id,
    "session_id": session_id,
    "query": "鸡冠肿胀",
    "intent": "diagnose",
    "entities": ["鸡冠肿胀"]
}

# 发送请求并处理响应
def send_request(data):
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        print("请检查网页链接的合法性，适当重试。")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")

# 模拟多轮对话
def multi_round_conversation():
    # 第一轮对话
    print("第一轮对话：")
    response1 = send_request(data1)
    print("Response 1:", response1)
    if response1 and response1.get("need_clarify"):
        print("系统提示：", response1.get("reply"))
    
    # 等待用户响应（模拟）
    time.sleep(2)
    
    # 第二轮对话
    print("\n第二轮对话：")
    response2 = send_request(data2)
    print("Response 2:", response2)
    if response2 and response2.get("need_clarify"):
        print("系统提示：", response2.get("reply"))
    
    # 等待用户响应（模拟）
    time.sleep(2)
    
    # 第三轮对话
    print("\n第三轮对话：")
    response3 = send_request(data3)
    print("Response 3:", response3)
    if response3 and response3.get("diagnosed"):
        print("最终诊断：", response3.get("reply"))

# 运行多轮对话测试用例
multi_round_conversation()
