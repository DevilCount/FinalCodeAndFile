# 实验室管理系统(LIS) v1.3.0 - 系统版本信息

## 文档元信息

| 项目 | 内容 |
|------|------|
| **文档编号** | SYSTEM-VERSION-INFO-V1.3.0 |
| **系统名称** | 实验室管理系统 (Laboratory Information System, LIS) |
| **系统版本** | v1.3.0 |
| **版本类型** | 验收发布版 (Acceptance Release) |
| **构建日期** | 2026年4月2日 |
| **发布状态** | 有条件通过 (Conditional Pass) |

---

## 一、版本基本信息

| 属性 | 值 |
|------|-----|
| 版本号 | **v1.3.0** |
| 版本名称 | Acceptance Release (验收发布版) |
| 构建时间 | 2026-04-02 19:00:00 (UTC+8) |
| Git Commit Hash | *待确认*(本地开发环境) |
| 分支名称 | main/master |
| 构建工具 | Apache Maven 3.9.12 |
| JDK版本 | Oracle JDK 17.0.11 |
| Node.js版本 | 18.x / 20.x |
| 包管理器 | npm / pnpm |

### 版本号语义说明

```
v1.3.0
 │  │  └── 补丁版本: 0 (验收基线版本)
 │  └───── 次版本: 3 (经过3次主要迭代)
 └──────── 主版本: 1 (首个正式版本线)
```

---

## 二、技术栈版本清单

### 2.1 后端技术栈

| 技术 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| **Java** | 17 (LTS) | 运行时语言 | GPL-2.0 |
| **Spring Boot** | 3.2.0 | 应用框架基础 | Apache 2.0 |
| **Spring Cloud** | 2023.0.0 | 微服务框架 | Apache 2.0 |
| **Spring Cloud Alibaba** | 2023.0.1.2 | 阿里云微服务套件 | Apache 2.0 |
| **MyBatis Plus** | 3.5.7 | ORM持久层框架 | Apache 2.0 |
| **MySQL Connector** | 8.0.33 | JDBC驱动 | GPL-2.0 |
| **Redisson** | 3.24.3 | 分布式锁/Redis客户端 | Apache 2.0 |
| **Spring Security Crypto** | (随Boot) | BCrypt密码加密 | Apache 2.0 |
| **HikariCP** | (Boot内置) | 数据库连接池 | Apache 2.0 |
| **SpringDoc OpenAPI** | 2.x | Swagger/API文档 | Apache 2.0 |
| **Lombok** | 1.18.30 | 代码简化 | MIT |
| **Jackson** | (Boot内置) | JSON序列化 | Apache 2.0 |
| **Spring Boot Actuator** | (Boot内置) | 监控端点 | Apache 2.0 |
| **Nacos Client** | 2.2.3 | 服务注册发现 | Apache 2.0 |

### 2.2 前端技术栈

| 技术 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| **Vue.js** | 3.4.21 | 前端框架 | MIT |
| **TypeScript** | 5.4.3 | 类型系统 | Apache 2.0 |
| **Vite** | 5.2.6 | 构建工具 | MIT |
| **Element Plus** | 2.6.1 | UI组件库 | MIT |
| **Pinia** | 2.1.7 | 状态管理 | MIT |
| **Vue Router** | 4.x | 路由管理 | MIT |
| **Axios** | 1.x | HTTP客户端 | MIT |
| **ECharts** | 5.x | 图表可视化 | Apache 2.0 |
| **SCSS/SASS** | 最新版 | CSS预处理器 | MIT |
| **Playwright** | 1.58.2 | E2E测试框架 | Apache 2.0 |
| **@vue/test-utils** | 2.x | Vue单元测试工具 | MIT |

### 2.3 基础设施/中间件

| 组件 | 版本 | 用途 | 端口 |
|------|------|------|------|
| **MySQL** | 8.3 | 关系型数据库 | 3306 |
| **Redis** | 3.0.504 | 缓存/会话存储 | 6379 |
| **Nacos Server** | 2.2.3 | 服务注册发现/配置中心 | 8848 |
| **Chromium** | latest (Playwright) | E2E测试浏览器 | - |

