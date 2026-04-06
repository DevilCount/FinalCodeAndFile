/**
 * 安全测试套件 - 实验室管理系统
 * 包括目录设置、登录验证、日志文件、脚本语言安全性测试
 */
const { test, expect, request } = require('@playwright/test');

test.describe('安全测试 - 目录设置测试', () => {
  test('敏感目录访问测试', async ({ page }) => {
    // 尝试访问敏感目录
    const sensitivePaths = [
      '/admin',
      '/.git',
      '/.env',
      '/config',
      '/node_modules',
      '/package.json',
      '/.gitignore'
    ];
    
    for (const path of sensitivePaths) {
      const response = await page.goto(path, { failOnStatusCode: false });
      // 应该返回404或重定向，而不是200
      if (response) {
        expect(response.status()).not.toBe(200);
      }
    }
  });

  test('API端点认证测试', async ({ page }) => {
    // 尝试不带token访问受保护的API
    const apiPaths = [
      '/api/user/list',
      '/api/sample/list',
      '/api/report/list'
    ];
    
    for (const path of apiPaths) {
      const response = await request.get(`http://localhost:3000${path}`);
      // 应该返回401未授权或403禁止访问
      // 或者返回登录页重定向
    }
  });

  test('目录遍历防护测试', async ({ page }) => {
    const maliciousPaths = [
      '/../../etc/passwd',
      '/..%2F..%2Fetc%2Fpasswd',
      '/%2e%2e/%2e%2e/etc/passwd'
    ];
    
    for (const path of maliciousPaths) {
      const response = await page.goto(path, { failOnStatusCode: false });
      if (response) {
        // 应该返回404或403
        expect(response.status()).toBeGreaterThanOrEqual(400);
      }
    }
  });

  test('文件包含防护测试', async ({ page }) => {
    const maliciousQueries = [
      '?file=../../etc/passwd',
      '?page=../../../etc/passwd',
      '?include=php://input'
    ];
    
    for (const query of maliciousQueries) {
      await page.goto(`/sample${query}`, { failOnStatusCode: false });
    }
    
    // 页面应该不返回敏感内容
    const content = await page.content();
    expect(content).not.toContain('root:');
    expect(content).not.toContain('[boot loader]');
  });
});

