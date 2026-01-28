import streamlit as st
from streamlit_local_storage import LocalStorage as BrowserStorage
from audio_recorder_streamlit import audio_recorder
import datetime

# --- IMPORTANT: This must be the first Streamlit command ---
st.set_page_config(page_title="上岸助手", layout="wide")

# 1. Initialize LocalStorage
# We use a container to ensure the component renders and can communicate with the browser
localS = BrowserStorage()

# --- 2. Logic to Sync Browser Storage with Session State ---
# getItem does NOT take a 'key' argument in this library's implementation.
# It returns the value directly if available.
raw_or_key = localS.getItem("openrouter_api_key")
raw_lf_key = localS.getItem("lemonfox_api_key")

# Store in session state for consistency during the current run
if raw_or_key is not None:
    st.session_state["or_key_internal"] = raw_or_key
if raw_lf_key is not None:
    st.session_state["lf_key_internal"] = raw_lf_key

# Final values to use in the app
or_key = st.session_state.get("or_key_internal", "")
lf_key = st.session_state.get("lf_key_internal", "")

# --- 3. Import Custom Engines (Mocking logic if files aren't found) ---
try:
    from core.ai_engine import InterviewAI
    from core.storage import LocalStorage as RemoteStorage
    data = RemoteStorage.load_data()
except ImportError:
    # Fallback for demonstration if your custom modules aren't path-accessible
    st.error("Missing core modules. Please ensure core/ai_engine.py and core/storage.py exist.")
    st.stop()

with st.sidebar:
    st.title("🚀 导航")
    page = st.radio("前往", ["模拟面试", "历史记录"])
    st.divider()
    st.title("⚙️ 配置")
    model_options = {
        "Gemini 3.0 Flash (最强大的模型)": "google/gemini-3-flash-preview",
        "Gemini 2.5 Flash Lite（省钱快速）": "google/gemini-2.5-flash-lite",
        "DeepSeek V3.2": "deepseek/deepseek-v3.2",
        "小米模型": "xiaomi/mimo-v2-flash"
    }
    saved_model_id = localS.getItem("selected_model_id")
    try:
        default_index = list(model_options.values()).index(saved_model_id)
    except:
        default_index = 0

    selected_model_display = st.selectbox(
        "选择 AI 模型", 
        options=list(model_options.keys()),
        index=default_index
    )
    selected_model_id = model_options[selected_model_display]

    # 当模型改变时，保存到本地存储
    if selected_model_id != saved_model_id:
        localS.setItem("selected_model_id", selected_model_id, key="set_model_action")
    # --- 1. 读取逻辑 (getItem 不传 key) ---
    # 尝试从浏览器获取现有值
    saved_or = localS.getItem("openrouter_api_key")
    saved_lf = localS.getItem("lemonfox_api_key")
     # 确定当前显示的初始值（优先 session_state，其次浏览器存储）
    curr_or = st.session_state.get("or_key_internal", saved_or or "")
    curr_lf = st.session_state.get("lf_key_internal", saved_lf or "")

    # --- 2. 界面输入 ---
    new_or = st.text_input("OpenRouter API Key", value=curr_or, type="password")
    new_lf = st.text_input("Lemonfox API Key", value=curr_lf, type="password")
    
    # --- 3. 保存逻辑 (setItem 必须传 key) ---
    if st.button("💾 保存 API 配置", key="main_save_btn"):
        if new_or and new_lf:
            localS.setItem(
                "openrouter_api_key",
                new_or,
                key="set_openrouter_key"
            )
            localS.setItem(
                "lemonfox_api_key",
                new_lf,
                key="set_lemonfox_key"
            )

            st.session_state["or_key_internal"] = new_or
            st.session_state["lf_key_internal"] = new_lf

            st.success("API Key 已成功保存！")
        else:
            st.error("请填写完整的 API Key")


    st.divider()
    
    # --- 评价模板部分也需要同样的处理 ---
    st.subheader("📝 评价模板定制")
    
    # 获取现有模板
    saved_prompt = localS.getItem("custom_interview_prompt")
    # 从本地加载已有的自定义模板
    default_prompt = """你是一位考公面试专家。请评价以下回答：
题目：{question}
回答：{answer}

我需要你按照以下格式给出反馈：
1. 说明根据题目内容说明回答思路，如何切入，特别是根据回答指出不足之处。注意每一个思路都必须有具体例子言之有物；
2. 根据我的回答内容，指出根据我的现有回答如何以最小的改进获得最大的提升，给出具体的回答例子。
"""

    user_template = st.text_area(
        "自定义 Prompt", 
        value=saved_prompt if saved_prompt else default_prompt,
        height=200
    )
    
    if st.button("保存模板", key="save_template_btn"):
        if "{question}" in user_template and "{answer}" in user_template:
            # 关键点：给 setItem 增加唯一 key
            localS.setItem("custom_interview_prompt", user_template, key="set_template_action")
            st.success("模板已保存")
        else:
            st.error("模板必须包含 {question} 和 {answer}")


