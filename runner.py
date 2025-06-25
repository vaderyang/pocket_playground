# runner.py
from pocketflow import AsyncNode, AsyncFlow
# 不需要 DEFAULT_ACTION

from utils import call_llm  # 请你根据实际代码实现该函数

class ChatNode(AsyncNode):
    async def prep_async(self, shared):
        shared.setdefault("history", [])
        return shared["user_input"]

    async def exec_async(self, user_input: str):
        messages = [{"role": "user", "content": user_input}]
        return call_llm(messages, stream=True)

    async def post_async(self, shared, inp, resp):
        shared["history"].append((inp, resp))
        shared["last_response"] = resp
        # 不返回任何值，相当于 'default'

async def run_chat_flow(user_input: str):
    shared = {"user_input": user_input}
    chat_node = ChatNode()
    await chat_node.run_async(shared)
    return shared["last_response"]
