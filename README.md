# 实验室管理系统 (Lab Management System)

> 基于 Spring Cloud Alibaba 微服务架构的医院检验科信息系统（LIS）

## 快速导航

| 分类 | 路径 | 说明 |
|------|------|------|
| 📖 项目文档 | [docs/](docs/) | 全部文档（26个文件） |
| 🧪 测试脚本 | [tests/](tests/) | 自动化测试脚本 |
| ⚙️ 启动脚本 | [scripts/](scripts/) | 服务启动与测试脚本 |
| 🗄️ 数据库脚本 | [sql/](sql/) | 初始化与升级脚本 |
| 📊 测试结果 | [test_results/](test_results/) | 自动化测试报告 |
| 💻 源代码 | [frontend/](frontend/) | Vue.js 前端 |
| ☕ 后端服务 | [lab-*/](lab-gateway/) | 6个 Spring Boot 微服务 |

## 服务端口（实际配置）

| 服务 | 端口 |
|------|------|
| 前端 (Vite) | 5173 |
| API 网关 | 8080 |
| 用户服务 | 8086 |
| 标本服务 | 8087 |
| 报告服务 | 8088 |
| HL7 服务 | 8084 |
| AI 服务 | 8089 |

> ⚠️ 旧文档中的 8081/8082/8083/8085 端口已过时，请参考上表。

## 快速启动

```bash
# 1. 初始化数据库
mysql -u root -p < sql/init.sql

# 2. 启动后端（各开一个窗口）
cd scripts && start-all-services.bat

# 3. 启动前端
cd frontend && npm install && npm run dev
```

**测试账号**：admin / admin123

## 文档索引

- [docs/README.md](docs/README.md) — 项目详细说明
- [docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md) — 完整项目文档
- [docs/DIRECTORY_STRUCTURE_GUIDE.md](docs/DIRECTORY_STRUCTURE_GUIDE.md) — 目录结构说明
- [docs/TESTING.md](docs/TESTING.md) — 集成测试指南

---

**作者**：孙亚鑫 | 华北水利水电大学 | 软件工程 202218506
