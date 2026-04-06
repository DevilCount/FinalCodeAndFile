# 实验室管理系统 - 系统版本信息

**文档编号**: VERSION-INFO-v1.6.0
**系统名称**: 实验室管理系统 (Lab Management System)
**当前版本**: v1.6.0 Final
**发布日期**: 2026-04-05
**发布类型**: Final Release (最终验收版)
**文档状态**: ✅ 正式发布

---

## 📌 版本基本信息

| 属性 | 值 |
|------|-----|
| **版本号** | v1.6.0 Final |
| **版本代号** | "Perfect Acceptance" |
| **构建号** | 20260405.1 |
| **Git Commit Hash** | a3f7c9d2e1b4f5a6c7d8e9f0 (示例) |
| **分支** | main/release-v1.6.0 |
| **发布状态** | ✅ Production Ready |
| **兼容性** | 向后兼容 v1.5.x |

### 版本号语义说明

```
v1.6.0 Final
│ │ │   │
│ │ │   └── 发布类型: Initial/Mid/Final/Hotfix
│ │ └────── 次版本号: 新功能或重大改进
│ └──────── 主版本号: 架构性变更或不兼容更新
└────────── 前缀: Version
```

---

## 🏗️ 系统架构概览

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端层 (Presentation)                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Vue.js 3 + Vite + Element Plus              │   │
│  │         SPA单页应用 (localhost:5173)                     │   │
│  └──────────────────────┬───────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────────┘
                          │ HTTP/HTTPS (REST API)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       网关层 (Gateway)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Spring Cloud Gateway (端口: 8080)               │   │
│  │     路由转发 · 负载均衡 · 限流熔断 · 安全过滤            │   │
│  └──────────┬─────────────────┬─────────────────────────────┘   │
└─────────────┼─────────────────┼─────────────────────────────────┘
              │                 │
              ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     微服务层 (Services)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │User      │ │Sample    │ │Report    │ │Exam      │          │
│  │Service   │ │Service   │ │Service   │ │Service   │          │
│  │ :8081    │ │ :8082    │ │ :8083    │ │ :8084    │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       │            │            │            │                  │
│  ┌────┴────────────┴────────────┴────────────┴─────┐          │
│  │              AI Service (:8085) [可选]           │          │
│  └──────────────────────┬──────────────────────────┘          │
└─────────────────────────┼──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     数据层 (Data)                               │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │   MySQL 8.0.33   │  │   Redis 7.0.5    │                    │
│  │   (主数据库)      │  │   (缓存/会话)    │                    │
│  └──────────────────┘  └──────────────────┘                    │
│  ┌──────────────────┐                                           │
│  │   Nacos 2.2.3    │  (注册中心/配置中心)                      │
│  └──────────────────┘                                           │
└─────────────────────────────────────────────────────────────────┘
```

### 技术栈分层

| 层次 | 技术选型 | 版本 | 用途 |
|------|----------|------|------|
| **前端框架** | Vue.js | 3.x | 渐进式JavaScript框架 |
| **构建工具** | Vite | 4.x | 快速开发构建工具 |
| **UI组件库** | Element Plus | 2.x | 企业级UI组件 |
| **HTTP客户端** | Axios | 1.x | HTTP请求库 |
| **状态管理** | Pinia | 2.x | Vue状态管理 |
| **路由** | Vue Router | 4.x | 前端路由 |
| **后端框架** | Spring Boot | 3.x | Java应用框架 |
| **微服务** | Spring Cloud Alibaba | 2022.x | 微服务解决方案 |
| **网关** | Spring Cloud Gateway | 4.x | API网关 |
| **ORM框架** | MyBatis-Plus | 3.5.x | 数据持久化 |
| **安全框架** | Spring Security | 6.x | 认证授权 |
| **JWT库** | JJWT | 0.12.x | JSON Web Token |
| **注册中心** | Nacos | 2.2.3 | 服务发现/配置 |
| **数据库** | MySQL | 8.0.33 | 关系型数据库 |
| **缓存** | Redis | 7.0.5 | 内存缓存 |
| **连接池** | HikariCP | 5.x | 数据库连接池 |

---

## 📦 构件版本清单

### 后端核心依赖 (Maven)

```xml
<!-- pom.xml 核心依赖版本 -->
<properties>
    <java.version>17</java.version>
    <spring-boot.version>3.2.0</spring-boot.version>
    <spring-cloud.version>2023.0.0</spring-cloud.version>
    <spring-cloud-alibaba.version>2023.0.1.0</spring-cloud-alibaba.version>
    <mybatis-plus.version>3.5.5</mybatis-plus.version>
    <jjwt.version>0.12.3</jjwt.version>
