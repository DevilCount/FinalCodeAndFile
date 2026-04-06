/**
 * 实验室管理系统 - 浏览器控制台错误检测 E2E 自动化测试脚本 (最严格版)
 *
 * 核心目标：
 * 1. 监控并报告浏览器控制台的所有错误和警告（这才是真正重要的！）
 * 2. 检测 Console.error() - 所有JavaScript错误
 * 3. 检测 Console.warn() - 所有警告信息
 * 4. 检测 [Vue warn] - Vue组件警告
 * 5. 检测网络请求失败 - HTTP 4xx/5xx 状态码
 * 6. 检测资源加载失败 - 404/500等
 * 7. 检测未捕获的Promise rejection
 * 8. 检测API响应错误
 *
 * 绝对不能忽略的错误类型：
 * - Failed to resolve component (组件未注册)
 * - Cannot read property (空指针)
 * - Network Error (网络错误)
 * - CORS policy (跨域错误)
 * - Unexpected token (语法错误)
 * - undefined is not a function (函数调用错误)
 *
 * @author Frontend Architect + Test Engineer
 * @version 1.0.0 (Console Error Detection Edition)
 * @date 2026-04-05
 */

const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

// ============================================================================
// 测试配置常量
// ============================================================================
const CONFIG = {
  baseURL: 'http://localhost:3000',
  credentials: {
    username: 'admin',
    password: 'admin123'
  },
  timeouts: {
    navigation: 30000,
    action: 10000,
    assertion: 5000,
    loginWait: 8000,
    pageStabilize: 2000  // 页面稳定等待时间
  },
  screenshotDir: path.join(__dirname, '../../../test_results/screenshots/console-error-detection')
};

// ============================================================================
// 全局错误收集器（核心！）
// ============================================================================
const errorCollector = {
  // 控制台错误 (致命)
  consoleErrors: [],
  // 控制台警告
  consoleWarnings: [],
  // 页面错误 (JavaScript异常)
  pageErrors: [],
  // 失败的请求
  failedRequests: [],
  // API错误响应 (4xx/5xx)
  apiErrorResponses: [],

  // 重置收集器
  reset() {
    this.consoleErrors = [];
    this.consoleWarnings = [];
    this.pageErrors = [];
    this.failedRequests = [];
    this.apiErrorResponses = [];
  },

  // 获取统计信息
  getStats() {
    return {
      totalErrors: this.consoleErrors.length + this.pageErrors.length + this.failedRequests.length,
      consoleErrorsCount: this.consoleErrors.length,
      consoleWarningsCount: this.consoleWarnings.length,
      pageErrorsCount: this.pageErrors.length,
      failedRequestsCount: this.failedRequests.length,
      apiErrorResponsesCount: this.apiErrorResponses.length
    };
  },

  // 判断是否有致命错误（只关注真正严重的问题）
  hasFatalErrors() {
    const hasConsoleErrors = this.consoleErrors.length > 0;
    const hasPageErrors = this.pageErrors.length > 0;
    const hasCriticalFailedRequests = this.failedRequests.some(req => req.isCritical);
    const hasServerErrors = this.apiErrorResponses.some(res => res.status >= 500);

    return (
      hasConsoleErrors ||
      hasPageErrors ||
      hasCriticalFailedRequests ||
      hasServerErrors
    );
  },

  // 获取真正的致命错误数量
  getFatalErrorCount() {
    return (
      this.consoleErrors.length +
      this.pageErrors.length +
      this.failedRequests.filter(req => req.isCritical).length +
      this.apiErrorResponses.filter(res => res.status >= 500).length
    );
  }
};

// ============================================================================
// 辅助函数
// ============================================================================

/**
 * 获取当前时间戳字符串
 */
function getTimestamp() {
  return new Date().toLocaleTimeString('zh-CN', { hour12: false });
}

/**
 * 确保截图目录存在
 */
function ensureScreenshotDir() {
  if (!fs.existsSync(CONFIG.screenshotDir)) {
    fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });
    console.log(`[创建目录] ${CONFIG.screenshotDir}`);
  }
}

/**
 * 保存截图并记录路径
 */
async function saveScreenshot(page, testName, step) {
  ensureScreenshotDir();
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `${testName}_${step}_${timestamp}.png`;
  const filepath = path.join(CONFIG.screenshotDir, filename);

  try {
    await page.screenshot({
      path: filepath,
      fullPage: true,
      type: 'png'
    });
    console.log(`[截图保存] ${filename}`);
    return filepath;
  } catch (error) {
    console.error(`[截图失败] ${error.message}`);
    return null;
  }
}

/**
 * 日志输出函数
 */
function log(testCase, action, status, detail = '') {
  const timestamp = getTimestamp();
  const icon = status === 'PASS' ? '✓' : status === 'FAIL' ? '✗' : status === 'WARN' ? '⚠' : status === 'ERROR' ? '✗✗' : '•';
  console.log(`[${timestamp}] [${testCase}] ${icon} ${action}${detail ? ' - ' + detail : ''}`);
}

/**
 * 等待页面网络空闲
 */
async function waitForNetworkIdle(page, timeout = CONFIG.timeouts.navigation) {
  try {
    await page.waitForLoadState('networkidle', { timeout });
  } catch (error) {
    log('SYSTEM', '网络空闲等待', 'WARN', `超时 (${timeout}ms)，继续执行`);
  }
}

/**
 * 设置所有事件监听器（核心功能）
 * @param {Page} page - Playwright页面对象
 * @param {string} testName - 当前测试名称，用于标记错误的来源
 */
