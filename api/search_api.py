from fastapi import FastAPI, HTTPException
from typing import Optional, List
import uvicorn
from pydantic import BaseModel
import sys
import os

# 添加父目录到系统路径以导入搜索模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pstdio.re_exa_web_search import me_search_web, SearXNGCategory

app = FastAPI(
    title="医疗搜索 API",
    description="提供医疗健康信息搜索服务",
    version="1.0.0"
)

class SearchRequest(BaseModel):
    query: str
    pageno: int = 1
    categories: Optional[List[SearXNGCategory]] = None
    engines: str = "bing,baidu,sogou,360search"
    language: str = 'all'

@app.post("/api/search")
async def search(request: SearchRequest):
    try:
        results = await me_search_web(
            query=request.query,
            pageno=request.pageno,
            categories=request.categories,
            engines=request.engines,
            language=request.language
        )
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7002)  # 修改为 0.0.0.0 以允许外部访问