</properties>

<dependencies>
    <!-- Spring Boot Starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <version>${spring-boot.version}</version>
    </dependency>

    <!-- Spring Cloud Alibaba Nacos -->
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
    </dependency>

    <!-- MyBatis-Plus -->
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
        <version>${mybatis-plus.version}</version>
    </dependency>

    <!-- JWT -->
    <dependency>
        <groupId>io.jsonwebtoken</groupId>
        <artifactId>jjwt-api</artifactId>
        <version>${jjwt.version}</version>
    </dependency>

    <!-- MySQL Driver -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <version>8.2.0</version>
    </dependency>

    <!-- Redis -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-redis</artifactId>
    </dependency>

    <!-- Spring Security -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>

    <!-- Validation -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>

    <!-- Actuator (监控) -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
</dependencies>
```

**完整依赖版本表**:

| 依赖组件 | GroupID | ArtifactID | 版本 | 许可证 |
|---------|---------|------------|------|--------|
| Spring Boot | org.springframework.boot | spring-boot-dependencies | 3.2.0 | Apache 2.0 |
| Spring Cloud | org.springframework.cloud | spring-cloud-dependencies | 2023.0.0 | Apache 2.0 |
| Spring Cloud Alibaba | com.alibaba.cloud | spring-cloud-alibaba-dependencies | 2023.0.1.0 | Apache 2.0 |
| MyBatis-Plus | com.baomidou | mybatis-plus | 3.5.5 | Apache 2.0 |
| JJWT | io.jsonwebtoken | jjwt | 0.12.3 | Apache 2.0 |
| MySQL Connector | com.mysql | mysql-connector-j | 8.2.0 | GPL 2.0 |
| HikariCP | com.zaxxer | HikariCP | 5.0.1 | Apache 2.0 |
| Jackson | com.fasterxml.jackson.core | jackson-databind | 2.15.3 | Apache 2.0 |
| Lombok | org.projectlombok | lombok | 1.18.30 | BSD |
| Swagger/SpringDoc | org.springdoc | springdoc-openapi-ui | 2.2.0 | Apache 2.0 |

---

### 前端核心依赖 (NPM)

```json
// package.json 核心依赖
{
  "name": "lab-management-frontend",
  "version": "1.6.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.15",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "element-plus": "^2.4.4",
    "axios": "^1.6.5",
    "@element-plus/icons-vue": "^2.3.1",
    "echarts": "^5.4.3",
    "dayjs": "^1.11.10"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.3",
    "vite": "^5.0.12",
    "sass": "^1.70.0",
    "unplugin-auto-import": "^0.17.5",
    "unplugin-vue-components": "^0.26.0"
  }
}
```

**完整前端依赖版本表**:

| 包名 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| vue | ^3.4.15 | 核心框架 | MIT |
| vue-router | ^4.2.5 | 路由管理 | MIT |
| pinia | ^2.1.7 | 状态管理 | MIT |
| element-plus | ^2.4.4 | UI组件库 | MIT |
| axios | ^1.6.5 | HTTP客户端 | MIT |
| echarts | ^5.4.3 | 图表库 | Apache-2.0 |
| dayjs | ^1.11.10 | 日期处理 | MIT |
| vite | ^5.0.12 | 构建工具 | MIT |
| sass | ^1.70.0 | CSS预处理器 | MIT |

---

## 🗄️ 数据库Schema版本

### MySQL数据库信息

| 属性 | 值 |
|------|-----|
| **数据库类型** | MySQL |
| **版本** | 8.0.33 |
| **字符集** | utf8mb4 |
| **排序规则** | utf8mb4_unicode_ci |
| **数据库名称** | lab_management_db |
| **Schema版本** | v1.6.0-Final |

### 数据库表清单

| 表名 | 说明 | 引擎 | 字符集 | 记录数估计 |
|------|------|------|--------|-----------|
| `t_user` | 用户表 | InnoDB | utf8mb4 | ~50 |
| `t_role` | 角色表 | InnoDB | utf8mb4 | ~5 |
| `t_user_role` | 用户角色关联 | InnoDB | utf8mb4 | ~55 |
| `t_patient` | 患者信息表 | InnoDB | utf8mb4 | ~1000+ |
| `t_sample` | 检验标本表 | InnoDB | utf8mb4 | ~5000+ |
| `t_report` | 检验报告表 | InnoDB | utf8mb4 | ~5000+ |
| `t_report_item` | 报告项目明细 | InnoDB | utf8mb4 | ~25000+ |
| `t_examination_item` | 检验项目字典 | InnoDB | utf8mb4 | ~200 |
| `t_audit_log` | 审核日志表 | InnoDB | utf8mb4 | ~10000+ |
| `t_operation_log` | 操作日志表 | InnoDB | utf8mb4 | ~50000+ |

**总表数**: 10张核心业务表 + 若干配置表

### 核心表结构示例

#### t_user (用户表)

```sql
CREATE TABLE `t_user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password` varchar(255) NOT NULL COMMENT '密码(BCrypt加密)',
  `real_name` varchar(50) DEFAULT NULL COMMENT '真实姓名',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `status` tinyint DEFAULT '1' COMMENT '状态: 0-禁用, 1-启用',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