function setupEventListeners(page, testName) {
  console.log(`\n[${getTimestamp()}] [${testName}] 🎯 设置事件监听器...`);

  // ========== 监听所有console消息 ==========
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    const location = msg.location();

    if (type === 'error') {
      const errorInfo = {
        type: 'CONSOLE_ERROR',
        message: text,
        file: location?.url || 'unknown',
        line: location?.lineNumber || 0,
        column: location?.columnNumber || 0,
        timestamp: new Date().toISOString(),
        sourceTest: testName
      };

      errorCollector.consoleErrors.push(errorInfo);

      // 根据错误类型判断严重性
      const isCritical = text.includes('Failed to resolve component') ||
                        text.includes('Cannot read property') ||
                        text.includes('Cannot read properties') ||
                        text.includes('undefined is not') ||
                        text.includes('null is not an object') ||
                        text.includes('is not a function') ||
                        text.includes('Unexpected token') ||
                        text.includes('SyntaxError') ||
                        text.includes('TypeError') ||
                        text.includes('ReferenceError') ||
                        text.includes('Network Error') ||
                        text.includes('CORS policy') ||
                        text.includes('Failed to fetch') ||
                        text.includes('Network request failed') ||
                        text.includes('Load failed');

      if (isCritical) {
        console.error(`[${getTimestamp()}] [${testName}] ✗✗ 致命CONSOLE_ERROR:`);
        console.error(`   消息: ${text}`);
        console.error(`   文件: ${location?.url}:${location?.lineNumber}`);
      } else {
        console.warn(`[${getTimestamp()}] [${testName}] ⚠ CONSOLE_ERROR: ${text}`);
      }
    }

    if (type === 'warning') {
      const warningInfo = {
        type: 'CONSOLE_WARNING',
        message: text,
        file: location?.url || 'unknown',
        line: location?.lineNumber || 0,
        timestamp: new Date().toISOString(),
        sourceTest: testName
      };

      errorCollector.consoleWarnings.push(warningInfo);

      // 特别关注Vue警告
      const isVueWarning = text.includes('[Vue warn]') || text.includes('Vue warning');
      if (isVueWarning) {
        console.warn(`[${getTimestamp()}] [${testName}] ⚠ Vue WARNING: ${text}`);
      } else {
        console.log(`[${getTimestamp()}] [${testName}] ⚠ Warning: ${text}`);
      }
    }
  });

  // ========== 监听页面错误（JavaScript异常）==========
  page.on('pageerror', error => {
    const errorInfo = {
      type: 'PAGE_ERROR',
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      sourceTest: testName
    };

    errorCollector.pageErrors.push(errorInfo);
    console.error(`[${getTimestamp()}] [${testName}] ✗✗ 致命PAGE_ERROR (JavaScript异常):`);
    console.error(`   消息: ${error.message}`);
    console.error(`   堆栈:\n${error.stack}`);
  });

  // ========== 监听请求失败 ==========
  page.on('requestfailed', request => {
    const url = request.url();
    const failure = request.failure();

    // 安全地获取响应状态码
    let responseStatus = 0;
    try {
      const response = request.response();
      if (response && typeof response.status === 'function') {
        responseStatus = response.status();
      }
    } catch (e) {
      // 忽略获取状态码时的错误
    }

    const errorInfo = {
      type: 'FAILED_REQUEST',
      url: url,
      method: request.method(),
      failure: failure?.errorText || 'Unknown failure',
      status: responseStatus,
      timestamp: new Date().toISOString(),
      sourceTest: testName,
      isCritical: !url.includes('.css') && !url.includes('.png') && !url.includes('.jpg') && !url.includes('.ico') && !url.includes('.woff')
    };

    errorCollector.failedRequests.push(errorInfo);

    if (errorInfo.isCritical) {
      console.error(`[${getTimestamp()}] [${testName}] ✗✗ 致命REQUEST_FAILED:`);
      console.error(`   方法: ${request.method()}`);
      console.error(`   URL: ${url}`);
      console.error(`   错误: ${failure?.errorText}`);
      console.error(`   状态码: ${responseStatus || 'N/A'}`);
    } else {
      console.warn(`[${getTimestamp()}] [${testName}] ⚠ Request Failed (非关键): ${url} - ${failure?.errorText}`);
    }
  });

  // ========== 监听响应（检查4xx/5xx）==========
  page.on('response', response => {
    try {
      const status = response.status();
      const url = response.url();

      // 只关注API请求和关键资源
      if (status >= 400 && (url.includes('/api/') || url.includes('/user') || url.includes('/sample') || url.includes('/report') || url.includes('/dashboard'))) {
        const errorInfo = {
          type: 'API_ERROR_RESPONSE',
          url: url,
          method: response.request().method(),
          status: status,
          statusText: response.statusText(),
          timestamp: new Date().toISOString(),
          sourceTest: testName
        };

        errorCollector.apiErrorResponses.push(errorInfo);

        if (status >= 500) {
          console.error(`[${getTimestamp()}] [${testName}] ✗✗ API ERROR (${status}):`);
          console.error(`   方法: ${response.request().method()}`);
          console.error(`   URL: ${url}`);
          console.error(`   状态: ${status} ${response.statusText()}`);
        } else if (status >= 400) {
          console.warn(`[${getTimestamp()}] [${testName}] ⚠ API Warning (${status}): ${response.request().method()} ${url}`);
        }

        // 尝试读取响应体（异步操作，不阻塞）
        response.text().then(body => {
          errorInfo.responseBody = body.substring(0, 500); // 只保留前500字符
          if (status >= 500) {
            console.error(`   响应体: ${body.substring(0, 200)}...`);
          }
        }).catch(() => {});
      }
    } catch (error) {
      // 忽略响应处理中的错误
    }
  });

  console.log(`[${getTimestamp()}] [${testName}] ✓ 事件监听器设置完成\n`);
}

/**
 * 打印当前错误摘要
 */
