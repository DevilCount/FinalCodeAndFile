# 基于微服务架构的实验室管理系统

## 项目简介

本项目是一个基于 **Spring Cloud Alibaba** 微服务架构的实验室管理系统（LIS)，适用于中小型医院检验科。系统包含以下核心功能：

- ✅ 用户管理（临床医生、检验医师、管理员）
- ✅ 标本全生命周期管理（扫码追溯）
- ✅ 检验报告管理（AI辅助诊断）
- ✅ HL7标准接口对接
- ✅ AI辅助诊断（血常规、尿常规）
- ✅ **操作日志记录（签收、发布报告等关键操作）**
- ✅ **Redis缓存（检验项目、标本类型字典）**

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                                │
│              (Vue.js / Element Plus)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────────────────┐
│                     API网关                                  │
│              lab-gateway : 8080                              │
│          (路由转发、负载均衡、统一入口)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        │              │              │              │
┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼──────┐ ┌────▼──────┐
│ 用户服务     │ │ 标本服务    │ │ 报告服务   │ │ HL7服务   │ │ AI服务    │
│ 8081         │ │ 8082        │ │ 8083       │ │ 8084      │ │ 8085      │
└──────────────┘ └─────────────┘ └────────────┘ └───────────┘ └───────────┘
        │              │              │              │              │
        └──────────────┴──────────────┴──────────────┴──────────────┘
                                    │
                       ┌────────────▼────────────┐
                       │      Nacos 注册中心     │
                       │      (8848端口)         │
                       └─────────────────────────┘
                                    │
                       ┌────────────▼────────────┐
                       │      MySQL 数据库       │
                       │    lab_management       │
                       └─────────────────────────┘
                                    │
                       ┌────────────▼────────────┐
                       │      Redis 缓存        │
                       │      (6379端口)         │
                       └─────────────────────────┘
```

## 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Spring Boot | 3.2.0 | 基础框架 |
| Spring Cloud | 2023.0.0 | 微服务框架 |
| Spring Cloud Alibaba | 2022.0.0.0 | 阿里微服务套件 |
| Nacos | 2.2.x | 注册中心/配置中心 |
| MySQL | 8.0+ | 关系型数据库 |
| Redis | 6.0+ | 缓存数据库 |
| MyBatis Plus | 3.5.5 | ORM框架 |
| OpenFeign | 4.x | 服务间调用 |
| HAPI HL7v2 | 2.3 | HL7消息处理 |
| Lombok | - | 代码简化 |
| Hutool | 5.8.22 | 工具类库 |
| Vue.js | 3.3.4 | 前端框架 |
| Vite | 4.4.5 | 构建工具 |
| Element Plus | 2.4.4 | UI组件库 |

## 项目结构

```
lab-management-system/
├── pom.xml                              # 父项目POM
├── README.md                            # 项目说明
│
├── sql/                                 # 数据库脚本
│   ├── init.sql                         # 初始化脚本
│   ├── upgrade_v1.1.0.sql               # 升级脚本(v1.1.0)
│   └── ...
│
├── lab-common/                          # 公共模块
│   ├── pom.xml
│   └── src/main/java/com/sunyaxin/common/
│       ├── entity/                      # 实体类
│       │   ├── User.java
│       │   ├── Sample.java
│       │   ├── Report.java
│       │   ├── SampleTrace.java
│       │   ├── OperationLog.java        # 操作日志(新增)
│       │   ├── PatientInfo.java         # 患者信息(新增)
│       │   ├── SampleType.java          # 标本类型(新增)
│       │   └── TestItem.java            # 检验项目(新增)
│       ├── result/                      # 统一返回结果
│       ├── constant/                    # 常量定义
│       │   ├── UserRoleConstant.java
│       │   ├── SampleStatusConstant.java
│       │   ├── ReportStatusConstant.java
│       │   └── OperationTypeConstant.java # 操作类型常量(新增)
│       ├── service/                     # 公共服务
│       │   ├── OperationLogService.java # 操作日志服务(新增)
│       │   ├── TestItemService.java     # 检验项目服务(新增)
│       │   └── SampleTypeService.java   # 标本类型服务(新增)
│       ├── mapper/                      # 公共Mapper
│       │   ├── OperationLogMapper.java   # (新增)
│       │   ├── TestItemMapper.java      # (新增)
│       │   └── SampleTypeMapper.java     # (新增)
│       ├── utils/                       # 工具类
│       ├── config/                      # 配置类
│       ├── aspect/                      # AOP切面
│       ├── exception/                   # 异常处理
│       └── dto/                         # 数据传输对象
│
├── lab-gateway/                         # 网关服务 (8080)
│
├── lab-user-service/                    # 用户服务 (8081)
│
├── lab-sample-service/                  # 标本服务 (8082)
│
├── lab-report-service/                  # 报告服务 (8083)
│
├── lab-hl7-service/                     # HL7接口服务 (8084)
│
├── lab-ai-service/                      # AI辅助诊断服务 (8085)
│
└── frontend/                           # 前端项目
    ├── src/
    │   ├── views/                       # 页面视图
    │   ├── components/                   # 组件
    │   ├── services/                    # API服务
    │   ├── router/                      # 路由
    │   └── store/                      # 状态管理
    └── package.json
```

## 快速启动

### 1. 环境准备

- JDK 17+
- Maven 3.8+
- MySQL 8.0+
- Redis 6.0+
- Node.js 16+ (前端)

### 2. 数据库初始化

```bash
# 登录MySQL
mysql -u root -p

# 执行初始化脚本
source sql/init.sql