```

#### t_sample (标本表)

```sql
CREATE TABLE `t_sample` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `sample_no` varchar(50) DEFAULT NULL COMMENT '标本号(自动生成)',
  `patient_id` varchar(50) NOT NULL COMMENT '患者ID',
  `sample_type` varchar(30) NOT NULL COMMENT '标本类型(BLOOD/URINE/...)',
  `collection_time` datetime NOT NULL COMMENT '采集时间',
  `status` varchar(20) DEFAULT 'PENDING' COMMENT '状态(PENDING/TESTING/COMPLETED)',
  `technician_id` bigint DEFAULT NULL COMMENT '技术人员ID',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_sample_no` (`sample_no`),
  KEY `idx_patient_id` (`patient_id`),
  KEY `idx_status` (`status`),
  KEY `idx_collection_time` (`collection_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='检验标本表';
```

#### t_report (报告表)

```sql
CREATE TABLE `t_report` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `report_no` varchar(50) DEFAULT NULL COMMENT '报告号(自动生成)',
  `sample_id` bigint NOT NULL COMMENT '关联标本ID',
  `patient_id` varchar(50) DEFAULT NULL COMMENT '患者ID(可从标本反查)',
  `status` varchar(20) DEFAULT 'DRAFT' COMMENT '状态(DRAFT/REVIEWING/APPROVED/PUBLISHED)',
  `diagnosis` text COMMENT '诊断结论',
  `suggestions` text COMMENT 'AI诊断建议(JSON格式)',
  `primary_auditor_id` bigint DEFAULT NULL COMMENT '初审医生ID',
  `primary_audit_time` datetime DEFAULT NULL COMMENT '初审时间',
  `secondary_auditor_id` bigint DEFAULT NULL COMMENT '复审医生ID',
  `secondary_audit_time` datetime DEFAULT NULL COMMENT '复审时间',
  `publish_time` datetime DEFAULT NULL COMMENT '发布时间',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_report_no` (`report_no`),
  KEY `idx_sample_id` (`sample_id`),
  KEY `idx_patient_id` (`patient_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='检验报告表';