function printErrorSummary(testName) {
  const stats = errorCollector.getStats();

  console.log(`\n[${getTimestamp()}] [${testName}] 📊 当前错误摘要:`);
  console.log(`   Console Errors: ${stats.consoleErrorsCount}`);
  console.log(`   Console Warnings: ${stats.consoleWarningsCount}`);
  console.log(`   Page Errors: ${stats.pageErrorsCount}`);
  console.log(`   Failed Requests: ${stats.failedRequestsCount}`);
  console.log(`   API Error Responses: ${stats.apiErrorResponsesCount}`);
  console.log(`   总计潜在问题: ${stats.totalErrors}\n`);

  return stats;
}

// ============================================================================
// TC001: 登录流程 + 控制台监控
// ============================================================================
test.describe('TC001_登录流程_控制台监控', () => {

  test('登录流程 - 必须检测所有控制台错误和警告', async ({ page }) => {
    const tcId = 'TC001';
    log(tcId, '开始登录流程+控制台监控测试', 'INFO');
    log(tcId, '═══════════════════════════════════', 'INFO');

    // 重置错误收集器
    errorCollector.reset();
    log(tcId, '重置错误收集器', 'INFO');

    // 设置浏览器上下文
    page.setDefaultTimeout(CONFIG.timeouts.action);
    page.setDefaultNavigationTimeout(CONFIG.timeouts.navigation);

    // ========== Step 0: 初始化监听器（在打开页面之前！）==========
    log(tcId, 'Step 0: 初始化事件监听器', 'INFO');
    setupEventListeners(page, tcId);

    try {
      // ========== Step 1: 打开浏览器访问登录页 ==========
      log(tcId, 'Step 1: 打开登录页面', 'INFO');
      await page.goto(`${CONFIG.baseURL}/login`, { waitUntil: 'domcontentloaded' });
      await waitForNetworkIdle(page);
      await page.waitForTimeout(CONFIG.timeouts.pageStabilize); // 等待页面稳定

      // 记录进入页面时的控制台状态
      log(tcId, '记录登录页初始状态的控制台输出', 'INFO');
      const statsAfterLoginLoad = printErrorSummary(tcId);

      // 截图: 登录页初始状态
      await saveScreenshot(page, tcId, '01_登录页初始状态');

      // 验证页面已加载
      const pageTitle = await page.title();
      log(tcId, '验证页面标题', 'INFO', `"${pageTitle}"`);

      // ========== Step 2: 填写表单 ==========
      log(tcId, 'Step 2: 填写登录表单', 'INFO');

      const usernameInput = page.locator('input[placeholder="请输入用户名"]');
      await expect(usernameInput).toBeVisible({ timeout: CONFIG.timeouts.assertion });
      await usernameInput.click({ clickCount: 3 });
      await page.waitForTimeout(200);
      await usernameInput.fill(CONFIG.credentials.username);
      log(tcId, '输入用户名', 'PASS', `"${CONFIG.credentials.username}"`);

      const passwordInput = page.locator('input[type="password"]');
      await expect(passwordInput).toBeVisible({ timeout: CONFIG.timeouts.assertion });
      await passwordInput.click({ clickCount: 3 });
      await page.waitForTimeout(200);
      await passwordInput.fill(CONFIG.credentials.password);
      log(tcId, '输入密码', 'PASS', '****');

      // 截图: 表单填写完成
      await saveScreenshot(page, tcId, '02_表单填写完成');

      // 记录填写表单后的控制台状态
      log(tcId, '记录填写表单后的控制台输出', 'INFO');
      printErrorSummary(tcId);

      // ========== Step 3: 点击登录按钮 ==========
      log(tcId, 'Step 3: 点击登录按钮', 'INFO');

      const loginButton = page.locator('button:has-text("登 录")');
      await expect(loginButton).toBeVisible({ timeout: CONFIG.timeouts.assertion });
      await loginButton.click();
      log(tcId, '点击登录按钮', 'PASS');

      // ========== Step 4: 等待跳转完成 ==========
      log(tcId, 'Step 4: 等待登录响应和页面跳转...', 'INFO');
      await page.waitForTimeout(CONFIG.timeouts.loginWait);

      // 特别重要：记录登录后的所有控制台输出
      log(tcId, '═══════════════════════════════════', 'INFO');
      log(tcId, '🔍 关键检查点: 登录后的控制台状态', 'INFO');
      log(tcId, '═══════════════════════════════════', 'INFO');
      const statsAfterLogin = printErrorSummary(tcId);

      // ========== Step 5: 验证URL ==========
      const currentUrl = page.url();
      log(tcId, 'Step 5: 验证当前URL', 'INFO', currentUrl);

      if (currentUrl.includes('/dashboard') || currentUrl.endsWith('/') || !currentUrl.includes('/login')) {
        log(tcId, '登录成功 - URL验证通过', 'PASS', `当前URL: ${currentUrl}`);

        // 截图: 登录成功后的页面
        await saveScreenshot(page, tcId, '03_登录成功后页面');

        // 最终错误检查
        log(tcId, '═══════════════════════════════════', 'INFO');
        log(tcId, '📋 TC001最终判定:', 'INFO');

        if (errorCollector.hasFatalErrors()) {
          log(tcId, '发现致命错误!', 'FAIL');
          throw new Error(`TC001 登录流程检测到 ${errorCollector.getFatalErrorCount()} 个致命错误`);
        } else {
          const finalStats = errorCollector.getStats();
          log(tcId, '登录流程完成', 'PASS', `Console Errors: ${finalStats.consoleErrorsCount}, Warnings: ${finalStats.consoleWarningsCount}, Page Errors: ${finalStats.pageErrorsCount}`);
        }

      } else {
        let errorMessage = '未知错误';
        try {
          const errorElement = page.locator('.el-message--error, .el-message-box__message').first();
          if (await errorElement.isVisible({ timeout: 2000 })) {
            errorMessage = await errorElement.textContent();
          }
        } catch (e) {}

        await saveScreenshot(page, tcId, 'FAIL_登录失败');
        throw new Error(`登录失败 - 错误信息: ${errorMessage}`);
      }

    } catch (error) {
      log(tcId, '登录流程失败', 'FAIL', error.message);

      // 打印完整的错误清单
      log(tcId, '═══════════════════════════════════', 'ERROR');
      log(tcId, '❌ 完整错误清单:', 'ERROR');
      log(tcId, '═══════════════════════════════════', 'ERROR');

      if (errorCollector.consoleErrors.length > 0) {
        console.error('\n--- Console Errors ---');
        errorCollector.consoleErrors.forEach((err, index) => {
          console.error(`${index + 1}. [${err.timestamp}] ${err.message}`);
          console.error(`   文件: ${err.file}:${err.line}`);
        });
      }

      if (errorCollector.pageErrors.length > 0) {
        console.error('\n--- Page Errors (JavaScript异常) ---');
        errorCollector.pageErrors.forEach((err, index) => {
          console.error(`${index + 1}. [${err.timestamp}] ${err.message}`);
          console.error(`   堆栈: ${err.stack}`);
        });
      }

      if (errorCollector.failedRequests.length > 0) {
        console.error('\n--- Failed Requests ---');
        errorCollector.failedRequests.forEach((req, index) => {
          console.error(`${index + 1}. [${req.timestamp}] ${req.method} ${req.url}`);
          console.error(`   错误: ${req.failure}`);
        });
      }

      try {
        await saveScreenshot(page, tcId, 'ERROR_异常截图');
      } catch (e) {}

      throw error;
    }
  });
});

