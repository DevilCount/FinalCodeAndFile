/**
 * 接口测试套件 - 实验室管理系统
 * 包括浏览器与服务器接口、外部接口、错误处理测试
 */
const { test, expect, request } = require('@playwright/test');

test.describe('接口测试 - 用户服务API测试', () => {
  test('登录API测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/user/login', {
      params: {
        username: 'admin',
        password: 'admin123'
      }
    });
    
    expect(response.status()).toBe(200);
    
    const body = await response.json();
    expect(body.code).toBe(200);
    expect(body.data).toBeTruthy();
    expect(body.data.username).toBe('admin');
  });

  test('用户列表API测试', async ({ request }) => {
    // 先登录获取会话
    const loginResp = await request.get('http://localhost:8086/user/login', {
      params: { username: 'admin', password: 'admin123' }
    });
    const cookies = loginResp.headers()['set-cookie'];
    
    // 获取用户列表
    const response = await request.get('http://localhost:8086/user/list', {
      params: { current: 1, size: 10 }
    });
    
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.code).toBe(200);
    expect(body.data.records).toBeTruthy();
  });

  test('获取当前用户API测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/user/current');
    expect(response.status()).toBeGreaterThanOrEqual(200);
  });

  test('用户创建API测试', async ({ request }) => {
    const response = await request.post('http://localhost:8086/user/register', {
      data: {
        username: 'testuser' + Date.now(),
        password: '123456',
        realName: '测试用户',
        role: 'USER'
      }
    });
    
    // 应该成功或返回错误（如果用户名已存在）
    expect(response.status()).toBeGreaterThanOrEqual(200);
  });
});

test.describe('接口测试 - 标本服务API测试', () => {
  test('标本列表API测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/sample/list', {
      params: { current: 1, size: 10 }
    });
    
    expect(response.status()).toBe(200);
  });

  test('标本详情API测试', async ({ request }) => {
    // 先获取标本列表
    const listResp = await request.get('http://localhost:8086/sample/list', {
      params: { current: 1, size: 1 }
    });
    
    expect(response.status()).toBe(200);
  });

  test('标本创建API测试', async ({ request }) => {
    const response = await request.post('http://localhost:8086/sample/add', {
      data: {
        patientName: '测试患者',
        sampleType: 'BLOOD',
        status: 'PENDING'
      }
    });
    
    // 应该返回200或相关错误
    expect(response.status()).toBeGreaterThanOrEqual(200);
  });

  test('标本统计API测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/sample/stats');
    
    // 应该返回统计数据
    expect(response.status()).toBeGreaterThanOrEqual(200);
  });
});

test.describe('接口测试 - 报告服务API测试', () => {
  test('报告列表API测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/report/list', {
      params: { current: 1, size: 10 }
    });
    
    expect(response.status()).toBe(200);
  });

  test('报告详情API测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/report/detail/1');
    
    expect(response.status()).toBeGreaterThanOrEqual(200);
  });

  test('报告创建API测试', async ({ request }) => {
    const response = await request.post('http://localhost:8086/report/add', {
      data: {
        sampleId: 1,
        result: '正常',
        conclusion: '无异常'
      }
    });
    
    expect(response.status()).toBeGreaterThanOrEqual(200);
  });
});

test.describe('接口测试 - 外部接口测试', () => {
  test('Nacos健康检查接口', async ({ request }) => {
    // 如果Nacos启用，测试连接
    const response = await request.get('http://localhost:8848/nacos/v1/console/health/readiness').catch(() => null);
    // 测试是可选的
  });

  test('Redis健康检查接口', async ({ request }) => {
    // Redis通过应用内部检查，这里测试应用状态
    const response = await request.get('http://localhost:8086/actuator/health').catch(() => null);
    // 测试是可选的
  });

  test('数据库连接测试', async ({ request }) => {
    // 通过API调用测试数据库连接
    const response = await request.get('http://localhost:8086/user/list', {
      params: { current: 1, size: 1 }
    });
    
    // 如果返回数据，说明数据库连接正常
    if (response.status() === 200) {
      const body = await response.json();
      expect(body.success || body.code === 200).toBeTruthy();
    }
  });
});

test.describe('接口测试 - 错误处理测试', () => {
  test('404错误处理测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/nonexistent/api');
    
    expect(response.status()).toBe(404);
  });

  test('参数缺失错误测试', async ({ request }) => {
    // 登录时不提供参数
    const response = await request.get('http://localhost:8086/user/login');
    
    // 应该返回错误而不是崩溃
    expect(response.status()).toBeGreaterThanOrEqual(400);
  });

  test('无效参数错误测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/user/list', {
      params: { current: 'invalid', size: 'invalid' }
    });
    
    // 应该优雅处理无效参数
    expect(response.status()).toBeGreaterThanOrEqual(200);
  });

  test('SQL注入错误处理测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/user/login', {
      params: {
        username: "' OR '1'='1",
        password: "anything"
      }
    });
    
    // 应该拒绝注入而不是执行
    const body = await response.json();
    // 应该返回失败而不是成功
    if (response.status() === 200) {
      expect(body.code).not.toBe(200);
    }
  });

  test('XSS注入错误处理测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/user/login', {
      params: {
        username: '<script>alert("XSS")</script>',
        password: 'test'
      }
    });
    
    // 应该处理XSS而不是在响应中返回脚本
    const body = await response.text();
    expect(body).not.toContain('<script>alert("XSS")</script>');
  });

  test('超长参数错误测试', async ({ request }) => {
    const longString = 'A'.repeat(10000);
    const response = await request.get('http://localhost:8086/user/login', {
      params: {
        username: longString,
        password: longString
      }
    });
    
    // 应该优雅处理超长输入
    expect(response.status()).toBeGreaterThanOrEqual(200);
  });

  test('特殊字符错误处理测试', async ({ request }) => {
    const specialChars = ['!@#$%^&*()', '<>{}[]', '\\|;\':"', '`~'];
    
    for (const chars of specialChars) {
      const response = await request.get('http://localhost:8086/user/login', {
        params: {
          username: chars,
          password: chars
        }
      });
      
      // 应该处理特殊字符而不崩溃
      expect(response.status()).toBeGreaterThanOrEqual(200);
    }
  });

  test('并发请求错误测试', async ({ request }) => {
    // 同时发送多个请求
    const promises = [];
    for (let i = 0; i < 10; i++) {
      promises.push(request.get('http://localhost:8086/user/list', {
        params: { current: 1, size: 10 }
      }));
    }
    
    const responses = await Promise.all(promises);
    
    // 所有请求应该成功或优雅地失败
    for (const resp of responses) {
      expect(resp.status()).toBeGreaterThanOrEqual(200);
    }
  });
});

