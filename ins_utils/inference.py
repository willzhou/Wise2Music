# Author: Ningbo Wise Effects, Inc. (汇视创影) & Will Zhou
# License: Apache 2.0

import os
import subprocess
from pathlib import Path
import logging
import tempfile
import json
from datetime import datetime
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 模型路径配置
MODEL_PATHS = {
    "InspireMusic-1.5B-Long": "../../pretrained_models/InspireMusic-1.5B-Long",
    "InspireMusic-700M": "../../pretrained_models/InspireMusic-700M"
}

def _generate_segment(
    model_name: str,
    model_dir: str,
    text: str,
    task: str,
    chorus: str,
    time_start: float,
    time_end: float,
    output_dir: Path,
    output_fn: str,
    output_format: str,
    fast: bool,
    gpu: int,
    output_sample_rate: int,
    fade_out: bool,
    fade_out_duration: float,
    trim: bool,
    fp16: bool,
    min_generate_audio_seconds: float = 10.0,
    max_generate_audio_seconds: float = 30.0,
    audio_prompt = None
) -> Path:
    """生成单个音乐段落"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        prompt_file = Path(tmp_dir) / "prompt.txt"
        with open(prompt_file, "w") as f:
            f.write(text)
        
        cmd = [
            "python", "-m", "inspiremusic.cli.inference",
            "--task", task,
            "-m", model_name,
            "--model_dir", model_dir,
            "-t", str(prompt_file),
            "-c", chorus,
            "-s", str(time_start),
            "-e", str(time_end),
            "--output_sample_rate", str(output_sample_rate),
            "--result_dir", str(output_dir),
            "--output_fn", str(output_fn),
            "--format", output_format,
            "--min_generate_audio_seconds", str(min_generate_audio_seconds),
            "--max_generate_audio_seconds", str(max_generate_audio_seconds),
            "--gpu", str(gpu),
            "--fp16", str(fp16)
        ]
        
        if audio_prompt:
            cmd.extend(["--audio_prompt", str(audio_prompt)])
        if fast:
            cmd.append("--fast True")
        if fade_out:
            cmd.extend(["--fade_out", "True", "--fade_out_duration", str(fade_out_duration)])
        if trim:
            cmd.append("--trim True")
        
        logger.info(f"Generating segment: {task} {chorus} ({time_start}-{time_end}s)")
        subprocess.run(cmd, check=True)
        
        output_files = list(output_dir.glob(f"*.{output_format}"))
        if not output_files:
            raise RuntimeError(f"No {output_format} file generated for segment")
        return output_files[0]

def _merge_audio(audio_files: list, output_file: Path, output_format: str):
    """合并音频文件"""
    if len(audio_files) == 1:
        audio_files[0].rename(output_file)
        return
    
    list_file = output_file.with_suffix('.txt')
    with open(list_file, 'w') as f:
        for file in audio_files:
            f.write(f"file '{file.absolute()}'\n")
    
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_file)
    ]
    
    logger.info(f"Merging {len(audio_files)} segments into {output_file}")
    subprocess.run(cmd, check=True)
    
    list_file.unlink()
    for file in audio_files:
        file.unlink()

def generate_music(
    model_name: str,
    text: str,
    task: str = "text-to-music",
    chorus: str = "intro",
    time_start: float = 0.0,
    time_end: float = 30.0,
    min_generate_audio_seconds: float = 10.0,
    max_generate_audio_seconds: float = 30.0,
    fast: bool = False,
    gpu: int = 0,
    output_sample_rate: int = 48000,
    format: str = "wav",
    fade_out: bool = True,
    fade_out_duration: float = 1.0,
    trim: bool = False,
    fp16: bool = True,
    audio_prompt = None
) -> str:
    """生成音乐（支持单段落或多段落JSON）"""
    # 检查是否是JSON格式
    try:
        music_data = json.loads(text)
        logger.info(music_data)
        is_json = True
    except json.JSONDecodeError:
        music_data = None
        is_json = False
    
    # 准备输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_fn = f"generated_music_{timestamp}.{format}"

    # 单段落生成
    if not is_json:
        audio_file = _generate_segment(
            model_name=model_name,
            model_dir=MODEL_PATHS[model_name],
            text=text,
            task=task,
            chorus=chorus,
            time_start=time_start,
            time_end=time_end,
            output_dir=output_dir,
            output_fn=output_fn,
            output_format=format,
            min_generate_audio_seconds=min_generate_audio_seconds,
            max_generate_audio_seconds=max_generate_audio_seconds,
            fast=fast,
            gpu=gpu,
            output_sample_rate=output_sample_rate,
            fade_out=fade_out,
            fade_out_duration=fade_out_duration,
            trim=trim,
            fp16=fp16
        )
        return str(audio_file)
    
    # 多段落JSON生成
    output_dir = output_dir / f"generated_music_{timestamp}"
    output_dir.mkdir(exist_ok=True)
    final_output = output_dir / f"generated_music_{timestamp}.{format}"
    audio_segments = []
    tags = {"intro", "verse", "chorus", "bridge", "outro","random"}

    segment_task = task
    for i, section in music_data.items():
        output_fn = f"generated_music_{timestamp}_{str(i)}"
        try:
            descriptions = [
                s for s in re.findall(r'<\|([^<>]+)\|>', section)
                if not s.replace('.', '').isdigit()
                and not s.strip().lower() in tags
            ]
            text = ".".join(descriptions)
        except:
            text = section
        try:
            chorus_matches = re.findall(r'<\|([^<>]+)\|>', section)
            chorus_i = [s for s in chorus_matches if s.lower() in tags][0]
            new_time_start = re.search(r'\|(\d+\.\d+)\|', section).group(1)
            new_time_end = re.findall(r'\|(\d+\.\d+)\|', section)[-1]
        except:
            new_time_start = time_start
            new_time_end = time_end
            chorus_i = "intro"
        logger.info(f"segment_task: {segment_task}")
        segment = _generate_segment(
            model_name=model_name,
            model_dir=MODEL_PATHS[model_name],
            text=text,
            audio_prompt=audio_segments[-1] if audio_segments else audio_prompt,
            task=segment_task,
            chorus=chorus_i if chorus_i else chorus,
            time_start=new_time_start,
            time_end=new_time_end,
            output_dir=output_dir,
            output_fn=output_fn,
            output_format=format,
            min_generate_audio_seconds=min_generate_audio_seconds,
            max_generate_audio_seconds=float(new_time_end)-float(new_time_start),
            fast=fast,
            gpu=gpu,
            output_sample_rate=output_sample_rate,
            fade_out=False, # no fade_out
            fade_out_duration=fade_out_duration,
            trim=trim,
            fp16=fp16
        )
        segment_task = "continuation"
        audio_segments.append(segment)
    
    _merge_audio(audio_segments, final_output, format)
    return str(final_output)