// ============================================================================
// TC002: 仪表盘 + 控制台监控
// ============================================================================
test.describe('TC002_仪表盘_控制台监控', () => {

  test('仪表盘页面 - 必须检测所有控制台错误', async ({ page }) => {
    const tcId = 'TC002';
    log(tcId, '开始仪表盘+控制台监控测试', 'INFO');
    log(tcId, '═══════════════════════════════════', 'INFO');

    // 重置错误收集器
    errorCollector.reset();
    log(tcId, '重置错误收集器', 'INFO');

    page.setDefaultTimeout(CONFIG.timeouts.action);
    page.setDefaultNavigationTimeout(CONFIG.timeouts.navigation);

    // 初始化监听器
    setupEventListeners(page, tcId);

    try {
      // 先登录
      log(tcId, '执行登录操作', 'INFO');
      await page.goto(`${CONFIG.baseURL}/login`, { waitUntil: 'domcontentloaded' });
      await page.locator('input[placeholder="请输入用户名"]').fill(CONFIG.credentials.username);
      await page.locator('input[type="password"]').fill(CONFIG.credentials.password);
      await page.locator('button:has-text("登 录")').click();
      await page.waitForTimeout(CONFIG.timeouts.loginWait);

      // 清除登录阶段的错误（如果有的话），重新开始监控仪表盘
      log(tcId, '清除登录阶段数据，开始仪表盘专项监控', 'INFO');
      errorCollector.reset();

      // ========== Step 1: 导航到仪表盘 ==========
      log(tcId, 'Step 1: 导航到仪表盘页面', 'INFO');
      await page.goto(`${CONFIG.baseURL}/dashboard`, { waitUntil: 'networkidle' });
      await waitForNetworkIdle(page);
      await page.waitForTimeout(CONFIG.timeouts.pageStabilize);

      // 记录仪表盘加载时的控制台状态
      log(tcId, '记录仪表盘初始加载的控制台输出', 'INFO');
      printErrorSummary(tcId);

      // 截图
      await saveScreenshot(page, tcId, '01_仪表盘初始状态');

      // ========== Step 2: 点击刷新按钮 ==========
      log(tcId, 'Step 2: 查找并点击刷新按钮', 'INFO');

      const refreshButton = page.locator('button:has-text("刷新"), button:has-text("刷 新")').first();
      if (await refreshButton.isVisible({ timeout: 3000 }).catch(() => false)) {
        await refreshButton.click();
        log(tcId, '点击刷新按钮', 'PASS');

        await page.waitForTimeout(3000);

        // 记录刷新后的控制台状态（特别重要！）
        log(tcId, '═══════════════════════════════════', 'INFO');
        log(tcId, '🔍 关键检查点: 刷新后的控制台状态', 'INFO');
        log(tcId, '═══════════════════════════════════', 'INFO');
        printErrorSummary(tcId);

        await saveScreenshot(page, tcId, '02_刷新后状态');
      } else {
        log(tcId, '未找到刷新按钮', 'WARN');
        await saveScreenshot(page, tcId, '02_当前状态');
      }

      // ========== 最终判定 ==========
      log(tcId, '═══════════════════════════════════', 'INFO');
      log(tcId, '📋 TC002最终判定:', 'INFO');

      if (errorCollector.hasFatalErrors()) {
        log(tcId, '发现致命错误!', 'FAIL');
        throw new Error(`TC002 仪表盘检测到 ${errorCollector.getFatalErrorCount()} 个致命错误`);
      } else {
        const finalStats = errorCollector.getStats();
        log(tcId, '仪表盘测试完成', 'PASS', `Errors: ${finalStats.consoleErrorsCount}, Warnings: ${finalStats.consoleWarningsCount}`);
      }

      await saveScreenshot(page, tcId, '03_最终状态');

    } catch (error) {
      log(tcId, '仪表盘测试失败', 'FAIL', error.message);
      printCompleteErrorReport(tcId);
      try { await saveScreenshot(page, tcId, 'ERROR_失败截图'); } catch (e) {}
      throw error;
    }
  });
});

