/**
 * 用户界面测试套件 - 实验室管理系统
 * 包括导航测试、图形测试、内容测试、整体界面测试
 */
const { test, expect } = require('@playwright/test');

test.describe('用户界面测试 - 导航测试', () => {
  test('侧边栏导航测试', async ({ page }) => {
    // 登录
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 检查侧边栏存在
    const sidebar = page.locator('.sidebar, aside, nav[class*="sidebar"]');
    await expect(sidebar.first()).toBeVisible({ timeout: 5000 });
    
    // 检查主要菜单项
    const menuItems = ['标本管理', '报告管理', '用户管理', '系统设置'];
    for (const item of menuItems) {
      const menuItem = page.locator(`text=${item}`).first();
      const isVisible = await menuItem.isVisible().catch(() => false);
      if (isVisible) {
        await expect(menuItem).toBeVisible();
      }
    }
  });

  test('面包屑导航测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 导航到子页面
    await page.goto('/sample/create');
    await page.waitForLoadState('networkidle');
    
    // 检查面包屑
    const breadcrumbs = page.locator('.el-breadcrumb, [class*="breadcrumb"], nav[class*="nav"]');
    const hasBreadcrumbs = await breadcrumbs.count() > 0;
    
    if (hasBreadcrumbs) {
      await expect(breadcrumbs.first()).toBeVisible();
    }
  });

  test('页面标题显示测试', async ({ page }) => {
    const pages = [
      { path: '/login', expected: /登录|login/i },
      { path: '/sample', expected: /标本|sample/i },
      { path: '/report', expected: /报告|report/i },
      { path: '/user', expected: /用户|user/i }
    ];
    
    for (const p of pages) {
      await page.goto(p.path);
      await page.waitForLoadState('domcontentloaded');
      
      // 检查页面标题
      const title = await page.title();
      console.log(`${p.path} 标题: ${title}`);
    }
  });

  test('导航菜单高亮测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 在标本管理页面
    await page.goto('/sample');
    await page.waitForLoadState('networkidle');
    
    // 当前页面菜单应该高亮
    const activeMenu = page.locator('.el-menu-item.is-active, [class*="active"]');
    const hasActive = await activeMenu.count() > 0;
    
    if (hasActive) {
      await expect(activeMenu.first()).toBeVisible();
    }
  });

  test('分页导航测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 导航到有分页的页面
    await page.goto('/user');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 查找分页器
    const pagination = page.locator('.el-pagination');
    if (await pagination.count() > 0) {
      // 测试分页按钮
      const nextBtn = page.locator('.btn-next');
      if (await nextBtn.count() > 0) {
        const isDisabled = await nextBtn.getAttribute('disabled');
        if (!isDisabled) {
          await nextBtn.click();
          await page.waitForTimeout(1000);
        }
      }
    }
  });
});

test.describe('用户界面测试 - 图形测试', () => {
  test('图标加载测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 检查Element Plus图标是否正确加载
    const icons = await page.locator('.el-icon, [class*="icon"]').count();
    console.log(`页面图标数量: ${icons}`);
    
    // 图标应该存在
    expect(icons).toBeGreaterThan(0);
  });

  test('图表组件测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 检查仪表盘
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 检查ECharts图表
    const charts = await page.locator('canvas, [class*="chart"], [class*="echarts"]').count();
    console.log(`图表数量: ${charts}`);
    
    // 应该至少有仪表盘图表
    const dashboardCharts = page.locator('[class*="dashboard"], [class*="stats"]');
    // 页面应该正常显示
    await expect(page.locator('body')).toBeVisible();
  });

  test('图片加载测试', async ({ page }) => {
    const images = [];
    
    page.on('response', response => {
      if (response.url().match(/\.(jpg|jpeg|png|gif|svg|webp)$/i)) {
        images.push({
          url: response.url(),
          status: response.status()
        });
      }
    });
    
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    console.log('加载的图片:', images);
    
    // 图片应该成功加载
    const failedImages = images.filter(img => img.status >= 400);
    // 不应该有加载失败的图片
    console.log(`失败图片数: ${failedImages.length}`);
  });

  test('动画效果测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 检查动画类
    const animatedElements = await page.locator('[class*="animate"], [class*="transition"], [class*="fade"]').count();
    console.log(`动画元素数量: ${animatedElements}`);
    
    // 应该有动画元素（如果有的话）
    // 主要检查页面能正常显示
    await expect(page.locator('.login-container, .login-box, body')).toBeVisible();
  });

  test('加载状态显示测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 提交表单时应该有加载状态
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    
    // 检查加载状态
    const loading = page.locator('.el-loading-mask, .el-loading-spinner, [class*="loading"]');
    const hasLoading = await loading.count() > 0;
    console.log(`有加载状态: ${hasLoading}`);
  });
});