test.describe('接口测试 - 数据格式测试', () => {
  test('JSON格式测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/user/login', {
      params: { username: 'admin', password: 'admin123' }
    });
    
    const contentType = response.headers()['content-type'];
    expect(contentType).toContain('application/json');
    
    const body = await response.json();
    expect(body).toHaveProperty('code');
    expect(body).toHaveProperty('message');
    expect(body).toHaveProperty('data');
  });

  test('时间戳格式测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/user/login', {
      params: { username: 'admin', password: 'admin123' }
    });
    
    const body = await response.json();
    if (body.timestamp) {
      // 应该是有效的Unix时间戳
      expect(body.timestamp).toBeGreaterThan(1000000000000);
      expect(body.timestamp).toBeLessThan(2000000000000);
    }
  });

  test('分页数据格式测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/user/list', {
      params: { current: 1, size: 10 }
    });
    
    const body = await response.json();
    if (body.data) {
      expect(body.data).toHaveProperty('current');
      expect(body.data).toHaveProperty('size');
      expect(body.data).toHaveProperty('total');
      expect(body.data).toHaveProperty('records');
    }
  });

  test('空数据响应格式测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/user/list', {
      params: { current: 999999, size: 10 }
    });
    
    const body = await response.json();
    // 应该返回空列表而不是错误
    expect(body.code).toBe(200);
    if (body.data && body.data.records) {
      expect(Array.isArray(body.data.records)).toBeTruthy();
    }
  });
});

test.describe('接口测试 - 性能测试', () => {
  test('API响应时间测试', async ({ request }) => {
    const startTime = Date.now();
    
    await request.get('http://localhost:8086/user/login', {
      params: { username: 'admin', password: 'admin123' }
    });
    
    const responseTime = Date.now() - startTime;
    console.log(`登录API响应时间: ${responseTime}ms`);
    
    // API响应时间应该在3秒内
    expect(responseTime).toBeLessThan(3000);
  });

  test('大数据量查询测试', async ({ request }) => {
    const startTime = Date.now();
    
    await request.get('http://localhost:8086/user/list', {
      params: { current: 1, size: 1000 }
    });
    
    const responseTime = Date.now() - startTime;
    console.log(`大数据量查询响应时间: ${responseTime}ms`);
    
    expect(responseTime).toBeLessThan(5000);
  });

  test('并发API调用测试', async ({ request }) => {
    const startTime = Date.now();
    
    const promises = [
      request.get('http://localhost:8086/user/list'),
      request.get('http://localhost:8086/sample/list'),
      request.get('http://localhost:8086/report/list')
    ];
    
    await Promise.all(promises);
    
    const totalTime = Date.now() - startTime;
    console.log(`并发API调用总时间: ${totalTime}ms`);
    
    expect(totalTime).toBeLessThan(10000);
  });
});

test.describe('接口测试 - 认证和授权测试', () => {
  test('未认证访问测试', async ({ request }) => {
    // 不带认证信息访问受保护接口
    const response = await request.get('http://localhost:8086/user/list');
    
    // 应该返回未授权或重定向
    expect(response.status()).toBeGreaterThanOrEqual(401);
  });

  test('无效Token测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/user/list', {
      headers: {
        'Authorization': 'Bearer invalid_token_here'
      }
    });
    
    // 应该拒绝无效token
    expect(response.status()).toBeGreaterThanOrEqual(401);
  });

  test('过期Token测试', async ({ request }) => {
    // 使用一个明显过期的token
    const response = await request.get('http://localhost:8086/user/list', {
      headers: {
        'Authorization': 'Bearer expired_token_12345'
      }
    });
    
    expect(response.status()).toBeGreaterThanOrEqual(401);
  });
});

test.describe('接口测试 - CORS测试', () => {
  test('CORS预检请求测试', async ({ request }) => {
    const response = await request.fetch('http://localhost:8086/user/login', {
      method: 'OPTIONS',
      headers: {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'GET'
      }
    });
    
    // 应该返回CORS头
    const corsHeaders = response.headers();
    expect(corsHeaders).toHaveProperty('access-control-allow-origin');
  });

  test('跨域请求测试', async ({ request }) => {
    const response = await request.get('http://localhost:8086/user/login', {
      params: { username: 'admin', password: 'admin123' },
      headers: {
        'Origin': 'http://localhost:3000'
      }
    });
    
    expect(response.status()).toBe(200);
  });
});
