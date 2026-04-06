# 后端代码审查清单

**审查版本**: v1.5.1
**审查时间**: 2026-04-05 01:37
**审查人**: 后端开发智能体

---

## 1. 服务功能完整性

| 服务 | 端口 | 功能完成度 | 主要问题 | 优先级 |
|------|------|-----------|---------|--------|
| Gateway | 8080 | 85% | 缺少JWT鉴权过滤器、CORS配置为`*`生产不安全、无actuator端点暴露 | P1 |
| User Service | 8086 | 80% | 缺少Spring Security FilterChain（仅有PasswordEncoder）、JWT未完整实现（无token生成/验证）、分页参数无上限保护 | P0 |
| Sample Service | 8087 | 75% | `searchSamples`存在内存过滤N+1风险、EnhancedSampleServiceImpl大量方法返回空数据、缺少完整全局异常处理 | P1 |
| Report Service | 8088 | 80% | AI服务Feign熔断器缺少fallback实现文件、report模块无全局异常处理器 | P1 |
| HL7 Service | 8084 | 65% | `sendToHis`方法为空实现（仅打印日志）、缺少HAPI HL7v2实际连接逻辑 | P2 |
| AI Service | 8089 | 70% | 无数据库连接（AI-service无`spring-boot-starter-jdbc`依赖）、无actuator依赖、规则引擎简单 | P1 |
| lab-common | - | 85% | `GlobalExceptionHandler`仅存在于common中，各service未依赖此handler、缺少统一的响应包装 | P1 |

---

## 2. API接口审查

| 接口 | 方法 | 服务 | 状态 | 问题描述 | 优先级 |
|------|------|------|------|---------|--------|
| `/api/user/user/login` | POST | User | ⚠️ | 参数通过`@RequestParam`传递，密码会暴露在URL参数中，应改用`@RequestBody` | P1 |
| `/api/user/user/list` | GET | User | ⚠️ | `size`参数无上限，恶意请求可导致内存溢出 | P0 |
| `/api/user/user/register` | POST | User | ✅ | 参数校验完整，密码BCrypt加密 | - |
| `/api/sample/sample/create` | POST | Sample | ✅ | 参数校验和事务处理完整 | - |
| `/api/sample/sample/list` | GET | Sample | ⚠️ | 无分页，一次性返回全部数据，大数据量有性能风险 | P1 |
| `/api/sample/sample/search` | GET | Sample | ❌ | 先`list()`全表再内存过滤（N+1+全表扫描），应走Mapper XML SQL | P0 |
| `/api/sample/enhanced/sample/dashboard/stats` | GET | Sample | ❌ | `EnhancedSampleServiceImpl.getDashboardStats()`返回全0空数据 | P0 |
| `/api/sample/enhanced/sample/export/excel` | GET | Sample | ❌ | `exportSamplesToExcel()`返回空`byte[0]` | P0 |
| `/api/sample/enhanced/sample/import/excel` | POST | Sample | ⚠️ | `importSamplesFromExcel()`永远返回"导入成功" | P0 |
| `/api/sample/enhanced/sample/batch/update-status` | POST | Sample | ❌ | 批量更新永远返回"批量更新成功"（未实际执行） | P0 |
| `/api/report/report/create` | POST | Report | ✅ | 核心逻辑完整 | - |
| `/api/report/report/input-results` | POST | Report | ⚠️ | AI服务不可用时降级处理存在（但AI服务本身未启动） | P1 |
| `/api/hl7/hl7/send-to-his` | POST | HL7 | ❌ | 实际未发送HL7消息，仅打印日志 | P0 |
| `/api/hl7/hl7/receive-from-his` | POST | HL7 | ⚠️ | 仅解析消息，无实际接收连接处理 | P2 |
| `/api/ai/ai/diagnose` | POST | AI | ⚠️ | 仅本地规则引擎，无外部AI接入能力 | P2 |
| `/api/ai/ai/simple-diagnose` | POST | AI | ⚠️ | 返回固定值"诊断建议：\n..."，前端拼接冗余前缀 | P2 |
| `/health` | GET | 全局 | ❌ | **所有服务均无`spring-boot-starter-actuator`依赖，`/actuator/health`返回404** | P0 |
| `/error` | GET | 全局 | ⚠️ | Spring Boot默认error端点暴露堆栈信息 | P1 |

---

## 3. 安全问题清单

