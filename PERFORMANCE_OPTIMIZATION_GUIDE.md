# 实验室管理系统性能优化指南

## 概述

本文档详细说明了实验室管理系统的性能优化方案，涵盖前端、后端、数据库、缓存和微服务调用等多个层面。

---

## 1. 前端Vite构建配置优化

### 文件位置
`d:\FinalCodeAndFile\lab-management-system\frontend\vite.config.ts`

### 主要优化内容

#### 1.1 构建优化
- **代码分割策略**：更精细的手动分块，将依赖分离为 `vue-vendor`、`element-plus`、`echarts`、`utils` 等
- **资源输出规范**：按文件类型分类输出到不同目录 (`assets/js/`, `assets/css/` 等)
- **压缩优化**：生产环境移除 `console.log`，保留 `console.error` 和 `console.warn`
- **目标浏览器**：设置为 `es2015` 以获得更好的兼容性和性能

#### 1.2 开发服务器优化
- **模块预热**：配置 `warmup` 选项，提前构建常用模块，加快开发启动速度
- **依赖预构建**：显式指定 `optimizeDeps.include`，避免运行时动态加载

#### 1.3 CSS优化
- **CSS代码分割**：启用 `cssCodeSplit: true`
- **开发环境源映射**：启用 `devSourcemap` 便于调试

---

## 2. 数据库查询优化与索引建议

### 文件位置
`d:\FinalCodeAndFile\lab-management-system\sql\performance-optimization-indexes.sql`

### 2.1 索引优化策略

#### 用户表 (sys_user)
```sql
-- 复合索引优化角色+状态查询
CREATE INDEX idx_user_role_status ON sys_user(role, status);
CREATE INDEX idx_user_create_time ON sys_user(create_time);
```

#### 标本表 (lab_sample)
```sql
-- 优化日期范围查询
CREATE INDEX idx_sample_create_time_deleted ON lab_sample(create_time, deleted);

-- 优化状态+日期复合查询
CREATE INDEX idx_sample_status_create_time ON lab_sample(status, create_time);

-- 优化搜索查询
CREATE INDEX idx_sample_patient_name ON lab_sample(patient_name);
CREATE INDEX idx_sample_doctor_name ON lab_sample(doctor_name);
```

#### 检验报告表 (lab_report)
```sql
-- 优化状态+时间查询
CREATE INDEX idx_report_status_create_time ON lab_report(status, create_time);

-- 优化医师查询
CREATE INDEX idx_report_technician ON lab_report(technician_id);
CREATE INDEX idx_report_reviewer ON lab_report(reviewer_id);

-- 复合索引
CREATE INDEX idx_report_status_technician ON lab_report(status, technician_id);
```

### 2.2 查询优化
- **避免使用 `DATE()` 函数**：改用时间范围查询，让索引生效
- **复合查询优化**：使用复合索引减少回表
- **模糊查询优化**：只在必要时使用 `LIKE '%...%'`，考虑全文索引

### Mapper优化文件
`d:\FinalCodeAndFile\lab-management-system\lab-sample-service\src\main\java\com\sunyaxin\sample\mapper\SampleMapper.java`

---

## 3. Redis缓存策略优化

### 文件位置
`d:\FinalCodeAndFile\lab-management-system\lab-common\src\main\java\com\sunyaxin\common\config\RedisCacheConfig.java`

### 3.1 缓存层级策略

| 缓存区域 | 过期时间 | 说明 |
|---------|---------|------|
| dashboard | 3分钟 | 仪表盘统计，更新频繁 |
| sample:list | 10分钟 | 标本列表 |
| sample:detail | 30分钟 | 标本详情 |
| report:list | 10分钟 | 报告列表 |
| report:detail | 30分钟 | 报告详情 |
| user:login | 2小时 | 登录用户信息 |
| dict | 12小时 | 字典数据 |
| config | 24小时 | 配置数据 |

### 3.2 缓存特性
- **缓存前缀**：使用 `cacheName:` 前缀便于管理
- **事务支持**：启用 `transactionAware()`
- **非阻塞写入**：使用 `nonLockingRedisCacheWriter`
- **精细的缓存配置**：为不同业务场景设置不同的TTL

