# fast-apitest

基于 Django + Vue 的接口自动化测试平台雏形，覆盖项目管理、环境配置、接口调试、场景编排以及测试套件执行等核心流程。

## 功能概览

- **后端（`backend/`）**：Django + Django REST Framework，提供项目、环境、接口、用例、场景、测试套件/报告等 REST API，并支持导入 OpenAPI/Swagger 规范快速生成接口。
- **前端（`frontend/`）**：使用 Vite + Vue 3 实现快速联调界面，内置项目管理、环境配置、接口定义与调试、场景编排、套件执行与报告展示模块。

## 环境依赖

- Python 3.11+
- Node.js 18+
- SQLite（默认数据库，可按需替换为其他后端）

## 后端安装与启动

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # 可选但推荐
pip install -r requirements.txt
python manage.py migrate
```

可使用以下命令快速创建演示账号（用户名 `admin`，密码 `admin123`）：

```bash
python manage.py shell -c "from django.contrib.auth import get_user_model;\nUser = get_user_model();\nUser.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
```

启动开发服务器：

```bash
python manage.py runserver
```

API 默认监听 `http://127.0.0.1:8000/`，主要接口位于 `http://127.0.0.1:8000/api/`。Swagger/OpenAPI 导入入口：`POST /api/swagger/import/`。

## 前端安装与启动

```bash
cd frontend
npm install
npm run dev
```

默认通过 `http://127.0.0.1:5173/` 访问界面。可在 `.env` 中配置 `VITE_API_BASE` 修改后端地址（默认指向 `http://localhost:8000/api/`）。

## 核心流程验证

1. 登录前端页面，创建新项目。
2. 在“环境”页配置环境变量与请求头。
3. 在“接口”页新建接口或导入 Swagger，再为接口创建断言/提取配置的调试用例。
4. 在“场景”页编排多个接口用例串联执行。
5. 在“测试套件”页选择用例生成套件，并执行生成报告。

## 目录结构

```
backend/    Django 项目与 REST API
frontend/   Vue 3 + Vite 前端工程
```

欢迎根据业务需求继续扩展身份认证、权限、调度执行等能力。
