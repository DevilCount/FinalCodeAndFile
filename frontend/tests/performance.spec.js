/**
 * 性能测试套件 - 实验室管理系统
 * 包括连接速度测试、负载测试、压力测试
 */
const { test, expect, chromium } = require('@playwright/test');

test.describe('性能测试 - 连接速度测试', () => {
  test('首页加载速度测试', async ({ page }) => {
    // 记录开始时间
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    
    const loadTime = Date.now() - startTime;
    console.log(`首页加载时间: ${loadTime}ms`);
    
    // 首页加载时间应该在3秒内
    expect(loadTime).toBeLessThan(3000);
  });

  test('登录页面响应速度测试', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    console.log(`登录页加载时间: ${loadTime}ms`);
    
    // 登录页应该在2秒内加载完成
    expect(loadTime).toBeLessThan(2000);
  });

  test('登录API响应时间测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    const startTime = Date.now();
    
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    
    // 等待响应
    await page.waitForTimeout(2000);
    
    const responseTime = Date.now() - startTime;
    console.log(`登录响应时间: ${responseTime}ms`);
    
    // API响应时间应该在2秒内
    expect(responseTime).toBeLessThan(2000);
  });

  test('页面切换速度测试', async ({ page }) => {
    // 先登录
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 测试页面切换速度
    const pages = ['/sample', '/report', '/user'];
    
    for (const path of pages) {
      const startTime = Date.now();
      await page.goto(path);
      await page.waitForLoadState('domcontentloaded');
      const switchTime = Date.now() - startTime;
      console.log(`${path} 切换时间: ${switchTime}ms`);
      expect(switchTime).toBeLessThan(2000);
    }
  });

  test('API数据加载速度测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 测试数据加载速度
    const startTime = Date.now();
    await page.goto('/user');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    const loadTime = Date.now() - startTime;
    
    console.log(`用户列表数据加载时间: ${loadTime}ms`);
    expect(loadTime).toBeLessThan(3000);
  });

  test('缓存效果测试', async ({ page }) => {
    // 第一次加载
    const startTime1 = Date.now();
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(2000);
    const time1 = Date.now() - startTime1;
    
    // 第二次加载（应该有缓存）
    const startTime2 = Date.now();
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    const time2 = Date.now() - startTime2;
    
    console.log(`第一次登录: ${time1}ms, 第二次加载: ${time2}ms`);
    
    // 第二次应该更快或相近
    expect(time2).toBeLessThanOrEqual(time1 * 1.5);
  });
});

test.describe('性能测试 - 负载测试', () => {
  test('并发登录请求测试', async ({ browser }) => {
    const concurrentUsers = 5;
    const promises = [];
    
    const startTime = Date.now();
    
    for (let i = 0; i < concurrentUsers; i++) {
      const context = await browser.newContext();
      const page = await context.newPage();
      
      promises.push((async () => {
        await page.goto('/login');
        await page.fill('input[placeholder*="用户名"]', 'admin');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button:has-text("登 录")');
        await page.waitForTimeout(1500);
        await context.close();
      })());
    }
    
    await Promise.all(promises);
    const totalTime = Date.now() - startTime;
    
    console.log(`${concurrentUsers}个并发用户完成时间: ${totalTime}ms`);
    
    // 所有并发请求应该在15秒内完成
    expect(totalTime).toBeLessThan(15000);
  });

  test('连续操作稳定性测试', async ({ page }) => {
    // 登录
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 执行多次页面切换
    for (let i = 0; i < 10; i++) {
      await page.goto('/sample');
      await page.waitForTimeout(500);
      await page.goto('/report');
      await page.waitForTimeout(500);
    }
    
    // 页面应该仍然正常工作
    await expect(page.locator('body')).toBeVisible();
    
    // 检查没有内存泄漏（页面仍可响应）
    const isResponsive = await page.evaluate(() => document.readyState === 'complete');
    expect(isResponsive).toBeTruthy();
  });

  test('数据密集页面性能测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 导航到标本列表
    const startTime = Date.now();
    await page.goto('/sample');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 检查表格渲染
    const tableRows = await page.locator('.el-table__row').count();
    const loadTime = Date.now() - startTime;
    
    console.log(`标本列表(${tableRows}行)渲染时间: ${loadTime}ms`);
    
    // 大数据量表格渲染应在3秒内
    expect(loadTime).toBeLessThan(3000);
  });
});

test.describe('性能测试 - 压力测试', () => {
  test('快速连续请求压力测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 快速发送多个请求
    const requests = [];
    for (let i = 0; i < 20; i++) {
      requests.push(page.goto('/sample'));
      await page.waitForTimeout(100);
    }
    
    // 所有请求完成
    await Promise.all(requests);
    
    // 页面应该仍可响应
    await page.waitForTimeout(1000);
    await expect(page.locator('body')).toBeVisible();
  });

  test('大数据量表单提交压力测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 导航到新建标本页面
    await page.goto('/sample/create');
    await page.waitForLoadState('networkidle');
    
    // 尝试快速填写多个字段
    const inputs = await page.locator('input').all();
    for (const input of inputs.slice(0, 10)) {
      await input.fill('压力测试数据');
      await page.waitForTimeout(50);
    }
    
    // 页面应该保持响应
    await expect(page.locator('body')).toBeVisible();
  });

  test('长时间运行稳定性测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 模拟用户会话
    const startTime = Date.now();
    const sessionDuration = 30000; // 30秒
    
    while (Date.now() - startTime < sessionDuration) {
      await page.goto('/sample');
      await page.waitForTimeout(2000);
      await page.goto('/report');
      await page.waitForTimeout(2000);
    }
    
    // 会话结束后仍应正常
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('性能测试 - 资源使用测试', () => {
  test('内存使用监控', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 获取初始内存使用
    const initialMemory = await page.evaluate(() => {
      if (performance.memory) {
        return {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize
        };
      }
      return null;
    });
    
    // 执行一些操作
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(2000);
    
    // 多次页面切换
    for (let i = 0; i < 5; i++) {
      await page.goto('/sample');
      await page.waitForTimeout(500);
      await page.goto('/report');
      await page.waitForTimeout(500);
    }
    
    // 获取最终内存使用
    const finalMemory = await page.evaluate(() => {
      if (performance.memory) {
        return {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize
        };
      }
      return null;
    });
    
    console.log('初始内存:', initialMemory);
    console.log('最终内存:', finalMemory);
    
    // 内存应该不会无限增长
    if (initialMemory && finalMemory) {
      const growth = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;
      console.log(`内存增长: ${growth / 1024 / 1024}MB`);
      // 内存增长应该在合理范围内（小于50MB）
      expect(growth).toBeLessThan(50 * 1024 * 1024);
    }
  });

  test('资源加载时间统计', async ({ page }) => {
    const resourceTimes = [];
    
    page.on('response', response => {
      if (response.url().includes('.js') || response.url().includes('.css')) {
        const time = Date.now();
        resourceTimes.push({
          url: response.url().split('/').pop(),
          status: response.status(),
          size: parseInt(response.headers()['content-length'] || '0')
        });
      }
    });
    
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    console.log('加载的资源:', resourceTimes);
    
    // 关键资源应该成功加载
    const failedResources = resourceTimes.filter(r => r.status >= 400);
    expect(failedResources.length).toBe(0);
  });
});
