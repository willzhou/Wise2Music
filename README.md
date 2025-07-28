# Wise2Music 🎵


一款基于AI模型的网络应用，能够通过文本提示生成高质量音乐。该项目融合了InspireMusic模型的强大音乐生成能力与深度求索（DeepSeek）的文本生成技术，为用户提供流畅的音乐创作体验。

本程序通过调用大语言模型生成提示语文本，然后对文本进行分段执行text-to-music和continuation任务，实现低端显卡也能运行超长音乐生成推理任务。

A web application that generates high-quality music from text prompts using AI models. This project combines the power of InspireMusic models with DeepSeek's text generation capabilities to create a seamless music generation experience.

This application generates prompt text by calling a large language model, then segments the text to perform text-to-music and continuation tasks, enabling low-end graphics cards to handle ultra-long music generation inference tasks.

 ![运行界面](https://raw.githubusercontent.com/willzhou/Wise2Music/main/assets/cmd.png)
 ![首页界面](https://raw.githubusercontent.com/willzhou/Wise2Music/main/assets/home.png)

## Features ✨

- **Text-to-Music Generation**: Convert text descriptions into musical compositions
- **AI-Powered Prompt Assistant**: Get help crafting perfect music descriptions
- **Multi-Segment Music**: Generate complex compositions with intro/verse/chorus/outro sections
- **Customizable Parameters**:
  - Music style (Jazz, Classical, Electronic, etc.)
  - Mood (Happy, Sad, Energetic, etc.)
  - Duration (5-180 seconds)
  - Quality modes (High Quality vs Fast Generation)
  - Output formats (WAV, MP3, FLAC)
- **Advanced Controls**: Sample rate, fade effects, silence trimming, GPU selection

## Installation 🛠️

1. Clone the repository:
   ```bash
   git clone https://github.com/willzhou/wise2music.git
   cd wise2music
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your DeepSeek API key:
     ```
     DEEPSEEK_API_KEY=your_api_key_here
     ```

4. Download the InspireMusic models and place them in the `pretrained_models/` directory:
   - InspireMusic-1.5B-Long
   - InspireMusic-700M

5. Install FFmpeg (required for audio processing):
   ```bash
   # On Ubuntu/Debian
   sudo apt install ffmpeg
   
   # On MacOS
   brew install ffmpeg
   ```

## Usage 🚀

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Access the web interface in your browser at `http://localhost:8501`

3. Use the AI Prompt Assistant to generate a music description or enter your own

4. Adjust generation parameters as needed

5. Click "Generate Music" to create your composition

## Requirements 📦

- Python 3.8+
- Streamlit
- Requests
- FFmpeg (for audio merging)
- Python-dotenv

## License 📄

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- InspireMusic for the music generation models
- DeepSeek for the text generation API
- Streamlit for the web interface framework
- FFmpeg for audio processing capabilities