### 2.4 开发工具链

| 工具 | 版本 | 用途 |
|------|------|------|
| IntelliJ IDEA / VS Code | 最新版 | IDE开发环境 |
| Maven | 3.9.12 | Java项目构建 |
| npm/pnpm | 最新版 | JavaScript包管理 |
| Git | 2.x | 版本控制 |
| PowerShell 5/7 | 内置 | Windows脚本执行 |

---

## 三、系统架构组件清单

### 3.1 微服务模块 (6个)

| 序号 | 模块名 | ArtifactId | 端口 | 核心职责 | 主要依赖 |
|------|--------|-----------|------|----------|----------|
| 1 | **Gateway网关** | lab-gateway | 8080 | API路由/跨域/限流 | Spring Cloud Gateway |
| 2 | **用户服务** | lab-user-service | 8081 | 用户认证/注册/CRUD | MyBatis Plus, BCrypt |
| 3 | **标本服务** | lab-sample-service | 8082 | 标本全生命周期管理 | MyBatis Plus, Redis |
| 4 | **报告服务** | lab-report-service | 8083 | 报告生成/审核/AI集成 | MyBatis Plus, OpenFeign |
| 5 | **AI诊断服务** | lab-ai-service | 8084 | 基于规则的智能诊断 | 自研规则引擎 |
| 6 | **HL7服务** | lab-hl7-service | 8085 | HIS系统集成(模拟) | HAPI HL7 (待引入) |

### 3.2 公共模块 (1个)

| 模块名 | ArtifactId | 核心内容 |
|--------|-----------|----------|
| **公共模块** | lab-common | 实体类、工具类、常量、异常处理、Redis配置、Feign配置、切面(AOP) |

### 3.3 前端应用 (1个)

| 属性 | 值 |
|------|-----|
| 项目名 | frontend (Vue SPA) |
| 开发端口 | 5173 (Vite Dev Server) |
| 构建产物 | dist/ 目录 |
| 页面数量 | 14个Vue组件 |
| 路由模式 | History Mode |

---

## 四、本次验收过程中修改的文件清单

### 4.1 新建文件

| 文件路径 | 类型 | 说明 | 创建原因 |
|----------|------|------|----------|
| `lab-user-service/src/main/java/com/sunyaxin/user/config/SecurityConfig.java` | Java源文件 | BCryptPasswordEncoder Bean配置 | 修复DEF-C001密码明文漏洞 |
| `TEST-REPORT-V1.3.0.md` | Markdown | 综合测试报告 | Phase 2测试结果汇总 |
| `FRONTEND-CODE-REVIEW-REPORT-V1.3.0.md` | Markdown | 前端代码审查报告 | Phase 1审查结果 |
| `BACKEND-CODE-REVIEW-REPORT-V1.3.0.md` | Markdown | 后端代码审查报告 | Phase 1审查结果 |
| `FINAL_SYSTEM_VERIFICATION_REPORT.md` | Markdown | 系统验证报告 | 验证辅助文档 |
| `ACCEPTANCE-DELIVERY-V1.3.0/*.md` | Markdown×7 | 验收交付文档包 | 本文档所在目录全部文件 |

### 4.2 修改文件

| 文件路径 | 修改类型 | 修改内容 | 关联缺陷 |
|----------|----------|----------|----------|
| `lab-user-service/src/main/java/com/sunyaxin/user/service/impl/UserServiceImpl.java` | **代码修改** | 注入PasswordEncoder，login()改用matches()，register()改用encode() | DEF-C001 |
| `lab-sample-service/src/main/java/com/sunyaxin/sample/controller/EnhancedSampleController.java` | **代码修改** | 取消@RestController和@RequestMapping注解的注释 | DEF-C003 |
| `frontend/tests/e2e/full-lab-flow.spec.cjs` | **测试调整** | E2E测试用例优化(如有) | TC-E2E-007 |
| `pom.xml` (根) | **依赖确认** | 确认spring-security-crypto依赖存在 | DEF-C001 |

### 4.3 未修改但标记需关注的文件

