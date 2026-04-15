import httpx
from mcp.server import FastMCP

import os
import sys

sys.path.append(os.getcwd())

from tradingagents.dataflows import baidu_search_utils as bsu
from tradingagents.utils import common_utils

# # 初始化 FastMCP 服务器
app = FastMCP('web-search', port=9000)


@app.tool()
async def web_search(query: str) -> str:
    """
    搜索互联网内容

    Args:
        query: 要搜索内容

    Returns:
        搜索结果的总结
    """

    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         'https://open.bigmodel.cn/api/paas/v4/tools',
    #         headers={'Authorization': '换成你自己的API KEY'},
    #         json={
    #             'tool': 'web-search-pro',
    #             'messages': [
    #                 {'role': 'user', 'content': query}
    #             ],
    #             'stream': False
    #         }
    #     )
    #
    #     res_data = []
    #     for choice in response.json()['choices']:
    #         for message in choice['message']['tool_calls']:
    #             search_results = message.get('search_result')
    #             if not search_results:
    #                 continue
    #             for result in search_results:
    #                 res_data.append(result['content'])
    #
    #     return '\n\n\n'.join(res_data)
    return f"这是你要的搜索结果:{query}"


@app.tool()
async def baidu_search(query: str, max_count: int=bsu.DEFAULT_MAX_COUNT) -> str:
    """
    使用百度搜索互联网内容

    Args:
        query: 要搜索内容,
        max_count: 最多返回多少条查询结果.

    Returns:
        搜索结果文本
    """
    if common_utils.is_empty(query):
        return ""

    return bsu.baidu_search(query, max_count)


if __name__ == "__main__":
    app.run(transport="streamable-http")