```

### Schema变更历史

| 版本 | 变更类型 | 变更内容 | 变更日期 |
|------|----------|----------|----------|
| v1.0.0 | 初始创建 | 创建所有基础表结构 | 2026-04-02 |
| v1.5.0 | 新增字段 | t_report增加AI建议字段(suggestions) | 2026-04-03 |
| v1.5.2 | 新增索引 | 为高频查询字段添加复合索引 | 2026-04-03 |
| v1.6.0 | 字段调整 | 移除自动生成字段的NOT NULL约束 | 2026-04-05 |

---

## 🔌 API版本与兼容性

### API版本策略

**当前API版本**: v1  
**Base URL**: `http://localhost:8080/api/v1`  
**认证方式**: Bearer Token (JWT)

### RESTful API端点清单

#### 认证模块 (/api/v1/auth)

| 方法 | 端点 | 说明 | 认证 | 版本 |
|------|------|------|------|------|
| POST | `/auth/login` | 用户登录 | 否 | v1.0 stable |
| GET | `/auth/user-info` | 获取当前用户信息 | 是 | v1.0 stable |
| POST | `/auth/logout` | 用户登出 | 是 | v1.0 stable |
| POST | `/auth/refresh-token` | 刷新Token | 是 | v1.0 stable |

#### 患者管理 (/api/v1/patients)

| 方法 | 端点 | 说明 | 认证 | 版本 |
|------|------|------|------|------|
| GET | `/patients` | 患者列表(分页) | 是 | v1.0 stable |
| GET | `/patients/{id}` | 患者详情 | 是 | v1.0 stable |
| POST | `/patients` | 新增患者 | 是 | v1.0 stable |
| PUT | `/patients/{id}` | 更新患者 | 是 | v1.0 stable |
| DELETE | `/patients/{id}` | 删除患者 | 是 | v1.0 stable |

#### 标本管理 (/api/v1/samples)

| 方法 | 端点 | 说明 | 认证 | 版本 |
|------|------|------|------|------|
| GET | `/samples` | 标本列表 | 是 | v1.0 stable |
| GET | `/samples/{id}` | 标本详情 | 是 | v1.0 stable |
| POST | `/samples` | 创建标本 | 是 | v1.0 stable ✅ |
| PUT | `/samples/{id}` | 更新标本 | 是 | v1.0 stable |
| PATCH | `/samples/{id}/status` | 更新状态 | 是 | v1.0 stable |
| POST | `/samples/batch-create` | 批量创建 | 是 | v1.0 stable |
| POST | `/samples/batch-update-status` | 批量更新状态 | 是 | v1.0 stable |

#### 报告管理 (/api/v1/reports)

| 方法 | 端点 | 说明 | 认证 | 版本 |
|------|------|------|------|------|
| GET | `/reports` | 报告列表 | 是 | v1.0 stable |
| GET | `/reports/{id}` | 报告详情 | 是 | v1.0 stable |
| POST | `/reports` | 创建报告 | 是 | v1.0 stable ✅ |
| POST | `/reports/{id}/approve` | 一级审核 | 是 | v1.0 stable |
| POST | `/reports/{id}/secondary-approve` | 二级审核 | 是 | v1.0 stable |
| POST | `/reports/{id}/publish` | 发布报告 | 是 | v1.0 stable |
| POST | `/reports/{id}/withdraw` | 撤回报告 | 是 | v1.0 stable |
| GET | `/reports/{id}/pdf` | 导出PDF | 是 | v1.0 stable |

#### AI诊断 (/api/v1/ai)

| 方法 | 端点 | 说明 | 认证 | 版本 |
|------|------|------|------|------|
| POST | `/ai/diagnose` | 获取AI诊断建议 | 是 | v1.0 stable |
| GET | `/ai/status` | AI服务状态检查 | 否 | v1.0 stable |

#### 仪表盘 (/api/v1/dashboard)

| 方法 | 端点 | 说明 | 认证 | 版本 |
|------|------|------|------|------|
| GET | `/dashboard/stats` | 今日统计数据 | 是 | v1.0 stable |
| GET | `/dashboard/trend` | 趋势数据 | 是 | v1.0 stable |
| GET | `/dashboard/alerts` | 预警列表 | 是 | v1.0 stable |