以下文件在审查中发现问题，计划在v1.4.0修改:

| 文件路径 | 问题简述 | 计划修改版本 |
|----------|----------|--------------|
| `frontend/src/views/auth/Login.vue` | 使用模拟数据登录 | v1.4.0 |
| `frontend/src/views/sample/create.vue` | 表单提交使用setTimeout模拟 | v1.4.0 |
| `lab-sample-service/src/main/java/com/sunyaxin/sample/service/impl/SampleServiceImpl.java` | searchSamples()全表查询 | v1.4.0 |
| `lab-common/src/main/java/com/sunyaxin/common/utils/CodeGenerator.java` | 4位随机数碰撞风险 | v1.4.0 |
| `lab-gateway/src/main/resources/application.yml` | CORS配置过于宽松 | v1.4.0 |
| `lab-report-service/src/main/java/com/sunyaxin/report/feign/AiServiceClient.java` | Feign路径不匹配 | v1.4.0 |

---

## 五、数据库变更记录

### 5.1 v1.3.0 数据库变更

| 变更类型 | 变更内容 | SQL文件 | 状态 |
|----------|----------|---------|------|
| DDL变更 | **无** | - | 无Schema变更 |
| DML变更 | **无** | - | 无数据迁移 |
| 说明 | 本次验收修复均为**纯代码层面修改**，未涉及数据库结构调整 | | |

### 5.2 数据库Schema概览

| 表名(推测) | 用途 | 关联服务 |
|------------|------|----------|
| user | 用户账号表 | lab-user-service |
| sample | 标本信息表 | lab-sample-service |
| sample_trace | 标本流转轨迹表 | lab-sample-service |
| report | 检验报告表 | lab-report-service |
| test_result | 检验结果明细表 | lab-report-service |
| patient | 患者信息表 | lab-common |
| device | 设备信息表 | lab-common |
| test_item | 检验项目字典表 | lab-common |
| sample_type | 标本类型字典表 | lab-common |
| operation_log | 操作日志表 | lab-common |
| sys_log | 系统日志表 | lab-common |
| panic_record | 危急值记录表 | lab-common |

> 详细DDL请参考: `sql/init.sql`, `sql/init-tables.sql`, `sql/upgrade_*.sql`

### 5.3 注意事项

**关于已有用户数据的密码兼容性**:

由于DEF-C001修复引入了BCrypt加密，现有数据库中以明文存储的用户密码将**无法通过新的matches()验证**。解决方案:

1. **方案A (推荐)**: 清空用户表，让所有用户重新注册(新密码自动BCrypt加密)
2. **方案B**: 编写数据迁移脚本，将现有明文密码批量encode为BCrypt哈希
3. **方案C**: 兼容模式——先尝试BCrypt匹配，失败再尝试明文匹配(临时过渡)

---

## 六、构建产物清单

### 6.1 后端JAR包

| 服务 | JAR文件 | 大小(约) | 位置 |
|------|---------|----------|------|
| Gateway | lab-gateway-1.0.0.jar | ~20MB | `lab-gateway/target/` |
| User Service | lab-user-service-1.0.0.jar | ~25MB | `lab-user-service/target/` |
| Sample Service | lab-sample-service-1.0.0.jar | ~30MB | `lab-sample-service/target/` |
| Report Service | lab-report-service-1.0.0.jar | ~28MB | `lab-report-service/target/` |
| AI Service | lab-ai-service-1.0.0.jar | ~22MB | `lab-ai-service/target/` |
| HL7 Service | lab-hl7-service-1.0.0.jar | ~22MB | `lab-hl7-service/target/` |
| Common (lib) | lab-common-1.0.0.jar | ~15MB | `lab-common/target/` |

### 6.2 前端构建产物

| 产物 | 位置 | 说明 |
|------|------|------|
| 开发服务器 | `http://localhost:5173` | Vite dev server |
| 生产构建 | `frontend/dist/` | 运行 `npm run build` 生成 |
| 估计大小 | ~300KB (gzip) | Vite tree-shaking优化后 |

### 6.3 测试产物