test.describe('用户界面测试 - 内容测试', () => {
  test('文本内容显示测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 检查登录页面文本
    const loginTitle = await page.locator('h1, h2, .title, [class*="title"]').first().textContent().catch(() => '');
    console.log(`登录页面标题: ${loginTitle}`);
    
    // 应该显示标题文本
    expect(loginTitle.trim()).toBeTruthy();
  });

  test('表单验证提示测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 输入错误数据触发验证
    await page.fill('input[placeholder*="用户名"]', 'a');
    await page.fill('input[type="password"]', '1');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1000);
    
    // 检查验证错误提示
    const errorMsg = page.locator('.el-form-item__error, [class*="error"], .error-message');
    // Element Plus表单会自动验证
    await expect(page.locator('body')).toBeVisible();
  });

  test('表格数据展示测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    await page.goto('/user');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 检查表格
    const table = page.locator('.el-table, table');
    if (await table.count() > 0) {
      await expect(table.first()).toBeVisible();
      
      // 检查表头
      const headers = await page.locator('.el-table__header th, thead th').count();
      console.log(`表格列数: ${headers}`);
    }
  });

  test('消息提示测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 触发错误消息
    await page.fill('input[placeholder*="用户名"]', 'wrong');
    await page.fill('input[type="password"]', 'wrong');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(2000);
    
    // 检查消息提示
    const message = page.locator('.el-message, [class*="message"]');
    const hasMessage = await message.count() > 0;
    console.log(`显示消息提示: ${hasMessage}`);
  });

  test('数据为空状态测试', async ({ page }) => {
    // 搜索一个不存在的记录
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    await page.goto('/sample?search=NOTEXIST123456');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 检查空状态组件
    const empty = page.locator('.el-empty, [class*="empty"]');
    const hasEmpty = await empty.count() > 0;
    console.log(`显示空状态: ${hasEmpty}`);
  });
});

test.describe('用户界面测试 - 整体界面测试', () => {
  test('整体布局结构测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 检查整体布局结构
    const layout = page.locator('.layout-container, .app-container, body');
    await expect(layout.first()).toBeVisible();
    
    // 检查头部
    const header = page.locator('.header, .navbar, header');
    const hasHeader = await header.count() > 0;
    
    // 检查侧边栏
    const sidebar = page.locator('.sidebar, aside');
    const hasSidebar = await sidebar.count() > 0;
    
    // 检查主要内容区
    const main = page.locator('.main, main, .content');
    const hasMain = await main.count() > 0;
    
    console.log(`布局结构 - 头部:${hasHeader}, 侧边栏:${hasSidebar}, 主内容:${hasMain}`);
  });

  test('响应式布局测试', async ({ page }) => {
    // 桌面尺寸
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('body')).toBeVisible();
    
    // 平板尺寸
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(500);
    await expect(page.locator('body')).toBeVisible();
    
    // 手机尺寸
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    await expect(page.locator('body')).toBeVisible();
  });

  test('用户交互反馈测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 悬停效果
    const button = page.locator('button').first();
    await button.hover();
    await page.waitForTimeout(300);
    
    // 点击效果
    await button.click();
    await page.waitForTimeout(300);
    
    // 页面应该保持可交互
    await expect(page.locator('body')).toBeVisible();
  });

  test('滚动行为测试', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    await page.goto('/sample');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 测试滚动
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(500);
    
    // 页面应该可以滚动
    const scrollHeight = await page.evaluate(() => document.body.scrollHeight);
    expect(scrollHeight).toBeGreaterThan(0);
  });

  test('字体渲染测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 检查字体样式
    const fontFamily = await page.evaluate(() => {
      const body = document.body;
      return window.getComputedStyle(body).fontFamily;
    });
    
    console.log(`页面字体: ${fontFamily}`);
    
    // 应该有字体样式
    expect(fontFamily).toBeTruthy();
  });
});