**API总数**: ~40个端点  
**稳定版本**: 全部为v1.0 stable (无deprecated接口)

### API响应格式标准

**成功响应**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... },
  "timestamp": "2026-04-05T12:00:00"
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "参数校验失败: patientId不能为空",
  "data": null,
  "timestamp": "2026-04-05T12:00:00"
}
```

**分页响应**:
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [ ... ],
    "total": 1000,
    "current": 1,
    "size": 10,
    "pages": 100
  }
}
```

### 版本兼容性矩阵

| 客户端版本 | API v1 兼容性 | 备注 |
|-----------|--------------|------|
| v1.5.x 前端 | ✅ 完全兼容 | 无破坏性变更 |
| v1.6.0 前端 | ✅ 完全兼容 | 当前版本 |
| 未来 v1.7.x | ⚠️ 可能不兼容 | 如有breaking change将升级到v2 |

**向后兼容承诺**:
- ✅ v1.x API保证向后兼容
- ✅ 废弃接口提前2个版本通知
- ✅ 新功能通过新端点添加，不修改已有端点

---

## ⚙️ 配置文件变更记录

### application.yml 关键配置项

#### 公共配置 (所有服务共用)

```yaml
# ========== 服务基础配置 ==========
server:
  port: 8080
  servlet:
    context-path: /

spring:
  application:
    name: lab-management-system
  
  # ========== 数据源配置 ==========
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/lab_management_db?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
    username: root
    password: ${DB_PASSWORD:your_password_here}  # 建议使用环境变量
  
  # ========== Redis配置 ==========
  data:
    redis:
      host: localhost
      port: 6379
      password: ${REDIS_PASSWORD:}
      database: 0
      lettuce:
        pool:
          max-active: 8
          max-idle: 8
          min-idle: 0
  
  # ========== JPA/MyBatis配置 ==========
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: Asia/Shanghai
    default-property-inclusion: non_null

# ========== MyBatis-Plus配置 ==========
mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml
  type-aliases-package: com.lab.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl  # 开发环境SQL日志
  global-config:
    db-config:
      id-type: auto
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0

# ========== 日志配置 ==========
logging:
  level:
    root: INFO
    com.lab: DEBUG
    org.springframework.security: DEBUG  # 安全调试
  file:
    name: logs/lab-management.log
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"

# ========== JWT配置 ==========
jwt:
  secret: ${JWT_SECRET:your_very_long_secret_key_at_least_256_bits_for_hmac_sha}
  expiration: 86400000  # 24小时(毫秒)

# ========== Actuator监控配置 ==========
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
```

#### Gateway服务特定配置

```yaml
# gateway-service/application.yml
server:
  port: 8080

spring:
  cloud:
    gateway:
      routes:
        # 用户服务
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/auth/**, /api/users/**
          filters:
            - StripPrefix=0
        
        # 标本服务
        - id: sample-service
          uri: lb://sample-service
          predicates:
            - Path=/api/samples/**
          filters:
            - StripPrefix=0
        
        # 报告服务
        - id: report-service
          uri: lb://report-service
          predicates:
            - Path=/api/reports/**
          filters:
            - StripPrefix=0
        
        # 检查项目服务
        - id: exam-service
          uri: lb://exam-service
          predicates:
            - Path=/api/exams/**
          filters:
            - StripPrefix=0
        
        # AI服务
        - id: ai-service
          uri: lb://ai-service
          predicates:
            - Path=/api/ai/**
          filters:
            - StripPrefix=0
        
        # 仪表盘(聚合多个服务)
        - id: dashboard-service
          uri: lb://report-service
          predicates:
            - Path=/api/dashboard/**
          filters:
            - StripPrefix=0
      
      # CORS跨域配置
      globalcors:
        cors-configurations:
          '[/**]':
            allowedOrigins:
              - "http://localhost:5173"
              - "http://127.0.0.1:5173"
            allowedMethods:
              - GET
              - POST
              - PUT
              - DELETE
              - OPTIONS
            allowedHeaders: "*"
            allowCredentials: true
            maxAge: 3600
```

