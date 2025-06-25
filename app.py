# app.py
import chainlit as cl
import asyncio
from runner import run_chat_flow
from thinking_parser import StreamingThinkingParser

@cl.on_chat_start
async def on_start():
    await cl.Message("欢迎进入 PocketFlow + Chainlit 聊天 Demo").send()

@cl.on_message
async def on_msg(msg: cl.Message):
    # 初始化流式思考解析器
    parser = StreamingThinkingParser()
    
    # 调用异步聊天 Flow 获取流式响应
    stream_response = await run_chat_flow(msg.content)
    
    # 处理流式响应
    for chunk in stream_response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            await parser.process_chunk(content)
    
    # 完成处理
    await parser.finalize()
