# 实验室管理系统(LIS) v1.3.0 - 部署指南

## 文档信息

| 项目 | 内容 |
|------|------|
| **文档编号** | DEPLOYMENT-GUIDE-V1.3.0 |
| **适用版本** | v1.3.0 (验收发布版) |
| **部署环境** | Windows 11 / Linux (Ubuntu 22.04+) |
| **难度等级** | 中等 (需要Java/Node.js/MySQL基础) |
| **预计耗时** | 30-60分钟 (首次部署) |

---

## 目录

- [6.1 环境要求](#61-环境要求)
- [6.2 安装步骤](#62-安装步骤)
- [6.3 服务启动顺序](#63-服务启动顺序)
- [6.4 前端启动](#64-前端启动)
- [6.5 验证方法](#65-验证方法)
- [6.6 常见问题排查(Troubleshooting)](#66-常见问题排查troubleshooting)
- [6.7 配置参考](#67-配置参考)

---

## 6.1 环境要求

### 6.1.1 硬件要求

| 组件 | 最低配置 | 推荐配置 | 说明 |
|------|----------|----------|------|
| CPU | 4核心 | 8核心+ | 微服务较多，建议多核 |
| 内存 | 8GB RAM | 16GB RAM | 6个JVM进程 + MySQL + Redis |
| 硬盘 | 20GB可用空间 | 50GB SSD | 代码 + 数据库 + 日志 |
| 网络 | 本地回环/局域网 | 局域网/内网 | 服务间通信 |

### 6.1.2 软件要求

#### 必须安装的软件:

| 软件 | 版本要求 | 用途 | 下载地址 |
|------|----------|------|----------|
| **JDK** | 17 (LTS) | Java运行环境 | https://adoptium.net/ |
| **Maven** | 3.8+ | Java项目构建 | https://maven.apache.org/ |
| **MySQL** | 8.0+ | 关系型数据库 | https://dev.mysql.com/ |
| **Redis** | 6.x+ (Windows用3.x兼容版) | 缓存存储 | https://redis.io/ |
| **Node.js** | 18.x 或 20.x LTS | 前端运行时 | https://nodejs.org/ |
| **npm/pnpm** | 最新版 | 包管理器 | 随Node.js安装 |

#### 可选软件:

| 软件 | 用途 | 说明 |
|------|------|------|
| Nacos | 服务注册发现(可用内置单机模式) | 下载nacos-server-2.2.3.zip |
| Git | 版本控制 | 代码克隆 |
| Postman/curl | API测试 | 验证接口 |

### 6.1.3 版本验证命令

```bash
# JDK版本
java -version
# 预期输出: openjdk version "17.0.11" ...

# Maven版本
mvn -version
# 预期输出: Apache Maven 3.9.x ...

# Node.js版本
node -v
# 预期输出: v18.x.x 或 v20.x.x

# MySQL版本
mysql --version
# 预期输出: mysql Ver 8.x.x ...

# Redis版本
redis-cli --version
# 预期输出: redis-cli x.x.x ...
```

---

## 6.2 安装步骤

### 6.2.1 步骤1: 安装配置JDK 17

#### Windows系统:

1. 下载 Adoptium Eclipse Temurin JDK 17:
   - 访问: https://adoptium.net/
   - 选择 JDK 17, Windows, x64, .msi 安装包
   - 下载并运行安装程序

2. 配置环境变量:
```powershell
# 打开系统环境变量设置
# Win+R → sysdm.cpl → 高级 → 环境变量

# 新建系统变量 JAVA_HOME
变量名: JAVA_HOME
变量值: C:\Program Files\Eclipse Adoptium\jdk-17.0.11-hotspot

# 编辑 Path 变量, 添加:
%JAVA_HOME%\bin
```

3. 验证安装:
```powershell
java -version
javac -version
```

#### Linux系统 (Ubuntu):

```bash
# 安装 JDK 17
sudo apt update
sudo apt install openjdk-17-jdk -y

# 设置 JAVA_HOME
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# 验证
java -version
```

### 6.2.2 步骤2: 安装配置Maven

#### Windows系统:

1. 下载 Apache Maven 3.9.x:
   - 访问: https://maven.apache.org/download.cgi
   - 下载 `apache-maven-3.9.x-bin.zip`
   - 解压到 `C:\Tools\apache-maven-3.9.x`

2. 配置环境变量:
```powershell
# 新建系统变量 MAVEN_HOME
变量名: MAVEN_HOME
变量值: C:\Tools\apache-maven-3.9.x

# 编辑 Path 变量, 添加:
%MAVEN_HOME%\bin
```

3. 配置阿里云镜像加速 (推荐):
编辑 `%MAVEN_HOME%\conf\settings.xml`, 在 `<mirrors>` 节添加:
```xml
<mirror>
    <id>aliyunmaven</id>
    <mirrorOf>*</mirrorOf>
    <name>阿里云公共仓库</name>
    <url>https://maven.aliyun.com/repository/public</url>
</mirror>
```

4. 验证:
```powershell
mvn -version
```

### 6.2.3 步骤3: 安装配置MySQL 8

#### Windows系统:

1. 下载 MySQL Installer:
   - 访问: https://dev.mysql.com/downloads/installer/
   - 下载 `mysql-installer-community-x.x.x.msi`
   - 运行安装程序, 选择 "Server only"

2. 安装过程中设置:
```
Type and Networking: Development Computer
Authentication Method: Use Strong Password Encryption
Root Password: 请设置强密码! (记录下来)
Windows Service: 配置为自动启动
```

3. 创建数据库和用户:
```sql
-- 使用root登录
mysql -u root -p

-- 创建数据库
CREATE DATABASE lab_management DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建专用用户 (请替换密码!)
CREATE USER 'lab_user'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';
GRANT ALL PRIVILEGES ON lab_management.* TO 'lab_user'@'localhost';
FLUSH PRIVILEGES;
```

4. 初始化表结构:
```bash
# 进入项目SQL目录
cd d:\FinalCodeAndFile\lab-management-system\sql

# 按顺序执行初始化脚本
mysql -u lab_user -p lab_management < init.sql
mysql -u lab_user -p lab_management < init-tables.sql
mysql -u lab_user -p lab_management < init-simple.sql
```

5. 插入测试数据 (可选):
```bash
mysql -u lab_user -p lab_management < test-data-enhanced.sql
mysql -u lab_user -p lab_management < test-data-enhanced-report.sql
```

### 6.2.4 步骤4: 安装启动Redis

#### Windows系统 (使用Memurai或Redis Windows版):

**方案A: Memurai (推荐用于Windows)**

1. 下载 Memurai Developer Edition:
   - 访问: https://www.memurai.com/get-memurai
   - 下载并安装

2. 启动 Redis:
```powershell
memurai --service-start
# 或直接运行
memurai
```

**方案B: Redis for Windows (旧版但稳定)**

1. 下载 Redis 3.x Windows版:
   - GitHub搜索: `tporadowski/redis`
   - 下载 Release 包

2. 启动:
```powershell
cd redis目录
redis-server.exe redis.windows.conf
```

#### Linux系统:

```bash
# Ubuntu/Debian
sudo apt install redis-server -y
sudo systemctl start redis
sudo systemctl enable redis

# 验证
redis-cli ping
# 预期输出: PONG
```

### 6.2.5 步骤5: 部署Nacos服务注册中心

1. 下载 Nacos Server 2.2.3:
   - 访问: https://github.com/alibaba/nacos/releases
   - 下载 `nacos-server-2.2.3.zip`

2. 解压到目标目录 (如 `C:\Tools\nacos`)

3. 启动 Nacos (单机模式):
```powershell
cd C:\Tools\nacos\bin

# Windows 单机模式启动
startup.cmd -m standalone

# Linux/Mac
sh startup.sh -m standalone
```

4. 验证 Nacos:
   - 浏览器访问: http://localhost:8848/nacos
   - 默认账号: `nacos` / 密码: `nacos`
   - 进入"服务管理"→"服务列表", 应为空(服务尚未启动)

---

## 6.3 服务启动顺序

> ⚠️ **重要**: 必须严格按照以下顺序启动服务，否则会出现连接失败!

### 启动顺序图:

```
第1步: Nacos (8848) ──────┐
                           │
第2步: MySQL (3306) ───────┤── 基础设施层
                           │
第3步: Redis (6379) ───────┘
                           │
              ┌────────────▼────────────┐
              │   第4步: Gateway (8080)   │ ← 网关层
              └────────────┬────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
  第5步: 业务微服务 (并行启动)                    │
  ├─ User Service (8081)                        │
  ├─ Sample Service (8082)                      │
  ├─ Report Service (8083)                      │
  ├─ AI Service (8084)                          │
  └─ HL7 Service (8085)                         │
                           │
              ┌────────────▼────────────┐
              │  第6步: Frontend (5173)   │ ← 前端层
              └─────────────────────────┘
```

### 详细启动命令:

#### 第1步: 启动Nacos
```powershell
# 终端1
cd C:\Tools\nacos\bin
startup.cmd -m standalone
# 等待看到: "Nacos started successfully in stand alone mode"
```

#### 第2步: 确认MySQL运行
```powershell
# 如果MySQL是Windows服务,应已自动启动
# 手动检查:
net start mysql
# 或
sc query mysql
```

#### 第3步: 确认Redis运行
```powershell
# Windows Memurai
memurai --service-status

# 或手动启动
redis-server.exe
```

#### 第4步: 启动API网关
```powershell
# 终端2
cd d:\FinalCodeAndFile\lab-management-system\lab-gateway
mvn spring-boot:run
# 等待: Started GatewayApplication in x.xxx seconds
```

#### 第5步: 启动业务微服务 (每个新开一个终端)

```powershell
# 终端3 - User Service
cd d:\FinalCodeAndFile\lab-management-system\lab-user-service
mvn spring-boot:run

# 终端4 - Sample Service
cd d:\FinalCodeAndFile\lab-management-system\lab-sample-service
mvn spring-boot:run

# 终端5 - Report Service
cd d:\FinalCodeAndFile\lab-management-system\lab-report-service
mvn spring-boot:run

# 终端6 - AI Service
cd d:\FinalCodeAndFile\lab-management-system\lab-ai-service
mvn spring-boot:run

# 终端7 - HL7 Service (可选)
cd d:\FinalCodeAndFile\lab-management-system\lab-hl7-service
mvn spring-boot:run
```

> 💡 **提示**: 可以使用项目提供的批处理脚本一键启动:
> ```batch
> d:\FinalCodeAndFile\lab-management-system\scripts\start-all-services.bat
> ```

---

## 6.4 前端启动

### 6.4.1 安装前端依赖

```powershell
# 进入前端目录
cd d:\FinalCodeAndFile\lab-management-system\frontend

# 安装依赖 (首次需要)
npm install
# 或使用 pnpm (更快)
pnpm install
```

### 6.4.2 启动开发服务器

```powershell
# 终端8 (最后一个终端)
npm run dev
# 或
pnpm dev
```

预期输出:
```
  VITE v5.2.6  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### 6.4.3 访问前端应用

浏览器打开: **http://localhost:5173**

应该看到实验室管理系统的登录页面。

---

## 6.5 验证方法

### 6.5.1 基础设施验证

| 组件 | 验证方法 | 预期结果 |
|------|----------|----------|
| Nacos | 浏览器 http://localhost:8848/nacos | 登录页可打开, 用户名 nacos/nacos |
| MySQL | `mysql -u lab_user -p -e "SELECT 1"` | 连接成功 |
| Redis | `redis-cli ping` | 返回 PONG |

### 6.5.2 微服务验证

| 服务 | 验证命令/URL | 预期结果 |
|------|-------------|----------|
| Gateway | curl http://localhost:8080 | 返回404或错误页(正常,无匹配路由) |
| User Service | curl http://localhost:8081/api/user/list | 返回用户列表JSON |
| Sample Service | curl http://localhost:8082/api/sample/list | 返回标本列表JSON |
| Report Service | curl http://localhost:8083/api/report/list | 返回报告列表JSON |
| AI Service | curl http://localhost:8084/api/ai/reference-ranges | 返回参考范围JSON |
| Nacos服务列表 | http://localhost:8848/nacos → 服务列表 | 看到6个服务已注册 |

### 6.5.3 前端验证

| 验证项 | 操作 | 预期结果 |
|--------|------|----------|
| 页面加载 | 打开 http://localhost:5173 | 显示登录页面 |
| 登录功能 | 输入任意用户名密码点击登录 | ⚠️ 当前使用模拟数据,会跳转到仪表盘 |
| 导航菜单 | 点击左侧菜单各选项 | 各页面可切换显示 |
| 仪表盘 | 进入仪表盘页面 | 图表和数据展示(模拟数据) |

### 6.5.4 快速健康检查脚本

创建文件 `check-health.ps1` 并运行:

```powershell
$services = @(
    @{Name="Nacos"; Url="http://localhost:8848/nacos"; Port=8848},
    @{Name="Gateway"; Url="http://localhost:8080"; Port=8080},
    @{Name="User Service"; Url="http://localhost:8081/api/user/list"; Port=8081},
    @{Name="Sample Service"; Url="http://localhost:8082/api/sample/list"; Port=8082},
    @{Name="Report Service"; Url="http://localhost:8083/api/report/list"; Port=8083},
    @{Name="AI Service"; Url="http://localhost:8084/api/ai/reference-ranges"; Port=8084},
    @{Name="Frontend"; Url="http://localhost:5173"; Port=5173}
)

foreach ($svc in $services) {
    try {
        $response = Invoke-WebRequest -Uri $svc.Url -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ $($svc.Name) ($($svc.Port)) - HTTP $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($svc.Name) ($($svc.Port)) - $($_.Exception.Message)" -ForegroundColor Red
    }
}
```

---

## 6.6 常见问题排查 (Troubleshooting)

### 问题1: Nacos连接超时

**现象**:
```
com.alibaba.nacos.exception.NacosConnectException: 
Keep alive error, connection refused
```

**原因分析**:
- Nacos服务未启动
- Nacos端口被占用
- 防火墙阻止连接

**解决方案**:

```powershell
# 1. 确认Nacos是否正在运行
netstat -an | findstr "8848"
# 如果没有输出说明未启动

# 2. 启动Nacos
cd C:\Tools\nacos\bin
startup.cmd -m standalone

# 3. 检查端口占用
netstat -ano | findstr ":8848"
# 如果被其他进程占用(PID xxx), 可选择终止:
taskkill /PID xxx /F

# 4. 检查防火墙
# Windows Defender防火墙 → 允许应用通过防火墙 → 添加 java.exe
```

**预防措施**:
- 将Nacos设置为Windows服务开机自启
- 在Nacos配置中增加超时时间容忍度

---

### 问题2: MyBatis-Plus兼容性问题

**现象**:
```
java.lang.NoSuchMethodError: com.baomidou.mybatisplus.core.metadata.TableInfoHelper
```

或
```
Caused by: java.lang.ClassNotFoundException: 
com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor
```

**原因分析**:
- MyBatis Plus版本不兼容
- Maven依赖冲突
- 多个版本的mybatis-plus同时存在

**解决方案**:

```xml
<!-- 确保pom.xml中MyBatis Plus版本正确 -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.7</version>  <!-- Spring Boot 3.x 必须用此starter -->
</dependency>

<!-- 排除可能的冲突依赖 -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus</artifactId>
    <version>3.5.7</version>
    <exclusions>
        <exclusion>
            <groupId>org.mybatis</groupId>
            <artifactId>mybatis</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

**操作步骤**:
```powershell
# 1. 清理Maven缓存重新构建
cd d:\FinalCodeAndFile\lab-management-system
mvn clean install -DskipTests -U

# 2. 查看依赖树确认版本
mvn dependency:tree -Dincludes=com.baomidou

# 3. 如果仍有问题, 删除本地Maven仓库中的mybatis-plus后重试
# 删除路径: ~/.m2/repository/com/baomidou/
```

---

### 问题3: 端口被占用

**现象**:
```
Failed to start port 8080 (or 8081/8082...)
Address already in use: bind
```

**原因分析**:
- 上次运行的进程未完全退出
- 其他程序占用了相同端口
- 服务重复启动

**解决方案**:

```powershell
# 1. 查找占用指定端口的进程
# 例如查找8080端口
netstat -ano | findstr ":8080"

# 输出示例:
# TCP    0.0.0.0:8080    0.0.0.0:0    LISTENING    12345
#                                              ^^^^ 这是PID

# 2. 终止占用进程
taskkill /PID 12345 /F

# 3. 批量清理所有项目相关端口 (8080-8085, 5173, 8848)
$ports = @(8080, 8081, 8082, 8083, 8084, 8085, 5173, 8848, 3306, 6379)
foreach ($port in $ports) {
    $pid = (netstat -ano | findstr ":$port.*LISTENING") -replace '.*\s+(\d+)$','$1'
    if ($pid -and $pid -match '^\d+$') {
        Write-Host "终止端口 $port 的进程 PID=$pid"
        taskkill /PID $pid -F -ErrorAction SilentlyContinue
    }
}
```

**预防措施**:
- 每次开发结束后使用 `Ctrl+C` 正常关闭服务
- 使用 `start-all-services.bat` 脚本前先执行清理

---

### 问题4: 前端无法连接后端API

**现象**:
- 前端页面加载正常, 但所有数据为空或报错
- 浏览器控制台(F12)显示网络错误:
```
GET http://localhost:8080/api/user/list net::ERR_CONNECTION_REFUSED
```
或
```
Access-Control-Allow-Origin header is not present
```

**原因分析**:
- 后端服务未启动或未就绪
- API网关(Gateway)未启动
- CORS跨域配置问题
- 前端代理配置错误

**解决方案**:

**情况A: 后端服务未启动**
```powershell
# 按照第6.3节顺序启动所有后端服务
# 确认Gateway在8080端口运行
curl http://localhost:8080
```

**情况B: CORS跨域问题**
检查Gateway配置 (`lab-gateway/src/main/resources/application.yml`):
```yaml
spring:
  cloud:
    gateway:
      globalcors:
        cors-configurations:
          '[/**]':
            allowedOrigins: 
              - "http://localhost:5173"
              - "http://localhost:3000"
            allowedMethods: "*"
            allowedHeaders: "*"
            allowCredentials: true
```

**情况C: 前端Vite代理配置**
检查 `frontend/vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      // 确保代理规则正确
    },
    port: 5173,
  },
})
```

**情况D: 前端.env配置错误**
检查 `frontend/.env.development`:
```
VITE_API_BASE_URL=http://localhost:8080/api
VITE_APP_TITLE=实验室管理系统
```

---

### 问题5: Redis连接失败

**现象**:
```
RedisConnectionFailureException: Unable to connect to Redis; 
nested exception is io.lettuce.core.RedisConnectionException
```

**原因分析**:
- Redis服务未启动
- Redis端口(6379)不对
- Redis密码配置不匹配
- Windows防火墙阻止

**解决方案**:

```powershell
# 1. 确认Redis运行状态
redis-cli ping
# 预期输出: PONG

# 如果提示"Could not connect", 说明Redis未运行

# 2. 启动Redis (Windows Memurai)
memurai --service-start
# 或
redis-server.exe redis.windows.conf

# 3. 检查Redis配置与application.yml一致
# application.yml中的Redis配置:
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password:    # 空表示无密码
      database: 0

# 4. 如果设置了密码, 确认配置匹配
redis-cli -a your_password ping
```

**Windows特有问题**:
- Windows版Redis可能需要以管理员身份运行
- 检查Windows Defender是否拦截了Redis

---

### 问题6: 登录失败

**现象**:
- 输入正确的用户名密码后提示"密码错误"
- 或登录后立即跳转回登录页

**原因分析与解决方案**:

**情况A: BCrypt加密后的密码不匹配 (v1.3.0新问题)**

由于v1.3.0修复了DEF-C001引入BCrypt加密，如果数据库中有旧明文密码数据:

```sql
-- 解决方案1: 清空用户表重新注册
TRUNCATE TABLE user;
-- 然后通过注册页面创建新用户(新密码会自动BCrypt加密)

-- 解决方案2: 编写迁移脚本更新现有密码
-- 在MySQL中执行 (将明文password替换为BCrypt哈希):
UPDATE user SET password='$2a$10$xxxxxxxxxxxxx' WHERE username='admin';
```

**情况B: 前端使用模拟数据 (DEF-C002未修复)**

当前Login.vue使用setTimeout模拟登录，实际行为:
- 任何非空用户名密码都会"成功"
- 成功后写入localStorage模拟用户信息
- 不调用真实后端API

这是**已知缺陷DEF-C002**, 计划在v1.4.0修复。

**临时验证方法**:
```javascript
// 在浏览器控制台(F12)查看localStorage
console.log(localStorage.getItem('user'))
// 应该能看到模拟的用户信息
```

**情况C: 后端服务未启动**

确保User Service (8081) 和 Gateway (8080) 已按顺序启动。

---

### 问题7: Maven构建失败

**现象**:
```
[ERROR] COMPILATION ERROR : cannot find symbol
[ERROR] symbol: class BCryptPasswordEncoder
```

**解决方案**:

```xml
<!-- 确保pom.xml包含Spring Security Crypto依赖 -->
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-crypto</artifactId>
</dependency>

<!-- 注意: 仅引入crypto模块,不需要完整的Spring Security Web -->
```

然后重新构建:
```bash
mvn clean compile -U
```

---

### 问题8: npm/pnpm依赖安装失败

**现象**:
```
npm ERR! code ERESOLVE
npm ERR! Could not resolve dependencies
```

**解决方案**:

```powershell
# 方法1: 清除缓存重试
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# 方法2: 使用legacy peer deps
npm install --legacy-peer-deps

# 方法3: 使用pnpm (更快的包管理器)
npm install -g pnpm
pnpm install

# 方法4: 指定镜像源
npm config set registry https://registry.npmmirror.com
npm install
```

---

## 6.7 配置参考

### 6.7.1 核心配置项说明

#### Gateway配置 (application.yml)

```yaml
server:
  port: 8080

spring:
  application:
    name: lab-gateway
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848
    gateway:
      routes:
        # 用户服务路由
        - id: user-service
          uri: lb://lab-user-service
          predicates:
            - Path=/api/user/**
        # 标本服务路由
        - id: sample-service
          uri: lb://lab-sample-service
          predicates:
            - Path=/api/sample/**
        # 报告服务路由
        - id: report-service
          uri: lb://lab-report-service
          predicates:
            - Path=/api/report/**
        # AI服务路由
        - id: ai-service
          uri: lb://lab-ai-service
          predicates:
            - Path=/api/ai/**

# 关键配置项说明:
# server.port: 网关监听端口 (默认8080)
# nacos.server-addr: Nacos地址 (必须与Nacos实际地址一致)
# uri: lb:// 表示负载均衡 (需配合Nacos服务发现)
# Path: 路由匹配规则
```

#### User Service配置 (application.yml)

```yaml
server:
  port: 8081

spring:
  application:
    name: lab-user-service
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/lab_management?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai
    username: lab_user        # ⚠️ 生产环境不要硬编码!
    password: YourPassword    # ⚠️ 生产环境使用环境变量!

# 关键配置项说明:
# datasource.url: JDBC连接URL
#   - lab_management: 数据库名称
#   - useUnicode=true&characterEncoding=utf-8: UTF-8编码
#   - serverTimezone=Asia/Shanghai: 时区设置(重要!)
```

#### Redis配置 (通用)

```yaml
spring:
  data:
    redis:
      host: localhost     # Redis服务器地址
      port: 6379          # Redis端口
      password:           # 密码(空=无密码)
      database: 0         # Redis数据库编号(0-15)
      lettuce:
        pool:
          max-active: 8   # 最大连接数
          max-idle: 8     # 最大空闲连接
          min-idle: 0     # 最小空闲连接
```

### 6.7.2 环境变量方式配置 (生产推荐)

避免在YAML中硬编码敏感信息:

**Windows PowerShell**:
```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_NAME="lab_management"
$env:DB_USERNAME="lab_user"
$env:DB_PASSWORD="YourSecurePassword!"
$env:REDIS_HOST="localhost"
$env:REDIS_PORT="6379"
$env:NACOS_ADDR="localhost:8848"

# 然后启动服务
mvn spring-boot:run
```

**application.yml 引用环境变量**:
```yaml
spring:
  datasource:
    url: jdbc:mysql://${DB_HOST:localhost}:${DB_PORT:3306}/${DB_NAME:lab_management}
    username: ${DB_USERNAME:root}
    password: ${DB_PASSWORD:123456}
```

### 6.7.3 常用运维命令

```powershell
# 查看所有Java进程
jps -l

# 查看特定服务的日志
# User Service日志
Get-Content d:\FinalCodeAndFile\lab-management-system\lab-user-service\logs\user-service.log -Tail 50

# 实时查看日志
Get-Content path\to\log -Wait

# 查看服务注册状态
Invoke-RestMethod http://localhost:8848/nacos/v1/ns/instance/list?serviceName=lab-user-service

# 重启单个服务 (无需重启全部)
# 先找到PID, 然后 taskkill /PID xxx /F, 再重新 mvn spring-boot:run
```

---

## 附录: 一键启动脚本参考

项目提供了以下辅助脚本:

| 脚本 | 位置 | 用途 |
|------|------|------|
| `start-all-services.bat` | `scripts/` | 一键启动所有后端服务 |
| `run-e2e-tests.bat` | 项目根目录 | 运行E2E自动化测试 |
| `run-tests.bat` | `scripts/` | 运行单元测试 |

---

*文档编制: Project Manager AI Agent + DevOps Engineer AI Agent*  
*最后更新: 2026-04-02*  
*© 2026 实验室管理系统项目组*
