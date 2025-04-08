#!/bin/bash
# 显示当前工作目录和文件列表，帮助调试
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# 检查文件是否存在
if [ -f "/app/psse/re_searxng_web_search.py" ]; then
    echo "Found re_searxng_web_search.py"
else
    echo "ERROR: re_searxng_web_search.py not found!"
    find /app -name "*.py" | grep -i search
fi

if [ -f "/app/api/search_api.py" ]; then
    echo "Found search_api.py"
else
    echo "ERROR: search_api.py not found!"
    find /app -name "*.py" | grep -i api
fi

# 启动服务
echo "Starting me_web_search mcp service..."
python /app/psse/re_searxng_web_search.py &
PID1=$!
echo "Starting me_search api services..."
python /app/api/search_api.py &
PID2=$!

# 保持容器运行
echo "Services started with PIDs: $PID1, $PID2"
wait $PID1 $PID2 || echo "A process exited with error"