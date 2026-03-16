# CampusBook 部署指南

## 项目概述

- **后端**: Flask + SQLite
- **前端**: Vue 3 + Vite

---

## 1. 后端部署到 Railway

### 步骤：

1. 访问 https://railway.app 并使用GitHub账号登录
2. 点击 "New Project" -> "Deploy from repo"
3. 选择你的 GitHub 仓库
4. 在配置中：
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn run:app --bind 0.0.0.0:$PORT`
5. 点击 "Deploy"

---

## 2. 前端部署到 Vercel

### 步骤：

1. 访问 https://vercel.com 并使用GitHub账号登录
2. 点击 "Import Project"
3. 选择你的 GitHub 仓库
4. 在配置中：
   - Root Directory: `frontend`
   - Framework Preset: Vite
5. 在 Environment Variables 中添加：
   - `VITE_API_URL`: 你的 Railway 后端地址（例如：`https://your-backend.railway.app`）
6. 点击 "Deploy"

---

## 3. 修改前端 API 地址

部署后，修改 `frontend/src/api/request.js` 中的 baseURL 为你的 Railway 后端地址。
