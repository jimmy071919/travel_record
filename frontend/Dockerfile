# 使用 Node.js 18 作為基礎映像
FROM node:18-slim

# 設置工作目錄
WORKDIR /app

# 複製 package.json 和 package-lock.json
COPY package*.json ./

# 安裝依賴
RUN npm install

# 複製源代碼
COPY . .

# 啟動開發服務器
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