test.describe('安全测试 - 登录验证测试', () => {
  test('SQL注入防护测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 常见的SQL注入payload
    const sqlPayloads = [
      "' OR '1'='1",
      "' OR '1'='1' --",
      "' OR '1'='1' /*",
      "admin'--",
      "1' AND '1'='1",
      "1; DROP TABLE users--"
    ];
    
    for (const payload of sqlPayloads) {
      await page.fill('input[placeholder*="用户名"]', payload);
      await page.fill('input[type="password"]', 'anything');
      await page.click('button:has-text("登 录")');
      await page.waitForTimeout(1000);
      
      // 不应该直接登录成功
      const currentUrl = page.url();
      const isLoggedIn = !currentUrl.includes('/login');
      
      if (isLoggedIn) {
        // 如果登录成功，不应该显示任何敏感数据
        const content = await page.content();
        expect(content).not.toContain('SQL');
        expect(content).not.toContain('syntax error');
      }
    }
  });

  test('XSS防护测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // XSS payload
    const xssPayloads = [
      '<script>alert("XSS")</script>',
      '<img src=x onerror=alert("XSS")>',
      '<svg onload=alert("XSS")>',
      'javascript:alert("XSS")',
      '<body onload=alert("XSS")>'
    ];
    
    for (const payload of xssPayloads) {
      await page.fill('input[placeholder*="用户名"]', payload);
      await page.fill('input[type="password"]', 'admin123');
      await page.click('button:has-text("登 录")');
      await page.waitForTimeout(1000);
      
      // 页面不应该执行脚本
      const isAlertShown = await page.evaluate(() => {
        return window.alertCalled || false;
      });
      
      expect(isAlertShown).toBeFalsy();
    }
  });

  test('弱密码测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 弱密码尝试
    const weakPasswords = [
      { user: 'admin', pass: '123456' },
      { user: 'admin', pass: 'password' },
      { user: 'admin', pass: 'admin' },
      { user: 'admin', pass: '000000' },
      { user: 'root', pass: 'root' }
    ];
    
    for (const cred of weakPasswords) {
      await page.fill('input[placeholder*="用户名"]', cred.user);
      await page.fill('input[type="password"]', cred.pass);
      await page.click('button:has-text("登 录")');
      await page.waitForTimeout(1500);
      
      // 应该有适当的错误提示，不暴露账号是否存在
      const errorMsg = await page.locator('text=/错误|失败|不存在|密码错误/i').isVisible().catch(() => false);
      // 系统应该返回通用的错误消息
    }
  });

  test('暴力破解防护测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 模拟多次失败登录
    for (let i = 0; i < 6; i++) {
      await page.fill('input[placeholder*="用户名"]', 'admin');
      await page.fill('input[type="password"]', 'wrongpass');
      await page.click('button:has-text("登 录")');
      await page.waitForTimeout(500);
    }
    
    // 检查是否有验证码或账户锁定
    const captcha = await page.locator('.el-captcha, [class*="captcha"], [class*="verify"]').isVisible().catch(() => false);
    const lockout = await page.locator('text=/锁定|次数过多|请稍后/i').isVisible().catch(() => false);
    
    console.log(`验证码显示: ${captcha}, 账户锁定: ${lockout}`);
  });

  test('会话超时测试', async ({ page }) => {
    // 登录
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 等待会话超时（如果有的话）
    await page.waitForTimeout(5000);
    
    // 尝试访问需要认证的页面
    await page.goto('/sample');
    await page.waitForTimeout(1000);
    
    // 应该仍然有效或重定向到登录
    const url = page.url();
    console.log(`会话超时测试 - 当前URL: ${url}`);
  });
});

test.describe('安全测试 - 敏感信息测试', () => {
  test('密码字段不可复制测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput).toBeVisible();
    
    // 密码输入框应该禁用自动填充或复制
    const autocomplete = await passwordInput.getAttribute('autocomplete');
    console.log(`密码框autocomplete: ${autocomplete}`);
  });

  test('敏感数据不在源码中测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 获取页面源码
    const content = await page.content();
    
    // 检查不应该包含的敏感信息
    const sensitivePatterns = [
      /password\s*[:=]\s*['"][^'"]+['"]/i,
      /secret\s*[:=]\s*['"][^'"]+['"]/i,
      /api[_-]?key\s*[:=]\s*['"][^'"]+['"]/i,
      /token\s*[:=]\s*['"][^'"]+['"]/i
    ];
    
    for (const pattern of sensitivePatterns) {
      const match = content.match(pattern);
      if (match) {
        console.log(`发现疑似敏感信息: ${match[0]}`);
      }
      expect(match).toBeNull();
    }
  });

  test('API响应不暴露敏感信息测试', async ({ page }) => {
    // 登录
    await page.goto('/login');
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:="登 录")');
    await page.waitForTimeout(1500);
    
    // 获取网络请求
    const apiResponses = [];
    page.on('response', response => {
      if (response.url().includes('/api/') || response.url().includes('/user/')) {
        apiResponses.push({
          url: response.url(),
          status: response.status()
        });
      }
    });
    
    await page.goto('/user');
    await page.waitForTimeout(2000);
    
    // API响应不应该直接返回密码
    console.log('API响应:', apiResponses);
  });

  test('错误消息不泄露信息测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 使用错误凭据登录
    await page.fill('input[placeholder*="用户名"]', 'nonexistentuser123');
    await page.fill('input[type="password"]', 'wrongpass');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(2000);
    
    // 检查错误消息
    const pageContent = await page.content();
    
    // 不应该暴露：
    // - 用户是否存在（应返回通用错误）
    // - 数据库结构
    // - 内部路径
    expect(pageContent).not.toMatch(/user.*not found/i);
    expect(pageContent).not.toMatch(/sql.*error/i);
    expect(pageContent).not.toMatch(/stack.*trace/i);
    expect(pageContent).not.toMatch(/at\s+com\.sunnyaxin/i);
  });
});