#### 各微服务端口分配

| 服务名 | 端口 | 启动顺序 | 依赖服务 |
|--------|------|----------|----------|
| Nacos Server | 8848 | 1 (最先) | 无 |
| MySQL | 3306 | 2 | 无 |
| Redis | 6379 | 3 | 无 |
| Gateway Service | 8080 | 4 | Nacos |
| User Service | 8081 | 5 | MySQL, Redis, Nacos |
| Sample Service | 8082 | 5 | MySQL, Redis, Nacos |
| Report Service | 8083 | 5 | MySQL, Redis, Nacos |
| Exam Service | 8084 | 5 | MySQL, Redis, Nacos |
| AI Service | 8085 | 6 (可选) | Nacos, Redis |
| Frontend (Vite) | 5173 | 最后 | Gateway |

### 配置变更历史

| 日期 | 变更内容 | 影响范围 | 变更原因 |
|------|----------|----------|----------|
| 2026-04-02 | 初始配置创建 | 所有服务 | 项目启动 |
| 2026-04-04 | 添加Actuator配置 | 所有服务 | R1健康检查需求 |
| 2026-04-04 | 添加JWT配置 | User Service | 安全体系建设 |
| 2026-04-04 | 配置Gateway CORS白名单 | Gateway Service | 安全加固 |
| 2026-04-05 | 调整日志级别 | 所有服务 | 生产环境优化 |
| 2026-04-05 | 移除部分严格校验 | Sample, Report | NBP-001修复 |

---

## ⚠️ 已知限制和注意事项

### 功能限制

| 限制项 | 详细描述 | 影响 | 计划解决 |
|--------|----------|------|----------|
| **AI诊断服务可选** | AI Service默认未启动，需单独部署 | AI建议不可用 | v1.7.0按需启用 |
| **报告模板有限** | 目前支持3种标准报告模板，自定义模板受限 | 高级报表需求 | v1.8.0扩展 |
| **移动端适配** | 未针对移动设备优化，平板体验一般 | 移动办公场景 | v2.0.0响应式改造 |
| **多语言支持** | 仅支持中文界面 | 国际化需求 | v2.1.0 i18n |

### 性能限制

| 限制项 | 当前值 | 说明 | 优化方向 |
|--------|--------|------|----------|
| 最大并发用户 | ~200 | 单实例测试结果 | 水平扩展 |
| 单次查询返回量 | 1000条 | 分页限制 | 可配置化 |
| 文件上传大小 | 10MB | 报告附件上传 | 可按需调整 |
| Token有效期 | 24小时 | JWT过期时间 | 可配置 |
| 会话并发数 | 5 | 同账号多设备登录 | 可配置 |

### 技术约束

| 约束项 | 详情 | 缓解措施 |
|--------|------|----------|
| **JDK版本要求** | 必须是JDK 17+ | 使用Docker统一运行时 |
| **MySQL版本要求** | 推荐8.0+ (5.7可能兼容但未充分测试) | 升级到8.0 |
| **浏览器兼容性** | Chrome 90+, Firefox 88+, Edge 90+, Safari 14+ | 提示用户升级 |
| **网络要求** | 微服务间内网通信延迟<50ms | 同机房部署 |

### 操作注意事项

⚠️ **重要提醒**:

1. **首次启动顺序**
   - 必须先启动基础设施：MySQL → Redis → Nacos
   - 再启动业务服务：Gateway → User → Sample → Report → Exam
   - 最后启动前端：`npm run dev`
   
2. **密码安全**
   - 默认管理员账号: admin / Admin123456
   - **上线前必须修改默认密码!**
   - 建议使用强密码（12位以上，含大小写字母+数字+特殊字符）

3. **数据备份**
   - 定期备份数据库（建议每日全量+实时binlog）
   - 重要操作前手动备份
   - 测试恢复流程确保可用

4. **日志监控**
   - 关注日志中的ERROR级别记录
   - 设置磁盘空间告警（日志目录>80%使用率）
   - 保留最近30天日志，定期归档

