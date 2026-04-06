@echo off
chcp 65001
echo ========================================
echo 实验室管理系统 - 一键启动所有服务
echo ========================================
echo.

echo [1/9] 启动 Redis...
start "Redis" cmd /k "cd /d C:\Users\86155\Desktop\Redis-x64-3.0.504\Redis-x64-3.0.504 && redis-server.exe"
timeout /t 3 /nobreak >nul

echo [2/9] 启动 Nacos...
start "Nacos" cmd /k "cd /d d:\FinalCodeAndFile\nacos\bin && startup.cmd -m standalone"
timeout /t 10 /nobreak >nul

echo [3/9] 启动 用户服务 (8086)...
start "User Service" cmd /k "cd /d d:\FinalCodeAndFile\lab-management-system\lab-user-service && java -jar target\lab-user-service-1.0.0.jar"
timeout /t 15 /nobreak >nul

echo [4/9] 启动 标本服务 (8087)...
start "Sample Service" cmd /k "cd /d d:\FinalCodeAndFile\lab-management-system\lab-sample-service && java -jar target\lab-sample-service-1.0.0.jar"
timeout /t 15 /nobreak >nul

echo [5/9] 启动 AI服务 (8089)...
start "AI Service" cmd /k "cd /d d:\FinalCodeAndFile\lab-management-system\lab-ai-service && java -jar target\lab-ai-service-1.0.0.jar"
timeout /t 15 /nobreak >nul

echo [6/9] 启动 报告服务 (8088)...
start "Report Service" cmd /k "cd /d d:\FinalCodeAndFile\lab-management-system\lab-report-service && java -jar target\lab-report-service-1.0.0.jar"
timeout /t 15 /nobreak >nul

echo [7/9] 启动 HL7服务 (8084)...
start "HL7 Service" cmd /k "cd /d d:\FinalCodeAndFile\lab-management-system\lab-hl7-service && java -jar target\lab-hl7-service-1.0.0.jar"
timeout /t 15 /nobreak >nul

echo [8/9] 启动 网关服务 (8080)...
start "Gateway Service" cmd /k "cd /d d:\FinalCodeAndFile\lab-management-system\lab-gateway && java -jar target\lab-gateway-1.0.0.jar"
timeout /t 15 /nobreak >nul

echo [9/9] 启动 前端服务 (3000)...
start "Frontend" cmd /k "cd /d d:\FinalCodeAndFile\lab-management-system\frontend && npm run dev"

echo.
echo ========================================
echo 所有服务启动命令已发送！
echo 请等待各服务完全启动后再使用
echo.
echo 服务端口列表:
echo   - Redis:     6379
echo   - Nacos:     8848
echo   - 用户服务:  8086
echo   - 标本服务:  8087
echo   - 报告服务:  8088
echo   - AI服务:    8089
echo   - HL7服务:   8084
echo   - 网关:      8080
echo   - 前端:      3000
echo.
echo 访问地址: http://localhost:3000
echo 测试账号: admin / admin123
echo ========================================
echo.
pause
