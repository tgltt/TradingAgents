import asyncio

from mcp.client.sse import sse_client
from mcp import ClientSession

from tradingagents.dataflows import baidu_search_utils as bsu
from tradingagents.utils import common_utils

async def baidu_search(query, max_count=bsu.DEFAULT_MAX_COUNT):
    # 创建sse客户端
    async with sse_client("http://localhost:9000/sse") as streams:
        # 创建 ClientSession 对象
        async with ClientSession(*streams) as session:
            # 初始化 ClientSession
            await session.initialize()

            # # 列出可用的工具
            # response = await session.list_tools()
            # print(response)

            # 调用工具
            response = session.call_tool('baidu_search', {"query": query, "max_count": max_count})
            print(response)