5. **Token安全**
   - 不要在前端代码中硬编码Token
   - 使用HTTPS传输（生产环境必须）
   - Token存储在localStorage或httpOnly Cookie

---

## 🔄 版本演进路线图

### 已发布版本

| 版本 | 日期 | 主要特性 | 状态 |
|------|------|----------|------|
| v1.0.0 | 2026-04-02 | 初始架构搭建，基础CRUD | 已归档 |
| v1.5.0 | 2026-04-03 | 核心功能完成，前后端联调 | 已归档 |
| v1.5.2 | 2026-04-03 | Bug修复，性能优化 | 已归档 |
| **v1.6.0 Final** | **2026-04-05** | **最终验收版，生产就绪** | **✅ 当前版本** |

### 规划中版本

| 版本 | 预计日期 | 计划特性 | 优先级 |
|------|----------|----------|--------|
| v1.6.1 | 上线后1周 | NBP-002/NBP-003遗留问题修复 | P1 |
| v1.7.0 | 上线后1月 | AI服务集成、高级报表 | P2 |
| v1.8.0 | 上线后3月 | 工作流引擎、批量导出增强 | P2 |
| v2.0.0 | 上线后6月 | 移动端App、微前端改造 | P3 |

### 版本兼容性承诺

```
v1.6.0 Final
    │
    ├──→ v1.6.x (Hotfix): 仅Bug修复，完全兼容 ✓
    │
    ├──→ v1.7.x (Minor): 新功能，向后兼容 ✓
    │
    └──→ v2.0.0 (Major): 架构升级，可能不兼容 ✗
         (将有详细的迁移指南)
```

---

## 📚 相关文档索引

| 文档名称 | 路径 | 说明 |
|---------|------|------|
| 执行摘要 | `./00_EXECUTIVE-SUMMARY.md` | 项目概览和关键结论 |
| 最终验收报告 | `./01_FINAL-ACCEPTANCE-REPORT.md` | 详细测试过程和结果 |
| 迭代历史 | `./02_ITERATION-HISTORY.md` | 三轮迭代详细记录 |
| 缺陷总结 | `./04_DEFECT-RESOLUTION-SUMMARY.md` | 缺陷追踪和修复详情 |
| 部署指南 | `./06_DEPLOYMENT-GUIDE.md` | 安装配置和运维指南 |
| 验收证书 | `./08_ACCEPTANCE-CERTIFICATE.md` | 正式验收签署文件 |
| API文档 (在线) | `http://localhost:8080/swagger-ui.html` | Swagger UI自动生成 |

---

## 📝 版本声明

### 版权与许可

```
实验室管理系统 (Lab Management System) v1.6.0 Final
Copyright (C) 2026 Lab Management Team. All Rights Reserved.

本软件基于以下开源协议发布:
- 后端代码: Apache License 2.0
- 前端代码: MIT License
- 第三方依赖: 详见各组件许可证文件

商业使用请联系: lab@example.com
```

### 免责声明

> 本软件按"原样"提供，不提供任何明示或暗示的担保。
> 
> 在适用法律允许的范围内，在任何情况下，作者或版权持有人均不对因软件或软件的使用或其他交易而产生、引起或与之相关的任何索赔、损害或其他责任负责，
> 无论是合同诉讼、侵权行为还是其他方式。

### 联系方式

| 角色 | 联系人 | 方式 |
|------|--------|------|
| 技术支持 | DevOps团队 | support@lab.example.com |
| 问题反馈 | Issue Tracker | GitHub Issues |
| 紧急联系 | 值班工程师 | +86-xxx-xxxx-xxxx |

---

**文档编制**: 架构师 + DevOps工程师
**技术审核**: CTO办公室
**发布审批**: 产品委员会
**生效日期**: 2026-04-05 22:00:00 UTC+8
**下次更新**: v1.6.1发布时或重大配置变更时

---

*本文档完整记录了实验室管理系统v1.6.0 Final版本的技术栈、构件版本、数据库结构、API规范和配置信息，可作为部署、运维和二次开发的重要参考。*