# 执行升级脚本(新增操作日志等功能)
source sql/upgrade_v1.1.0.sql
```

### 3. Redis配置

确保Redis已启动，默认配置：
- 主机：localhost
- 端口：6379

### 4. 启动服务

**方式一：命令行启动**

```bash
# 编译打包
mvn clean install -DskipTests

# 启动各服务（各开一个命令行窗口）
cd lab-user-service && mvn spring-boot:run    # 端口 8086
cd lab-sample-service && mvn spring-boot:run  # 端口 8087
cd lab-report-service && mvn spring-boot:run  # 端口 8088
cd lab-hl7-service && mvn spring-boot:run     # 端口 8084
cd lab-ai-service && mvn spring-boot:run      # 端口 8089
cd lab-gateway && mvn spring-boot:run         # 端口 8080
```

**方式二：启动前端**

```bash
cd frontend
npm install
npm run dev  # 访问 http://localhost:5173
```

### 5. 访问系统

| 服务 | 地址 |
|------|------|
| 前端主页 | http://localhost:5173 |
| API网关 | http://localhost:8080 |
| 用户服务 | http://localhost:8086 |
| 标本服务 | http://localhost:8087 |
| 报告服务 | http://localhost:8088 |
| HL7服务 | http://localhost:8084 |
| AI服务 | http://localhost:8089 |

### 6. 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 医生 | doctor1 | doctor123 |
| 检验师 | labtech1 | lab123 |

## 核心功能

### 1. 标本全生命周期追溯

```
采集 → 运输 → 签收 → 检验 → 完成 → 归档
```

每个标本都有唯一的编号（如：SP202402240001），系统自动记录每个环节的操作人、时间、位置。

### 2. 操作日志记录

系统自动记录关键业务操作，包括：

| 操作类型 | 记录内容 |
|----------|----------|
| 创建标本 | 标本编号、患者姓名、操作人 |
| 签收标本 | 标本编号、签收人 |
| 开始检验 | 标本编号、检验人 |
| 录入结果 | 报告编号、检验项目、AI诊断 |
| 审核报告 | 审核结果、审核人 |
| 发布报告 | 报告编号、发布人 |

### 3. Redis缓存

- **检验项目字典**：启动时加载，定期更新
- **标本类型字典**：启动时加载，定期更新

### 4. HL7标准对接

支持HL7 v2.x标准消息格式：
- **ORM^O01**：检验申请
- **ORU^R01**：检验结果回传
- **ADT^A01**：患者入院信息

### 5. AI辅助诊断

基于规则的AI辅助诊断引擎，支持：
- 血常规分析
- 尿常规分析

> ⚠️ **免责声明**：AI诊断结果仅供参考，不作为最终诊断依据。

## 数据库表说明

### 核心表

| 表名 | 说明 |
|------|------|
| sys_user | 用户表 |
| lab_sample | 标本表 |
| lab_report | 报告表 |
| lab_sample_trace | 标本追踪记录 |

### 新增表(v1.1.0)

| 表名 | 说明 |
|------|------|
| operation_log | 操作日志表 |
| patient_info | 患者信息表 |
| sample_type | 标本类型字典 |
| test_item | 检验项目字典 |

## API接口说明

### 用户服务 (/api/user)

| 接口 | 方法 | 说明 |
|------|------|------|
| /user/login | POST | 用户登录 |
| /user/register | POST | 用户注册 |
| /user/list | GET | 获取所有用户 |

### 标本服务 (/api/sample)

| 接口 | 方法 | 说明 |
|------|------|------|
| /sample/create | POST | 创建标本 |
| /sample/scan/{sampleNo} | GET | 扫码查询标本 |
| /sample/{id}/receive | POST | 签收标本 |
| /sample/{id}/start-test | POST | 开始检验 |
| /sample/{id}/complete | POST | 完成检验 |
| /sample/{id}/traces | GET | 获取追踪记录 |

### 报告服务 (/api/report)

| 接口 | 方法 | 说明 |
|------|------|------|
| /report/create | POST | 创建报告 |
| /report/{id}/input-results | POST | 录入检验结果 |
| /report/{id}/review | POST | 审核报告 |
| /report/{id}/publish | POST | 发布报告 |

### AI服务 (/api/ai)

| 接口 | 方法 | 说明 |
|------|------|------|
| /ai/diagnose | POST | AI辅助诊断 |
| /ai/health | GET | 健康检查 |

## 项目更新日志

### v1.1.0 (2024-03-22)

- ✅ 新增操作日志表，记录关键业务操作
- ✅ 新增患者信息表
- ✅ 新增标本类型字典表
- ✅ 新增检验项目字典表
- ✅ 改造lab_sample表（新增条码号、优先级等字段）
- ✅ 改造lab_report表（新增打印次数、发布时间等字段）
- ✅ 添加Redis缓存支持
- ✅ 代码层面添加操作日志记录逻辑

### v1.0.0 (初始版本)

- ✅ 用户管理
- ✅ 标本管理
- ✅ 报告管理
- ✅ HL7接口
- ✅ AI辅助诊断

## 常见问题

### Q1: Nacos连接失败？

确保Nacos已启动且访问地址正确。

### Q2: Redis连接失败？

确保Redis已启动，默认端口6379。

### Q3: 服务间调用失败？

确保所有服务都已注册到Nacos。

## 作者

- **姓名**：孙亚鑫
- **学号**：202218506
- **专业**：软件工程
- **学校**：华北水利水电大学

## 许可证

本项目仅供学习交流使用。
