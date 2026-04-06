@echo off
chcp 65001 >nul
echo ============================================
echo  实验室管理系统 - E2E 自动化测试工具
echo ============================================
echo.

cd /d "%~dp0\frontend"

echo [信息] 检查环境...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

echo [信息] Node.js 版本:
node --version

echo.
echo [信息] Playwright 版本:
npx playwright --version

echo.
echo ============================================
echo  请选择操作:
echo ============================================
echo  1. 运行全部测试 (推荐)
echo  2. 只运行登录测试 (TC001)
echo  3. 只运行仪表盘测试 (TC002)
echo  4. 只运行标本管理测试 (TC003)
echo  5. 只运行报告管理测试 (TC004)
echo  6. 只运行AI诊断测试 (TC005)
echo  7. 只运行用户管理测试 (TC006)
echo  8. 运行健康检查 (HC001-HC002)
echo  9. UI模式调试 (可视化)
echo  10. 查看测试报告
echo  11. 安装Playwright浏览器
echo  0. 退出
echo ============================================

set /p choice=请输入选项编号:

if "%choice%"=="1" goto run_all
if "%choice%"=="2" goto run_tc001
if "%choice%"=="3" goto run_tc002
if "%choice%"=="4" goto run_tc003
if "%choice%"=="5" goto run_tc004
if "%choice%"=="6" goto run_tc005
if "%choice%"=="7" goto run_tc006
if "%choice%"=="8" goto run_health
if "%choice%"=="9" goto ui_mode
if "%choice%"=="10" goto show_report
if "%choice%"=="11" goto install_browser
if "%choice%"=="0" goto end

echo [错误] 无效选项
pause
goto end

:run_all
echo.
echo [开始] 运行全部E2E测试...
echo 预计耗时: 3-4 分钟
echo.
npx playwright test tests/e2e/full-lab-flow.spec.js --reporter=list,html
goto show_result

:run_tc001
echo.
echo [开始] 运行登录流程测试...
npx playwright test tests/e2e/full-lab-flow.spec.js -g "TC001_用户登录流程" --reporter=list
goto show_result

:run_tc002
echo.
echo [开始] 运行仪表盘测试...
npx playwright test tests/e2e/full-lab-flow.spec.js -g "TC002_仪表盘" --reporter=list
goto show_result

:run_tc003
echo.
echo [开始] 运行标本管理测试...
npx playwright test tests/e2e/full-lab-flow.spec.js -g "TC003_标本管理" --reporter=list
goto show_result

:run_tc004
echo.
echo [开始] 运行报告管理测试...
npx playwright test tests/e2e/full-lab-flow.spec.js -g "TC004_报告管理" --reporter=list
goto show_result

:run_tc005
echo.
echo [开始] 运行AI诊断测试...
npx playwright test tests/e2e/full-lab-flow.spec.js -g "TC005_AI诊断" --reporter=list
goto show_result

:run_tc006
echo.
echo [开始] 运行用户管理测试...
npx playwright test tests/e2e/full-lab-flow.spec.js -g "TC006_用户管理" --reporter=list
goto show_result

:run_health
echo.
echo [开始] 运行健康检查...
npx playwright test tests/e2e/full-lab-flow.spec.js -g "快速健康检查" --reporter=list
goto show_result

:ui_mode
echo.
echo [启动] Playwright UI 模式...
echo 提示: 可视化界面中可以单步调试和查看详情
npx playwright test --ui
goto end

:show_report
echo.
echo [打开] 测试报告...
if exist "playwright-report\index.html" (
    start playwright-report\index.html
) else (
    echo [警告] 未找到测试报告，请先运行测试
)
goto end

:install_browser
echo.
echo [安装] Playwright 浏览器...
npx playwright install chromium firefox webkit
echo.
echo [完成] 浏览器安装完成!
goto end

:show_result
echo.
echo ============================================
if %errorlevel% equ 0 (
    echo  ✓ 测试完成!
) else (
    echo  ✗ 测试失败，请检查上方日志
)
echo ============================================
echo.
echo [提示] 查看详细HTML报告请选择选项 10
echo [提示] 截图保存在 ..\test_results\screenshots\
echo.

:end
pause