---

## 4. 微服务间调用优化

### 文件位置
`d:\FinalCodeAndFile\lab-management-system\lab-common\src\main\java\com\sunyaxin\common\config\FeignConfig.java`

### 4.1 Feign客户端配置

| 配置项 | 值 | 说明 |
|-------|----|------|
| 连接超时 | 5秒 | 建立连接的最大等待时间 |
| 读取超时 | 10秒 | 等待响应的最大时间 |
| 初始重试间隔 | 100ms | 第一次重试等待时间 |
| 最大重试间隔 | 1秒 | 重试的最大间隔 |
| 最大重试次数 | 3次 | 包括第一次请求 |
| 日志级别 | BASIC | 记录请求方法、URL、状态码和执行时间 |

### 使用示例
```java
@FeignClient(name = "ai-service", configuration = FeignConfig.class, fallback = AiServiceClientFallback.class)
public interface AiServiceClient {
    // ...
}
```

---

## 5. 前端资源加载优化

### 文件位置
`d:\FinalCodeAndFile\lab-management-system\frontend\src\utils\performance.ts`

### 5.1 图片懒加载
使用 `IntersectionObserver` API 实现高性能图片懒加载：

```typescript
import { lazyLoadImages } from '@/utils/performance';

// 在组件挂载时调用
onMounted(() => {
  lazyLoadImages('.lazy-image');
});
```

### 5.2 防抖与节流
```typescript
import { debounce, throttle } from '@/utils/performance';

// 搜索框防抖
const handleSearch = debounce((keyword) => {
  // 执行搜索
}, 300);

// 滚动事件节流
const handleScroll = throttle(() => {
  // 处理滚动
}, 100);
```

### 5.3 请求缓存
```typescript
import { requestCache } from '@/utils/performance';

// 缓存GET请求
const fetchData = async (id) => {
  const cacheKey = `data:${id}`;
  const cached = requestCache.get(cacheKey);
  if (cached) return cached;
  
  const data = await api.getData(id);
  requestCache.set(cacheKey, data);
  return data;
};
```

### 5.4 性能监控
```typescript
import { initPerformanceMonitoring } from '@/utils/performance';

// 在应用启动时初始化
initPerformanceMonitoring();
```

---

## 6. 实施步骤

### 6.1 数据库优化
1. 备份数据库
2. 执行 `performance-optimization-indexes.sql`
3. 验证索引创建成功：`SHOW INDEX FROM lab_sample;`

### 6.2 后端优化
1. 重新编译 `lab-common` 模块
2. 重新编译各个微服务
3. 重启服务

### 6.3 前端优化
1. 安装依赖（如有新增）
2. 执行构建：`npm run build`
3. 部署构建产物

---

## 7. 性能监控建议

### 7.1 数据库监控
- 开启慢查询日志：`SET GLOBAL slow_query_log = 'ON';`
- 设置慢查询阈值：`SET GLOBAL long_query_time = 1;`
- 定期使用 `EXPLAIN` 分析查询执行计划

### 7.2 Redis监控
- 监控内存使用情况
- 监控缓存命中率
- 定期清理过期键

### 7.3 前端监控
- 使用 Lighthouse 定期审计
- 监控 Core Web Vitals
- 收集真实用户监控(RUM)数据

---

## 8. 预期效果

| 优化项 | 预期提升 |
|-------|---------|
| 首屏加载时间 | 减少 30-50% |
| API响应时间 | 减少 40-60%（有缓存时） |
| 数据库查询 | 减少 50-70%（索引生效） |
| 构建时间 | 减少 20-30% |
| 内存占用 | 更稳定的内存使用 |

---

## 9. 注意事项

1. **索引维护**：索引会增加写入开销，根据读写比例调整
2. **缓存一致性**：更新数据时及时清除相关缓存
3. **重试策略**：非幂等接口谨慎使用重试
4. **定期维护**：定期分析慢查询，优化索引
5. **压力测试**：优化后进行压力测试验证效果
