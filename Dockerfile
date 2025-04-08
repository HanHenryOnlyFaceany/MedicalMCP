FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 设置启动脚本权限
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]