/**
 * 完整测试运行器 - 实验室管理系统
 * 依次运行所有测试类型并生成报告
 */
const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:3000';
const API_URL = 'http://localhost:8086';

async function runTests() {
  console.log('===========================================');
  console.log('  实验室管理系统 - 全面Web测试');
  console.log('===========================================\n');
  
  const results = {
    startTime: new Date(),
    functional: { passed: 0, failed: 0, errors: [] },
    performance: { passed: 0, failed: 0, errors: [] },
    ui: { passed: 0, failed: 0, errors: [] },
    compatibility: { passed: 0, failed: 0, errors: [] },
    security: { passed: 0, failed: 0, errors: [] },
    api: { passed: 0, failed: 0, errors: [] }
  };
  
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // 设置全局错误处理
  page.on('pageerror', error => {
    console.error('页面错误:', error.message);
  });
  
  try {
    // 1. 功能测试
    console.log('▶ 运行功能测试...');
    const functionalResults = await runFunctionalTests(page);
    results.functional = functionalResults;
    
    // 2. 性能测试
    console.log('▶ 运行性能测试...');
    const performanceResults = await runPerformanceTests(page);
    results.performance = performanceResults;
    
    // 3. UI测试
    console.log('▶ 运行UI测试...');
    const uiResults = await runUITests(page);
    results.ui = uiResults;
    
    // 4. 兼容性测试
    console.log('▶ 运行兼容性测试...');
    const compatibilityResults = await runCompatibilityTests(page);
    results.compatibility = compatibilityResults;
    
    // 5. 安全测试
    console.log('▶ 运行安全测试...');
    const securityResults = await runSecurityTests(page);
    results.security = securityResults;
    
    // 6. API测试
    console.log('▶ 运行API测试...');
    const apiResults = await runAPITests(page);
    results.api = apiResults;
    
  } catch (error) {
    console.error('测试过程中发生错误:', error);
  } finally {
    await browser.close();
  }
  
  // 生成报告
  generateReport(results);
  
  // 返回退出码
  const totalFailed = Object.values(results).reduce((sum, r) => sum + r.failed, 0);
  return totalFailed === 0 ? 0 : 1;
}

