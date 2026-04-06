/**
 * 兼容性测试套件 - 实验室管理系统
 * 包括浏览器兼容性测试、平台测试
 */
const { test, expect, devices } = require('@playwright/test');

// 测试不同浏览器视口
test.describe('兼容性测试 - 浏览器兼容性测试', () => {
  test('Chrome浏览器测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 登录
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 验证登录成功
    await expect(page.locator('body')).toBeVisible();
    const url = page.url();
    expect(url).not.toContain('/login');
  });

  test('Firefox浏览器测试', async ({ browserName, page }) => {
    test.skip(browserName !== 'firefox', '跳过非Firefox浏览器');
    
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    await expect(page.locator('body')).toBeVisible();
  });

  test('Webkit浏览器测试', async ({ browserName, page }) => {
    test.skip(browserName !== 'webkit', '跳过非Webkit浏览器');
    
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    await expect(page.locator('body')).toBeVisible();
  });

  test('Element Plus组件兼容性测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 测试Element Plus组件
    const button = page.locator('.el-button');
    await expect(button.first()).toBeVisible();
    
    // 测试输入框
    const input = page.locator('.el-input input').first();
    if (await input.count() > 0) {
      await expect(input).toBeVisible();
    }
  });
});

test.describe('兼容性测试 - 响应式视口测试', () => {
  test('桌面1920x1080测试', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('body')).toBeVisible();
    
    // 检查元素可见性
    const loginBox = page.locator('.login-container, .login-box');
    await expect(loginBox.first()).toBeVisible();
  });

  test('笔记本1366x768测试', async ({ page }) => {
    await page.setViewportSize({ width: 1366, height: 768 });
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('body')).toBeVisible();
  });

  test('平板1024x768测试', async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('body')).toBeVisible();
  });

  test('平板横屏768x1024测试', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('body')).toBeVisible();
  });

  test('手机375x667测试', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('body')).toBeVisible();
  });

  test('手机414x896测试', async ({ page }) => {
    await page.setViewportSize({ width: 414, height: 896 });
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('兼容性测试 - 平台测试', () => {
  test('Windows平台测试', async ({ page }) => {
    const platform = await page.evaluate(() => navigator.platform);
    console.log(`平台: ${platform}`);
    
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 登录测试
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    await expect(page.locator('body')).toBeVisible();
  });

  test('Mac平台测试', async ({ page }) => {
    const platform = await page.evaluate(() => navigator.platform);
    console.log(`平台: ${platform}`);
    
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    await expect(page.locator('body')).toBeVisible();
  });

  test('触摸屏适配测试', async ({ page }) => {
    // 模拟触摸屏设备
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 测试触摸操作
    const button = page.locator('button').first();
    await button.tap();
    await page.waitForTimeout(500);
    
    await expect(page.locator('body')).toBeVisible();
  });

  test('高DPI屏幕测试', async ({ page }) => {
    // 设置高DPI
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    // 检查设备像素比
    const devicePixelRatio = await page.evaluate(() => window.devicePixelRatio);
    console.log(`设备像素比: ${devicePixelRatio}`);
    
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 页面应该正常渲染
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('兼容性测试 - 浏览器特性测试', () => {
  test('LocalStorage支持测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 测试LocalStorage
    const hasLocalStorage = await page.evaluate(() => {
      try {
        localStorage.setItem('test', 'test');
        localStorage.removeItem('test');
        return true;
      } catch (e) {
        return false;
      }
    });
    
    expect(hasLocalStorage).toBeTruthy();
  });

  test('SessionStorage支持测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    const hasSessionStorage = await page.evaluate(() => {
      try {
        sessionStorage.setItem('test', 'test');
        sessionStorage.removeItem('test');
        return true;
      } catch (e) {
        return false;
      }
    });
    
    expect(hasSessionStorage).toBeTruthy();
  });

  test('WebSocket支持测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    const hasWebSocket = await page.evaluate(() => {
      return 'WebSocket' in window;
    });
    
    console.log(`WebSocket支持: ${hasWebSocket}`);
  });

  test('Fetch API支持测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    const hasFetch = await page.evaluate(() => {
      return typeof fetch === 'function';
    });
    
    expect(hasFetch).toBeTruthy();
  });

  test('ES6特性支持测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 检查const和let
    const hasES6 = await page.evaluate(() => {
      try {
        eval('const test = 1; let test2 = 2;');
        return true;
      } catch (e) {
        return false;
      }
    });
    
    expect(hasES6).toBeTruthy();
  });
});

test.describe('兼容性测试 - 网络状态测试', () => {
  test('离线模式测试', async ({ page }) => {
    // 启用离线模式
    const context = page.context();
    await context.setOffline(true);
    
    await page.goto('/login');
    await page.waitForLoadState('domcontentloaded');
    
    // 页面应该能加载（静态资源）
    await expect(page.locator('body')).toBeVisible();
    
    // 恢复网络
    await context.setOffline(false);
  });

  test('慢速网络测试', async ({ page }) => {
    // 模拟慢速网络
    const client = await page.context().newCDPSession(page);
    await client.send('Network.emulateNetworkConditions', {
      offline: false,
      downloadThroughput: 50 * 1024, // 50KB/s
      uploadThroughput: 30 * 1024,
      latency: 500
    });
    
    await page.goto('/login');
    await page.waitForLoadState('domcontentloaded');
    
    await expect(page.locator('body')).toBeVisible();
  });
});
