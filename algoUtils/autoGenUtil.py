import time
from typing import List, Optional

from autogen_agentchat.base import Response, TaskResult
from autogen_agentchat.messages import ModelClientStreamingChunkEvent
from autogen_core.models import RequestUsage


async def custom_output(_agents, ignore_agents: Optional[List[str]] = None):
    """
    自定义输出格式
    Args:
        ignore_agents: List[str], 需要忽略消息的agent名称列表
    """
    start_time = time.time()
    total_usage = RequestUsage(prompt_tokens=0, completion_tokens=0)
    streaming_chunks = []
    ignore_agents = ignore_agents or []

    async for message in _agents.run_stream(task="开始"):
        # 检查是否需要忽略该agent的消息
        source = message.source if hasattr(message, "source") else (
            message.chat_message.source if isinstance(message, Response) else None
        )
        if source and any(agent in source for agent in ignore_agents):
            continue

        if isinstance(message, TaskResult):
            duration = time.time() - start_time
            print(f"\n{'-' * 10} 任务结果 {'-' * 10}")
            print(f"完成原因: {message.stop_reason}")
            print(f"总耗时: {duration:.2f} 秒")
            print(f"总Token统计 - Prompt: {total_usage.prompt_tokens}, Completion: {total_usage.completion_tokens}")
            
        elif isinstance(message, Response):
            print(f"\n{'-' * 10} {message.chat_message.source} {'-' * 10}")
            print(f"{message.chat_message.content}")
            
            if message.chat_message.models_usage:
                total_usage.completion_tokens += message.chat_message.models_usage.completion_tokens
                total_usage.prompt_tokens += message.chat_message.models_usage.prompt_tokens
                print(f"[Token统计 - Prompt: {message.chat_message.models_usage.prompt_tokens}, Completion: {message.chat_message.models_usage.completion_tokens}]")
            print()
                
        elif isinstance(message, ModelClientStreamingChunkEvent):
            if not streaming_chunks:
                print(f"\n{'-' * 10} {message.source} {'-' * 10}")
            print(message.content, end="")
            streaming_chunks.append(message.content)
            
        else:
            if streaming_chunks:
                streaming_chunks.clear()
            else:
                print(f"\n{'-' * 10} {message.source} {'-' * 10}")
                print(f"{message.content}")
                
            if hasattr(message, "models_usage") and message.models_usage:
                total_usage.completion_tokens += message.models_usage.completion_tokens
                total_usage.prompt_tokens += message.models_usage.prompt_tokens
                print(f"[Token统计 - Prompt: {message.models_usage.prompt_tokens}, Completion: {message.models_usage.completion_tokens}]")
            print()
