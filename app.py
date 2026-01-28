import streamlit as st
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_title="考公面试练习测试", page_icon="🎤")

st.title("🎤 面试练习 MVP 测试版")

# 1. 简单的题库测试
questions = ["请谈谈你对'为人民服务'的理解。", "如果你在工作中与领导产生分歧，你会怎么做？"]
if 'q_idx' not in st.session_state:
    st.session_state.q_idx = 0

current_q = questions[st.session_state.q_idx]
st.subheader(f"当前题目：{current_q}")

if st.button("换一题"):
    st.session_state.q_idx = (st.session_state.q_idx + 1) % len(questions)
    st.rerun()

st.divider()

# 2. 录音组件测试
st.write("点击下方麦克风图标开始录音（请确保浏览器允许麦克风权限）：")
audio_bytes = audio_recorder(
    text="点击录音",
    recording_color="#e8b62c",
    neutral_color="#6aa36f",
    icon_size="3x",
)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    st.success("录音成功！如果能听到回放，说明录音模块正常。")
    st.info("下一步：接入 Whisper API 即可转为文字。")

# 3. 侧边栏设置测试
with st.sidebar:
    st.header("系统设置")
    api_key = st.text_input("输入 API Key (仅作演示)", type="password")
    if api_key:
        st.write("API Key 已接收（模拟存储）")