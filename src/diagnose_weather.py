import requests
import sys

def diagnose():
    url = "https://wttr.in/?format=%c+%t"
    print(f"--- 正在连接: {url} ---")
    
    try:
        # 测试直接连接
        print("1. 尝试直接连接...")
        r = requests.get(url, timeout=5)
        print(f"状态码: {r.status_code}")
        print(f"内容: {r.text}")
    except Exception as e:
        print(f"直接连接失败: {e}")

    try:
        # 测试使用代理 (考虑到您的项目背景中提到了 127.0.0.1:7890)
        print("\n2. 尝试使用代理 (127.0.0.1:7890)...")
        proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        }
        r = requests.get(url, proxies=proxies, timeout=5)
        print(f"状态码: {r.status_code}")
        print(f"内容: {r.text}")
    except Exception as e:
        print(f"代理连接失败: {e}")

if __name__ == "__main__":
    diagnose()