// ============================================================================
// TC003: 标本管理 + 控制台监控
// ============================================================================
test.describe('TC003_标本管理_控制台监控', () => {

  test('标本管理 - 必须检测API调用错误和控制台错误', async ({ page }) => {
    const tcId = 'TC003';
    log(tcId, '开始标本管理+控制台监控测试', 'INFO');
    log(tcId, '═══════════════════════════════════', 'INFO');

    errorCollector.reset();
    setupEventListeners(page, tcId);

    page.setDefaultTimeout(CONFIG.timeouts.action);
    page.setDefaultNavigationTimeout(CONFIG.timeouts.navigation);

    try {
      // 先登录
      log(tcId, '执行登录', 'INFO');
      await page.goto(`${CONFIG.baseURL}/login`, { waitUntil: 'domcontentloaded' });
      await page.locator('input[placeholder="请输入用户名"]').fill(CONFIG.credentials.username);
      await page.locator('input[type="password"]').fill(CONFIG.credentials.password);
      await page.locator('button:has-text("登 录")').click();
      await page.waitForTimeout(CONFIG.timeouts.loginWait);

      // 重置，开始标本管理专项监控
      errorCollector.reset();

      // ========== Step 1: 导航到标本管理 ==========
      log(tcId, 'Step 1: 导航到标本管理页面', 'INFO');
      await page.goto(`${CONFIG.baseURL}/sample`, { waitUntil: 'networkidle' });
      await waitForNetworkIdle(page);
      await page.waitForTimeout(CONFIG.timeouts.pageStabilize);

      // 记录标本列表加载时的控制台状态
      log(tcId, '记录标本列表加载的控制台输出', 'INFO');
      printErrorSummary(tcId);

      await saveScreenshot(page, tcId, '01_标本列表页面');

      // ========== Step 2: 尝试创建标本 ==========
      log(tcId, 'Step 2: 尝试创建标本', 'INFO');

      const createButton = page.locator('button:has-text("新建标本"), button:has-text("新 建")').first();
      if (await createButton.isVisible({ timeout: 5000 }).catch(() => false)) {
        await createButton.click();
        log(tcId, '点击新建标本按钮', 'PASS');

        await page.waitForTimeout(2000);

        await saveScreenshot(page, tcId, '02_创建标本表单');

        // 填写表单
        const patientInput = page.locator('input[placeholder*="患者姓名"], input[placeholder*="请输入患者"]').first();
        if (await patientInput.isVisible({ timeout: 3000 }).catch(() => false)) {
          await patientInput.fill(`ConsoleTest_${Date.now()}`);
          log(tcId, '填写患者姓名', 'PASS');
        }

        await saveScreenshot(page, tcId, '03_表单填写完成');

        // 提交
        const submitButton = page.locator('button:has-text("提交"), button:has-text("创 建")').first();
        if (await submitButton.isVisible({ timeout: 3000 }).catch(() => false)) {
          await submitButton.scrollIntoViewIfNeeded();
          await submitButton.click();
          log(tcId, '点击提交按钮', 'PASS');

          // 等待API响应
          await page.waitForTimeout(4000);

          // ★★★ 关键：检查API调用的HTTP状态码 ★★★
          log(tcId, '═══════════════════════════════════', 'INFO');
          log(tcId, '🔍 关键检查点: 提交标本后的API响应状态', 'INFO');
          log(tcId, '═══════════════════════════════════', 'INFO');
          printErrorSummary(tcId);

          await saveScreenshot(page, tcId, '04_提交结果');
        }
      }

      // ========== 最终判定 ==========
      log(tcId, '═══════════════════════════════════', 'INFO');
      log(tcId, '📋 TC003最终判定:', 'INFO');

      if (errorCollector.hasFatalErrors()) {
        log(tcId, '发现致命错误!', 'FAIL');
        throw new Error(`TC003 标本管理检测到 ${errorCollector.getFatalErrorCount()} 个致命错误`);
      } else {
        const finalStats = errorCollector.getStats();
        log(tcId, '标本管理测试完成', 'PASS', `Errors: ${finalStats.consoleErrorsCount}, Warnings: ${finalStats.consoleWarningsCount}, API Errors: ${finalStats.apiErrorResponsesCount}`);
      }

      await saveScreenshot(page, tcId, '05_最终状态');

    } catch (error) {
      log(tcId, '标本管理测试失败', 'FAIL', error.message);
      printCompleteErrorReport(tcId);
      try { await saveScreenshot(page, tcId, 'ERROR_失败截图'); } catch (e) {}
      throw error;
    }
  });
});

// ============================================================================
// TC004-007: 其他页面快速扫描（同样标准）
// ============================================================================

test.describe('TC004_报告管理_控制台监控', () => {

  test('报告管理 - 控制台错误检测', async ({ page }) => {
    const tcId = 'TC004';
    log(tcId, '开始报告管理+控制台监控测试', 'INFO');

    errorCollector.reset();
    setupEventListeners(page, tcId);

    page.setDefaultTimeout(CONFIG.timeouts.action);
    page.setDefaultNavigationTimeout(CONFIG.timeouts.navigation);

    try {
      // 登录
      await page.goto(`${CONFIG.baseURL}/login`, { waitUntil: 'domcontentloaded' });
      await page.locator('input[placeholder="请输入用户名"]').fill(CONFIG.credentials.username);
      await page.locator('input[type="password"]').fill(CONFIG.credentials.password);
      await page.locator('button:has-text("登 录")').click();
      await page.waitForTimeout(CONFIG.timeouts.loginWait);

      errorCollector.reset();

      // 导航到报告管理
      log(tcId, '导航到报告管理页面', 'INFO');
      await page.goto(`${CONFIG.baseURL}/report`, { waitUntil: 'networkidle' });
      await waitForNetworkIdle(page);
      await page.waitForTimeout(CONFIG.timeouts.pageStabilize);

      printErrorSummary(tcId);
      await saveScreenshot(page, tcId, '01_报告列表页面');

      // 尝试创建报告
      const createBtn = page.locator('button:has-text("新建报告")').first();
      if (await createBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
        await createBtn.click();
        await page.waitForTimeout(2000);
        await saveScreenshot(page, tcId, '02_创建报告表单');
      }

      printErrorSummary(tcId);

      if (errorCollector.hasFatalErrors()) {
        throw new Error(`TC004 报告管理检测到 ${errorCollector.getFatalErrorCount()} 个致命错误`);
      }

      log(tcId, '报告管理测试完成', 'PASS');
      await saveScreenshot(page, tcId, '03_最终状态');

    } catch (error) {
      log(tcId, '报告管理测试失败', 'FAIL', error.message);
      printCompleteErrorReport(tcId);
      throw error;
    }
  });
});