| 问题ID | 服务 | 问题描述 | 文件位置 | 风险等级 | 修复建议 |
|--------|------|---------|---------|---------|---------|
| SEC-001 | Gateway | CORS配置`allowedOriginPatterns: "*"`允许任意来源 | `lab-gateway/.../application.yml` | 🔴 高 | 生产环境改为具体域名列表 |
| SEC-002 | User | 无JWT FilterChain，用户认证仅在Service层检查，API无状态保护 | `lab-user-service/` | 🔴 高 | 实现`SecurityFilterChain` + JWT Token过滤器 |
| SEC-003 | User | 注册接口无验证码/图形验证码，容易被暴力注册 | `UserController.java` | 🟡 中 | 添加图形验证码或频率限制 |
| SEC-004 | User | `getUserList`分页参数`size`无上限（默认10），大值可OOM | `UserServiceImpl.java` | 🟡 中 | 添加`max(size, 100)`保护 |
| SEC-005 | User | 登录使用`System.err.println`记录敏感操作日志 | `UserServiceImpl.java` 多处 | 🟡 中 | 统一使用`log.warn/error` |
| SEC-006 | Sample | `listSamples`无分页，大数据量返回可能导致内存溢出 | `SampleController.java` | 🔴 高 | 添加分页支持 |
| SEC-007 | Gateway | 所有服务路由无JWT验证过滤器 | `GatewayApplication.java` | 🔴 高 | 添加JWT验证Filter |
| SEC-008 | 全局 | `/error`端点未禁用，异常信息暴露内部路径 | 所有服务 | 🟡 中 | 配置`server.error.include-message=never` |
| SEC-009 | AI | AI-service无数据源，无法持久化诊断记录 | `lab-ai-service/pom.xml` | 🟡 中 | 补充`spring-boot-starter-jdbc`或MyBatis依赖 |
| SEC-010 | Report | `AiServiceClientFallback`缺失导致AI服务down时Feign调用直接报错 | `lab-report-service/` | 🟡 中 | 实现`AiServiceClientFallback` fallback类 |
| SEC-011 | 全局 | 缺少`@RateLimit`实现或全局限流机制 | 全部Controller | 🟡 中 | 补充Sentinel或Redis限流 |
| SEC-012 | Sample | `searchSamples`全表内存过滤，无数据库层WHERE | `SampleServiceImpl.java:searchSamples` | 🟡 中 | 改用MyBatis Mapper XML实现 |
| SEC-013 | Common | 密码字段存在明文兼容模式（向后兼容遗留数据） | `UserServiceImpl.java` | 🟡 中 | 迁移完成后移除明文密码比较代码 |

---

## 4. 空实现/TODO清单

| 服务 | 类/方法 | 功能描述 | 当前状态 | 优先级 |
|------|---------|---------|---------|--------|
| Sample | `EnhancedSampleServiceImpl.getDashboardStats()` | 仪表盘统计数据 | 返回全0硬编码数据，未查DB | P0 |
| Sample | `EnhancedSampleServiceImpl.countByStatus()` | 标本状态统计 | 返回全0硬编码Map | P0 |
| Sample | `EnhancedSampleServiceImpl.countByLastDays()` | 近N天趋势 | 返回全0数据 | P0 |
| Sample | `EnhancedSampleServiceImpl.getTodayStats()` | 今日统计 | 返回全0数据 | P0 |
| Sample | `EnhancedSampleServiceImpl.getTodoList()` | 待办事项列表 | 返回空ArrayList | P1 |
| Sample | `EnhancedSampleServiceImpl.getHotTestItems()` | 热门项目排行 | 返回空ArrayList | P1 |
| Sample | `EnhancedSampleServiceImpl.exportSamplesToExcel()` | Excel导出 | 返回`byte[0]`空数据 | P0 |
| Sample | `EnhancedSampleServiceImpl.importSamplesFromExcel()` | Excel导入 | 永远返回"导入成功" | P0 |
| Sample | `EnhancedSampleServiceImpl.batchUpdateStatus()` | 批量更新状态 | 永远返回成功，未执行 | P0 |
| Sample | `EnhancedSampleServiceImpl.batchDelete()` | 批量删除 | 永远返回成功，未执行 | P0 |
| Sample | `EnhancedSampleServiceImpl.clearDashboardCache()` | 清除缓存 | 空方法体 | P1 |
| Sample | `SampleServiceImpl.getDashboardStats()` | 仪表盘统计（主服务） | 返回全0数据 | P0 |
| Sample | `SampleServiceImpl.getStatusStats()` | 状态分布统计 | 返回空列表 | P0 |
| Sample | `SampleServiceImpl.getWeeklyTrend()` | 近7天趋势 | 返回空Map | P0 |
| Sample | `SampleServiceImpl.getHotTestItems()` | 热门项目 | 返回空列表 | P1 |
| HL7 | `Hl7ServiceImpl.sendToHis()` | 发送HL7到HIS | 仅打印日志，未实际发送 | P0 |
| HL7 | `Hl7ServiceImpl.receiveFromHis()` | 从HIS接收消息 | 仅解析，无实际监听 | P1 |
| Report | `AiServiceClientFallback` | AI服务降级处理 | 类文件缺失，Feign fallback未实现 | P1 |
| Report | `lab-report-service/` 全局异常处理 | 报告服务异常处理 | 仅有`lab-common`的handler，本服务无覆盖 | P1 |
| AI | `ai-service` 数据存储 | AI诊断历史记录 | 无数据库，诊断结果不持久化 | P1 |

---

## 5. 健康检查修复方案

### 症状
`/actuator/health` 返回 404（端点不存在）或 500（数据源检查失败）