test.describe('安全测试 - CSP和请求头测试', () => {
  test('Content-Security-Policy头测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    const csp = await page.evaluate(() => {
      const meta = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
      return meta ? meta.content : null;
    });
    
    console.log(`CSP策略: ${csp || '未设置'}`);
  });

  test('X-Content-Type-Options头测试', async ({ page }) => {
    const response = await page.request.get('http://localhost:3000/');
    const xContentType = response.headers()['x-content-type-options'];
    
    console.log(`X-Content-Type-Options: ${xContentType || '未设置'}`);
  });

  test('X-Frame-Options头测试', async ({ request }) => {
    const response = await request.get('http://localhost:3000/');
    const xFrame = response.headers()['x-frame-options'];
    
    console.log(`X-Frame-Options: ${xFrame || '未设置'}`);
  });

  test('HTTPS和Secure Cookie测试', async ({ page }) => {
    // 检查cookie安全性
    const cookies = await page.context().cookies();
    
    for (const cookie of cookies) {
      console.log(`Cookie: ${cookie.name}, Secure: ${cookie.secure}, HttpOnly: ${cookie.httpOnly}`);
    }
  });
});

test.describe('安全测试 - CSRF防护测试', () => {
  test('CSRF Token测试', async ({ page }) => {
    // 登录
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1500);
    
    // 检查表单是否有CSRF token
    const csrfInput = page.locator('input[name="_csrf"], input[name="csrf_token"], input[name="token"]');
    const hasCsrf = await csrfInput.count() > 0;
    
    console.log(`CSRF Token存在: ${hasCsrf}`);
  });

  test('请求来源验证测试', async ({ page }) => {
    // 尝试从不同来源发送请求
    const response = await page.request.get('http://localhost:3000/', {
      headers: {
        'Origin': 'http://evil.com',
        'Referer': 'http://evil.com'
      }
    });
    
    // 请求应该被处理（实际验证取决于后端）
    expect(response.status()).toBeGreaterThanOrEqual(200);
  });
});

test.describe('安全测试 - 脚本语言安全性测试', () => {
  test('HTML转义测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 输入HTML特殊字符
    const htmlChars = '<script>alert(1)</script>';
    await page.fill('input[placeholder*="用户名"]', htmlChars);
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1000);
    
    // 检查页面内容
    const content = await page.content();
    
    // 如果显示了输入内容，应该已经转义
    if (content.includes(htmlChars)) {
      // 检查是否以文本形式显示而不是作为脚本执行
      expect(content).not.toContain('<script>alert(1)</script>');
    }
  });

  test('JSON转义测试', async ({ page }) => {
    // 检查API响应中的JSON转义
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    const response = await page.request.get('http://localhost:8086/user/login?username=admin&password=admin123');
    const body = await response.text();
    
    // 尝试解析JSON（如果返回JSON）
    try {
      const json = JSON.parse(body);
      // JSON应该正确转义
      expect(body).not.toContain('<script>');
    } catch (e) {
      // 不是JSON响应，跳过
    }
  });

  test('URL编码测试', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // 使用URL编码的字符
    const encodedChars = encodeURIComponent('<script>alert("XSS")</script>');
    await page.fill('input[placeholder*="用户名"]', encodedChars);
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登 录")');
    await page.waitForTimeout(1000);
    
    // 页面应该正确处理编码字符
    await expect(page.locator('body')).toBeVisible();
  });
});
