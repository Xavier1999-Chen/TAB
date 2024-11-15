import streamlit as st
import openai
import re
import time
import random

from streamlit.components.v1 import html

# 设置 OpenAI API 密钥
# openai.api_key = 'YOUR_OPENAI_API_KEY'

openai.api_key = "sk-de60092d49084f7883d3caef532a6b69"
openai.base_url = "https://api.deepseek.com"

# Streamlit 页面配置
st.set_page_config(page_title="TAB", page_icon="🤖")


def phone_card(phone_number, text):
    card_html = f"""
    <div style="background-color: #FFFFFF; border: 1px solid #ddd; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
        <h3 style="color: #333; margin-bottom: 10px;">{text}</h3>
        <p style="color: #555; font-size: 16px; margin-bottom: 20px;">电话号码: <a href="tel:{phone_number}" style="color: #007BFF; text-decoration: none;">{phone_number}</a></p>
        <button style="background-color: #7FE656; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; transition: background-color 0.3s;">
            Call
        </button>
    </div>
    """
    
    return {"role": "assistant", "content": card_html, "is_card": True}
def assistant_msg(text):
    return {"role": "assistant", "content": text}

def llm_response(messages, chat_title):

    chat_title.title("Typing……")
    response = openai.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )
    chat_title.title("TAB")

    return response.choices[0].message.content

def check_crisis(prompt, chat_title):
    chat_title.title("Typing……")

    messages = [
        {"role": "system", "content": "You are a mental suppoort specialist."},
        {"role": "user", "content": f'''Determine if the following contains suicidal or self-harming tendencies by responding YES or NO only: {prompt}'''}
    ]
    response = openai.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )
    
    chat_title.title("TAB")

    return response.choices[0].message.content
def non_crisis_case(session_state, prompt):
    # if "messages" not in session_state:
    #     session_state.messages = []
    # session_state.messages.append({"role": "user", "content": prompt})

    for message in session_state.messages:
        with st.chat_message(message["role"]):
            if message.get('is_card'):
                        html(message["content"], height=200)
            else:
                st.markdown(message["content"])

    response = llm_response(st.session_state.messages, chat_title)
    sentences = re.split(r'[，。,.]', response)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    # print(sentences)
    for sentence in sentences:
        st.session_state.messages.append({"role": "assistant", "content": sentence})
        chat_title.title("Typing……")

        time.sleep((random.random()*0.05+0.01)*float(len(sentence)))
        with st.chat_message("assistant"):
            st.markdown(sentence)
        chat_title.title("TAB")

def crisis_case(session_state, prompt):
    # if "messages" not in session_state:
    #     session_state.messages = []

    for message in session_state.messages:
        with st.chat_message(message["role"]):
            if message.get('is_card'):
                html(message["content"], height=200)
            else:
                st.markdown(message["content"])
    msg_1 = assistant_msg('hi')
    hotline_1 = phone_card("+852 4567890", '客服热线1')
    hotline_2 = phone_card("+852 4567120", '客服热线2')
    msg_2 = assistant_msg('You can seek more professional help from the above hotlines. Of a certainty, I am always willing to be your listener.')
    msg_3 = assistant_msg('Are there things around you that could cause you harm? ')
    msg_4 = assistant_msg('If so, please put them away.')

    sentences = [msg_1, hotline_1, hotline_2, msg_2, msg_3, msg_4]


    for sentence in sentences:
        session_state.messages.append(sentence)
        chat_title.title("Typing……")

        time.sleep(0.5)
        with st.chat_message("assistant"):
            if sentence.get('is_card'):
                html(sentence["content"], height=200)
            else:
                st.markdown(sentence["content"])
    
        chat_title.title("TAB")

    

chat_title = st.title("TAB")
chat_win = st.empty()
chat_input = st.empty()


with chat_win.container(height=500):

    if "status" not in st.session_state:
        st.session_state.status = 'no_check_crisis'

    if "get_reply" not in st.session_state:
        st.session_state.get_reply = False

    if prompt := chat_input.chat_input("What is up?"):
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.status == 'no_check_crisis':
            is_crisis = check_crisis(prompt, chat_title)
            if 'yes' in is_crisis.lower():
                st.session_state.status = 'need_to_confirm_crisis'
            else:
                st.session_state.status = 'non_crisis_case'

        if st.session_state.status == 'need_to_confirm_crisis':
            sentence = {"role": "assistant", "content": 'Are you thinking about suicide or self-harm?'}
            st.session_state.messages.append(sentence)
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    if message.get('is_card'):
                        html(message["content"], height=200)
                    else:
                        st.markdown(message["content"])

            st.session_state.status = 'wait_for_confirmation'

        if st.session_state.status == 'wait_for_confirmation' and st.session_state.get_reply:
            if 'yes' in prompt.lower():
                st.session_state.status = 'crisis_case'       
            else:
                st.session_state.status = 'non_crisis_case'
            st.session_state.get_reply = False

        if st.session_state.status == 'crisis_case':
            crisis_case(st.session_state, prompt)
            st.session_state.status = 'no_check_crisis'

        if st.session_state.status == 'non_crisis_case':
            non_crisis_case(st.session_state, prompt)
            st.session_state.status = 'no_check_crisis'

        if st.session_state.status == 'wait_for_confirmation':    
            st.session_state.get_reply = True
       

       