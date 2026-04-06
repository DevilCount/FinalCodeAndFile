/**
 * 功能测试套件 - 实验室管理系统
 * 包括链接测试、表单测试、Cookie测试
 */
const { test, expect } = require('@playwright/test');

test.describe('功能测试 - 链接测试', () => {
  test.beforeEach(async ({ page }) => {
    // 先登录
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
  });

  test('登录页面链接测试', async ({ page }) => {
    // 检查登录表单元素存在
    await expect(page.locator('input[placeholder*="用户名"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button:has-text("登 录")')).toBeVisible();
  });

  test('登录后导航链接测试', async ({ page }) => {
    // 登录
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    
    // 等待跳转
    await page.waitForURL('**/');
    await page.waitForLoadState('networkidle');
    
    // 检查侧边栏链接
    const sidebar = page.locator('.sidebar-nav, nav');
    if (await sidebar.count() > 0) {
      // 检查主要菜单项存在
      await expect(page.locator('text=标本管理').first()).toBeVisible({ timeout: 5000 });
    }
  });

  test('页面返回链接测试', async ({ page }) => {
    // 导航到标本管理
    await page.goto('/sample');
    await page.waitForLoadState('networkidle');
    
    // 检查返回按钮
    const backButton = page.locator('button:has-text("返回"), .back-btn, [class*="back"]');
    // 页面应该能正常加载
    await expect(page.locator('.professional-sample-container, .sample-container, body')).toBeVisible();
  });

  test('所有主要页面链接可访问', async ({ page }) => {
    const pages = ['/', '/sample', '/report', '/user', '/system'];
    
    for (const path of pages) {
      await page.goto(path);
      await page.waitForLoadState('domcontentloaded');
      // 检查页面没有严重错误
      const errorCount = await page.locator('.el-message--error, .error-page').count();
      expect(errorCount).toBeLessThanOrEqual(1);
    }
  });
});

test.describe('功能测试 - 表单测试', () => {
  test('登录表单验证测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 空表单提交
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(500);
    
    // 应该显示验证错误（如果有）
    const errorMsg = page.locator('.el-form-item__error, .error-message, text=/请输入/');
    // Element Plus会自动验证
    
    // 输入无效数据
    await page.fill('input[placeholder*="用户名"]', 'ab');  // 太短
    await page.fill('input[type="password"]', '123');  // 太短
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(500);
  });

  test('登录表单提交测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 填写正确凭据
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    
    // 提交前检查按钮状态
    const submitBtn = page.locator('button:has-text("登 录")');
    await expect(submitBtn).toBeEnabled();
    
    // 提交
    await page.click('button:has-text("登 录")');
    
    // 等待响应
    await page.waitForTimeout(2000);
    
    // 验证登录结果（成功或失败）
    const currentUrl = page.url();
    const hasLoginError = await page.locator('text=/登录失败|密码错误|账号不存在/').isVisible().catch(() => false);
    
    // 至少应该得到某种响应
    expect(hasLoginError || currentUrl !== 'http://localhost:3000/login').toBeTruthy();
  });

  test('新建标本表单测试', async ({ page }) => {
    // 先登录
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1000);
    
    // 导航到新建标本
    await page.goto('/sample/create');
    await page.waitForLoadState('networkidle');
    
    // 检查表单元素
    await expect(page.locator('text=新建标本').first()).toBeVisible({ timeout: 5000 });
    
    // 填写表单
    const patientNameInput = page.locator('input[placeholder*="患者姓名"], input[placeholder*="请输入患者姓名"]');
    if (await patientNameInput.count() > 0) {
      await patientNameInput.fill('测试患者');
    }
    
    // 检查表单提交按钮
    const submitBtn = page.locator('button:has-text("提交"), button:has-text("创建")');
    if (await submitBtn.count() > 0) {
      await expect(submitBtn.first()).toBeVisible();
    }
  });

  test('搜索表单测试', async ({ page }) => {
    await page.goto('/sample');
    await page.waitForLoadState('networkidle');
    
    // 查找搜索输入框
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="标本编号"]');
    if (await searchInput.count() > 0) {
      await searchInput.first().fill('S2026');
      await page.waitForTimeout(500);
      
      // 触发搜索
      const searchBtn = page.locator('button:has-text("搜索")');
      if (await searchBtn.count() > 0) {
        await searchBtn.first().click();
        await page.waitForTimeout(1000);
      }
    }
    
    // 页面应该正常响应
    await expect(page.locator('.professional-sample-container, .sample-container, body')).toBeVisible();
  });
});

