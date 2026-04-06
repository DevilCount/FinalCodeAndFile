// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * Playwright 测试配置 - 实验室管理系统
 * 包含功能测试、性能测试、UI测试、兼容性测试、安全测试
 */
module.exports = defineConfig({
  testDir: './tests',
  timeout: 60000,
  expect: {
    timeout: 10000
  },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],
  
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    // 自定义截图目录
    screenshotDir: '../test_results/screenshots/',
  },

  projects: [
    // Chromium - 主要测试
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Firefox
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    // Webkit
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // 移动端模拟
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: true,
    timeout: 120000,
  },
});
