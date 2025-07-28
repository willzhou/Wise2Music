# Author: Ningbo Wise Effects, Inc. (汇视创影) & Will Zhou
# License: Apache 2.0

import os
import streamlit as st
from ins_utils.inference import generate_music
from ins_utils.deepseek import generate_text_prompt
import time
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="Wise2Music - An AI Music Generator",
    page_icon="🎵",
    layout="wide"
)

# 初始化session state
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'ai_prompt' not in st.session_state:
    st.session_state.ai_prompt = ""

# 侧边栏配置
with st.sidebar:
    st.title("Settings")
    model_name = st.selectbox(
        "Model",
        ["InspireMusic-1.5B-Long", "InspireMusic-700M"],
        index=0
    )
    
    task = st.selectbox(
        "Task",
        ["text-to-music", "continuation"],
        index=0
    )
    
    chorus_type = st.selectbox(
        "Music Section",
        ["intro", "verse", "chorus", "outro", "random"],
        index=0
    )
    
    duration = st.slider(
        "Duration (seconds)",
        min_value=5.0,
        max_value=180.0,
        value=30.0,
        step=5.0
    )
    
    quality_mode = st.radio(
        "Quality Mode",
        ["High Quality", "Fast Generation"],
        index=0
    )
    
    output_format = st.selectbox(
        "Output Format",
        ["wav", "mp3", "flac"],
        index=0
    )
    
    fade_out = st.checkbox("Fade Out", value=True)
    fade_duration = st.slider(
        "Fade Duration (seconds)",
        min_value=0.5,
        max_value=3.0,
        value=1.0,
        step=0.5,
        disabled=not fade_out
    )

# 主界面
st.title("Wise2Music")
st.write("Generate high-quality music from text prompts using AI")

# AI Prompt Assistant区域 - 上方
st.subheader("AI Prompt Assistant")

# 主题输入框
theme = st.text_input(
    "Theme/Subject (Optional)",
    placeholder="e.g. 'A day at the beach', 'Space exploration', 'Romantic sunset'",
    help="Optional: Describe the theme or subject you want the music to convey"
)
 
# 三列布局
col1, col2, col3 = st.columns(3)
 
with col1:
    style = st.selectbox(
        "Music Style",
        ["Jazz", "Classical", "Electronic", "Pop", "Rock", "Hip-hop", "Custom"],
        index=0
    )
    if style == "Custom":
        custom_style = st.text_input("Custom Style")
 
with col2:
    mood = st.selectbox(
        "Mood",
        ["Happy", "Sad", "Energetic", "Relaxing", "Romantic", "Mysterious", "Custom"],
        index=0
    )
    if mood == "Custom":
        custom_mood = st.text_input("Custom Mood")
 
with col3:
    situation = st.selectbox(
        "Use Case",
        ["Background Music", "Dancing", "Meditation", "Studying", "Gaming", "Custom"],
        index=0
    )
    if situation == "Custom":
        custom_situation = st.text_input("Custom Use Case")
 
ai_help_btn = st.button(
    "Generate Description",
    help="Let AI help you create a better music description",
    type="primary"
)
 
if ai_help_btn:
    with st.spinner("Generating music description..."):
        try:
            # 准备参数
            kwargs = {
                "style": style,
                "mood": mood,
                "situation": situation,
                "theme": theme if theme else None
            }
            
            # 添加自定义字段
            if style == "Custom" and 'custom_style' in locals():
                kwargs["custom_style"] = custom_style
            if mood == "Custom" and 'custom_mood' in locals():
                kwargs["custom_mood"] = custom_mood
            if situation == "Custom" and 'custom_situation' in locals():
                kwargs["custom_situation"] = custom_situation
            
            result = generate_text_prompt(**kwargs)
            st.info(result)

            st.session_state.ai_prompt = result

        except Exception as e:
            st.error(f"Failed to generate prompt: {str(e)}")

# 分割线
st.divider()

# 音乐生成区域 - 下方
st.subheader("Music Generation")

# 文本输入区域
prompt = st.text_area(
    "Music Description (Edit if needed)",
    value=st.session_state.ai_prompt if st.session_state.ai_prompt else "",
    height=150,
    placeholder="Describe the music you want to generate or use the AI-generated description above",
    key="music_prompt_input"
)

# 高级选项
with st.expander("Advanced Options"):
    min_duration = st.slider(
        "Minimum Duration (seconds)",
        min_value=5.0,
        max_value=30.0,
        value=10.0,
        step=1.0
    )
    
    sample_rate = st.selectbox(
        "Sample Rate",
        [24000, 48000],
        index=1,
        help="Higher sample rate = better quality but larger file size"
    )
    
    trim_silence = st.checkbox("Trim Silence", value=False)
    
    gpu_id = st.number_input(
        "GPU ID",
        min_value=-1,
        max_value=7,
        value=0,
        help="-1 for CPU, 0-7 for GPU index"
    )

# 生成按钮
generate_btn = st.button(
    "Generate Music",
    type="primary",
    disabled=not prompt,
    help="Enter a music description or use the AI assistant above" if not prompt else None
)

# 生成音乐逻辑
if generate_btn and prompt:
    with st.spinner(f"Generating {duration} seconds of music..."):
        start_time = time.time()
        
        # 检查是否是JSON格式
        try:
            json.loads(prompt)
            is_json = True
        except:
            is_json = False
        
        # 准备参数
        params = {
            "model_name": model_name,
            "text": prompt,
            "task": task,
            "chorus": chorus_type if not is_json else None,
            "time_start": 0.0 if not is_json else None,
            "time_end": duration if not is_json else None,
            "min_generate_audio_seconds": min_duration,
            "max_generate_audio_seconds": duration,
            "fast": quality_mode == "Fast Generation",
            "gpu": gpu_id,
            "output_sample_rate": sample_rate,
            "format": output_format,
            "fade_out": fade_out,
            "fade_out_duration": fade_duration,
            "trim": trim_silence,
            "fp16": True
        }
        
        # 调用生成函数
        try:
            audio_file = generate_music(**params)
            st.session_state.generated = True
            st.session_state.audio_file = audio_file
            st.session_state.generation_time = time.time() - start_time
            st.session_state.used_prompt = prompt
            
            # 显示JSON格式提示
            if is_json:
                st.info("Detected JSON format - generating multi-segment music")
        except Exception as e:
            st.error(f"Error generating music: {str(e)}")

# 显示生成结果
if st.session_state.get("generated", False):
    st.success("Music generated successfully!")
    st.audio(st.session_state.audio_file, format=f"audio/{output_format}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download Music",
            data=open(st.session_state.audio_file, "rb"),
            file_name=f"generated_music.{output_format}",
            mime=f"audio/{output_format}"
        )
    
    with col2:
        st.write(f"Generation time: {st.session_state.generation_time:.2f} seconds")
    
    st.divider()
    st.subheader("Generation Parameters")
    st.json({
        "prompt": st.session_state.used_prompt,
        "model": model_name,
        "duration": f"{duration} seconds",
        "quality": quality_mode,
        "sample_rate": f"{sample_rate} Hz",
        "format": output_format
    })
