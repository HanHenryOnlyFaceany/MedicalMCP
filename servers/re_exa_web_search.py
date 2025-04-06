# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
import json
import requests
from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel
import asyncio

load_dotenv(override=True)

#通过 Searxng 搜索来自可靠医疗健康信息源的内容
mcp = FastMCP(
    name = "re_searxng_web_search",
    version = "0.0.1",
    description = """
    Search the web using SearxnSearch 
    for reliable medical and health 
    information from trusted sources 
    using Searxng
    """
)

# 定义搜索类别枚举
class SearXNGCategory(str, Enum):
    SCIENCE = 'science'
    IT = 'it'
    GENERAL = 'general'
    IMAGES = 'images'
    VIDEOS = 'videos'
    NEWS = 'news'
    MUSIC = 'music'

# 获取 SearXNG 主机名，默认为本地地址
URL = os.environ.get('SEARXNG_HOSTNAME', 'http://localhost:9090')

def http_request(endpoint: str, method: str = 'GET', query: Dict[str, Any] = None) -> requests.Response:
    """发送 HTTP 请求的工具函数"""
    if method.upper() == 'GET':
        return requests.get(endpoint, params=query)
    elif method.upper() == 'POST':
        return requests.post(endpoint, data=query)
    else:
        raise ValueError(f"不支持的 HTTP 方法: {method}")

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), '../configs/config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 加载配置
config = load_config()
medical_site = config.get('re_websearch', {}).get('medical_sites', [])


mcp = FastMCP(
    name = "re_searxng_web_search",
    version = "0.0.1",
    description = """
    Search the web using SearxnSearch 
    for reliable medical and health 
    information from trusted sources 
    using Searxng
    """
)

# class SearchParams(BaseModel):
#     q: str
#     pageno: int = 1
#     categories: List[SearXNGCategory] = None
#     engines: str = ''
#     language: str = 'all'
#     medical_sites: List[str] = medical_sites

#     def __init__(self, **data):
#         # 添加编码处理
#         if 'q' in data and isinstance(data['q'], bytes):
#             data['q'] = data['q'].decode('utf-8')
#         categories = data.get('categories') or [SearXNGCategory.GENERAL,SearXNGCategory.IMAGES]
#         super().__init__(**{**data, 'categories': categories})

#     def to_dict(self) -> Dict[str, Any]:
#         """转换为字典格式"""
#         return {
#             'q': self.q.encode('utf-8').decode('utf-8') if isinstance(self.q, str) else self.q,
#             'pageno': self.pageno,
#             'categories': [cat.value for cat in self.categories],
#             'engines': self.engines,
#             'language': self.language,
#         }

def filter_medical_results(results: List[Dict[str, Any]], medical_sites: List[str]) -> List[Dict[str, Any]]:
    """
    过滤搜索结果，只保留来自指定医疗网站的内容
    
    参数:
        results (List[Dict[str, Any]]): 原始搜索结果列表
        medical_sites (List[str]): 允许的医疗网站域名列表
    
    返回:
        List[Dict[str, Any]]: 过滤后的结果列表
    
    示例:
        >>> results = [{'url': 'https://msdmanuals.cn/article'}, {'url': 'https://other.com/article'}]
        >>> medical_sites = ['msdmanuals.cn', 'a-hospital.com']
        >>> filtered = filter_medical_results(results, medical_sites)
        >>> print(len(filtered))  # 1
    """
    return [
        item for item in results
        if any(site in item.get('url', '') for site in medical_sites if not site.startswith('#'))
    ]