test.describe('TC005_AI诊断_控制台监控', () => {

  test('AI诊断 - 控制台错误检测', async ({ page }) => {
    const tcId = 'TC005';
    log(tcId, '开始AI诊断+控制台监控测试', 'INFO');

    errorCollector.reset();
    setupEventListeners(page, tcId);

    page.setDefaultTimeout(CONFIG.timeouts.action);
    page.setDefaultNavigationTimeout(CONFIG.timeouts.navigation);

    try {
      // 登录
      await page.goto(`${CONFIG.baseURL}/login`, { waitUntil: 'domcontentloaded' });
      await page.locator('input[placeholder="请输入用户名"]').fill(CONFIG.credentials.username);
      await page.locator('input[type="password"]').fill(CONFIG.credentials.password);
      await page.locator('button:has-text("登 录")').click();
      await page.waitForTimeout(CONFIG.timeouts.loginWait);

      errorCollector.reset();

      // 导航到AI诊断
      log(tcId, '导航到AI诊断页面', 'INFO');
      await page.goto(`${CONFIG.baseURL}/ai`, { waitUntil: 'networkidle' });
      await waitForNetworkIdle(page);
      await page.waitForTimeout(CONFIG.timeouts.pageStabilize);

      printErrorSummary(tcId);
      await saveScreenshot(page, tcId, '01_AI诊断页面');

      if (errorCollector.hasFatalErrors()) {
        throw new Error(`TC005 AI诊断检测到 ${errorCollector.getStats().totalErrors} 个错误/警告`);
      }

      log(tcId, 'AI诊断测试完成', 'PASS');
      await saveScreenshot(page, tcId, '02_最终状态');

    } catch (error) {
      log(tcId, 'AI诊断测试失败', 'FAIL', error.message);
      printCompleteErrorReport(tcId);
      throw error;
    }
  });
});

test.describe('TC006_用户管理_控制台监控', () => {

  test('用户管理 - 控制台错误检测', async ({ page }) => {
    const tcId = 'TC006';
    log(tcId, '开始用户管理+控制台监控测试', 'INFO');

    errorCollector.reset();
    setupEventListeners(page, tcId);

    page.setDefaultTimeout(CONFIG.timeouts.action);
    page.setDefaultNavigationTimeout(CONFIG.timeouts.navigation);

    try {
      // 登录
      await page.goto(`${CONFIG.baseURL}/login`, { waitUntil: 'domcontentloaded' });
      await page.locator('input[placeholder="请输入用户名"]').fill(CONFIG.credentials.username);
      await page.locator('input[type="password"]').fill(CONFIG.credentials.password);
      await page.locator('button:has-text("登 录")').click();
      await page.waitForTimeout(CONFIG.timeouts.loginWait);

      errorCollector.reset();

      // 导航到用户管理
      log(tcId, '导航到用户管理页面', 'INFO');
      await page.goto(`${CONFIG.baseURL}/user`, { waitUntil: 'networkidle' });
      await waitForNetworkIdle(page);
      await page.waitForTimeout(CONFIG.timeouts.pageStabilize);

      printErrorSummary(tcId);
      await saveScreenshot(page, tcId, '01_用户列表');

      if (errorCollector.hasFatalErrors()) {
        throw new Error(`TC006 用户管理检测到 ${errorCollector.getStats().totalErrors} 个错误/警告`);
      }

      log(tcId, '用户管理测试完成', 'PASS');
      await saveScreenshot(page, tcId, '02_最终状态');

    } catch (error) {
      log(tcId, '用户管理测试失败', 'FAIL', error.message);
      printCompleteErrorReport(tcId);
      throw error;
    }
  });
});

test.describe('TC007_系统设置_控制台监控', () => {

  test('系统设置 - 控制台错误检测', async ({ page }) => {
    const tcId = 'TC007';
    log(tcId, '开始系统设置+控制台监控测试', 'INFO');

    errorCollector.reset();
    setupEventListeners(page, tcId);

    page.setDefaultTimeout(CONFIG.timeouts.action);
    page.setDefaultNavigationTimeout(CONFIG.timeouts.navigation);

    try {
      // 登录
      await page.goto(`${CONFIG.baseURL}/login`, { waitUntil: 'domcontentloaded' });
      await page.locator('input[placeholder="请输入用户名"]').fill(CONFIG.credentials.username);
      await page.locator('input[type="password"]').fill(CONFIG.credentials.password);
      await page.locator('button:has-text("登 录")').click();
      await page.waitForTimeout(CONFIG.timeouts.loginWait);

      errorCollector.reset();

      // 导航到系统设置
      log(tcId, '导航到系统设置页面', 'INFO');
      await page.goto(`${CONFIG.baseURL}/system`, { waitUntil: 'networkidle' });
      await waitForNetworkIdle(page);
      await page.waitForTimeout(CONFIG.timeouts.pageStabilize);

      printErrorSummary(tcId);
      await saveScreenshot(page, tcId, '01_系统设置页面');

      if (errorCollector.hasFatalErrors()) {
        throw new Error(`TC007 系统设置检测到 ${errorCollector.getStats().totalErrors} 个错误/警告`);
      }

      log(tcId, '系统设置测试完成', 'PASS');
      await saveScreenshot(page, tcId, '02_最终状态');

    } catch (error) {
      log(tcId, '系统设置测试失败', 'FAIL', error.message);
      printCompleteErrorReport(tcId);
      throw error;
    }
  });
});

