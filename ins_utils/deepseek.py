# Author: Ningbo Wise Effects, Inc. (汇视创影) & Will Zhou
# License: Apache 2.0

import os
import requests
from typing import Optional

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def generate_text_prompt(
    style: str,
    mood: str,
    situation: str,
    theme: Optional[str] = None,
    custom_style: Optional[str] = None,
    custom_mood: Optional[str] = None,
    custom_situation: Optional[str] = None
) -> str:
    """使用DeepSeek API生成音乐描述文本
    
    参数:
        style: 音乐风格
        mood: 情绪/氛围
        situation: 使用场景
        theme: 用户自定义主题/描述
        custom_style: 自定义风格(当style为Custom时使用)
        custom_mood: 自定义情绪(当mood为Custom时使用)
        custom_situation: 自定义场景(当situation为Custom时使用)
        
    返回:
        生成的音乐描述文本
    """
    if not DEEPSEEK_API_KEY:
        raise ValueError("DeepSeek API key not configured")
    
    # 处理自定义输入
    actual_style = custom_style if style == "Custom" else style
    actual_mood = custom_mood if mood == "Custom" else mood
    actual_situation = custom_situation if situation == "Custom" else situation
    
    # 构建提示
    base_prompt = (
        f"Please generate a music description exactly as per the example for a {actual_style.lower()} "
        f"track that is {actual_mood.lower()} and suitable for {actual_situation.lower()}. "
    )
    
    if theme:
        base_prompt += (
            f"The music should be about: {theme}. "
            "Incorporate this theme creatively into the description. "
        )
    
    prompt = base_prompt + (
        """返回格式必须为JSON格式：
        {
            "1": "<|0.0|><|intro|><|A delightful collection of classical keyboard music, purely instrumental, exuding a timeless and elegant charm.|><|30.0|>",
            "2": "<|30.0|><|verse|><|Experience soothing and sensual instrumental jazz with a touch of Bossa Nova, perfect for a relaxing restaurant or spa ambiance.|><|60.0|>",
            "3": "<|60.0|><|chorus|><|The instrumental rap track exudes a classic boom bap vibe, characterized by its French hip-hop roots and a smooth, rhythmic flow.|><|120.0|>",
            "4": "<|120.0|><|outro|><|The music exudes a vibrant and sophisticated jazz ambiance, characterized by the rich, dynamic sounds of a big band ensemble. With instrumental purity and a touch of classical influence, it offers a captivating listening experience.|><|180.0|>"
        }
        注意：
        1. 必须返回合法JSON
        2. 所有值必须来自给定选项
        3. 不要包含任何额外文字
        """
    )
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a professional music composer assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 3000
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Failed to generate text prompt: {str(e)}")
