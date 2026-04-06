# 实验室管理系统 E2E 测试使用指南

## 📋 测试概述

本测试套件为实验室管理系统提供完整的端到端（E2E）自动化测试，覆盖所有核心业务流程。

### 测试范围

| 序号 | 测试用例 | 描述 | 预计耗时 |
|------|---------|------|---------|
| TC001 | 用户登录流程 | 验证登录功能、表单验证、跳转逻辑 | ~15秒 |
| TC002 | 仪表盘数据展示 | 验证统计卡片、图表、功能模块加载 | ~20秒 |
| TC003 | 标本管理流程 | 完整的标本创建流程测试 | ~30秒 |
| TC004 | 报告管理流程 | 完整的报告创建流程测试 | ~30秒 |
| TC005 | AI辅助诊断功能 | AI诊断界面和结果展示测试 | ~25秒 |
| TC006 | 用户管理功能 | 管理员权限下的用户管理测试 | ~20秒 |
| HC001 | 页面性能检查 | 各页面加载性能基准测试 | ~40秒 |
| HC002 | 响应式布局检查 | 多设备视口适配性测试 | ~20秒 |

**总预计耗时**: 约 3-4 分钟

---

## 🔧 环境要求

### 前置条件

1. **Node.js**: >= 16.0.0
2. **Playwright**: 1.58.2 (已安装)
3. **前端服务**: http://localhost:3001 (必须运行中)
4. **后端服务**: http://localhost:8080 (必须运行中)

### 服务状态检查

```bash
# 检查前端服务
curl http://localhost:3001/login

# 检查后端服务
curl http://localhost:8080/api/health
```

---

## 🚀 快速开始

### 1. 安装依赖 (首次)

```bash
cd d:\FinalCodeAndFile\lab-management-system\frontend

# 安装 Playwright 浏览器
npx playwright install chromium
```

### 2. 运行全部测试

```bash
cd d:\FinalCodeAndFile\lab-management-system\frontend

# 运行所有 E2E 测试
npx playwright test tests/e2e/full-lab-flow.spec.js
```

### 3. 运行特定测试用例

```bash
# 只运行登录测试
npx playwright test -g "TC001_用户登录流程"

# 只运行标本管理测试
npx playwright test -g "TC003_标本管理"

# 只运行健康检查
npx playwright test -g "快速健康检查"
```

### 4. 使用 UI 模式调试

```bash
# 可视化测试执行过程
npx playwright test --ui
```

---

## 📊 测试报告

### HTML 报告位置

测试完成后自动生成 HTML 格式的详细报告：

```
d:\FinalCodeAndFile\lab-management-system\frontend\playwright-report\index.html
```

查看报告：

```bash
npx playwright show-report
```

### 截图保存位置

所有测试截图保存在：

```
d:\FinalCodeAndFile\lab-management-system\test_results\screenshots\
```

截图命名规则：
```
{测试用例编号}_{步骤描述}_{时间戳}.png
示例: TC001_用户登录_01_登录页面初始状态_2026-04-01T10-30-00-000Z.png
```

---

## ⚙️ 配置说明

### Playwright 配置文件

配置文件位置：`d:\FinalCodeAndFile\lab-management-system\frontend\playwright.config.js`

关键配置项：

```javascript
{
  baseURL: 'http://localhost:3001',  // 前端服务地址
  timeout: 30000,                     // 全局超时 30秒
  retries: 0,                         // 失败重试次数 (CI环境为2)
  screenshot: 'only-on-failure',      // 仅失败时截图
  video: 'retain-on-failure',         // 失败时保留视频
}
```

### 测试账号配置

在测试脚本 `full-lab-flow.spec.js` 中配置：

```javascript
const TEST_CONFIG = {
  credentials: {
    username: 'admin',
    password: 'admin123'
  }
};
```

---

## 🎯 测试场景详解

### TC001: 用户登录流程

**测试步骤**：
1. 打开登录页面 `/login`
2. 输入用户名 `admin`
3. 输入密码 `admin123`
4. 点击登录按钮
5. 验证跳转到仪表盘 `/dashboard`

**验证点**:
- [x] 登录页面正确加载
- [x] 表单输入正常工作
- [x] 登录按钮可点击
- [x] 成功跳转到仪表盘
- [x] 无错误提示显示

---

### TC002: 仪表盘数据展示

**测试步骤**：
1. 登录系统
2. 访问仪表盘 `/dashboard`
3. 验证统计卡片（标本总数、报告数等）
4. 验证图表组件加载
5. 验证待办事项模块

**验证点**:
- [x] 页面标题包含"仪表盘"或"检验科工作台"
- [x] 4个核心统计卡片可见
- [x] ECharts 图表渲染完成
- [x] 待办事项列表加载
- [x] 热门检验项目显示

---

### TC003: 标本管理流程

**测试步骤**：
1. 登录系统
2. 导航到标本管理 `/sample`
3. 点击"创建标本"按钮
4. 填写患者信息（姓名、ID、年龄等）
5. 选择标本类型和检验项目
6. 填写送检信息
7. 提交表单
8. 验证成功提示