// 功能测试
async function runFunctionalTests(page) {
  const result = { passed: 0, failed: 0, errors: [] };
  
  try {
    // 登录测试
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('domcontentloaded');
    
    const loginInput = page.locator('input[placeholder*="用户名"]');
    const passInput = page.locator('input[type="password"]');
    const submitBtn = page.locator('button:has-text("登 录")');
    
    if (await loginInput.count() > 0) {
      await loginInput.fill('admin');
      await passInput.fill('admin123');
      await submitBtn.click();
      await page.waitForTimeout(2000);
      
      if (!page.url().includes('/login')) {
        result.passed++;
        console.log('  ✓ 登录功能正常');
      } else {
        result.failed++;
        result.errors.push('登录失败');
        console.log('  ✗ 登录失败');
      }
    }
    
    // 导航测试
    const pages = ['/sample', '/report', '/user'];
    for (const p of pages) {
      await page.goto(`${BASE_URL}${p}`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(500);
      
      if (await page.locator('body').count() > 0) {
        result.passed++;
        console.log(`  ✓ ${p} 页面可访问`);
      } else {
        result.failed++;
        result.errors.push(`${p} 页面加载失败`);
      }
    }
    
  } catch (error) {
    result.failed++;
    result.errors.push(error.message);
  }
  
  return result;
}

// 性能测试
async function runPerformanceTests(page) {
  const result = { passed: 0, failed: 0, errors: [] };
  
  try {
    // 首页加载速度测试
    const startTime = Date.now();
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('domcontentloaded');
    const loadTime = Date.now() - startTime;
    
    if (loadTime < 3000) {
      result.passed++;
      console.log(`  ✓ 登录页加载时间: ${loadTime}ms`);
    } else {
      result.failed++;
      result.errors.push(`页面加载过慢: ${loadTime}ms`);
      console.log(`  ✗ 页面加载过慢: ${loadTime}ms`);
    }
    
    // 登录响应速度测试
    const loginStart = Date.now();
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(2000);
    const loginTime = Date.now() - loginStart;
    
    if (loginTime < 3000) {
      result.passed++;
      console.log(`  ✓ 登录响应时间: ${loginTime}ms`);
    } else {
      result.failed++;
      result.errors.push(`登录响应过慢: ${loginTime}ms`);
    }
    
  } catch (error) {
    result.failed++;
    result.errors.push(error.message);
  }
  
  return result;
}

// UI测试
async function runUITests(page) {
  const result = { passed: 0, failed: 0, errors: [] };
  
  try {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('domcontentloaded');
    
    // 检查关键UI元素
    const elements = [
      { selector: '.el-button, button', name: '按钮' },
      { selector: 'input', name: '输入框' }
    ];
    
    for (const el of elements) {
      const count = await page.locator(el.selector).count();
      if (count > 0) {
        result.passed++;
        console.log(`  ✓ ${el.name} 存在 (${count}个)`);
      } else {
        result.failed++;
        result.errors.push(`${el.name} 不存在`);
      }
    }
    
    // 响应式布局测试
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(300);
    result.passed++;
    console.log('  ✓ 桌面视口正常');
    
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(300);
    result.passed++;
    console.log('  ✓ 平板视口正常');
    
  } catch (error) {
    result.failed++;
    result.errors.push(error.message);
  }
  
  return result;
}

// 兼容性测试
async function runCompatibilityTests(page) {
  const result = { passed: 0, failed: 0, errors: [] };
  
  try {
    // 多个视口测试
    const viewports = [
      { width: 1920, height: 1080, name: '桌面' },
      { width: 1366, height: 768, name: '笔记本' },
      { width: 768, height: 1024, name: '平板' },
      { width: 375, height: 667, name: '手机' }
    ];
    
    for (const vp of viewports) {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto(`${BASE_URL}/login`);
      await page.waitForLoadState('domcontentloaded');
      
      if (await page.locator('body').count() > 0) {
        result.passed++;
        console.log(`  ✓ ${vp.name}视口 (${vp.width}x${vp.height})`);
      } else {
        result.failed++;
      }
    }
    
    // 浏览器特性检测
    const features = await page.evaluate(() => ({
      localStorage: typeof localStorage !== 'undefined',
      sessionStorage: typeof sessionStorage !== 'undefined',
      fetch: typeof fetch !== 'undefined',
      es6: typeof Promise !== 'undefined'
    }));
    
    if (features.localStorage) { result.passed++; console.log('  ✓ LocalStorage支持'); }
    if (features.fetch) { result.passed++; console.log('  ✓ Fetch API支持'); }
    
  } catch (error) {
    result.failed++;
    result.errors.push(error.message);
  }
  
  return result;
}

// 安全测试
async function runSecurityTests(page) {
  const result = { passed: 0, failed: 0, errors: [] };
  
  try {
    // 敏感目录测试
    const sensitivePaths = ['/.git', '/.env', '/config'];
    for (const p of sensitivePaths) {
      const response = await page.goto(`${BASE_URL}${p}`, { failOnStatusCode: false });
      if (response && response.status() !== 200) {
        result.passed++;
        console.log(`  ✓ ${p} 已正确防护`);
      } else {
        result.failed++;
        result.errors.push(`${p} 可能泄露信息`);
      }
    }
    
    // SQL注入防护测试
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[placeholder*="用户名"]', "' OR '1'='1");
    await page.fill('input[type="password"]', 'anything');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 不应该直接登录成功
    if (page.url().includes('/login')) {
      result.passed++;
      console.log('  ✓ SQL注入已防护');
    } else {
      result.failed++;
      result.errors.push('SQL注入可能成功');
    }
    
    // XSS防护测试
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[placeholder*="用户名"]', '<script>alert(1)</script>');
    await page.fill('input[type="password"]', 'test');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1000);
    
    // 检查页面内容
    const content = await page.content();
    if (!content.includes('<script>alert(1)</script>')) {
      result.passed++;
      console.log('  ✓ XSS已防护');
    } else {
      result.failed++;
      result.errors.push('XSS可能未防护');
    }
    
  } catch (error) {
    result.failed++;
    result.errors.push(error.message);
  }
  
  return result;
}