@mcp.tool()
async def me_search_web(
    query: str,
    pageno: int = 1,
    categories: List[SearXNGCategory] = [SearXNGCategory.VIDEOS],
    engines: str = None,
    language: str = 'all',
) -> str:
    """
    使用 SearXNG 搜索医疗健康相关信息，并返回格式化的 Markdown 结果。
    
    Args:
        query: str - 搜索关键词
                    
    Returns:
        str: Markdown 格式的搜索结果，包含标题、链接、摘要和图片
    """
    try:
        q = query
        medical_sites = medical_site
        # 获取安全搜索级别
        safesearch = os.environ.get('SEARXNG_SAFE', 0)

        site_query = " OR ".join([f"site:{site}" for site in medical_sites])
        full_query = f"({q})({site_query})"

        query = {
            'q': full_query,
            'pageno': pageno,
            'categories': ','.join(categories) if isinstance(categories,list) else categories,
            'format': 'json',
            'engines': engines,
            'language': language,
            'safesearch': safesearch,
            'image_proxy': True,
        }

        try:
            res = http_request(
                endpoint=f"{URL}/search",
                method='POST',
                query=query
            )
            print(f"HTTP Response Status: {res.status_code}")  # 添加状态码输出
            print(f"Response Content: {res.text[:200]}")  # 打印响应内容前200个字符
            result = res.json()
        except requests.exceptions.ConnectionError:
            print(f"连接错误: 无法连接到 {URL}")
            return "搜索服务暂时无法访问，请稍后再试"
        except requests.exceptions.Timeout:
            print(f"请求超时: {URL}/search")
            return "搜索请求超时，请稍后再试"
        except requests.exceptions.RequestException as e:
            print(f"HTTP 请求错误: {str(e)}")
            print(f"请求参数: {query}")  # 添加请求参数输出
            return "搜索过程中发生错误，请稍后再试"
        except json.JSONDecodeError as e:
            print(f"返回数据格式错误: {str(e)}")
            print(f"原始响应: {res.text}")  # 添加完整响应输出
            return "搜索结果解析失败，请稍后再试"

        if 'results' in result:
            # 使用过滤函数处理结果   限制条件限制在docker配置中为前10个
            filtered_results = filter_medical_results(result['results'], medical_sites)
            """
                redo: JSON format为markdown格式
            """
            return format_search_results(filtered_results)
            
            # return [
            #     {
            #         'id': index + 1,
            #         'name': item.get('title', ''),
            #         'url': item.get('url', ''),
            #         'source': item.get('source', ''),
            #         'img': item.get('img_src', ''),
            #         'thumbnail': item.get('thumbnail_src', ''),
            #         'snippet': item.get('content', ''),
            #         'engine': item.get('engine', '')
            #     }
            #     for index, item in enumerate(filtered_results)
            # ]
        return "未在指定网站找到相关信息"

    except Exception as e:
        print(f"搜索过程中发生错误: {e}")
        return ""

def format_search_results(results: List[Dict[str, Any]]) -> str:
    """Format search results into markdown.
    
    Args:
        search_results: Results from Searxng search
        
    Returns:
        Formatted markdown string
    """
    if not results:
        return "未找到相关结果"
        
    markdown_results = "### 搜索结果\n\n"
    for index, item in enumerate(results, 1):
        title = item.get('title', '')
        url = item.get('url', '')
        source = item.get('source', '')
        snippet = item.get('content', '')
        img = item.get('img_src', '')
        thumbnail = item.get('thumbnail_src', '')
        engine = item.get('engine', '')
        
        markdown_results += f"**{index}.** [{title}]({url})"
        if source:
            markdown_results += f" - 来源: {source}"
        markdown_results += "\n"
        if snippet:
            markdown_results += f"> {snippet}\n"
        markdown_results += "\n"
        if img:
            markdown_results += f"![图片]({img})\n"
        if thumbnail:
            markdown_results += f"![缩略图]({thumbnail})\n"
        if engine:
            markdown_results += f"搜索引擎: {engine}\n"
            
    
    return markdown_results

# 修改 test_search 函数
async def test_search():
    print("\nTesting sear_web_search:")
    result = await me_search_web(query="咳嗽")
    print(result)  # 直接打印格式化后的 markdown 字符串
    # print(f"找到 {len(result)} 条结果：")

    # if me_results:
    #     print(f"打印前二十个结果：")
    #     for i in range(min(10,len(me_results))):
    #         print(f"结果 {i+1}:")
    #         for key , value in me_results[i].items():
    #             print(f"{key}: {value}")
    #         print("-" * 50) 

if __name__ == "__main__":
    print(f"Running Searxng Web Search MCP server...")
    mcp.run()
    # asyncio.run(test_search())