### 根因分析

**根因1：所有服务缺少 actuator 依赖**

检查结果：
- `lab-gateway/pom.xml` → 无 `spring-boot-starter-actuator`
- `lab-user-service/pom.xml` → 无 `spring-boot-starter-actuator`
- `lab-sample-service/pom.xml` → 无 `spring-boot-starter-actuator`
- `lab-report-service/pom.xml` → 无 `spring-boot-starter-actuator`
- `lab-hl7-service/pom.xml` → 无 `spring-boot-starter-actuator`
- `lab-ai-service/pom.xml` → 无 `spring-boot-starter-actuator`

**根因2：AI-service 无数据源依赖**

`lab-ai-service/pom.xml` 仅依赖 `lab-common`、`spring-boot-starter-web`、`nacos-discovery`，无 MySQL JDBC。
即使添加了 actuator，数据源健康检查也会因无数据源而报错。

### 修复方案

#### 步骤1：在各服务 pom.xml 中添加 actuator 依赖

在 `lab-common/pom.xml` 的 `<dependencies>` 中添加（各服务间接依赖）：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

或在每个微服务单独添加（推荐，版本可控）。

#### 步骤2：在各服务 application.yml 中暴露健康端点

```yaml
# lab-user-service/src/main/resources/application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info
  endpoint:
    health:
      show-details: when_authorized
  health:
    redis:
      enabled: true
    db:
      enabled: true
```

对其他服务类似配置（sample-service 去掉 db health 如果不需要）。

#### 步骤3：AI-service 补充数据源（如果需要健康检查）

在 `lab-ai-service/pom.xml` 添加：

```xml
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <scope>runtime</scope>
</dependency>
```

并在 `application.yml` 中配置数据源（AI-service 目前没有独立数据库，可选择禁用数据源健康检查）：

```yaml
management:
  health:
    db:
      enabled: false   # AI服务无数据库，禁用
```

#### 步骤4：验证修复

```bash
curl http://localhost:8086/actuator/health
# 应返回: {"status":"UP"}

curl http://localhost:8080/actuator/health
# 通过Gateway: {"status":"UP","components":{"reactiveDiscoveryClients":{"status":"UP"},"router":{"status":"UP"}}}
```

---

## 6. 总结

### 功能完成度：68%

| 服务 | 实际可用接口比例 | 说明 |
|------|----------------|------|
| Gateway | 85% | 路由完整，缺少JWT鉴权和CORS修复 |
| User Service | 75% | 登录/注册可用，分页无限大，JWT未实现 |
| Sample Service | 50% | 核心CRUD可用，增强功能多为空实现 |
| Report Service | 75% | 核心流程完整，AI降级缺失 |
| HL7 Service | 45% | 解析功能可用，发送/接收为空实现 |
| AI Service | 55% | 规则引擎可用，无外部AI接入，无数据持久化 |

### 安全评分：52/100

- ✅ 密码使用BCrypt加密
- ✅ 统一异常处理防止堆栈外泄（部分）
- ✅ 敏感字段（password）返回前清空
- ❌ **无JWT鉴权FilterChain**
- ❌ **无RBAC权限控制**
- ❌ CORS为`*`
- ❌ 分页无上限保护
- ❌ `/error`端点信息泄露

### 主要问题（按优先级排序）

| 优先级 | 问题 | 影响 |
|--------|------|------|
| P0 | `/actuator/health` 404 | K8s/负载均衡无法探测服务存活 |
| P0 | 大量EnhancedSampleService空实现 | 仪表盘、Excel导入导出、批量操作不可用 |
| P0 | `searchSamples` 全表内存过滤 | 大数据量OOM风险 |
| P0 | `sendToHis` 空实现 | HL7发送功能不可用 |
| P0 | 无JWT FilterChain | API无认证保护 |
| P1 | `listSamples` 无分页 | 性能风险 |
| P1 | `AiServiceClientFallback` 缺失 | AI服务down时报告录入报错 |
| P1 | CORS `*` | 生产安全风险 |
| P2 | AI-service 无数据源 | 诊断记录无法持久化 |
| P2 | `simple-diagnose` 返回格式问题 | 前端拼接冗余前缀 |

### 修复优先级建议

**立即修复（不影响上线）：**
1. 添加 `spring-boot-starter-actuator` 依赖 + 配置端点暴露
2. `listSamples` 接口添加分页（`size` 限制 max=100）
3. 实现 `AiServiceClientFallback` fallback类

**上线前必须修复：**
4. 实现 JWT FilterChain + 网关鉴权
5. CORS 配置改为具体域名
6. 完善 `sendToHis` HL7 发送逻辑或明确标注为模拟接口
7. `searchSamples` 改为数据库层 WHERE 查询

**建议后续迭代：**
8. 完善 EnhancedSampleService 仪表盘统计和 Excel 导入导出
9. AI-service 补充数据源支持诊断历史持久化
10. 添加全局限流（Sentinel）和操作审计日志