**测试数据**:
```javascript
{
  patientName: `测试患者_${Date.now()}`,
  patientId: `P${Date.now()}`,
  sampleType: 'blood',
  department: '内科'
}
```

---

### TC004: 报告管理流程

**测试步骤**：
1. 登录系统
2. 导航到报告管理 `/report`
3. 点击"创建报告"按钮
4. 填写基本信息（类型、关联标本）
5. 填写患者信息
6. 添加检验结果
7. 填写备注和医生意见
8. 提交审核
9. 验证提交成功

---

### TC005: AI辅助诊断功能

**测试步骤**：
1. 登录系统
2. 导航到AI诊断 `/ai`
3. 切换到血常规诊断标签
4. 输入测试数据：
   - 白细胞: 7.5
   - 红细胞: 4.8
   - 血红蛋白: 145
   - 血小板: 220
5. 点击"开始诊断"
6. 等待AI分析完成
7. 验证诊断结果显示

**注意**: 此测试需要后端AI服务正常运行

---

### TC006: 用户管理功能

**测试步骤**：
1. 使用管理员账号登录
2. 导航到用户管理 `/user`
3. 验证用户列表加载
4. 查看用户详情
5. 测试搜索功能
6. 验证分页组件

**权限要求**: 需要 ADMIN 角色权限

---

## 🔍 故障排查

### 常见问题

#### 1. 连接被拒绝 (ECONNREFUSED)

**原因**: 前端或后端服务未启动

**解决方案**:
```bash
# 启动前端服务
cd d:\FinalCodeAndFile\lab-management-system\frontend
npm run dev

# 启动后端服务 (另开终端)
cd d:\FinalCodeAndFile\lab-management-system
# 启动各个微服务...
```

#### 2. 超时错误 (Timeout)

**原因**: 网络慢或服务器响应慢

**解决方案**:
- 在 `playwright.config.js` 中增加超时时间
- 检查网络连接
- 减少并行测试数: `workers: 1`

#### 3. 元素找不到 (Element not found)

**原因**: UI结构变化或选择器过时

**解决方案**:
- 使用 UI 模式调试: `npx playwright test --ui`
- 更新测试脚本中的选择器
- 截图查看当前页面状态

#### 4. 权限不足

**原因**: 测试账号角色不匹配

**解决方案**:
- 确认使用 admin 账号登录
- 检查用户角色是否为 ADMIN

#### 5. Playwright 浏览器未安装

**解决方案**:
```bash
npx playwright install
```

---

## 📈 性能基准

### 页面加载时间标准

| 页面 | 可接受时间 | 优秀时间 |
|------|----------|---------|
| 登录页 | < 3秒 | < 1.5秒 |
| 仪表盘 | < 5秒 | < 3秒 |
| 标本列表 | < 4秒 | < 2秒 |
| 创建表单 | < 3秒 | < 1.5秒 |
| AI诊断页 | < 4秒 | < 2秒 |

### 浏览器兼容性

✅ Chromium (推荐)  
✅ Firefox  
✅ WebKit (Safari)  

移动端模拟:
- Pixel 5 (Android)
- iPhone 12 (iOS)

---

## 🛠️ 高级用法

### 自定义测试数据

编辑 `full-lab-flow.spec.js` 中的 `TEST_DATA` 对象：

```javascript
const TEST_DATA = {
  sample: {
    patientName: '自定义患者名称',
    // ... 其他字段
  }
};
```

### 并行执行控制

在 `playwright.config.js` 中：

```javascript
workers: 1,  // 串行执行（适合调试）
workers: 4,  // 4个并行（适合CI）
```

### CI/CD 集成

GitHub Actions 示例:

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - setup-node@v3
      - run: npm install
      - run: npx playwright install --with-deps
      - run: npx playwright test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 📝 最佳实践

### 1. 编写稳定的选择器

```javascript
// ✅ 好: 使用语义化选择器
page.locator('button:has-text("提交")')

// ❌ 差: 使用脆弱的CSS类
page.locator('.el-button--primary')
```

### 2. 等待策略

```javascript
// ✅ 好: 明确等待
await page.waitForLoadState('networkidle')
await expect(element).toBeVisible()

// ❌ 差: 固定等待
await page.waitForTimeout(5000)
```

### 3. 错误处理

```javascript
try {
  await operation();
} catch (error) {
  await saveScreenshot(page, 'testName', 'error');
  throw error;
}
```

---

## 📞 支持与反馈

遇到问题时：

1. 查看 `playwright-report/index.html` 详细报告
2. 检查 `test_results/screenshots/` 截图
3. 查看终端输出的日志信息
4. 使用 `--ui` 模式交互式调试

---

## 📄 更新日志

### v1.0.0 (2026-04-01)
- ✅ 初始版本发布
- ✅ 覆盖6大核心业务流程
- ✅ 包含性能和兼容性检查
- ✅ 自动截图和HTML报告生成
- ✅ 完善的错误处理机制

---

**测试框架**: Playwright 1.58.2  
**适用项目**: 实验室管理系统 v1.0  
**最后更新**: 2026-04-01  
**维护者**: Frontend Architect Team