// ============================================================================
// 辅助函数：打印完整错误报告
// ============================================================================
function printCompleteErrorReport(testName) {
  console.log(`\n${'='.repeat(70)}`);
  console.log(`   [${testName}] ❌ 完整错误报告`);
  console.log(`${'='.repeat(70)}`);

  if (errorCollector.consoleErrors.length > 0) {
    console.log(`\n--- Console Errors (${errorCollector.consoleErrors.length}) ---`);
    errorCollector.consoleErrors.forEach((err, index) => {
      console.log(`\nError #${index + 1}:`);
      console.log(`  类型: ${err.type}`);
      console.log(`  时间: ${err.timestamp}`);
      console.log(`  文件: ${err.file}:${err.line}`);
      console.log(`  消息: ${err.message}`);
      console.log(`  来源: ${err.sourceTest}`);
    });
  }

  if (errorCollector.consoleWarnings.length > 0) {
    console.log(`\n--- Console Warnings (${errorCollector.consoleWarnings.length}) ---`);
    errorCollector.consoleWarnings.forEach((warn, index) => {
      console.log(`\nWarning #${index + 1}:`);
      console.log(`  类型: ${warn.type}`);
      console.log(`  时间: ${warn.timestamp}`);
      console.log(`  文件: ${warn.file}:${warn.line}`);
      console.log(`  消息: ${warn.message}`);
    });
  }

  if (errorCollector.pageErrors.length > 0) {
    console.log(`\n--- Page Errors / JavaScript Exceptions (${errorCollector.pageErrors.length}) ---`);
    errorCollector.pageErrors.forEach((err, index) => {
      console.log(`\nError #${index + 1}:`);
      console.log(`  类型: ${err.type}`);
      console.log(`  时间: ${err.timestamp}`);
      console.log(`  消息: ${err.message}`);
      console.log(`  堆栈:\n${err.stack}`);
    });
  }

  if (errorCollector.failedRequests.length > 0) {
    console.log(`\n--- Failed Requests (${errorCollector.failedRequests.length}) ---`);
    errorCollector.failedRequests.forEach((req, index) => {
      console.log(`\nRequest #${index + 1}:`);
      console.log(`  方法: ${req.method}`);
      console.log(`  URL: ${req.url}`);
      console.log(`  状态码: ${req.status}`);
      console.log(`  错误原因: ${req.failure}`);
      console.log(`  是否关键: ${req.isCritical ? '是' : '否'}`);
    });
  }

  if (errorCollector.apiErrorResponses.length > 0) {
    console.log(`\n--- API Error Responses (${errorCollector.apiErrorResponses.length}) ---`);
    errorCollector.apiErrorResponses.forEach((res, index) => {
      console.log(`\nResponse #${index + 1}:`);
      console.log(`  方法: ${res.method}`);
      console.log(`  URL: ${res.url}`);
      console.log(`  状态码: ${res.status}`);
      console.log(`  状态文本: ${res.statusText}`);
      if (res.responseBody) {
        console.log(`  响应体: ${res.responseBody}`);
      }
    });
  }

  console.log(`\n${'='.repeat(70)}`);
  console.log(`   统计汇总`);
  console.log(`${'='.repeat(70)}`);
  const stats = errorCollector.getStats();
  console.log(`Console Errors: ${stats.consoleErrorsCount}`);
  console.log(`Console Warnings: ${stats.consoleWarningsCount}`);
  console.log(`Page Errors: ${stats.pageErrorsCount}`);
  console.log(`Failed Requests: ${stats.failedRequestsCount}`);
  console.log(`API Error Responses: ${stats.apiErrorResponsesCount}`);
  console.log(`总计: ${stats.totalErrors}\n`);
}

