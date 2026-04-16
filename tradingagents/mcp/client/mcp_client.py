import asyncio

from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession

import os
import sys

sys.path.append(os.getcwd())

from tradingagents.dataflows import baidu_search_utils as bsu
from tradingagents.utils import common_utils

import logging
from tradingagents.log.log import TRADING_AGENTS_GRAPH
tag_logger = logging.getLogger(TRADING_AGENTS_GRAPH)

async def baidu_search(query, max_count=bsu.DEFAULT_MAX_COUNT):
    # 创建sse客户端
    mcp_server_url = "http://localhost:9000/mcp"
    async with streamable_http_client(mcp_server_url) as (read, write, _):
        # 创建 ClientSession 对象
        async with ClientSession(read, write) as session:
            tag_logger.info(f"Connecting {mcp_server_url}")
            # 初始化 ClientSession
            await session.initialize()

            # # 列出可用的工具
            # response = await session.list_tools()
            # print(response)

            tag_logger.info(f"call_tool: baidu_search, args=(query: {query}, max_count: {max_count})")
            # 调用工具
            response = await session.call_tool('baidu_search', {"query": query, "max_count": max_count})
            
            tag_logger.info(f"response={response}")

            return response


# asyncio.run(baidu_search("301368.SZ 丰立智能"))