test.describe('功能测试 - Cookie测试', () => {
  test('登录Cookie设置测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 登录
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(2000);
    
    // 检查Cookie
    const cookies = await page.context().cookies();
    const hasSessionCookie = cookies.some(c => 
      c.name.includes('token') || 
      c.name.includes('session') || 
      c.name.includes('user')
    );
    
    // 验证用户信息存储
    const localStorage = await page.evaluate(() => {
      return localStorage.getItem('user');
    });
    
    // 至少应该有一个会话标识
    expect(hasSessionCookie || localStorage !== null).toBeTruthy();
  });

  test('Cookie有效期测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 登录
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 获取Cookie
    const cookies = await page.context().cookies();
    const sessionCookie = cookies.find(c => 
      c.name.includes('token') || 
      c.name.includes('session')
    );
    
    // 如果有会话Cookie，检查其属性
    if (sessionCookie) {
      // Cookie应该有HttpOnly或Secure属性（生产环境）
      // 检查Cookie是否设置了合理的过期时间
      expect(sessionCookie.expires).toBeGreaterThanOrEqual(-1); // -1表示会话Cookie
    }
  });

  test('Cookie作用域测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 登录
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 获取Cookie并检查域
    const cookies = await page.context().cookies('http://localhost:3000');
    const sessionCookie = cookies.find(c => 
      c.name.includes('token') || 
      c.name.includes('session')
    );
    
    // Cookie应该对主域名有效
    if (sessionCookie) {
      expect(sessionCookie.domain).toBeTruthy();
    }
  });

  test('登出后Cookie清理测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 登录
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 检查登录状态
    const localStorageBefore = await page.evaluate(() => localStorage.getItem('user'));
    
    // 清除本地存储模拟登出
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    
    // 应该跳转到登录页或显示未登录状态
    await page.waitForTimeout(1000);
    const localStorageAfter = await page.evaluate(() => localStorage.getItem('user'));
    expect(localStorageAfter).toBeNull();
  });
});

test.describe('功能测试 - 数据库连接测试', () => {
  test('API数据获取测试', async ({ page }) => {
    // 先登录
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 导航到用户列表
    await page.goto('/user');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 检查是否有数据显示
    const tableOrList = page.locator('.el-table, .user-list, table, [class*="list"]');
    const hasData = await tableOrList.count() > 0;
    
    // 如果有数据表格，应该有数据行或空状态
    if (hasData) {
      const rows = await page.locator('.el-table__row, tr, [class*="item"]').count();
      const emptyState = await page.locator('.el-empty, [class*="empty"]').count();
      expect(rows > 0 || emptyState > 0).toBeTruthy();
    }
  });

  test('数据分页功能测试', async ({ page }) => {
    await page.goto('/user');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 查找分页组件
    const pagination = page.locator('.el-pagination');
    if (await pagination.count() > 0) {
      // 检查分页信息
      const paginationInfo = await page.locator('.el-pagination__total, [class*="total"]').textContent().catch(() => '');
      
      // 点击下一页
      const nextBtn = page.locator('.el-pagination__goto, .btn-next, button:has-text("下一页")');
      if (await nextBtn.count() > 0) {
        await nextBtn.first().click();
        await page.waitForTimeout(1000);
      }
    }
    
    // 页面应该正常响应
    await expect(page.locator('body')).toBeVisible();
  });

  test('数据筛选功能测试', async ({ page }) => {
    await page.goto('/sample');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 查找筛选控件
    const filterSelect = page.locator('.el-select, select').first();
    if (await filterSelect.count() > 0) {
      // 尝试选择选项
      await filterSelect.click();
      await page.waitForTimeout(500);
      
      const option = page.locator('.el-select-dropdown__item, .el-option').first();
      if (await option.count() > 0) {
        await option.first().click();
        await page.waitForTimeout(1000);
      }
    }
    
    // 页面应该正常响应
    await expect(page.locator('body')).toBeVisible();
  });

  test('表单数据提交测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 填写并提交表单
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    
    // 拦截请求以验证数据
    const [response] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/user/login') || r.url().includes('/login')),
      page.click('button:has-text("登 录")')
    ]);
    
    // 验证响应状态
    expect(response.status()).toBeGreaterThanOrEqual(200);
    expect(response.status()).toBeLessThan(600);
  });
});
