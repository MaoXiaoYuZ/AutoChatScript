# 对chatgpt_auto_script.py进行封装，存储对话数据并且实现类似api的chat功能

import json
import os
import time
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel

from chatgpt_auto_script import ChatGPTAutoScript

class ChatMessage(BaseModel):
    role: Literal['user', 'assistant', 'system']
    content: Optional[str]

class Chat(BaseModel):
    chatid: str
    name: Optional[str] = None
    messages: List[ChatMessage]

class ChatGPTChatScript:
    def __init__(self):
        self.auto_script: ChatGPTAutoScript = ChatGPTAutoScript()
        self.chats : List[Chat] = []

        self.auto_script.init_submit_button()

        if os.path.exists('chats.json'):
            self.load_chats('chats.json')
    
    def save_chats(self, filename: str):
        """
        将chats列表保存到文件
        """
        with open(filename, 'w', encoding='utf-8') as file:
            # Pydantic模型的json()方法将模型转换为JSON字符串
            json_data = [chat.model_dump() for chat in self.chats]
            json.dump(json_data, file, ensure_ascii=False, indent=1)
    
    def load_chats(self, filename: str):
        """
        从文件加载chats列表
        """
        with open(filename, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            # 使用Chat.parse_obj将字典转换回Chat对象
            self.chats = [Chat.model_validate(chat) for chat in json_data]

    def find_chat(self, messages:List[ChatMessage]):
        # 从self.chats中匹配对应的chat
        for chat in self.chats:
            if len(messages) <= len(chat.messages) and all(len(msg.content) == len(chat_msg.content) and msg.content == chat_msg.content for msg, chat_msg in zip(messages, chat.messages)):
                return chat
        return None

    def auto_chat(self, messages:List[ChatMessage]):
        messages = messages.copy()
        # 像api一样接受messages输入，将自动判定该new/submit/resubmit chat
        assert len(messages) > 0 and messages[-1].role == 'user'
        
        if len(messages) == 1:
            if (chat := self.find_chat(messages)) is None:
                action = 'new'
                self.auto_script.new_chat()
                chat_id = str(int(time.time() * 1000))  # Use milliseconds for uniqueness
                chat = Chat(chatid=chat_id, messages=messages)
                self.chats.append(chat)
            else:
                action = 'resubmit'
        else:
            if (chat := self.find_chat(messages[:-1])) is None:
                raise Exception('Previous messages not found')
            else:
                if len(chat.messages) == len(messages) - 1:
                    action = 'submit'

                else:
                    action = 'resubmit'
        
        # check
        if action != 'new' and chat.messages[-1].content != self.auto_script.copy_last_response():
            raise Exception('Current chat is not consistent with last response') 

        if action == 'new':
            response = self.auto_script.submit(messages[-1].content)
            response_msg = ChatMessage(role='assistant', content=response)
            chat.messages.append(response_msg)
        elif action == 'submit':
            response = self.auto_script.submit(messages[-1].content)
            response_msg = ChatMessage(role='assistant', content=response)
            chat.messages.append(response_msg)
        elif action == 'resubmit':
            response = self.auto_script.resubmit(messages[-1].content, chat.messages[len(messages)].content)
            response_msg = ChatMessage(role='assistant', content=response)
            chat.messages = messages + [response_msg, ]

        self.save_chats('chats.json')
        return response_msg
        
if __name__ == '__main__':
    chat_script = ChatGPTChatScript()
    messages = [
        ChatMessage(role='user', content='Hello, how are you?'),
        ChatMessage(role='assistant', content="I'm here and ready to assist you. How can I help you today?"),
        ChatMessage(role='user', content='What can you do for me ?'),
    ]
    chat_script.auto_chat(messages)
    print(chat_script.chats)