| 产物 | 位置 | 说明 |
|------|------|------|
| Surefire报告 | `lab-sample-service/target/surefire-reports/` | JUnit XML格式 |
| E2E截图 | `frontend/test-results/e2e-full-lab-flow-*/` | PNG图片+WebM录屏 |
| E2E JSON | `frontend/test-results/.last-run.json` | Playwright运行记录 |
| API测试JSON | `test_results/api-deep-test-v1.3.0.json` | API测试结果(待填充) |
| 性能测试JSON | `test_results/performance-benchmark-results.json` | 性能数据(待填充) |

---

## 七、依赖安全状态

### 7.1 已知依赖漏洞 (基于公开CVE数据库)

| 依赖 | 已知CVE | 严重程度 | 当前版本 | 修复版本 | 状态 |
|------|---------|----------|----------|----------|------|
| Spring Boot 3.2.0 | CVE-2024-xxx | Medium | 3.2.0 | 3.2.2+ | ⚠️ 建议升级 |
| Jackson-databind | CVE-2020-xxx | Low | (Boot内置) | 2.15.3+ | ✅ Boot已包含补丁 |
| MySQL Connector | CVE-2023-xxx | Low | 8.0.33 | 8.0.35+ | ⚠️ 建议升级 |

> **注意**: 以上为基于版本的通用风险评估，未经实际扫描工具验证。建议在v1.4.0中使用OWASP Dependency-Check或Snyk进行全面扫描。

### 7.2 许可证合规

本项目使用的所有开源依赖均采用**商业友好许可证**:
- ✅ Apache 2.0 (大部分Spring生态)
- ✅ MIT (Vue/Vite/Element Plus等前端库)
- ✅ GPL-2.0 (MySQL Connector, 仅链接无需开源自身代码)

---

## 八、版本兼容性

### 8.1 运行环境要求

| 环境 | 最低版本 | 推荐版本 | 测试版本 |
|------|----------|----------|----------|
| JDK | 17 | 17.0.11+ (LTS) | Oracle JDK 17.0.11 |
| Node.js | 18.x | 20.x LTS | 18.x / 20.x |
| MySQL | 8.0 | 8.3 | 8.3 |
| Redis | 6.x | 7.x | 3.0.504 (Windows兼容版) |
| OS | Windows 10/11, Ubuntu 20.04+, CentOS 8+ | Windows 11 / Ubuntu 22.04 LTS | Windows 11 |
| 内存 | 8GB | 16GB | 16GB |
| 磁盘 | 10GB可用 | 50GB SSD | SSD |

### 8.2 向前/向后兼容

| 场景 | 兼容性 | 说明 |
|------|--------|------|
| v1.3.0 → v1.4.0 | ✅ 兼容 | v1.4.0将在v1.3.0基础上增量修复 |
| v1.3.0 数据库 → v1.4.0 | ✅ 兼容 | v1.4.0不涉及DDL变更 |
| v1.3.0 API → v1.4.0 | ✅ 兼容 | v1.4.0不涉及API破坏性变更 |
| v1.3.0 前端 → v1.4.0 | ⚠️ 需适配 | Login.vue等页面将有较大改动 |

---

## 九、版本签名

```
╔═════════════════════════════════════════════════════════╗
║                                                          ║
║   实验室管理系统 (LIS)                                   ║
║   版本: v1.3.0                                          ║
║   类型: 验收发布版 (Acceptance Release)                  ║
║   状态: ⚠️ 有条件通过 (Conditional Pass)                ║
║   构建: 2026-04-02 19:00 CST                            ║
║   JDK: 17.0.11 (Oracle)                                 ║
║   Spring Boot: 3.2.0                                    ║
║   Vue: 3.4.21                                           ║
║                                                          ║
║   Build: SUCCESS                                        ║
║   Tests: 14/14 PASS (100%)                              ║
║   E2E: 8/9 PASS (88.9%)                                 ║
║                                                          ║
╚═════════════════════════════════════════════════════════╝
```

---

*文档编制: Project Manager AI Agent*  
*最后更新: 2026-04-02*  
*© 2026 实验室管理系统项目组*
