from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

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

if __name__ == "__main__":
    print(f"Running {mcp.name} MCP Server : version = {mcp.version}")
    mcp.run()

