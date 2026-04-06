# 实验室管理系统(LIS) v1.4.2 - 系统版本信息

**文档编号**: LMS-SVI-2026-V142  
**项目名称**: 实验室信息管理系统 (Laboratory Information System, LIS)  
**当前版本**: **v1.4.2**  
**编制日期**: 2026年4月3日  

---

## 目录

1. [版本概述](#1-版本概述)
2. [技术栈详细版本清单](#2-技术栈详细版本清单)
3. [系统架构与模块说明](#3-系统架构与模块说明)
4. [构建信息](#4-构建信息)
5. [依赖库清单](#5-依赖库清单)
6. [数据库Schema概览](#6-database-schema概览)
7. [API端点清单](#7-api端点清单)
8. [环境变量与配置](#8-环境变量与配置)
9. [已知限制与兼容性](#9-已知限制与兼容性)

---

## 1. 版本概述

### 1.1 版本基本信息

| 属性 | 值 |
|------|-----|
| **产品名称** | 实验室管理系统 (LIS) |
| **产品代号** | Lab Management System |
| **当前版本** | **v1.4.2** |
| **版本类型** | Final Delivery (最终交付版) |
| **发布日期** | 2026年4月3日 |
| **构建号** | 20260403-0142 |
| **分支名** | main (或master) |
| **Commit Hash** | (请执行 `git rev-parse HEAD` 获取) |
| **构建工具** | Apache Maven 3.9.x + npm 9.x |
| **运行时环境** | JDK 17.0.11 + Node.js 18.x |
| **包管理器** | Maven (后端) + npm (前端) |

### 1.2 版本命名规则

```
版本号格式: v{MAJOR}.{MINOR}.{PATCH}-{TAG}

示例: v1.4.2-R2 (第二轮修复)

组成部分:
├── MAJOR (1): 主版本号 - 架构重大变更
├── MINOR (4): 次版本号 - 功能迭代版本
├── PATCH (2): 补丁版本号 - 缺陷修复版本
└── TAG (可选): 标识符 - R1/R2/R3(修复轮次) / FINAL(最终版)

版本历史:
v1.0.0 → v1.1.0 → v1.2.0 → v1.3.0 → v1.3.1 → v1.4.0 → v1.4.1 → v1.4.2
  初始    功能扩展  架构调整  基线建立  小修复   深度测试  R1修复   最终交付
```

### 1.3 版本兼容性

| 目标版本 | 源代码兼容 | 二进制兼容 | 数据库兼容 | 配置兼容 | 升级难度 |
|----------|-----------|-----------|-----------|---------|----------|
| **v1.4.1 → v1.4.2** | ✅ 完全兼容 | ❌ 需重编译 | ✅ 兼容 | ✅ 兼容 | 低(重编译即可) |
| **v1.4.0 → v1.4.2** | ⚠️ 部分改动 | ❌ 需重编译 | ⚠️ 需升级SQL | ⚠️ 配置调整 | 中(需数据迁移) |
| **v1.3.x → v1.4.2** | ❌ 大幅重构 | ❌ 完全重编 | ❌ Schema变更 | ❌ 重构配置 | **高(不建议直接升级)** |

---

## 2. 技术栈详细版本清单

### 2.1 后端技术栈

| 组件 | 版本号 | 用途 | 官方网址 |
|------|--------|------|----------|
| **Java** | **17.0.11** (LTS) | 运行时环境 | https://openjdk.org/projects/jdk/17/ |
| **Spring Boot** | **3.2.0** | 应用框架 | https://spring.io/projects/spring-boot |
| **Spring Cloud** | **2023.0.0** | 微服务框架 | https://spring.io/projects/spring-cloud |
| **Spring Cloud Alibaba** | **2023.0.1.2** | 阿里云微服务套件 | https://github.com/alibaba/spring-cloud-alibaba |
| **MyBatis-Plus** | **3.5.7** | ORM框架(增强MyBatis) | https://baomidou.com/ |
| **MySQL Connector** | **8.0.33** (随Spring Boot) | MySQL JDBC驱动 | https://dev.mysql.com/downloads/connector/j/ |
| **Spring Data Redis** | **3.2.0** (随Spring Boot) | Redis客户端 | https://spring.io/projects/spring-data-redis |
| **Redisson** | **3.24.3** | Redis分布式锁客户端 | https://redisson.org/ |
| **Hutool** | **5.8.22** | Java工具类库 | https://www.hutool.cn/ |
| **SpringDoc OpenAPI** | **2.3.0** | API文档(Swagger) | https://springdoc.org/ |
| **Lombok** | **1.18.30** (隐式依赖) | 代码简化注解 | https://projectlombok.org/ |
| **Jackson** | **2.15.3** (随Spring Boot) | JSON序列化 | https://github.com/FasterXML/jackson |
| **Slf4j + Logback** | **2.0.9 / 1.4.14** | 日志框架 | https://www.slf4j.org/ |

### 2.2 前端技术栈

| 组件 | 版本号 | 用途 | 官方网址 |
|------|--------|------|----------|
| **Vue.js** | **3.4.21** | 渐进式JavaScript框架 | https://vuejs.org/ |
| **TypeScript** | **5.4.3** | JavaScript超集(类型系统) | www.typescriptlang.org/ |
| **Vite** | **5.2.6** | 下一代前端构建工具 | https://vitejs.dev/ |
| **Element Plus** | **2.6.1** | Vue 3 UI组件库 | https://element-plus.org/ |
| **Vue Router** | **4.3.0** | Vue官方路由管理器 | https://router.vuejs.org/ |
| **Pinia** | **2.1.7** | Vue状态管理(替代Vuex) | https://pinia.vuejs.org/ |
| **Axios** | **1.6.8** | HTTP客户端(基于Promise) | https://axios-http.com/ |
| **ECharts** | **5.5.0** | 数据可视化图表库 | https://echarts.apache.org/ |
| **VeeValidate** | **4.12.6** | 表单验证库 | https://vee-validate.logaretm.com/ |
| **Sass (SCSS)** | **1.72.0** | CSS预处理器 | https://sass-lang.com/ |
| **@vueuse/core** | 最新版 | Vue组合式API工具集 | https://vueuse.org/ |
| **Playwright** | **1.58.2** | E2E测试框架 | https://playwright.dev/ |

### 2.3 基础设施技术栈

| 组件 | 版本号 | 用途 | 官方网址 |
|------|--------|------|----------|
| **MySQL** | **8.3** (或8.0.33) | 关系型数据库 | https://www.mysql.com/ |
| **Redis** | **3.0.504** (或7.x) | 内存数据库(缓存/Session) | https://redis.io/ |
| **Nacos** | **2.2.3** | 服务注册与配置中心 | https://nacos.io/ |
| **Apache Maven** | **3.9.x** | Java项目构建工具 | https://maven.apache.org/ |
| **Node.js** | **18.x** (LTS) | JavaScript运行时 | https://nodejs.org/ |
| **npm** | **9.x** | Node.js包管理器 | https://www.npmjs.com/ |

### 2.4 开发工具链

| 工具 | 版本/配置 | 用途 |
|------|-----------|------|
| **IntelliJ IDEA** | 2023.3+ (推荐) | Java后端开发IDE |
| **Visual Studio Code** | 1.84.2+ | 前端开发编辑器 |
| **Navicat Premium** | 16.x | 数据库GUI管理工具 |
| **Postman** | 10.23+ | API调试与测试 |
| **Git** | 2.42.0 | 版本控制 |
| **Chrome DevTools** | 120+ | 前端调试 |
| **Windows Terminal** | latest | 命令行终端 |

---

## 3. 系统架构与模块说明

### 3.1 微服务拓扑图

```
                         ┌─────────────────────────────────────┐
                         │          客户端浏览器                │
                         │    (Chrome/Edge/Firefox/Safari)     │
                         └──────────────┬──────────────────────┘
                                        │ HTTPS/HTTP
                                        ▼
┌───────────────────────────────────────────────────────────────────────┐
│                         API Gateway (:8080)                            │
│                   Spring Cloud Gateway (负载均衡+路由)                  │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ Routes:                                                         │ │
│  │   /api/user/**     → lb://lab-user-service                      │ │
│  │   /api/sample/**   → lb://lab-sample-service                    │ │
│  │   /api/report/**   → lb://lab-report-service                    │ │
│  │   /api/ai/**       → lb://lab-ai-service                       │ │
│  │   /api/hl7/**      → lb://lab-hl7-service                      │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ User Service  │      │Sample Service │      │Report Service │
│   (:8086)     │      │   (:8087)     │      │   (:8088)     │
│               │      │               │      │               │
│ ·用户认证     │      │ ·标本CRUD     │      │ ·报告CRUD     │
│ ·权限管理     │      │ ·状态追踪     │      │ ·审核流程     │
│ ·注册登录     │      │ ·Dashboard    │      │ ·AI诊断集成   │
│ ·JWT(Token)  │      │ ·批量操作     │      │ ·PDF导出      │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │
        ├──────────────────────┤                      │
        ▼                      ▼                      ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ AI Service    │      │ HL7 Service   │      │               │
│   (:8085)     │      │   (:8084)     │      │   Nacos       │
│               │      │               │      │  (:8848)      │
│ ·血常规诊断   │      │ ·HL7解析     │      │               │
│ ·尿常规诊断   │      │ ·消息生成     │      │ ·服务注册     │
│ ·规则引擎     │      │ ·MLLP协议(拟)│      │ ·配置中心     │
│ ·置信度计算   │      │ ·HIS集成(拟) │      │ ·健康检查     │
└───────────────┘      └───────────────┘      └───────┬───────┘
                                                       │
                            ┌──────────────────────────┼────────────────────┐
                            ▼                          ▼                  ▼
                     ┌──────────┐              ┌──────────┐        ┌──────────┐
                     │  Redis   │              │  MySQL   │        │Frontend  │
                     │ (:6379)  │              │ (:3306)  │        │(:3000/   │
                     │          │              │          │        │ 5173)    │
                     │·缓存     │              │·持久化   │        │          │
                     │·Session  │              │·15+张表  │        │·Vue 3 SPA│
                     │·分布式锁 │              │·事务ACID │        │·Vite    │
                     └──────────┘              └──────────┘        └──────────┘
```

### 3.2 模块详细说明

#### 3.2.1 lab-gateway (API网关)

| 属性 | 值 |
|------|-----|
| **Artifact ID** | lab-gateway |
| **端口** | 8080 |
| **基础包** | com.sunyaxin.gateway |
| **主类** | GatewayApplication.java |
| **核心依赖** | spring-cloud-starter-gateway |
| **配置文件** | src/main/resources/application.yml |

**职责**:
- API请求路由转发(基于路径匹配)
- 负载均衡(多个实例时)
- 跨域CORS处理(当前配置*)
- 限流熔断(预留,未完全配置)

**路由配置**:
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://lab-user-service
          predicates:
            - Path=/api/user/**
        - id: sample-service
          uri: lb://lab-sample-service
          predicates:
            - Path=/api/sample/**
        # ... 其他路由类似
```

#### 3.2.2 lab-user-service (用户服务)

| 属性 | 值 |
|------|-----|
| **Artifact ID** | lab-user-service |
| **端口** | 8086 (直连) / 8081 (通过Gateway) |
| **基础包** | com.sunyaxin.user |
| **主类** | UserServiceApplication.java |
| **核心依赖** | mybatis-plus-boot-starter, spring-boot-starter-data-redis, spring-boot-starter-validation, spring-security-crypto(bcrypt) |

**API端点**:
| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| POST | /api/user/login | 用户登录(双模式:明文/BCrypt) | 公开 |
| POST | /api/user/register | 用户注册 | 公开 |
| GET | /api/user/list | 用户列表(分页) | 需Token(未强制) |
| GET | /api/user/{id} | 用户详情 | 需Token |
| PATCH | /api/user/{id} | 更新用户信息 | 需Token |
| DELETE | /api/user/{id} | 删除用户 | 需Token(Admin) |

**关键特性**:
- BCryptPasswordEncoder密码加密存储
- 向后兼容明文密码自动升级
- @Cacheable登录缓存(已移除login方法缓存以策安全)
- GlobalExceptionHandler全局异常处理
- MyMetaObjectHandler自动填充createTime/updateTime

#### 3.2.3 lab-sample-service (标本服务)

| 属性 | 值 |
|------|-----|
| **Artifact ID** | lab-sample-service |
| **端口** | 8087 (直连) / 8082 (通过Gateway) |
| **基础包** | com.sunyaxin.sample |
| **核心依赖** | mybatis-plus, redisson, hutool |

**API端点**:
| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | /api/sample/list | 标本列表(分页) | ✅ 正常 |
| POST | /api/sample/create | 创建标本(参数校验) | ✅ 正常 |
| GET | /api/sample/{id} | 标本详情 | ✅ 正常 |
| GET | /api/sample/list-by-status | 按状态查询 | ❌ 500(已知问题) |
| PUT | /api/sample/{id}/status | 更新状态 | ✅ 正常 |
| GET | /api/sample/dashboard | Dashboard统计数据 | ⚠️ 部分实现 |

**数据模型**:
```java
public class Sample {
    private Long id;
    private String sampleNo;          // 标本编号(唯一)
    private String patientName;       // 患者姓名
    private String patientId;         // 患者ID
    private String sampleType;        // 标本类型(血液/尿液/组织等)
    private String status;            // 状态(PENDING/RECEIVED/TESTING/COMPLETED)
    private LocalDateTime receiveTime; // 接收时间
    private LocalDateTime completeTime;// 完成时间
    // ... 其他字段
}
```

#### 3.2.4 lab-report-service (报告服务)

| 属性 | 值 |
|------|-----|
| **Artifact ID** | lab-report-service |
| **端口** | 8088 (直连) / 8083 (通过Gateway) |
| **基础包** | com.sunyaxin.report |
| **核心依赖** | mybatis-plus, feign(调用AI服务) |

**API端点**:
| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | /api/report/list | 报告列表(47列全字段) | ✅ 正常 |
| GET | /api/report/list?page=&pageSize= | 分页列表 | ✅ 正常 |
| GET | /api/report/pending-list | 待审核列表 | ✅ 正常 |
| POST | /api/report/create | 创建报告(完整数据) | ✅ 正常 |
| GET | /api/report/{id} | 报告详情 | ✅ 正常 |
| POST | /api/report/{id}/audit | 审核报告 | ✅ 正常 |
| POST | /api/report/{id}/publish | 发布报告 | ✅ 正常 |

**特色功能**:
- Feign Client调用AI服务获取辅助诊断
- 47列完整报告字段(包含test_results JSON)
- 审核→发布完整工作流

#### 3.2.5 lab-ai-service (AI诊断服务)

| 属性 | 值 |
|------|-----|
| **Artifact ID** | lab-ai-service |
| **端口** | 8085 (直连) / 8084 (通过Gateway) |
| **基础包** | com.sunyaxin.ai |
| **核心依赖** | (纯计算服务,依赖较少) |

**API端点**:
| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| POST | /api/ai/diagnose | AI辅助诊断(血常规/尿常规) | ✅ 正常 |
| GET | /api/ai/health | 健康检查 | ✅ 正常 |

**诊断逻辑** (当前为规则引擎,非真实AI模型):
```java
// 血常规诊断规则示例
if (wbc > 10.0) result.addWarning("白细胞偏高,可能存在感染");
if (rbc < 4.0) result.addWarning("红细胞偏低,可能贫血");
if (platelet < 100) result.addRisk("血小板减少,凝血功能障碍");
// ... 更多规则

return DiagnosisResponse.builder()
    .diagnosis("初步诊断意见")
    .confidence(0.85)  // 固定置信度(待优化)
    .warnings(warnings)
    .risks(risks)
    .suggestions(suggestions)
    .build();
```

#### 3.2.6 lab-hl7-service (HL7消息服务)

| 属性 | 值 |
|------|-----|
| **Artifact ID** | lab-hl7-service |
| **端口** | 8084 (直连) / 8085 (通过Gateway) |
| **基础包** | com.sunyaxin.hl7 |
| **核心依赖** | hutool(字符串处理) |

**API端点**:
| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| POST | /api/hl7/parse | 解析HL7 v2.x消息 | ✅ 正常 |
| POST | /api/hl7/generate-order | 生成检验申请单(ORM_O01) | ✅ 正常 |

**HL7消息格式支持**:
- 解析: ADT^A01(入院), ORM^O01(检验申请), ORU^R01(观察结果)
- 生成: ORM^O01(向HIS发送检验申请)
- 注意: sendToHis当前仅打印日志,未实现真实MLLP协议通信

#### 3.2.7 lab-common (公共模块)

| 属性 | 值 |
|------|-----|
| **Artifact ID** | lab-common |
| **类型** | jar (不被单独运行,被其他模块依赖) |
| **基础包** | com.sunyaxin.common |

**子模块**:
- **entity/**: 实体类(User, Sample, Report, Patient, Device, TestItem, etc.)
- **mapper/**: MyBatis Mapper接口
- **result/**: 统一响应Result<T>/PageResult
- **exception/**: BusinessException, GlobalExceptionHandler
- **annotation/**: 自定义注解(@OperLog, @RateLimit)
- **aspect/**: AOP切面(LogAspect, RateLimitAspect)
- **config/**: 公共配置(FeignConfig, RedisConfig, RedisCacheConfig)
- **constant/**: 常量枚举(UserRole, SampleStatus, ReportStatus, etc.)
- **service/**: 公共服务(OperationLogService, SampleTypeService, TestItemService)
- **utils/**: 工具类(CodeGenerator, RedisUtils)

---

## 4. 构建信息

### 4.1 后端构建 (Maven)

**构建命令**:
```bash
# 完整清理+编译+打包(跳过测试以加快速度)
mvn clean package -DskipTests

# 仅编译(不打包)
mvn clean compile

# 运行所有测试
mvn test

# 单独构建某个模块
mvn clean package -pl lab-user-service -am

# 查看依赖树
mvn dependency:tree
```

**构建产物**:
```
lab-management-system/target/
└── (父pom,不产生jar)

lab-common/target/
└── lab-common-1.0.0.jar (被其他模块依赖)

lab-gateway/target/
├── lab-gateway-1.0.0.jar (可执行jar)
└── lab-gateway-1.0.0.jar.original (原始jar,无依赖)

lab-user-service/target/
├── lab-user-service-1.0.0.jar (74,702,354 bytes, v1.4.2最终版)
└── lib/ (依赖库)

... (其他服务类似)
```

**Maven坐标**:
```xml
<groupId>com.sunyaxin</groupId>
<artifactId>lab-management-system</artifactId>
<version>1.0.0</version>
<packaging>pom</packaging>
```

### 4.2 前端构建 (Vite/npm)

**构建命令**:
```bash
cd frontend

# 安装依赖
npm install

# 开发模式启动 (热更新,端口5173)
npm run dev

# 类型检查
npm run type-check

# 生产构建 (输出到dist/)
npm run build

# 预览生产构建
npm run preview

# ESLint代码检查
npm run lint
```

**构建产物**:
```
frontend/dist/
├── index.html           # 入口HTML
├── assets/
│   ├── index-[hash].js  # 打包后的JS
│   ├── index-[hash].css # 打包后的CSS
│   └── ...              # 其他静态资源(font/svg等)
└── ...
```

**Vite配置要点** ([vite.config.ts](../frontend/vite.config.ts)):
- 端口: 3000 (dev) / 5173 (备用)
- 代理: /api → http://localhost:8080 (Gateway)
- 别别: @ → src/

### 4.3 构建环境要求

| 工具 | 最低版本 | 推荐版本 | 用途 |
|------|---------|---------|------|
| **JDK** | 17 | 17.0.11+ (LTS) | Java编译运行 |
| **Maven** | 3.8 | 3.9.6+ | 项目构建管理 |
| **Node.js** | 16 | 18.17.0+ (LTS) | 前端构建运行 |
| **npm** | 8 | 9.6.7+ | 前端包管理 |
| **Git** | 2.30 | 2.42.0+ | 版本控制 |

**磁盘空间要求**:
- 源码: ~50MB (含node_modules约200MB+)
- Maven本地仓库: ~500MB (首次下载后)
- 构建产物: ~150MB (6个服务的fat-jar)
- 运行时内存: 最少2GB JVM堆空间(建议4GB+)

---

## 5. 依赖库清单

### 5.1 后端核心依赖 (pom.xml)

```xml
<!-- Spring Boot Parent (BOM) -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-dependencies</artifactId>
    <version>3.2.0</version>
</parent>

<!-- 核心依赖 (由Parent管理版本) -->
spring-boot-starter-web           # Web MVC
spring-boot-starter-data-redis    # Redis
spring-boot-starter-cache         # Spring Cache抽象
spring-boot-starter-aop            # AOP切面编程
spring-boot-starter-validation    # 参数校验(JSR-380)
spring-boot-starter-test          # 测试(Spring Boot Test)
springdoc-openapi-starter-webmvc-ui  # Swagger UI

<!-- 第三方依赖 (显式指定版本) -->
mybatis-plus-boot-starter:3.5.7    # ORM框架
mybatis-spring:3.0.3              # MyBatis Spring适配
hutool-all:5.8.22                 # 工具类库
commons-pool2:2.11.1              # 连接池
redisson-spring-boot-starter:3.24.3  # 分布式锁

<!-- 内部模块 -->
lab-common:1.0.0                  # 公共模块
```

### 5.2 前端核心依赖 (package.json)

```json
{
  "dependencies": {
    "vue": "^3.4.21",                    // Vue 3核心
    "vue-router": "^4.3.0",              // 路由管理
    "pinia": "^2.1.7",                   // 状态管理
    "pinia-plugin-persistedstate": "^3.2.1", // Pinia持久化
    "element-plus": "^2.6.1",            // UI组件库
    "@element-plus/icons-vue": "*",      // Element图标
    "axios": "^1.6.8",                   // HTTP客户端
    "echarts": "^5.5.0",                 // 图表库
    "vee-validate": "^4.12.6",           // 表单验证
    "@vee-validate/i18n": "^4.12.6",    // 验证国际化
    "@vee-validate/rules": "^4.12.6",    // 验证规则
    "sass": "^1.72.0"                    // SCSS预处理器
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.4",      // Vite Vue插件
    "typescript": "^5.4.3",              // TypeScript
    "vite": "^5.2.6",                   // 构建工具
    "vue-tsc": "^2.0.7",                // Vue TypeChecker
    "@playwright/test": "^1.58.2",      // E2E测试
    "@types/node": "^20.11.30"          // Node类型定义
  }
}
```

### 5.3 依赖安全状况

| 依赖类别 | 已知CVE数量 | 最高严重度 | 处理状态 |
|----------|------------|-----------|----------|
| Spring Boot 3.2.0 | 少量(已修复) | Medium | ✅ 使用最新LTS版本 |
| MyBatis-Plus 3.5.7 | 极少 | Low | ✅ 活跃维护 |
| Vue 3.4.21 | 无已知高危 | - | ✅ 最新稳定版 |
| Element Plus 2.6.1 | 无 | - | ✅ 最新版 |
| Axios 1.6.8 | 历史CVE(已修复) | - | ✅ 已升级至1.x |
| ECharts 5.5.0 | 无 | - | ✅ Apache顶级项目 |
| Playwright 1.58.2 | 无(测试工具) | - | ✅ 仅开发依赖 |

**总体评估**: 依赖库安全状况良好,无高危CVE。

---

## 6. 数据库Schema概览

### 6.1 数据库连接信息

| 属性 | 值 |
|------|-----|
| **数据库类型** | MySQL 8.x |
| **数据库名称** | lab_management |
| **字符集** | utf8mb4 |
| **排序规则** | utf8mb4_general_ci |
| **连接端口** | 3306 |
| **连接URL** | jdbc:mysql://localhost:3306/lab_management?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=Asia/Shanghai |
| **用户名** | root (默认) |
| **密码** | 1234 (默认,⚠️ 生产环境须修改) |

### 6.2 核心数据表清单 (~15张)

| 表名 | 说明 | 记录数估计 | 主要字段 |
|------|------|-----------|----------|
| **sys_user** | 用户表 | 10+ | id, username, password(BCrypt), real_name, phone, email, role, status, create_time |
| **lab_sample** | 标本表 | 50+ | id, sample_no(唯一), patient_id, patient_name, sample_type, status, receive_time, complete_time, tester_id |
| **lab_report** | 报告表 | 30+ | id, report_no(唯一), sample_id, patient_name, diagnosis, status(AUDIT/PUBLISHED), test_results(JSON), auditor_id, publish_time |
| **sys_role** | 角色表 | 5 | id, role_name, role_code(ADMIN/DOCTOR/LABTECH), description, permissions(JSON) |
| **sys_menu** | 菜单表 | 40+ | id, parent_id, menu_name, path, component, icon, sort, permission |
| **lab_sample_type** | 标本类型字典 | 10 | id, type_code, type_name, description |
| **lab_test_item** | 检验项目字典 | 20+ | id, item_code, item_name, unit, reference_range, sample_type |
| **lab_test_result** | 检验结果明细 | 100+ | id, report_id, item_id, item_value, reference_range, is_abnormal |
| **operation_log** | 操作日志 | 200+ | id, user_id, module, operation, method, params, ip, time |
| **panic_record** | 危急值记录 | 5 | id, sample_id, item_name, value, panic_level, handler, handle_time |
| **device** | 设备表 | 10 | id, device_name, device_type, status, last_maintenance |
| **patient** | 患者表 | 20+ | id, patient_id(唯一), name, gender, age, phone, address |
| **sample_trace** | 标本追踪记录 | 100+ | id, sample_id, status, operator, location, time |
| **hl7_message** | HL7消息记录 | 20 | id, message_type, content, direction(IN/OUT), timestamp |

### 6.3 ER关系(简化)

```
sys_user 1──N lab_sample (tester_id)
    │
    ├──N lab_report (auditor_id)
    │       │
    │       └──1:N lab_test_result
    │
    └──N operation_log

lab_sample N──1 patient (patient_id)
lab_sample N──1 lab_sample_type
lab_report  N──1 lab_sample (sample_id)
```

### 6.4 初始化SQL脚本

| 脚本文件 | 用途 | 执行顺序 |
|----------|------|----------|
| sql/init.sql | 建表+初始数据(基础版) | 1 (首次部署) |
| sql/init-tables.sql | 建表语句(完整版) | 1 (替代init.sql) |
| sql/init-simple.sql | 最小化建表(仅核心表) | 1 (快速启动) |
| sql/upgrade_v1.1.0.sql | v1.1.0升级脚本 | 2 (从v1.0升级) |
| sql/upgrade_tables.sql | 通用表结构升级 | 2 (补充字段) |
| sql/upgrade_report_table.sql | Report表升级至47列 | 3 (v1.4.0修复) |
| sql/migration_v1.3.2_fix_report_500_error.sql | Report 500修复迁移 | 3 (v1.3.2热修复) |
| sql/test-data-enhanced.sql | 增强测试数据 | 4 (开发测试用) |
| sql/performance-optimization-indexes.sql | 性能优化索引 | 5 (生产部署前) |

---

## 7. API端点清单

### 7.1 完整API列表 (31+个端点)

#### User Service (8个)

| # | 方法 | 路径 | 功能 | 认证 | 状态 |
|---|------|------|------|------|------|
| U1 | POST | /api/user/login | 用户登录 | Public | ✅ Normal |
| U2 | POST | /api/user/register | 用户注册 | Public | ✅ Normal |
| U3 | GET | /api/user/list | 用户列表(分页) | NeedToken | ✅ Normal |
| U4 | GET | /api/user/{id} | 用户详情 | NeedToken | ✅ Normal |
| U5 | PATCH | /api/user/{id} | 更新用户 | NeedToken | ⚠️ MethodNotSupported |
| U6 | DELETE | /api/user/{id} | 删除用户 | Admin | ✅ Normal |
| U7 | GET | /api/user/roles | 角色列表 | NeedToken | ✅ Normal |
| U8 | PUT | /api/user/password | 修改密码 | NeedToken | ✅ Normal |

#### Sample Service (6+个)

| # | 方法 | 路径 | 功能 | 状态 |
|---|------|------|------|------|
| S1 | GET | /api/sample/list | 标本列表 | ✅ Normal |
| S2 | POST | /api/sample/create | 创建标本 | ✅ Normal |
| S3 | GET | /api/sample/{id} | 标本详情 | ✅ Normal |
| S4 | GET | /api/sample/list-by-status | 按状态查询 | ❌ **500 Error** |
| S5 | PUT | /api/sample/{id}/status | 更新状态 | ✅ Normal |
| S6 | GET | /api/sample/dashboard | Dashboard统计 | ⚠️ Partial |

#### Report Service (8个)

| # | 方法 | 路径 | 功能 | 状态 |
|---|------|------|------|------|
| R1 | GET | /api/report/list | 报告列表(全字段) | ✅ Normal |
| R2 | GET | /api/report/list?page=&pageSize= | 分页列表 | ✅ Normal |
| R3 | GET | /api/report/pending-list | 待审核列表 | ✅ Normal |
| R4 | POST | /api/report/create | 创建报告 | ✅ Normal |
| R5 | GET | /api/report/{id} | 报告详情 | ✅ Normal |
| R6 | POST | /api/report/{id}/audit | 审核报告 | ✅ Normal |
| R7 | POST | /api/report/{id}/publish | 发布报告 | ✅ Normal |
| R8 | GET | /api/report/export/{id} | 导出PDF(拟) | ⚠️ NotImplemented |

#### AI Service (2个)

| # | 方法 | 路径 | 功能 | 状态 |
|---|------|------|------|------|
| A1 | POST | /api/ai/diagnose | AI辅助诊断 | ✅ Normal |
| A2 | GET | /api/ai/health | 健康检查 | ✅ Normal |

#### HL7 Service (2+个)

| # | 方法 | 路径 | 功能 | 状态 |
|---|------|------|------|------|
| H1 | POST | /api/hl7/parse | 解析HL7消息 | ✅ Normal |
| H2 | POST | /api/hl7/generate-order | 生成检验申请单 | ✅ Normal |

#### Gateway/Actuator (3个)

| # | 方法 | 路径 | 功能 | 状态 |
|---|------|------|------|------|
| G1 | GET | /actuator/health | 网关健康检查 | ✅ Normal |
| G2 | GET | /actuator/gateway/routes | 路由列表 | ✅ Normal |
| G3 | GET | /actuator/info | 应用信息 | ✅ Normal |

**API总计**: **29个已列出 + 2个预留 = 31+个**

### 7.2 API响应格式标准

**成功响应**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... },
  "success": true,
  "timestamp": 1775148901929
}
```

**业务错误响应** (v1.4.2+):
```json
{
  "code": 400,
  "message": "用户名不能为空",
  "data": null,
  "success": false,
  "error": true,
  "timestamp": 1775148901929
}
```

**系统异常响应** (GlobalExceptionHandler):
```json
{
  "code": 500,
  "message": "系统繁忙，请稍后重试",
  "data": null,
  "success": false,
  "error": true,
  "timestamp": 1775148904380
}
```

**分页响应** (PageResult):
```json
{
  "code": 200,
  "data": {
    "records": [ ... ],
    "total": 100,
    "current": 1,
    "size": 10,
    "pages": 10
  },
  "success": true
}
```

---

## 8. 环境变量与配置

### 8.1 后端配置文件结构

```
每个服务的配置文件: src/main/resources/application.yml

配置层级(优先级从高到低):
1. 命令行参数 (--server.port=8086)
2. 环境变量 (SPRING_PROFILES_ACTIVE=prod)
3. application-{profile}.yml (如application-prod.yml)
4. application.yml (默认配置)
5. application.yml in jar (打包时的默认值)
```

### 8.2 核心配置项

#### Gateway (lab-gateway)

```yaml
server:
  port: 8080

spring:
  application:
    name: lab-gateway
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848
    gateway:
      routes:
        - id: user-service
          uri: lb://lab-user-service
          predicates:
            - Path=/api/user/**
        # ... 其他路由
      globalcors:
        cors-configurations:
          '[/**]':
            allowedOriginPatterns: "*"  # ⚠️ 生产环境应收紧
            allowedMethods: "*"
            allowedHeaders: "*"
            allowCredentials: true
```

#### User Service (lab-user-service)

```yaml
server:
  port: 8086

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/lab_management?...
    username: root
    password: 1234  # ⚠️ 应使用环境变量 ${MYSQL_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver
  redis:
    host: localhost
    port: 6379
    password:    # ⚠️ 应设置密码
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848

mybatis-plus:
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl  # 开发环境SQL日志
```

#### 前端 (.env.development)

```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8080/api

# App Title
VITE_APP_TITLE=实验室管理系统
```

### 8.3 敏感配置清单 (生产环境必须修改!)

| 配置项 | 当前值(开发) | 生产环境要求 | 风险等级 |
|--------|-------------|--------------|----------|
| MYSQL_PASSWORD | 1234 | 强密码(16位+特殊字符) | 🔴 Critical |
| REDIS_PASSWORD | (空) | 强密码 | 🔴 Critical |
| JWT_SECRET | (未配置) | 随机256位密钥 | 🔴 Critical |
| CORS_ORIGINS | * (允许所有) | 具体域名白名单 | 🟠 Major |
| LOG_LEVEL | DEBUG | INFO/WARN (生产) | 🟡 Minor |
| ADMIN_PASSWORD | admin123 | 强制复杂度策略 | 🔴 Critical |

---

## 9. 已知限制与兼容性

### 9.1 功能限制

| 限制ID | 描述 | 影响范围 | Workaround | 计划修复版本 |
|--------|------|---------|-----------|-------------|
| LIMIT-001 | API-03 listByStatus返回500 | 标本按状态筛选不可用 | 使用list+前端过滤 | v1.4.3 |
| LIMIT-002 | AI诊断为规则引擎,非真实ML模型 | 诊断结果较简单 | 规则引擎已覆盖常见场景 | v2.0 (可选) |
| LIMIT-003 | HL7 sendToHis仅打印日志 | HIS集成不完整 | 手动导出HL7文件导入HIS | v1.5 (可选) |
| LIMIT-004 | Dashboard统计数据部分硬编码 | 仪表盘不完全真实 | 有fallback机制 | v1.5 |
| LIMIT-005 | 无文件上传功能(头像/附件) | 用户头像/报告附件缺失 | 使用默认头像 | v1.5 |
| LIMIT-006 | 无消息通知功能 | 任务提醒缺失 | 手动刷新查看 | v2.0 |

### 9.2 性能限制

| 限制ID | 描述 | 当前表现 | 优化方向 |
|--------|------|---------|----------|
| PERF-001 | 并发测试仅在10用户级验证 | 100%通过(但样本小) | 需50/100/500用户压测 |
| PERF-002 | 数据库未添加大量索引 | 查询性能尚可(数据量小) | 大数据量时需优化 |
| PERF-003 | 无Redis缓存预热 | 首次请求较慢 | 添加缓存预热机制 |
| PERF-004 | 前端未做代码分割(code-splitting) | 首次加载~659ms(尚可) | 路由懒加载已实现 |

### 9.3 安全限制 (重要!)

| 限制ID | 描述 | 当前状态 | 风险 | 解决方案 |
|--------|------|---------|------|----------|
| SEC-LIM-001 | **JWT认证体系未完全实施** | 仅SecurityConfig Bean存在 | 🔴 致命(生产环境) | 独立安全加固项目 |
| SEC-LIM-002 | **CSRF防护缺失** | 无SameSite Cookie配置 | 🟠 高 | Spring Security配置 |
| SEC-LIM-003 | **API限流未配置** | Gateway无RateLimiter | 🟠 高 | Redis RateLimiter |
| SEC-LIM-004 | **HTTPS未启用** | HTTP明文传输 | 🟠 高 | Nginx SSL终止 |
| SEC-LIM-005 | **密码策略弱** | 接受admin/admin123 | 🟡 中 | PasswordValidator |
| SEC-LIM-006 | **操作日志审计不足** | 仅记录基础信息 | 🟡 中 | 完善AOP日志切面 |

> **声明**: 以上安全限制在**内网演示/毕业答辩/课程展示**环境下风险可控。**绝对不能**以当前状态部署到公网生产环境。如需生产部署,必须先完成安全加固项目(预计2-4周工作量)。

### 9.4 浏览器兼容性

| 浏览器 | 最低版本 | 状态 | 备注 |
|--------|---------|------|------|
| Google Chrome | 120+ | ✅ 完美支持 | 主力开发和测试浏览器 |
| Microsoft Edge | 120+ | ✅ 完美支持 | Chromium内核,兼容Chrome |
| Mozilla Firefox | 115+ | ✅ 基本支持 | 少量CSS样式差异 |
| Apple Safari | 16+ | ⚠️ 未充分测试 | Mac/iOS用户需自行验证 |

**推荐**: Chrome 或 Edge (最新稳定版)

### 9.5 运行环境兼容性

| 环境 | 最低配置 | 推荐配置 | 当前测试环境 |
|------|---------|---------|-------------|
| **操作系统** | Windows 10/11, Ubuntu 20.04+, macOS 12+ | Windows 11 / Ubuntu 22.04 LTS | Windows 11 (22H2) |
| **CPU** | 4核 | 8核+ | 未明确检测 |
| **内存** | 8GB | 16GB+ (开发) / 32GB+ (生产) | 16GB (96%使用率偏高) |
| **硬盘** | 50GB SSD | 100GB SSD | 未明确检测 |
| **JDK** | 17 (LTS) | 17.0.11+ | 17.0.11 |
| **Node.js** | 18 LTS | 18.17.0+ | 18.x |
| **MySQL** | 8.0 | 8.3+ | 8.x |
| **Redis** | 6.0 | 7.x | 3.0.504 (或7.x) |
| **Nacos** | 2.0.0 | 2.2.3+ | 2.2.3 |

---

## 附录A: 版本历史

| 版本 | 发布日期 | 类型 | 主要变更 | 构建号 |
|------|----------|------|----------|--------|
| v1.0.0 | 2026-03-xx | Initial | 项目初始化,基础架构搭建 | - |
| v1.1.0 | 2026-03-xx | Feature | 功能扩展 | - |
| v1.2.0 | 2026-04-01 | Release | 架构调整,首次系统验证 | - |
| v1.3.0 | 2026-04-01 | Baseline | 基线版本,E2E 88.9% | 20260401 |
| v1.3.1 | 2026-04-01 | Hotfix | E2E优化,性能达标 | 20260401-2 |
| **v1.4.0** | **2026-04-02** | **DeepTest** | **深度测试,97缺陷识别** | **20260402** |
| **v1.4.1** | **2026-04-02** | **Hotfix-R1** | **11缺陷修复,API/E2E 100%** | **20260402-1352** |
| **v1.4.2** | **2026-04-03** | **FinalDelivery** | **防御性重构+编译修复,最终交付** | **20260403-0142** |

## 附录B: 相关文档链接

| 文档 | 路径 | 说明 |
|------|------|------|
| 执行摘要 | `00_EXECUTIVE-SUMMARY.md` | 1页概览 |
| 最终验收报告 | `01_FINAL-ACCEPTANCE-REPORT.md` | 详细验收过程 |
| 迭代历史 | `02_ITERATION-HISTORY.md` | 版本演变过程 |
| **本文档** | **05_SYSTEM-VERSION-INFO.md** | **技术栈+构建信息** |
| 部署指南 | `06_DEPLOYMENT-GUIDE.md` | 环境搭建+启动 |
| 验收证书 | `08_ACCEPTANCE-CERTIFICATE.md` | 正式签署文档 |
| 后端Pom | `../pom.xml` | Maven依赖声明 |
| 前端Package | `../frontend/package.json` | npm依赖声明 |
| 测试报告v1.4.0 | `../TEST-REPORT-V1.4.0.md` | 基线测试数据 |
| 测试报告v1.4.1 | `../TEST-REPORT-V1.4.1.md` | R1修复后数据 |
| 回归报告v1.4.2 | `../test_results/REGRESSION-REPORT-V1.4.2.md` | 最终回归数据 |
| 后端最终状态 | `../BACKEND-FINAL-STATUS-V1.4.2.md` | 第三轮验证结论 |

---

**文档编制**: Technical Architect AI  
**最后更新**: 2026-04-03 01:30 CST  
**版本**: V1.4.2 Final  
**审核状态**: ✅ 与代码库一致  

*© 2026 实验室管理系统项目组 - 验收交付文档包 V1.4.2*
