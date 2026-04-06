# 实验室管理系统(LIS) v1.4.2 - 部署指南

**文档编号**: LMS-DG-2026-V142  
**项目名称**: 实验室信息管理系统 (Laboratory Information System, LIS)  
**系统版本**: **v1.4.2**  
**编制日期**: 2026年4月3日  
**适用环境**: 开发/测试/演示 (不适用于生产环境直接部署,见安全说明)

---

## 目录

1. [部署前准备](#1-部署前准备)
2. [环境要求](#2-环境要求)
3. [安装步骤](#3-安装步骤)
4. [启动顺序](#4-启动顺序)
5. [配置说明](#5-配置说明)
6. [验证部署](#6-验证部署)
7. [常见问题排查](#7-常见问题排查)
8. [停止与卸载](#8-停止与卸载)

---

## 1. 部署前准备

### 1.1 硬件要求

| 组件 | 最低配置 | 推荐配置(开发/演示) | 生产环境建议 |
|------|---------|-------------------|-------------|
| **CPU** | 4核 | 8核+ | 16核+ |
| **内存** | 8GB | 16GB | 32GB+ |
| **硬盘** | 50GB SSD | 100GB SSD | 200GB SSD (日志分离) |
| **网络** | 本地回环(localhost) | 局域网(内网) | 公网IP + SSL证书 |

### 1.2 软件依赖清单

#### 必须安装 (Required)

| 软件 | 版本要求 | 用途 | 下载地址 |
|------|---------|------|----------|
| **JDK (Java)** | 17 LTS (17.0.11+) | 后端运行时 | https://adoptium.net/ |
| **Maven** | 3.8+ | 项目构建 | https://maven.apache.org/download.cgi |
| **Node.js** | 18 LTS (18.17.0+) | 前端构建运行 | https://nodejs.org/ |
| **npm** | 9.x (随Node.js) | 前端包管理 | (随Node.js安装) |
| **MySQL** | 8.0+ (推荐8.3) | 数据库 | https://dev.mysql.com/downloads/ |
| **Redis** | 6.0+ (推荐7.x) | 缓存/Session | https://redis.io/download |
| **Nacos** | 2.2.3 | 服务注册中心 | https://github.com/alibaba/nacos/releases |

#### 可选安装 (Optional)

| 软件 | 用途 | 是否必须 |
|------|------|----------|
| **Git** | 版本控制 | 强烈建议 |
| **Navicat/DBeaver** | 数据库GUI管理 | 推荐(方便查看数据) |
| **Postman** | API调试 | 推荐(开发调试用) |
| **Redis Desktop Manager** | Redis可视化 | 可选 |
| **VS Code / IntelliJ IDEA** | 代码编辑 | 必须(开发时) |

### 1.3 前置检查清单

在开始部署前,请确认以下事项:

```markdown
## 部署前置检查清单 ☐

### 环境检查
- [ ] JDK 17已安装: 执行 `java -version` 显示 17.0.11+
- [ ] Maven已安装: 执行 `mvn -v` 显示 Apache Maven 3.8+
- [ ] Node.js已安装: 执行 `node -v` 显示 v18.x
- [ ] npm已安装: 执行 `npm -v` 显示 9.x
- [ ] MySQL已安装并启动: 执行 `mysql --version` 显示 8.x
- [ ] Redis已安装并启动: 执行 `redis-cli ping` 返回 PONG
- [ ] Nacos已下载: nacos目录存在

### 端口检查 (确保以下端口未被占用)
- [ ] 3306 (MySQL)
- [ ] 6379 (Redis)
- [ ] 8848 (Nacos)
- [ ] 8080 (Gateway)
- [ ] 8084 (HL7 Service)
- [ ] 8085 (AI Service)
- [ ] 8086 (User Service)
- [ ] 8087 (Sample Service)
- [ ] 8088 (Report Service)
- [ ] 3000/5173 (Frontend Dev Server)

### 权限检查
- [ ] 当前用户有读写项目目录的权限
- [ ] MySQL root用户可远程连接(或配置了本地访问)
- [ ] Redis无密码或已配置正确密码
- [ ] 防火墙允许上述端口通信(开发环境可关闭防火墙)
```

---

## 2. 环境要求

### 2.1 操作系统支持

| 操作系统 | 支持版本 | 说明 |
|----------|---------|------|
| **Windows 10/11** | ✅ 推荐 | 主要开发和测试平台 |
| **Windows Server 2019/2022** | ✅ 支持 | 生产服务器(需额外安全配置) |
| **Ubuntu 20.04/22.04 LTS** | ✅ 支持 | Linux生产环境首选 |
| **macOS 12+ (Monterey/Ventura)** | ✅ 支持 | Apple Silicon (M1/M2) 需注意架构 |

> **本文档以 Windows 11 为例进行说明**, Linux/macOS 用户需要适当调整命令格式。

### 2.2 JDK 17 安装与配置

#### Windows 安装步骤:

```powershell
# 1. 下载 Adoptium Eclipse Temurin JDK 17
#    访问: https://adoptium.net/
#    选择: Windows x64 installer (.msi)

# 2. 运行安装程序,按向导完成安装
#    默认路径: C:\Program Files\Eclipse Adoptium\jdk-17.0.11+11

# 3. 配置环境变量
[System.Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Eclipse Adoptium\jdk-17.0.11+11", "User")
[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";%JAVA_HOME%\bin", "User")

# 4. 验证安装
java -version
# 应输出:
# openjdk version "17.0.11" 2024-04-16
# OpenJDK Runtime Environment Temurin-17.0.11+11 (build 17.0.11+9)
# OpenJDK 64-Bit Server VM Temurin-17.0.11+11 (build 17.0.11+9, mixed mode, sharing)
```

#### Linux 安装步骤:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-17-jdk -y
java -version

# CentOS/RHEL
sudo yum install java-17-openjdk-devel -y
# 或使用 SDKMAN
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install java 17.0.11-tem
```

### 2.3 Maven 安装与配置

#### Windows:

```powershell
# 1. 下载 Apache Maven 3.9.x
#    访问: https://maven.apache.org/download.cgi
#    选择: apache-maven-3.9.6-bin.zip

# 2. 解压到指定目录 (如 D:\tools\apache-maven-3.9.6)

# 3. 配置环境变量
[System.Environment]::SetEnvironmentVariable("MAVEN_HOME", "D:\tools\apache-maven-3.9.6", "User")
[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";%MAVEN_HOME%\bin", "User")

# 4. 验证安装
mvn -v
# 应输出:
# Apache Maven 3.9.6 (...)
# Maven home: D:\tools\apache-maven-3.9.6
# Java version: 17.0.11, vendor: Eclipse Adoptium
```

#### Maven 配置优化 (可选):

编辑 `%USERPROFILE%\.m2\settings.xml`:
```xml
<settings>
  <localRepository>D:/maven_repo</localRepository>
  <mirrors>
    <mirror>
      <id>aliyun</id>
      <name>Aliyun Maven Mirror</name>
      <url>https://maven.aliyun.com/repository/public</url>
      <mirrorOf>central</mirrorOf>
    </mirror>
  </mirrors>
</settings>
```
> 使用阿里云镜像可大幅加速依赖下载(国内推荐)

### 2.4 Node.js 与 npm 安装

#### Windows:

```powershell
# 1. 下载 Node.js 18 LTS
#    访问: https://nodejs.org/
#    选择: LTS版本 (推荐v18.20.x或更新)
#    安装包: node-v18.20.3-x64.msi

# 2. 运行安装程序,勾选以下选项:
#    ☑ Automatically install the necessary tools
#    ☑ Add to PATH (recommended)

# 3. 验证安装
node -v   # 应输出 v18.x.x
npm -v    # 应输出 10.x.x
```

#### npm 淘宝镜像配置 (国内加速):

```bash
npm config set registry https://registry.npmmirror.com
# 验证
npm config get registry
# 应输出: https://registry.npmmirror.com
```

### 2.5 MySQL 8 安装与初始化

#### Windows 安装:

```powershell
# 1. 下载 MySQL Installer
#    访问: https://dev.mysql.com/downloads/installer/
#    选择: mysql-installer-community-8.3.0.msi

# 2. 运行安装程序,选择"Server only"
#    配置类型: Development Computer
#    认证方式: Use Strong Password Encryption for Authentication (推荐)

# 3. 设置root密码 (记住此密码!)
#    开发环境可设为简单密码(如1234),但⚠️ 生产环境必须使用强密码

# 4. 配置MySQL服务
#    Windows Service Name: MySQL80
#    勾选: Configure MySQL Server as a Windows Service
#    勾选: Start the MySQL Server at System Startup

# 5. 验证安装
mysql --version
# 应输出: mysql  Ver 8.3.0 for Win64 on x86_64 (MySQL Community Server - GPL)

# 6. 连接测试
mysql -u root -p
# 输入设置的密码,应成功进入MySQL命令行
mysql> SHOW DATABASES;
# 应看到: information_schema, mysql, performance_schema, sys
```

#### 创建数据库和用户:

```sql
-- 以root身份登录MySQL后执行:
CREATE DATABASE lab_management 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_general_ci;

-- 创建应用专用用户 (可选,开发环境可直接用root)
CREATE USER 'lab_user'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON lab_management.* TO 'lab_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2.6 Redis 安装与配置

#### Windows (通过WSL2或Docker):

> **重要**: Redis官方不支持Windows原生运行! 推荐以下方案:

**方案A: WSL2 + Linux版Redis (推荐)**
```bash
# 在WSL2中执行:
# 1. 更新包列表
sudo apt update

# 2. 安装Redis
sudo apt install redis-server -y

# 3. 启动Redis
sudo service redis-server start

# 4. 验证
redis-cli ping
# 应返回: PONG
```

**方案B: Docker (最简单)**
```powershell
# 1. 安装Docker Desktop for Windows
#    访问: https://www.docker.com/products/docker-desktop/

# 2. 启动Docker Desktop

# 3. 运行Redis容器
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 4. 验证
docker exec -it redis redis-cli ping
# 应返回: PONG
```

**方案C: Memurai (Windows原生Redis替代品)**
- 下载: https://www.memurai.com/
- 类似Redis,兼容Redis协议
- 免费用于开发环境

#### Linux 原生安装:

```bash
# Ubuntu/Debian
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server
redis-cli ping
# PONG
```

### 2.7 Nacos 安装与配置

#### 下载与启动:

```powershell
# 1. 下载Nacos 2.2.3
#    访问: https://github.com/alibaba/nacos/releases
#    选择: nacos-server-2.2.3.zip

# 2. 解压到目标目录 (如 D:\middleware\nacos)

# 3. 进入bin目录
cd D:\middleware\nacos\nacos\bin

# 4. 启动Nacos (standalone单机模式)
startup.cmd -m standalone
# 或 Linux/Mac:
# sh startup.sh -m standalone

# 5. 等待启动完成 (约30秒-1分钟)
#    看到"Nacos started successfully in stand alone mode"即成功

# 6. 访问Nacos控制台
#    浏览器打开: http://localhost:8848/nacos
#    默认账号: nacos / nacos
```

#### Nacos配置说明:

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 端口 | 8848 | Web控制台+API端口 |
| gRPC端口 | 9848 (主) + 9849 (备用) | 服务间gRPC通信 (⚠️ 当前未开放可能导致日志刷屏) |
| 存储模式 | 内嵌Derby数据库 | 单机模式足够,集群需MySQL |
| 账号/密码 | nacos/nacos | 首次登录后请修改! |

---

## 3. 安装步骤

### 3.1 获取源代码

```bash
# 方式1: Git克隆 (如果有仓库)
git clone <repository-url> lab-management-system
cd lab-management-system

# 方式2: 直接使用已有代码
# 项目路径: d:\FinalCodeAndFile\lab-management-system
cd d:\FinalCodeAndFile\lab-management-system
```

### 3.2 后端构建 (Maven)

```bash
# 进入项目根目录
cd d:\FinalCodeAndFile\lab-management-system

# 清理之前的构建产物 (如果有的话)
mvn clean

# 编译项目 (跳过测试以加快速度)
mvn compile

# 如果编译失败,检查:
# 1. JDK版本是否为17 (java -version)
# 2. Maven是否正确配置 (mvn -v)
# 3. 网络是否能访问Maven中央仓库 (或阿里云镜像)
# 4. 查看错误日志中的具体原因

# 打包所有模块 (生成可执行jar)
mvn package -DskipTests

# 构建成功后,各服务的jar文件位置:
# lab-gateway/target/lab-gateway-1.0.0.jar
# lab-user-service/target/lab-user-service-1.0.0.jar
# lab-sample-service/target/lab-sample-service-1.0.0.jar
# lab-report-service/target/lab-report-service-1.0.0.jar
# lab-hl7-service/target/lab-hl7-service-1.0.0.jar
# lab-ai-service/target/lab-ai-service-1.0.0.jar
```

**常见编译问题及解决方案**:

| 错误信息 | 原因 | 解决方案 |
|----------|------|---------|
| `package org.springframework.bind does not exist` | Spring Boot 3.x import路径变更 | 修改GlobalExceptionHandler.java的import为`org.springframework.web.bind.*` |
| `cannot find symbol: class ArrayList` | SampleController缺少import | 添加`import java.util.ArrayList;` |
| `Failed to execute goal on lab-xxx` | 编译错误导致打包失败 | 先修复编译错误再重新package |
| `Dependency resolution failed` | 网络问题或仓库配置错误 | 检查settings.xml镜像配置,尝试`mvn -U clean package` |

### 3.3 数据库初始化

```bash
# 方式1: 使用完整初始化脚本 (推荐首次部署)
mysql -u root -p lab_management < sql/init-tables.sql

# 方式2: 使用最小化脚本 (快速启动)
mysql -u root -p lab_management < sql/init-simple.sql

# 方式3: 手动执行SQL (如果上述脚本不存在问题)
mysql -u root -p
> USE lab_management;
> SOURCE sql/init.sql;  -- 或手动复制SQL内容粘贴执行
```

**验证数据库初始化**:
```sql
-- 连接MySQL后执行:
USE lab_management;
SHOW TABLES;
-- 应看到15+张表,包括: sys_user, lab_sample, lab_report, etc.

SELECT COUNT(*) FROM sys_user;
-- 应返回 >0 (有初始测试数据)

SELECT COUNT(*) FROM lab_sample;
-- 应返回 >0 (有初始测试数据)
```

### 3.4 前端依赖安装与构建

```bash
# 进入前端目录
cd frontend

# 安装npm依赖 (首次较慢,约2-5分钟)
npm install

# 验证依赖安装
ls node_modules | Select-Object Name
# 应看到大量文件夹(vue, axios, element-plus等)

# 开发模式启动 (可选,用于验证前端是否正常)
npm run dev
# 浏览器访问: http://localhost:3000 或 http://localhost:5173
# 应能看到登录页面

# 生产构建 (生成dist目录)
npm run build
# 构建产物在 frontend/dist/ 目录
```

**常见前端问题**:

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `npm ERR! network` | 网络问题 | 切换淘宝镜像: `npm config set registry https://registry.npmmirror.com` |
| `ENOENT: no such file or file` | node_modules损坏 | 删除node_modules和package-lock.json,重新`npm install` |
| `Vite build failed (TypeScript error)` | 类型错误 | 执行`npm run type-check`查看具体错误,修复类型定义 |
| 端口3000被占用 | 其他进程占用 | 修改`.env.development`中的PORT,或关闭占用进程 |

---

## 4. 启动顺序

### 4.1 启动顺序图

```
正确的启动顺序 (严格按照此顺序!)

Step 1: 基础设施层
├── ① MySQL (:3306)        ← 数据持久化基础
├── ② Redis (:6379)         ← 缓存/Session基础
└── ③ Nacos (:8848)         ← 服务注册发现基础

Step 2: 微服务层 (按依赖关系)
├── ④ User Service (:8086)  ← 无其他微服务依赖 (最先启动业务服务)
├── ⑤ AI Service (:8085)    ← 无其他微服务依赖
├── ⑥ HL7 Service (:8084)   ← 无其他微服务依赖
├── ⑦ Sample Service (:8087)← 可能依赖User(校验操作人)
├── ⑧ Report Service (:8088)← 依赖User(审核人)+AI(诊断集成)
└── ⑨ Gateway (:8080)       ← 最后启动 (路由到以上所有服务)

Step 3: 前端层
└── ⑩ Frontend (:3000)     ← 最后启动 (通过Gateway访问后端)
```

### 4.2 一键启动脚本 (Windows)

创建文件 `start-all-services.bat`:
```batch
@echo off
echo ========================================
echo   实验室管理系统(LIS) v1.4.2 一键启动脚本
echo ========================================

:: Step 0: 检查Java环境
java -version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Java未安装或未配置PATH!
    pause
    exit /b 1
)
echo [OK] Java环境检查通过

:: Step 1: 启动基础设施
echo.
echo [Step 1/3] 启动基础设施...
echo [1/3] 检查MySQL...
mysqladmin -u root -p1234 ping >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] MySQL正在运行
) else (
    echo [WARN] MySQL可能未启动,请手动确认!
)

echo [2/3] 检查Redis...
redis-cli ping >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Redis正在运行
) else (
    echo [WARN] Redis可能未启动,请手动确认!
)

echo [3/3] 启动Nacos...
start "Nacos" /MIN cmd /c "cd d:\middleware\nacos\nacos\bin && startup.cmd -m standalone"
echo [INFO] Nacos正在启动,等待30秒...
timeout /t 30 /nobreak >nul
echo [OK] Nacos应已启动 (访问 http://localhost:8848/nacos 确认)

:: Step 2: 启动微服务
echo.
echo [Step 2/3] 启动微服务...
set JAVA_OPTS=-Xms512m -Xmx1024m

start "User-Service" /MIN cmd /c "cd d:\FinalCodeAndFile\lab-management-system && java -jar lab-user-service\target\lab-user-service-1.0.0.jar"
echo [1/6] User Service 启动中... (端口8086)
timeout /t 8 /nobreak >nul

start "AI-Service" /MIN cmd /c "cd d:\FinalCodeAndFile\lab-management-system && java -jar lab-ai-service\target\lab-ai-service-1.0.0.jar"
echo [2/6] AI Service 启动中... (端口8085)
timeout /t 8 /nobreak >nul

start "HL7-Service" /MIN cmd /c "cd d:\FinalCodeAndFile\lab-management-system && java -jar lab-hl7-service\target\lab-hl7-service-1.0.0.jar"
echo [3/6] HL7 Service 启动中... (端口8084)
timeout /t 8 /nobreak >nul

start "Sample-Service" /MIN cmd /c "cd d:\FinalCodeAndFile\lab-management-system && java -jar lab-sample-service\target\lab-sample-service-1.0.0.jar"
echo [4/6] Sample Service 启动中... (端口8087)
timeout /t 8 /nobreak >nul

start "Report-Service" /MIN cmd /c "cd d:\FinalCodeAndFile\lab-management-system && java -jar lab-report-service\target\lab-report-service-1.0.0.jar"
echo [5/6] Report Service 启动中... (端口8088)
timeout /t 8 /nobreak >nul

start "Gateway" /MIN cmd /c "cd d:\FinalCodeAndFile\lab-management-system && java -jar lab-gateway\target\lab-gateway-1.0.0.jar"
echo [6/6] Gateway 启动中... (端口8080)
timeout /t 10 /nobreak >nul

:: Step 3: 启动前端
echo.
echo [Step 3/3] 启动前端...
start "Frontend" cmd /c "cd d:\FinalCodeAndFile\lab-management-system\frontend && npm run dev"
echo [INFO] Frontend启动中... (端口3000或5173)
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo   ✅ 所有服务启动完成!
echo ========================================
echo.
echo 访问地址:
echo   前端应用: http://localhost:3000 (或 http://localhost:5173)
echo   API网关: http://localhost:8080
echo   Nacos控制台: http://localhost:8848/nacos (nacos/nacos)
echo.
echo 测试账号:
echo   管理员: admin / admin123
echo   医生: doctor1 / doctor123
echo   检验师: labtech1 / lab123
echo.
pause
```

**使用方法**: 双击 `start-all-services.bat` 即可一键启动全部服务!

### 4.3 手动分步启动 (详细版)

#### Step 1: 启动基础设施

```powershell
# 1.1 确保MySQL运行
# Windows服务方式:
net start MySQL80
# 或手动启动MySQL服务

# 1.2 确保Redis运行
# Docker方式:
docker start redis
# 或WSL2方式:
wsl sudo service redis-server start

# 1.3 启动Nacos
cd D:\middleware\nacos\nacos\bin
startup.cmd -m standalone
# 等待30秒...
# 验证: 浏览器访问 http://localhost:8848/nacos
```

#### Step 2: 启动微服务 (新开6个终端窗口)

**终端1 - User Service**:
```powershell
cd d:\FinalCodeAndFile\lab-management-system
java -jar lab-user-service\target\lab-user-service-1.0.0.jar
# 观察日志输出,直到看到"Started UserServiceApplication"
```

**终端2 - AI Service**:
```powershell
cd d:\FinalCodeAndFile\lab-management-system
java -jar lab-ai-service\target\lab-ai-service-1.0.0.jar
```

**终端3 - HL7 Service**:
```powershell
cd d:\FinalCodeAndFile\lab-management-system
java -jar lab-hl7-service\target\lab-hl7-service-1.0.0.jar
```

**终端4 - Sample Service**:
```powershell
cd d:\FinalCodeAndFile\lab-management-system
java -jar lab-sample-service\target\lab-sample-service-1.0.0.jar
```

**终端5 - Report Service**:
```powershell
cd d:\FinalCodeAndFile\lab-management-system
java -jar lab-report-service\target\lab-report-service-1.0.0.jar
```

**终端6 - Gateway**:
```powershell
cd d:\FinalCodeAndFile\lab-management-system
java -jar lab-gateway\target\lab-gateway-1.0.0.jar
```

#### Step 3: 启动前端

**终端7 - Frontend**:
```powershell
cd d:\FinalCodeAndFile\lab-management-system\frontend
npm run dev
# 输出:
#   VITE v5.2.5  ready in XXX ms
#   ➜  Local:   http://localhost:3000/
#   ➜  Network: use --host to expose
```

### 4.4 JVM参数调优 (可选)

对于生产环境或内存受限环境,可调整JVM参数:

```bash
# 基础参数 (每个服务通用)
java -Xms512m          # 初始堆内存512MB
     -Xmx1024m         # 最大堆内存1024MB
     -XX:+UseG1GC      # 使用G1垃圾收集器 (JDK 9+默认,性能优秀)
     -XX:MaxGCPauseMillis=200  # GC最大停顿200ms
     -Dfile.encoding=UTF-8     # 文件编码UTF-8
     -Duser.timezone=Asia/Shanghai  # 时区设置
     -jar xxx.jar

# 示例: 启动User Service (优化参数)
java -Xms512m -Xmx1024m -XX:+UseG1GC -XX:MaxGCPauseMillis=200 ^
   -Dfile.encoding=UTF-8 -Duser.timezone=Asia/Shanghai ^
   -jar lab-user-service\target\lab-user-service-1.0.0.jar
```

---

## 5. 配置说明

### 5.1 后端核心配置项

每个微服务的配置文件位于: `{module}/src/main/resources/application.yml`

#### 数据库配置 (所有服务相同):

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/lab_management?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
    username: root              # ⚠️ 生产环境改用专用账户
    password: 1234             # ⚠️ 生产环境必须使用强密码!
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 10     # 连接池最大连接数
      minimum-idle: 5           # 最小空闲连接
      connection-timeout: 30000 # 连接超时30s
      idle-timeout: 600000      # 空闲超时10分钟
      max-lifetime: 1800000     # 连接最大存活30分钟
```

#### Redis配置:

```yaml
spring:
  redis:
    host: localhost
    port: 6379
    password:                # ⚠️ 生产环境必须设置密码!
    database: 0               # Redis数据库索引(默认0)
    lettuce:                  # Lettuce连接池配置
      pool:
        max-active: 8         # 最大连接数
        max-idle: 8           # 最大空闲连接
        min-idle: 0           # 最小空闲连接
        max-wait: -1ms        # 连接等待时间(-1表示无限)
```

#### Nacos注册中心配置:

```yaml
spring:
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848  # Nacos地址
        namespace: public            # 命名空间
        group: DEFAULT_GROUP         # 分组
      config:
        server-addr: localhost:8848  # 配置中心地址(可选)
        enabled: false               # 本项目未使用Nacos配置中心
```

#### 日志配置:

```yaml
logging:
  level:
    root: INFO                    # 全局日志级别
    com.sunyaxin: DEBUG            # 项目包日志级别(开发DEBUG,生产INFO)
    org.springframework.cloud.gateway: DEBUG  # Gateway日志(排障时开启)
  file:
    name: logs/${spring.application.name}.log  # 日志文件路径
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"
```

### 5.2 前端环境变量配置

文件: `frontend/.env.development`
```env
# API基础地址 (代理到Gateway)
VITE_API_BASE_URL=http://localhost:8080/api

# 应用标题
VITE_APP_TITLE=实验室管理系统 LIS v1.4.2

# 是否启用Mock数据 (true=使用模拟数据, false=调用真实API)
VITE_USE_MOCK_DATA=false

# 开发服务器端口
VITE_DEV_PORT=3000
```

文件: `frontend/.env.production`
```env
# 生产环境API地址 (部署时改为实际域名/IP)
VITE_API_BASE_URL=/api

# 应用标题
VITE_APP_TITLE=实验室管理系统

# 生产环境禁用Mock
VITE_USE_MOCK_DATA=false
```

### 5.3 Gateway路由配置详解

文件: `lab-gateway/src/main/resources/application.yml`
```yaml
spring:
  cloud:
    gateway:
      routes:
        # 用户服务路由
        - id: user-service
          uri: lb://lab-user-service    #负载均衡到user-service实例
          predicates:
            - Path=/api/user/**          #匹配所有/api/user/开头的请求
          filters:
            - StripPrefix=1              #去掉第一级路径(api),转发到/user/**

        # 标本服务路由
        - id: sample-service
          uri: lb://lab-sample-service
          predicates:
            - Path=/api/sample/**
          filters:
            - StripPrefix=1

        # 报告服务路由
        - id: report-service
          uri: lb://lab-report-service
          predicates:
            - Path=/api/report/**
          filters:
            - StripPrefix=1

        # AI服务路由
        - id: ai-service
          uri: lb://lab-ai-service
          predicates:
            - Path=/api/ai/**
          filters:
            - StripPrefix=1

        # HL7服务路由
        - id: hl7-service
          uri: lb://lab-hl7-service
          predicates:
            - Path=/api/hl7/**
          filters:
            - StripPrefix=1

      # 全局CORS配置 (⚠️ 生产环境应收紧!)
      globalcors:
        cors-configurations:
          '[/**]':
            allowedOriginPatterns: "*"     # 允许所有来源 (仅开发环境!)
            allowedMethods: "*"
            allowedHeaders: "*"
            allowCredentials: true
            maxAge: 3600
```

**路由转发示例**:
```
客户端请求: GET http://localhost:8080/api/user/list
                    │
                    ▼ (Gateway匹配 /api/user/** 路由)
去除前缀 /api → /user/list
                    │
                    ▼ (转发到 lab-user-service)
http://localhost:8086/user/list
                    │
                    ▼ (User Service处理)
响应: {"code":200,"data":[...],"success":true}
```

---

## 6. 验证部署

### 6.1 基础设施验证

```powershell
# 1. MySQL验证
mysql -u root -p1234 -e "SELECT 1;"
# 应输出: 1

# 2. Redis验证
redis-cli ping
# 应输出: PONG

# 3. Nacos验证
# 浏览器访问: http://localhost:8848/nacos
# 登录: nacos / nacos
# 左侧菜单 → 服务管理 → 服务列表
# 应看到6个服务: lab-gateway, lab-user-service, lab-sample-service, lab-report-service, lab-ai-service, lab-hl7-service
```

### 6.2 微服务健康检查

```powershell
# 通过Gateway Actuator检查 (需Spring Boot Actuator依赖)
Invoke-RestMethod -Uri "http://localhost:8080/actuator/health" -Method Get
# 应返回: {"status":"UP"}

# 直接检查各服务 (可选)
Invoke-RestMethod -Uri "http://localhost:8086/actuator/health"
Invoke-RestMethod -Uri "http://localhost:8087/actuator/health"
# ... 所有服务都应返回 status: UP
```

### 6.3 API功能验证 (快速冒烟测试)

```powershell
# 使用PowerShell或Postman执行以下测试:

# 1. 用户登录 (应该成功)
$body = @{username="admin";password="admin123"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/api/user/login" -Method Post -Body $body -ContentType "application/json"
# 应返回: code=200, data包含token和用户信息

# 2. 获取标本列表 (应该成功)
Invoke-RestMethod -Uri "http://localhost:8080/api/sample/list" -Method Get
# 应返回: code=200, data.records包含标本数组

# 3. 获取报告列表 (应该成功)
Invoke-RestMethod -Uri "http://localhost:8080/api/report/list" -Method Get
# 应返回: code=200, data.records包含报告数组

# 4. AI健康检查 (应该成功)
Invoke-RestMethod -Uri "http://localhost:8080/api/ai/health" -Method Get
# 应返回: code=200, data包含AI服务状态

# 5. HL7解析测试 (应该成功)
$hl7Body = @"MSH|^~&|LABADT|APP|LAB|202604031200||ORM^O01|P|2.3||||CHN"
Invoke-RestMethod -Uri "http://localhost:8080/api/hl7/parse" -Method Post -Body $hl7Body -ContentType "text/plain"
# 应返回: code=200, data包含解析后的结构化数据
```

### 6.4 前端页面验证

```bash
# 1. 浏览器访问前端
open http://localhost:3000
# 或 start http://localhost:3000

# 2. 应看到登录页面

# 3. 使用测试账号登录:
#    用户名: admin
#    密码: admin123

# 4. 登录成功后应自动跳转到仪表盘(Dashboard)页面

# 5. 验证左侧菜单各项:
#    ✅ 仪表盘首页 - 统计卡片+图表
#    ✅ 标本管理 - 列表+创建按钮
#    ✅ 报告管理 - 列表+创建按钮
#    ✅ AI辅助诊断 - 血常规/尿常规标签页
#    ✅ 用户管理 - 列表+搜索
#    ✅ 系统监控 - 服务状态(可能有硬编码数据)
```

### 6.5 E2E自动化验证 (完整流程)

如果已配置Playwright E2E测试:
```bash
cd frontend

# 运行E2E测试套件
npx playwright test tests/e2e/full-lab-flow.spec.cjs

# 预期结果: 9/9 PASS (100%)
# 测试覆盖: 登录→仪表盘→标本→报告→AI诊断→用户管理→性能→响应式→全流程
```

---

## 7. 常见问题排查

### 7.1 服务启动失败

#### 问题1: 端口被占用

**症状**: `Address already in use: bind [::]:8080`

**解决方案**:
```powershell
# 查找占用端口的进程
netstat -ano | findstr :8080

# 输出示例:
#   TCP    0.0.0.0:8080    0.0.0.0:0    LISTENING       12345

# 结束该进程 (PID=12345)
taskkill /F /PID 12345

# 或者修改该服务的端口 (如改为8081):
# 编辑 application.yml: server.port: 8081
```

#### 问题2: 无法连接到Nacos

**症状**: `Failed to connect to Nacos server` 或 `connect timed out`

**排查步骤**:
```powershell
# 1. 检查Nacos是否启动
curl http://localhost:8848/nacos/v1/console/health/liveness
# 应返回: {"code":200,...}

# 2. 检查Nacos端口是否正确 (默认8848)
netstat -an | findstr :8848

# 3. 检查防火墙是否阻止
# Windows Defender → 允许Java通过防火墙

# 4. 查看服务日志中的Nacos相关错误
# 日志通常在: logs/{service-name}.log
# 搜索关键字: "nacos" 或 "connect"
```

**常见原因及解决**:
| 原因 | 解决方案 |
|------|---------|
| Nacos未启动 | 先启动Nacos (`startup.cmd -m standalone`) |
| Nacos端口错误 | 检查application.yml中的`spring.cloud.nacos.discovery.server-addr` |
| 网络不通 | 检查localhost能否ping通,防火墙设置 |
| Nacos版本不兼容 | 确保使用2.2.3版本 (本项目测试通过) |

#### 问题3: 数据库连接失败

**症状**: `Could not create connection to database` 或 `Access denied for user 'root'@'localhost'`

**解决方案**:
```powershell
# 1. 验证MySQL是否运行
mysqladmin -u root -p1234 ping

# 2. 验证数据库是否存在
mysql -u root -p1234 -e "SHOW DATABASES LIKE 'lab_management';"

# 3. 检查连接字符串 (application.yml)
#    url: jdbc:mysql://localhost:3306/lab_management?...
#    username: root
#    password: 1234  (确保与实际密码一致)

# 4. 检查MySQL用户权限
mysql -u root -p
> GRANT ALL ON lab_management.* TO 'root'@'localhost';
> FLUSH PRIVILEGES;

# 5. 如果是首次运行,确保已执行初始化SQL
mysql -u root -p1234 lab_management < sql/init-tables.sql
```

#### 问题4: Redis连接失败

**症状**: `Unable to connect to Redis` 或 `Connection refused`

**解决方案**:
```powershell
# 1. 验证Redis是否运行
redis-cli ping
# 应返回: PONG

# 2. 检查Redis端口
netstat -an | findstr :6379

# 3. 如果使用Docker,检查容器状态
docker ps -a | findstr redis
# 如果未运行: docker start redis

# 4. 检查Redis密码配置 (如有)
redis-cli -a your_password ping
```

#### 问题5: Bean创建失败 (循环依赖等)

**症状**: `Error creating bean with name 'xxx': Requested bean is currently in creation`

**解决方案**:
- 通常是由于构造器注入导致的循环依赖
- 尝试使用`@Lazy`注解延迟加载
- 或使用`@Autowired`字段注入替代构造器注入
- 查看具体报错的Bean名称,针对性修复

### 7.2 API调用异常

#### 问题6: API返回404 Not Found

**可能原因**:
1. Gateway路由未配置该路径
2. 微服务未正常启动或未注册到Nacos
3. URL路径拼写错误

**排查步骤**:
```powershell
# 1. 检查Gateway路由配置
# 文件: lab-gateway/src/main/resources/application.yml
# 确认是否有对应的routes配置

# 2. 检查Nacos服务列表
# 访问: http://localhost:8848/nacos
# 左侧 → 服务管理 → 服务列表
# 确认目标服务是否显示"UP"状态

# 3. 检查URL路径
# 正确示例: http://localhost:8080/api/user/login
# 错误示例: http://localhost:8080/user/login (缺少/api/)
#             http://localhost:8080/api/User/Login (大小写敏感!)
```

#### 问题7: API返回500 Internal Server Error

**可能原因**:
1. 后端代码异常 (NullPointerException, SQLException等)
2. 数据库表/字段不存在
3. 参数校验失败 (@Validated触发)
4. 业务逻辑错误

**排查步骤**:
```powershell
# 1. 查看后端服务日志 (最重要!!!)
# 日志文件位置: {service}/logs/{service-name}.log
# 或查看启动该服务的终端窗口输出的红色错误堆栈

# 2. 常见的500错误及对应修复:
#
# a) java.lang.NullPointerException
#    → 检查是否对null值进行了操作 (如user.getUsername()当user为null)
#    → 修复: 添加null检查
#
# b) SQLSyntaxErrorException: Table 'xxx' doesn't exist
#    → 数据库表未创建,执行初始化SQL: mysql -u root -p < sql/init-tables.sql
#
# c) DataIntegrityViolationException: Column 'xxx' cannot be null
#    → 插入数据时必填字段为空
#    → 检查实体类@NotNull注解和前端传参
#
# d) MethodArgumentNotValidException
#    → 参数校验失败 (@Valid/@NotBlank等)
#    → 检查前端传递的参数是否符合校验规则
```

#### 问题8: CORS跨域错误

**浏览器Console错误**: `Access-Control-Allow-Origin header is not present`

**解决方案**:
```yaml
# Gateway的application.yml中已配置全局CORS (当前为*允许所有来源)
# 如果仍有问题,可能是:
# 1. 前端请求未经过Gateway (直接访问微服务端口)
#    → 确保前端API_BASE_URL指向Gateway (http://localhost:8080/api)
#    → 而非直接指向微服务 (http://localhost:8086)
#
# 2. Gateway CORS配置未生效
#    → 重启Gateway服务
#
# 3. 浏览器插件干扰
#    → 禁用可能影响CORS的浏览器扩展 (如某些广告拦截器)
```

### 7.3 前端问题

#### 问题9: 页面空白或白屏

**可能原因**:
1. Vite dev server未启动或崩溃
2. JavaScript运行时错误
3. API请求失败导致渲染中断

**排查步骤**:
```bash
# 1. 检查Vite终端是否有报错
#    查看 npm run dev 的输出窗口

# 2. 打开浏览器开发者工具 (F12)
#    Console标签: 查看红色错误信息
#    Network标签: 查看哪些请求失败 (红色的)

# 3. 检查浏览器地址是否正确
#    开发环境: http://localhost:3000 或 http://localhost:5173
#    不是: http://localhost:3000/index.html (SPA不应带.html后缀)

# 4. 清除缓存强制刷新
#    Chrome: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)
```

#### 问题10: 登录后无法跳转或Token无效

**可能原因**:
1. 后端login接口返回的数据格式不符合前端预期
2. Token存储失败 (localStorage可能被禁用)
3. 跨域Cookie问题 (虽然本项目主要用localStorage存储token)

**排查步骤**:
```javascript
// 1. 在浏览器Console中检查:
console.log(localStorage.getItem('token'))
// 应该有值 (如果不是null或undefined)

// 2. 检查Network标签中的login请求响应:
// Response应为: {code:200, data:{token:"xxx", user:{...}}, success:true}

// 3. 如果token存在但仍被拦截:
//    检查前端request.ts中的拦截器逻辑
//    确认Authorization头是否正确附加
```

### 7.4 性能问题

#### 问题11: 页面加载缓慢 (>3秒)

**优化建议**:
```javascript
// 1. 检查Network标签 (F12 → Network)
//    勾选 Disable cache
//    刷新页面,查看哪些资源加载慢

// 2. 常见慢资源及优化:
//    a) vendor.js过大 (Vue+Element+ECharts打包在一起)
//       → Vite已做代码分割,但可进一步优化动态导入
//
//    b) API请求响应慢
//       → 检查后端日志,优化慢查询SQL
//       → 添加Redis缓存
//
//    c) 图片/字体文件大
//       → 压缩图片,使用WebP格式
//       → 字体子集化 (只保留使用的字符)

// 3. 启用Gzip压缩 (生产环境Nginx配置)
// nginx.conf:
// gzip on;
// gzip_types text/plain text/css application/json application/javascript;
```

#### 问题12: 内存占用过高 (96%+)

**当前状况**: 开发环境下内存占用96%属正常 (IDE+多个JVM进程+浏览器)

**优化方向**:
```bash
# 1. 减少JVM堆内存分配 (如果不需要太多)
#    -Xmx512m (而非1024m) 对开发环境足够

# 2. 关闭不必要的应用程序
#    IDE (IntelliJ IDEA) 占用大量内存 (~1-2GB)
#    浏览器 (Chrome) 多个标签页也会占用不少

# 3. 定期重启服务 (开发阶段每天重启1-2次正常)

# 4. 生产环境优化:
#    - 使用JVM调优参数 (-XX:+UseG1GC -Xmx2g ...)
#    - 监控GC日志,分析内存泄漏
#    - 考虑容器化部署 (Docker限制内存上限)
```

---

## 8. 停止与卸载

### 8.1 停止服务

#### 方式1: 关闭所有终端窗口 (最简单)

直接关闭所有运行Java服务和npm dev server的终端窗口即可。

#### 方式2: 使用脚本批量停止

创建 `stop-all-services.bat`:
```batch
@echo off
echo 正在停止所有服务...

:: 停止所有Java进程 (谨慎!会停止所有Java程序)
taskkill /F /IM java.exe

:: 停止Node.js前端进程 (可选,根据端口查找)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do taskkill /F /PID %%a

echo 所有服务已停止。
pause
```

#### 方式3: 逐个停止 (推荐,更安全)

```powershell
# 1. 停止前端 (Ctrl+C 在前端终端)
# 或查找并结束node进程:
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# 2. 停止各微服务 (Ctrl+C 在各服务终端, 或按顺序:)
# Gateway → Report → Sample → HL7 → AI → User

# 3. 可选: 停止Nacos (如果不常驻)
# 在Nacos终端 Ctrl+C, 或:
taskkill /F /IM java.exe /FI "WINDOWTITLE eq *nacos*"

# 4. 可选: 停止Redis (如果不常驻)
# Docker: docker stop redis
# WSL: wsl sudo service redis-server stop
```

### 8.2 完全卸载 (清理环境)

> ⚠️ **警告**: 以下操作会删除所有数据和配置! 仅在确定不再需要时执行!

```bash
# 1. 停止所有服务 (参考8.1节)

# 2. 删除构建产物
Remove-Item -Recurse -Force d:\FinalCodeAndFile\lab-management-system\target
Remove-Item -Recurse -Force d:\FinalCodeAndFile\lab-management-system\frontend\dist
Remove-Item -Recurse -Force d:\FinalCodeAndFile\lab-management-system\frontend\node_modules

# 3. 删除Maven本地仓库中的本项目依赖 (可选,释放磁盘空间)
#    路径: ~/.m2/repository/com/sunyaxin/
Remove-Item -Recurse -Force $HOME\.m2\repository\com\sunyaxin

# 4. 删除数据库 (⚠️ 会丢失所有数据!)
mysql -u root -p -e "DROP DATABASE IF EXISTS lab_management;"

# 5. 删除Nacos数据 (可选)
Remove-Item -Recurse -Force D:\middleware\nacos\data
Remove-Item -Recurse -Force D:\middleware\nacos\logs

# 6. (可选) 卸载软件本身
#    - JDK, Maven, Node.js, MySQL, Redis, Nacos 等
#    按照各自官方卸载指南操作
```

---

## 附录A: 快速启动清单 (Checklist)

```
✅ 首次部署快速检查清单

[ ] 1. 环境准备
    [ ] JDK 17 已安装 (java -version)
    [ ] Maven 3.8+ 已安装 (mvn -v)
    [ ] Node.js 18 已安装 (node -v)
    [ ] MySQL 8 已安装并启动 (mysql --version)
    [ ] Redis 已启动 (redis-cli ping → PONG)
    [ ] Nacos 已下载

[ ] 2. 项目构建
    [ ] 源代码已获取 (cd project-dir)
    [ ] 后端编译成功 (mvn compile 无错误)
    [ ] 后端打包成功 (mvn package -DskipTests, 生成6个jar)
    [ ] 数据库已初始化 (mysql导入init-tables.sql, 15+张表)
    [ ] 前端依赖已安装 (cd frontend && npm install)
    [ ] 前端构建成功 (npm run build, 生成dist/)

[ ] 3. 服务启动 (按顺序!)
    [ ] ① MySQL 运行中 (端口3306)
    [ ] ② Redis 运行中 (端口6379)
    [ ] ③ Nacos 运行中 (端口8848, 访问http://localhost:8848/nacos)
    [ ] ④ User Service 启动 (端口8086, 日志无ERROR)
    [ ] ⑤ AI Service 启动 (端口8085)
    [ ] ⑥ HL7 Service 启动 (端口8084)
    [ ] ⑦ Sample Service 启动 (端口8087)
    [ ] ⑧ Report Service 启动 (端口8088)
    [ ] ⑨ Gateway 启动 (端口8080)
    [ ] ⑩ Frontend 启动 (端口3000/5173)

[ ] 4. 功能验证
    [ ] 浏览器打开 http://localhost:3000 → 看到登录页
    [ ] admin/admin123 登录成功 → 跳转Dashboard
    [ ] 各菜单页面可访问且数据显示正常
    [ ] API测试: /api/user/login, /api/sample/list 等返回200

🎉 全部完成! 系统已成功部署并可使用!
```

---

## 附录B: 生产环境部署注意事项 (重要!)

> ⚠️ **当前版本(v1.4.2)不建议直接部署到公网生产环境!**
> 如需生产部署,必须先完成以下安全加固工作:

### 必须完成的安全加固项:

| 序号 | 加固项 | 当前状态 | 工作量估计 | 优先级 |
|------|--------|---------|-----------|--------|
| 1 | **实施JWT认证体系** | ❌ 未实施 | 3-5天 | P0-致命 |
| 2 | **CSRF防护配置** | ❌ 未实施 | 0.5-1天 | P0-致命 |
| 3 | **API限流(Rate Limiting)** | ❌ 未配置 | 1-2天 | P0-高 |
| 4 | **HTTPS/SSL加密传输** | ❌ HTTP明文 | 1天 | P0-高 |
| 5 | **强密码策略** | ⚠️ 弱口令可登录 | 0.5天 | P0-高 |
| 6 | **数据库连接安全** | ⚠️ 弱密码/明文 | 0.5天 | P1-中 |
| 7 | **CORS域名白名单** | ⚠️ 允许*所有来源 | 0.25天 | P1-中 |
| 8 | **安全响应头配置** | ❌ 未配置 | 0.5天 | P1-中 |

**预计总工作量**: 7-11天 (建议独立安全加固项目)

### 生产环境架构建议:

```
                    ┌─────────────────┐
                    │   Load Balancer │  (Nginx/ALB)
                    │   (SSL终止)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌────────────┐ ┌────────────┐ ┌────────────┐
       │ Firewall   │ │ WAF         │ │ IDS/IPS    │
       └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                 ┌─────────────────────┐
                 │   Gateway Cluster   │  (多节点高可用)
                 │   (JWT Auth Filter) │
                 └──────────┬──────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐       ┌───────────┐       ┌─────────┐
   │ K8s Pod  │       │ K8s Pod   │       │ K8s Pod  │
   │ ×3 User │       │ ×3 Sample│       │ ×3 Other│
   └────┬────┘       └─────┬─────┘       └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
              ┌────────────────────────┐
              │   Redis Cluster ×3   │
              │   MySQL Master-Slave │
              │   Nacos Cluster ×3   │
              └────────────────────────┘
```

---

**文档编制**: DevOps Engineer AI  
**最后更新**: 2026-04-03 01:30 CST  
**适用版本**: v1.4.2 Final  
**测试环境**: Windows 11 (22H2) + JDK 17.0.11 + Node.js 18.x  

*© 2026 实验室管理系统项目组 - 验收交付文档包 V1.4.2*
