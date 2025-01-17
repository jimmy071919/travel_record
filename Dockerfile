# 使用 Ubuntu 作為基礎映像
FROM ubuntu:22.04

# 避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# 設置工作目錄
WORKDIR /app

# 安裝必要的套件和 Node.js 18.x
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    python3 \
    python3-pip \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 安裝 MongoDB
RUN curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
    --dearmor \
    && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
    tee /etc/apt/sources.list.d/mongodb-org-7.0.list \
    && apt-get update \
    && apt-get install -y mongodb-org \
    && rm -rf /var/lib/apt/lists/*

# 創建 MongoDB 數據目錄
RUN mkdir -p /data/db

# 複製後端文件並安裝依賴
COPY backend /app/backend
RUN cd backend && pip3 install -r requirements.txt

# 複製前端文件
COPY frontend /app/frontend
WORKDIR /app/frontend

# 清除現有的 node_modules 並重新安裝依賴
RUN rm -rf node_modules && npm install

# 複製啟動腳本
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

WORKDIR /app

# 設置容器啟動命令
CMD ["/bin/bash", "/app/start.sh"]