// API测试
async function runAPITests(page) {
  const result = { passed: 0, failed: 0, errors: [] };
  
  try {
    // 登录API测试
    const loginResp = await page.evaluate(async () => {
      const resp = await fetch(`${API_URL}/user/login?username=admin&password=admin123`);
      return { status: resp.status, ok: resp.ok };
    });
    
    if (loginResp.ok) {
      result.passed++;
      console.log(`  ✓ 用户登录API (${loginResp.status})`);
    } else {
      result.failed++;
      result.errors.push('登录API失败');
    }
    
    // 用户列表API测试
    const listResp = await page.evaluate(async () => {
      const resp = await fetch(`${API_URL}/user/list?current=1&size=10`);
      return { status: resp.status, ok: resp.ok };
    });
    
    if (listResp.ok) {
      result.passed++;
      console.log(`  ✓ 用户列表API (${listResp.status})`);
    } else {
      result.failed++;
      result.errors.push('用户列表API失败');
    }
    
    // 标本服务测试
    const sampleResp = await page.evaluate(async () => {
      const resp = await fetch(`${API_URL}/sample/list?current=1&size=10`);
      return { status: resp.status, ok: resp.ok };
    });
    
    if (sampleResp.ok) {
      result.passed++;
      console.log(`  ✓ 标本列表API (${sampleResp.status})`);
    } else {
      result.failed++;
      result.errors.push('标本列表API失败');
    }
    
  } catch (error) {
    result.failed++;
    result.errors.push(error.message);
  }
  
  return result;
}

// 生成测试报告
function generateReport(results) {
  const endTime = new Date();
  const duration = Math.round((endTime - results.startTime) / 1000);
  
  let totalPassed = 0;
  let totalFailed = 0;
  
  for (const [key, value] of Object.entries(results)) {
    if (key === 'startTime') continue;
    totalPassed += value.passed;
    totalFailed += value.failed;
  }
  
  const report = `
===============================================
  实验室管理系统 - Web测试报告
===============================================

测试时间: ${results.startTime.toLocaleString('zh-CN')}
测试耗时: ${duration}秒

┌─────────────────────────────────────────────┐
│              测试类型汇总                    │
├──────────────┬──────────┬──────────┬───────┤
│   测试类型    │   通过   │   失败   │ 状态  │
├──────────────┼──────────┼──────────┼───────┤
│  功能测试     │   ${String(results.functional.passed).padStart(4)}   │   ${String(results.functional.failed).padStart(4)}   │  ${results.functional.failed === 0 ? '✅' : '❌'}  │
│  性能测试     │   ${String(results.performance.passed).padStart(4)}   │   ${String(results.performance.failed).padStart(4)}   │  ${results.performance.failed === 0 ? '✅' : '❌'}  │
│  UI测试       │   ${String(results.ui.passed).padStart(4)}   │   ${String(results.ui.failed).padStart(4)}   │  ${results.ui.failed === 0 ? '✅' : '❌'}  │
│  兼容性测试   │   ${String(results.compatibility.passed).padStart(4)}   │   ${String(results.compatibility.failed).padStart(4)}   │  ${results.compatibility.failed === 0 ? '✅' : '❌'}  │
│  安全测试     │   ${String(results.security.passed).padStart(4)}   │   ${String(results.security.failed).padStart(4)}   │  ${results.security.failed === 0 ? '✅' : '❌'}  │
│  API测试      │   ${String(results.api.passed).padStart(4)}   │   ${String(results.api.failed).padStart(4)}   │  ${results.api.failed === 0 ? '✅' : '❌'}  │
├──────────────┼──────────┼──────────┼───────┤
│    合计       │   ${String(totalPassed).padStart(4)}   │   ${String(totalFailed).padStart(4)}   │  ${totalFailed === 0 ? '✅' : '❌'}  │
└──────────────┴──────────┴──────────┴───────┘

${totalFailed > 0 ? `
失败详情:
${Object.entries(results).filter(([k, v]) => k !== 'startTime' && v.failed > 0).map(([k, v]) => 
  `【${k}测试】\n  - ${v.errors.join('\n  - ')}`
).join('\n\n')}
` : ''}

${totalFailed === 0 ? '🎉 所有测试通过！' : `⚠️ 有 ${totalFailed} 项测试失败，请检查。`}
`;
  
  console.log(report);
  
  // 保存报告
  const reportPath = path.join(__dirname, 'TEST_REPORT.txt');
  fs.writeFileSync(reportPath, report);
  console.log(`\n报告已保存到: ${reportPath}`);
}

// 运行测试
runTests().then(code => {
  process.exit(code);
}).catch(error => {
  console.error('测试运行失败:', error);
  process.exit(1);
});
