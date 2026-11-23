import streamlit as st#智能填充用“tab”保存
from openai import OpenAI #从openai第三方库中导入OpenAI类
#基础配置
st.set_page_config(
    page_title="AI交互对话",#标签页名称
    page_icon="🧊",#图标显示
    layout="wide",#显示方式
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# This is a header. This is an *extremely* cool app!"#纯文本输出
    }
)
系统提示词 = """你是一位性格温和的烟台南山校园智能助手，你的名字是%s,你的性格是%s。
              关于快递：
              中通、圆通快递一般会发在3区。极兔快递会发在2区。邮政快递会发在一区。
              特别的，如果你的快递地址在东区，并且是中通，圆通、顺丰快递的话，快递会发在东区。
              """
st.title("AI智能交互对话")
st.write("欢迎来到AI智能交互对话")
#以上仅为界面设置--------------------------------------------------------------------

#st.session_state相当于一个数据库，用于存储会话中的数据
#初始化默认聊天信息
if "messages" not in st.session_state:
    st.session_state.messages =[]
#名字
if "name" not in st.session_state:
    st.session_state.name = "小海"
#性格特点
if "character" not in st.session_state:
    st.session_state.character = "致力以学生的角度，讲述非官方的校园生活。"

#侧边栏
#st.sidebar.write("系统信息：")
#name = st.sidebar.text_input("姓名：")#.sidebar的内容都在侧边栏中

#展示聊天信息
for message in st.session_state.messages:

    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

#with:创建一个上下文管理器，用于管理代码块中的变量作用域。
with st.sidebar:
    st.write("系统信息：")
    name = st.text_input("昵称：",value=st.session_state.name)
    if name:
        st.session_state.name = name
    character = st.text_area("简介",value=st.session_state.character)
    if character:
        st.session_state.character = character

#输入界面
消息提示词 = st.chat_input("请输入消息：")
if 消息提示词:
    st.chat_message("user").write(消息提示词)
    #保存用户输入的提示词
    st.session_state.messages.append({"role": "user", "content": 消息提示词})

#以下为调用大模型-------------------------------------------------------------------------
    import os

    api_key = st.secrets.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("没找到 API key：本地填 .streamlit/secrets.toml，线上在 Settings → Secrets 里加")
        st.stop()

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    # 发送请求调用大模型
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": 系统提示词 % (st.session_state.name,st.session_state.character)},
            *st.session_state.messages
        ],
        stream= True
    )
    response_message = st.empty()#创建一个空的元素，用于展示大模型返回的流式数据
    # 处理大模型返回的流式数据。
#以上为调用大模型-------------------------------------------------------------------------
    full_text = ""
    for chunk in response:#chunk是一个对象，对象中有choices属性，choices属性中有delta属性，delta属性中有content属性，content属性中有内容
        # 为什么要这样写呢，是因为数据在chunk的delta属性中，所以要这样写
        if chunk.choices[0].delta.content is not None: # 确保有内容
            contect = chunk.choices[0].delta.content # 使用contect存储内容
            full_text += contect # 将内容添加到full_text
            response_message.chat_message("assistant").write(full_text)

    #answer = response.choices[0].message.content
    #st.chat_message("assistant").write(answer)
    #保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": full_text })