# --- 5. Main UI ---
st.title("🚀 考公面试 AI 练习")

if page == "模拟面试":
    st.title("🎙️ 面试练习")
    
    # 增加一个重置按钮在顶部，方便用户随时开启新题
    if st.session_state.get("transcript"):
        if st.button("🆕 开启新题目"):
            # 清除相关 session 状态
            for key in ["transcript", "last_audio"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    custom_q = st.text_input("请输入面试题目：", placeholder="例如：谈谈你对‘为人民服务’的理解")
    if custom_q:
        st.info(f"**当前题目：** {custom_q}")
        
        # 录音逻辑
        audio_bytes = audio_recorder(text="点击录音", pause_threshold=60.0, sample_rate=16000)
        
        if audio_bytes:
            st.audio(audio_bytes)
            # 识别逻辑 (保持不变)
            if "last_audio" not in st.session_state or st.session_state.last_audio != audio_bytes:
                with st.spinner("正在识别语音..."):
                    ai = InterviewAI(or_key)
                    transcript = ai.transcribe(audio_bytes, lf_key)
                    st.session_state.transcript = transcript
                    st.session_state.last_audio = audio_bytes

            corrected_text = st.text_area("识别结果（可手动微调）：", 
                                          value=st.session_state.get("transcript", ""), 
                                          height=150)

            if st.button("开始 AI 评分"):
                if not or_key:
                    st.error("请先配置 API Key")
                else:
                    ai = InterviewAI(or_key)
                    with st.spinner("AI 批阅中..."):
                        result = ai.get_score(
                            question=custom_q, 
                            answer=corrected_text, 
                            prompt_template=user_template,
                            model=selected_model_id
                        )
                        st.markdown("---")
                        st.markdown(result)

                        RemoteStorage.save_record(custom_q, corrected_text, result)
                        st.success("✅ 练习已保存！")
                        col_nav1, col_nav2 = st.columns(2)
                        with col_nav1:
                            if st.button("➡️ 练习下一题"):
                                # 清除状态并刷新
                                for key in ["transcript", "last_audio"]:
                                    st.session_state.pop(key, None)
                                st.rerun()
                        with col_nav2:
                            if st.button("📜 前往查看历史记录"):
                                # 这里的逻辑需要配合侧边栏 radio 的 index
                                st.info("请在左侧菜单点击 '历史记录'")
# --- 页面 2：历史记录 ---
elif page == "历史记录":
    st.title("📜 练习历史")
    data = RemoteStorage.load_data()
    
    if not data["history"]:
        st.warning("暂无历史记录，快去练习吧！")
    else:
        for idx, h in enumerate(data["history"]):
            # 这里的 h['id'] 是我们在 load_data 里新加的
            with st.expander(f"📅 {h['date']} | 题目：{h['q'][:20]}..."):
                st.subheader("题目")
                st.write(h['q'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info("📝 你的回答")
                    st.write(h['a'])
                with col2:
                    st.success("🤖 AI 评分")
                    st.markdown(h['result'])
                
                # --- 删除逻辑开始 ---
                if st.button(f"🗑️ 删除此条记录", key=f"del_{h['id']}"):
                    if RemoteStorage.delete_record(h['id']):
                        st.success("记录已删除！")
                        st.rerun()  # 刷新页面以隐藏已删除的记录
                # --- 删除逻辑结束 ---