// ============================================================================
// 测试完成后生成最终报告
// ============================================================================
test.afterAll(async () => {
  console.log('\n\n');
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║                                                              ║');
  console.log('║     🔍 浏览器控制台错误检测报告 (最终版)                     ║');
  console.log('║                                                              ║');
  console.log('╚══════════════════════════════════════════════════════════════╝');

  console.log(`\n📅 测试时间: ${new Date().toLocaleString('zh-CN')}`);
  console.log(`🌐 测试地址: ${CONFIG.baseURL}`);
  console.log(`🔧 浏览器: Chromium (Playwright v1.58.2)`);

  console.log('\n' + '─'.repeat(70));
  console.log('❌ CONSOLE ERRORS (致命错误):');
  console.log('─'.repeat(70));

  if (errorCollector.consoleErrors.length === 0) {
    console.log('✓ 无Console错误 (优秀!)');
  } else {
    errorCollector.consoleErrors.forEach((err, index) => {
      console.log(`\nError #${index + 1}:`);
      console.log(`  类型: ${err.type}`);
      console.log(`  时间: ${err.timestamp}`);
      console.log(`  文件: ${err.file}:${err.line}`);
      console.log(`  消息: ${err.message}`);
      console.log(`  来源测试: ${err.sourceTest}`);
    });
  }

  console.log('\n' + '─'.repeat(70));
  console.log('⚠️  CONSOLE WARNINGS (警告):');
  console.log('─'.repeat(70));

  if (errorCollector.consoleWarnings.length === 0) {
    console.log('✓ 无Console警告 (优秀!)');
  } else {
    errorCollector.consoleWarnings.forEach((warn, index) => {
      console.log(`\nWarning #${index + 1}:`);
      console.log(`  类型: ${warn.type}`);
      console.log(`  时间: ${warn.timestamp}`);
      console.log(`  文件: ${warn.file}:${warn.line}`);
      console.log(`  消息: ${warn.message}`);

      // 判断是否为Vue组件警告
      const isVueWarning = warn.message.includes('[Vue warn]');
      console.log(`  建议: ${isVueWarning ? '需修复 - Vue组件未正确注册或使用' : '可忽略 - 一般性警告'}`);
    });
  }

  console.log('\n' + '─'.repeat(70));
  console.log('💥 PAGE ERRORS (JavaScript异常):');
  console.log('─'.repeat(70));

  if (errorCollector.pageErrors.length === 0) {
    console.log('✓ 无JavaScript异常 (优秀!)');
  } else {
    errorCollector.pageErrors.forEach((err, index) => {
      console.log(`\nError #${index + 1}:`);
      console.log(`  类型: ${err.type}`);
      console.log(`  时间: ${err.timestamp}`);
      console.log(`  消息: ${err.message}`);
      console.log(`  堆栈: ${err.stack ? err.stack.substring(0, 500) + '...' : 'N/A'}`);
    });
  }

  console.log('\n' + '─'.repeat(70));
  console.log('🌐 FAILED REQUESTS (失败请求):');
  console.log('─'.repeat(70));

  if (errorCollector.failedRequests.length === 0) {
    console.log('✓ 无失败请求 (优秀!)');
  } else {
    errorCollector.failedRequests.forEach((req, index) => {
      console.log(`\nRequest #${index + 1}:`);
      console.log(`  方法: ${req.method}`);
      console.log(`  URL: ${req.url}`);
      console.log(`  状态码: ${req.status}`);
      console.log(`  错误原因: ${req.failure}`);
      console.log(`  是否关键: ${req.isCritical ? '是 - 可能影响功能' : '否 - 非关键资源'}`);
    });
  }

  console.log('\n' + '─'.repeat(70));
  console.log('📈 API ERROR RESPONSES (API错误响应):');
  console.log('─'.repeat(70));

  if (errorCollector.apiErrorResponses.length === 0) {
    console.log('✓ 无API错误响应 (优秀!)');
  } else {
    errorCollector.apiErrorResponses.forEach((res, index) => {
      console.log(`\nResponse #${index + 1}:`);
      console.log(`  方法: ${res.method}`);
      console.log(`  URL: ${res.url}`);
      console.log(`  状态码: ${res.status}`);
      console.log(`  状态文本: ${res.statusText}`);
      if (res.responseBody) {
        console.log(`  响应体: ${res.responseBody}`);
      }
      console.log(`  业务影响: ${res.status >= 500 ? '服务端错误 - 功能可能不可用' : '客户端错误 - 参数或权限问题'}`);
    });
  }

  // ========== 最终判定 ==========
  console.log('\n\n' + '═'.repeat(70));
  console.log('           最终判定结果');
  console.log('═'.repeat(70));

  const stats = errorCollector.getStats();
  let verdict = 'PASS';
  let passRate = 100;

  // 判定逻辑
  if (stats.consoleErrorsCount > 0 || stats.pageErrorsCount > 0) {
    verdict = 'FAIL';
    passRate = 0;
  } else if (stats.failedRequestsCount > 0 && errorCollector.failedRequests.some(r => r.isCritical)) {
    verdict = 'FAIL';
    passRate = 30;
  } else if (stats.apiErrorResponsesCount > 0 && errorCollector.apiErrorResponses.some(r => r.status >= 500)) {
    verdict = 'FAIL';
    passRate = 40;
  } else if (stats.consoleWarningsCount <= 3) {
    verdict = 'PASS';
    passRate = 95 - (stats.consoleWarningsCount * 5);
  } else if (stats.consoleWarningsCount > 3 && stats.consoleWarningsCount <= 10) {
    verdict = 'WARNING';
    passRate = 80 - (stats.consoleWarningsCount * 2);
  } else {
    verdict = 'FAIL';
    passRate = 50;
  }

  const verdictIcon = verdict === 'PASS' ? '✅' : verdict === 'WARNING' ? '⚠️' : '❌';
  console.log(`\n当前判定: ${verdictIcon} ${verdict}`);
  console.log(`通过率: ${passRate}%`);

  console.log(`\n判定依据:`);
  console.log(`  • Console Errors: ${stats.consoleErrorsCount} (要求: 0) ${stats.consoleErrorsCount === 0 ? '✓' : '✗'}`);
  console.log(`  • Page Errors: ${stats.pageErrorsCount} (要求: 0) ${stats.pageErrorsCount === 0 ? '✓' : '✗'}`);
  console.log(`  • Critical Failed Requests: ${errorCollector.failedRequests.filter(r => r.isCritical).length} (要求: 0) ${errorCollector.failedRequests.filter(r => r.isCritical).length === 0 ? '✓' : '✗'}`);
  console.log(`  • Server Errors (5xx): ${errorCollector.apiErrorResponses.filter(r => r.status >= 500).length} (要求: 0) ${errorCollector.apiErrorResponses.filter(r => r.status >= 500).length === 0 ? '✓' : '✗'}`);
  console.log(`  • Warnings: ${stats.consoleWarningsCount} (允许: ≤3) ${stats.consoleWarningsCount <= 3 ? '✓' : '⚠'}`);

  console.log('\n' + '═'.repeat(70));
  console.log(`截图保存位置: ${CONFIG.screenshotDir}`);
  console.log(`测试完成时间: ${new Date().toLocaleString('zh-CN')}`);
  console.log('═'.repeat(70) + '\n');
});
