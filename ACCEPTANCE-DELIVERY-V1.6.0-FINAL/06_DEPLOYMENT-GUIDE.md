# 实验室管理系统 - 部署指南

**文档编号**: DEPLOY-GUIDE-v1.6.0
**适用版本**: v1.6.0 Final
**发布日期**: 2026-04-05
**文档类型**: 操作手册 (Operations Manual)
**目标读者**: 系统管理员、DevOps工程师、运维人员

---

## 📋 目录

- [1. 环境要求](#1-环境要求)
- [2. 安装准备](#2-安装准备)
- [3. 基础设施部署](#3-基础设施部署)
- [4. 应用服务部署](#4-应用服务部署)
- [5. 前端部署](#5-前端部署)
- [6. 服务启动与验证](#6-服务启动与验证)
- [7. 配置文件详解](#7-配置文件详解)
- [8. 健康检查与监控](#8-健康检查与监控)
- [9. 故障排查指南](#9-故障排查指南)
- [10. 备份恢复策略](#10-备份恢复策略)
- [11. 安全加固建议](#11-安全加固建议)
- [12. 日常运维检查清单](#12-日常运维检查清单)

---

## 1. 环境要求

### 1.1 硬件要求

#### 开发/测试环境（最低配置）

| 资源 | 最低配置 | 推荐配置 |
|------|----------|----------|
| **CPU** | 4核 | 8核 |
| **内存** | 8GB | 16GB |
| **硬盘** | 100GB SSD | 256GB SSD |
| **网络** | 100Mbps | 1Gbps |

#### 生产环境（推荐配置）

| 资源 | 最低配置 | 推荐配置 | 高可用配置 |
|------|----------|----------|-----------|
| **CPU** | 8核 | 16核 | 32核 (多节点) |
| **内存** | 16GB | 32GB | 64GB |
| **硬盘** | 500GB SSD | 1TB SSD | 2TB SSD + NAS |
| **网络** | 1Gbps | 10Gbps | 双网卡绑定 |

### 1.2 软件依赖

| 软件 | 版本要求 | 用途 | 必需性 |
|------|----------|------|--------|
| **JDK (Java Development Kit)** | 17.0+ (LTS) | 运行Spring Boot应用 | ✅ 必须 |
| **Node.js** | 18.x LTS | 构建和运行前端 | ✅ 必须 |
| **MySQL** | 8.0+ | 主数据库 | ✅ 必须 |
| **Redis** | 6.0+ (推荐7.0) | 缓存/会话存储 | ✅ 必须 |
| **Nacos** | 2.2.3+ | 注册中心/配置中心 | ✅ 必须 |
| **Maven** | 3.8+ | Java项目构建 | ✅ 构建时必须 |
| **npm/yarn** | 9.x / 1.22+ | 前端包管理 | ✅ 构建时必须 |
| **Git** | 2.x+ | 版本控制 | ✅ 必须 |
| **Nginx** (可选) | 1.24+ | 反向代理/静态资源 | ⚠️ 推荐 |
| **Docker** (可选) | 24.0+ | 容器化部署 | 🔵 可选 |

### 1.3 操作系统支持

| 操作系统 | 版本 | 支持级别 | 备注 |
|---------|------|----------|------|
| **CentOS / Rocky Linux** | 8.x, 9.x | ✅ 完全支持 | 生产推荐 |
| **Ubuntu Server** | 22.04 LTS, 24.04 LTS | ✅ 完全支持 | 生产推荐 |
| **Windows Server** | 2019, 2022 | ✅ 支持 | 开发测试用 |
| **macOS** | 13+ (Ventura+) | ⚠️ 仅开发 | 不用于生产 |

---

## 2. 安装准备

### 2.1 获取安装包

```bash
# 方式A: 从Git仓库克隆
git clone https://github.com/your-org/lab-management-system.git
cd lab-management-system
git checkout v1.6.0-final

# 方式B: 下载发布包 (如果提供)
wget https://releases.example.com/lab-management-v1.6.0-final.tar.gz
tar -xzf lab-management-v1.6.0-final.tar.gz
cd lab-management-v1.6.0-final
```

### 2.2 目录结构规划

```
/opt/lab-management/              # 系统根目录
├── app/                          # 应用程序目录
│   ├── gateway/                  # Gateway服务
│   ├── user-service/             # 用户服务
│   ├── sample-service/           # 标本服务
│   ├── report-service/           # 报告服务
│   ├── exam-service/             # 检查项目服务
│   └── ai-service/               # AI服务(可选)
├── frontend/                     # 前端构建产物
│   └── dist/                     # Vite构建输出
├── config/                       # 配置文件目录
│   ├── application-prod.yml      # 生产环境配置
│   ├── nacos/                    # Nacos配置
│   └── nginx/                    # Nginx配置
├── logs/                         # 日志目录
│   ├── gateway/
│   ├── user-service/
│   ├── sample-service/
│   └── ...
├── data/                         # 数据目录
│   ├── mysql/                    # MySQL数据文件
│   └── redis/                    # Redis数据文件
├── backup/                       # 备份目录
│   ├── database/                 # 数据库备份
│   └── config/                   # 配置备份
└── scripts/                      # 运维脚本
    ├── start-all.sh              # 一键启动
    ├── stop-all.sh               # 一键停止
    ├── health-check.sh           # 健康检查
    └── backup-database.sh        # 数据库备份
```

### 2.3 创建系统用户和权限

```bash
# 创建专用运行用户 (安全最佳实践)
sudo useradd -r -m -s /bin/bash labadmin
sudo passwd labadmin

# 创建目录结构
sudo mkdir -p /opt/lab-management/{app,frontend,config,logs,data,backup,scripts}
sudo chown -R labadmin:labadmin /opt/lab-management

# 设置权限
chmod 755 /opt/lab-management
chmod 700 /opt/lab-management/config  # 配置文件敏感，限制访问
```

---

## 3. 基础设施部署

### 3.1 MySQL 8.0 安装与配置

#### 安装MySQL (CentOS/Rocky)

```bash
# 添加MySQL官方YUM仓库
sudo yum localinstall https://dev.mysql.com/get/mysql80-community-release-el9-5.noarch.rpm

# 安装MySQL Server
sudo yum install mysql-community-server -y

# 启动并设置开机自启
sudo systemctl start mysqld
sudo systemctl enable mysqld

# 获取临时root密码
sudo grep 'temporary password' /var/log/mysqld.log
```

#### 初始化安全设置

```bash
# 运行安全配置脚本
sudo mysql_secure_installation

# 按提示操作:
# 1. 设置root密码 (强密码: 至少12位,大小写+数字+特殊字符)
# 2. 移除匿名用户: Y
# 3. 禁止root远程登录: Y (或按需)
# 4. 移除test数据库: Y
# 5. 重新加载权限表: Y
```

#### 创建应用数据库

```sql
-- 以root身份登录MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE lab_management_db 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- 创建应用用户 (最小权限原则)
CREATE USER 'lab_app'@'%' IDENTIFIED BY 'YourStrongPassword123!';

-- 授权
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, EXECUTE 
ON lab_management_db.* TO 'lab_app'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证连接
SHOW DATABASES;
SHOW GRANTS FOR 'lab_app'@'%';
```

#### 导入初始Schema和数据

```bash
# 进入SQL脚本目录
cd /path/to/project/backend/sql

# 导入表结构
mysql -u lab_app -p lab_management_db < schema-v1.6.0.sql

# 导入初始数据 (字典数据、默认账号等)
mysql -u lab_app -p lab_management_db < init-data.sql

# 验证导入
mysql -u lab_app -p lab_management_db -e "SHOW TABLES;"
```

#### MySQL性能优化配置

```ini
# /etc/my.cnf.d/server.cnf 或 /etc/mysql/my.cnf

[mysqld]
# 基本设置
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# InnoDB引擎优化
innodb_buffer_pool_size = 2G          # 物理内存的50-70%
innodb_log_file_size = 512M
innodb_flush_method = O_DIRECT
innodb_flush_log_at_trx_commit = 2     # 性能与安全的平衡
innodb_file_per_table = 1

# 连接设置
max_connections = 500
max_allowed_packet = 64M
wait_timeout = 600
interactive_timeout = 600

# 查询缓存 (MySQL 8.0已移除query_cache，使用其他方式)

# 慢查询日志 (性能调优必备)
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2                   # 超过2秒记录

# 二进制日志 (用于备份和主从复制)
log-bin = mysql-bin
binlog_format = ROW
expire_logs_days = 7                  # 保留7天

[client]
default-character-set = utf8mb4
```

重启MySQL使配置生效:
```bash
sudo systemctl restart mysqld
```

---

### 3.2 Redis 7.0 安装与配置

#### 安装Redis (CentOS/Rocky)

```bash
# 安装EPEL和Remi仓库
sudo yum install epel-release -y
sudo yum install https://rpms.remirepo.net enterprise/remi-release-9.rpm -y

# 启用Remi Redis模块
sudo yum module enable redis:remi-7.0 -y

# 安装Redis
sudo yum install redis -y

# 启动并设置开机自启
sudo systemctl start redis
sudo systemctl enable redis
```

#### Redis安全配置

```bash
# 编辑Redis配置文件
sudo vi /etc/redis.conf

# 关键配置项修改:

# 绑定地址 (仅允许内网访问，不要绑定0.0.0.0)
bind 127.0.0.1 192.168.1.100  # 替换为实际内网IP

# 设置访问密码 (必须!)
requirepass YourRedisPasswordHere!

# 禁用危险命令 (生产环境强烈建议)
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command DEBUG ""

# 持久化配置
save 900 1      # 900秒内至少1个key变更则快照
save 300 10     # 300秒内至少10个key变更
save 60 10000   # 60秒内至少10000个key变更

appendonly yes   # 开启AOF持久化 (更可靠)
appendfsync everysec  # 每秒同步一次

# 最大内存限制
maxmemory 2gb
maxmemory-policy allkeys-lru  # 内存满时淘汰最近最少使用的key
```

重启Redis:
```bash
sudo systemctl restart redis

# 测试连接
redis-cli -h 127.0.0.1 -p 6379 -a YourRedisPasswordHere PING
# 应返回: PONG
```

---

### 3.3 Nacos 2.2.3 安装与配置

#### 下载并安装Nacos

```bash
# 创建Nacos目录
mkdir -p /opt/nacos
cd /opt/nacos

# 下载Nacos 2.2.3 (单机模式)
wget https://github.com/alibaba/nacos/releases/download/2.2.3/nacos-server-2.2.3.tar.gz
tar -xzf nacos-server-2.2.3.tar.gz
mv nacos nacos-home

# 创建Nacos专用用户
sudo useradd -r -m -s /bin/bash nacos
sudo chown -R nacos:nacos /opt/nacos
```

#### 配置Nacos为单机模式

```bash
# 编辑启动脚本，设置为单机模式
vi /opt/nacos/nacos-home/bin/startup.sh

# 找到以下内容并修改:
# 大约在第26行左右
# 默认是集群模式 cluster
# 改为 standalone 单机模式

export MODE="standalone"
export FUNCTION_MODE="all"
export SERVER_PORT="8848"
export JVM_XMS="512m"   # 根据服务器内存调整
export JVM_XMX="512m"
export JVM_XMN="256m"
```

#### 配置MySQL作为Nacos数据源 (推荐生产环境)

```sql
-- 在MySQL中创建Nacos数据库
CREATE DATABASE nacos_config CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON nacos_config.* TO 'nacos'@'%' IDENTIFIED BY 'NacosPassword123!';
FLUSH PRIVILEGES;

-- 导入Nacos初始化脚本 (在nacos解压目录的conf目录下)
mysql -u nacos -p nacos_config < /opt/nacos/nacos-home/conf/nacos-mysql.sql
```

修改Nacos配置文件:
```properties
# /opt/nacos/nacos-home/conf/application.properties

# spring.datasource.platform 改为 mysql
spring.datasource.platform=mysql

# 数量为1
db.num=1

db.url.0=jdbc:mysql://127.0.0.1:3306/nacos_config?characterEncoding=utf8&connectTimeout=10000&socketTimeout=30000&autoReconnect=true&useUnicode=true&useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
db.user.0=nacos
db.password.0=NacosPassword123!
```

#### 启动Nacos

```bash
# 使用nacos用户启动
su - nacs
cd /opt/nacos/nacos-home
sh bin/startup.sh -m standalone

# 验证启动成功
tail -f logs/start.out
# 看到 "Nacos started successfully in stand alone mode." 即成功

# 访问Web控制台
# http://your-server-ip:8848/nacos
# 默认账号: nacos / nacos
# ⚠️ 生产环境请立即修改默认密码!
```

#### 创建Systemd服务 (开机自启)

```ini
# /etc/systemd/system/nacos.service

[Unit]
Description=Nacos Server
After=network.target mysql.service redis.service

[Service]
Type=simple
User=nacos
Group=nacos
Environment="MODE=standalone"
WorkingDirectory=/opt/nacos/nacos-home
ExecStart=/opt/nacos/nacos-home/bin/startup.sh -m standalone
ExecStop=/opt/nacos/nacos-home/bin/shutdown.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 重载并启用服务
sudo systemctl daemon-reload
sudo systemctl enable nacos
sudo systemctl start nacos
sudo systemctl status nacos
```

---

## 4. 应用服务部署

### 4.1 构建后端应用

```bash
# 进入后端项目根目录
cd /path/to/lab-management-system/backend

# 清理并打包 (跳过测试以加快速度，生产环境应运行完整测试)
mvn clean package -DskipTests

# 构建产物位置
# 各服务的target目录下会生成可执行JAR:
# user-service/target/user-service-1.6.0.jar
# sample-service/target/sample-service-1.6.0.jar
# report-service/target/report-service-1.6.0.jar
# exam-service/target/exam-service-1.6.0.jar
# gateway-service/target/gateway-service-1.6.0.jar
# ai-service/target/ai-service-1.6.0.jar (可选)
```

### 4.2 部署各微服务

#### 通用部署步骤 (每个服务重复此流程)

以User Service为例:

```bash
# 1. 复制JAR到部署目录
cp user-service/target/user-service-1.6.0.jar /opt/lab-management/app/user-service/

# 2. 创建日志目录
mkdir -p /opt/lab-management/logs/user-service

# 3. 创建启动脚本
cat > /opt/lab-management/app/user-service/start.sh << 'EOF'
#!/bin/bash
APP_NAME="user-service"
JAR_FILE="/opt/lab-management/app/user-service/user-service-1.6.0.jar"
LOG_FILE="/opt/lab-management/logs/user-service/console.log"
PID_FILE="/opt/lab-management/app/user-service/app.pid"

# JVM参数 (根据服务器内存调整)
JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# Spring Profile
SPRING_PROFILES_ACTIVE="prod"

echo "Starting ${APP_NAME}..."
nohup java $JAVA_OPTS \
  -jar $JAR_FILE \
  --spring.profiles.active=$SPRING_PROFILES_ACTIVE \
  > $LOG_FILE 2>&1 &

echo $! > $PID_FILE
echo "${APP_NAME} started with PID $(cat $PID_FILE)"
EOF

chmod +x /opt/lab-management/app/user-service/start.sh

# 4. 创建停止脚本
cat > /opt/lab-management/app/user-service/stop.sh << 'EOF'
#!/bin/bash
APP_NAME="user-service"
PID_FILE="/opt/lab-management/app/user-service/app.pid"

if [ -f "$PID_FILE" ]; then
  PID=$(cat $PID_FILE)
  echo "Stopping ${APP_NAME} (PID: ${PID})..."
  kill $PID
  rm -f $PID_FILE
  echo "${APP_NAME} stopped."
else
  echo "${APP_NAME} is not running."
fi
EOF
chmod +x /opt/lab-management/app/user-service/stop.sh
```

#### 为所有服务创建Systemd单元文件

**Gateway Service**:
```ini
# /etc/systemd/system/lab-gateway.service

[Unit]
Description=Lab Management System - API Gateway
After=network.target nacos.service mysql.service redis.service

[Service]
Type=simple
User=labadmin
Group=labadmin
WorkingDirectory=/opt/lab-management/app/gateway
ExecStart=/usr/bin/java -Xms512m -Xmx1024m \
  -jar /opt/lab-management/app/gateway/gateway-service-1.6.0.jar \
  --spring.profiles.active=prod
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lab-gateway

[Install]
WantedBy=multi-user.target
```

**User Service**:
```ini
# /etc/systemd/system/lab-user-service.service

[Unit]
Description=Lab Management System - User Service
After=network.target nacos.service mysql.service redis.service lab-gateway.service

[Service]
Type=simple
User=labadmin
Group=labadmin
WorkingDirectory=/opt/lab-management/app/user-service
ExecStart=/usr/bin/java -Xms512m -Xmx1024m \
  -jar /opt/lab-management/app/user-service/user-service-1.6.0.jar \
  --spring.profiles.active=prod
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lab-user-service

[Install]
WantedBy=multi-user.target
```

*(Sample Service, Report Service, Exam Service类似，只需修改Description、WorkingDirectory、ExecStart和SyslogIdentifier)*

#### 启用所有服务

```bash
# 重载systemd
sudo systemctl daemon-reload

# 启用各服务 (设置开机自启)
sudo systemctl enable lab-gateway
sudo systemctl enable lab-user-service
sudo systemctl enable lab-sample-service
sudo systemctl enable lab-report-service
sudo systemctl enable lab-exam-service

# 按顺序启动
sudo systemctl start lab-gateway
sleep 5       # 等待网关就绪
sudo systemctl start lab-user-service
sudo systemctl start lab-sample-service
sudo systemctl start lab-report-service
sudo systemctl start lab-exam-service

# 检查状态
sudo systemctl status lab-* --no-pager
```

---

## 5. 前端部署

### 5.1 构建前端

```bash
# 进入前端项目目录
cd /path/to/lab-management-system/frontend

# 安装依赖
npm install

# 生产构建
npm run build

# 构建产物位于 dist/ 目录
# 将dist目录复制到部署位置
cp -r dist/* /opt/lab-management/frontend/dist/

# 验证构建结果
ls -la /opt/lab-management/frontend/dist/
# 应看到: index.html, assets/, favicon.ico 等
```

### 5.2 配置Nginx反向代理

#### 安装Nginx

```bash
# CentOS/Rocky
sudo yum install nginx -y

# Ubuntu
sudo apt update && sudo apt install nginx -y
```

#### 创建站点配置

```nginx
# /etc/nginx/conf.d/lab-management.conf

# 上游定义 (后端微服务集群)
upstream lab_backend {
    server 127.0.0.1:8080;  # Gateway端口
    # 如果有多个Gateway实例，可以添加:
    # server 127.0.0.1:8081 backup;
}

server {
    listen 80;
    server_name your-lab-domain.com;  # 替换为实际域名或IP
    
    # 前端静态文件根目录
    root /opt/lab-management/frontend/dist;
    index index.html;
    
    # 字符集
    charset utf-8;
    
    # 访问日志
    access_log /var/log/nginx/lab-management.access.log main;
    error_log /var/log/nginx/lab-management.error.log warn;
    
    # Gzip压缩 (提升传输效率)
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/javascript
        application/json
        application/javascript
        application/xml
        image/svg+xml;
    
    # 前端路由 (Vue Router history模式)
    location / {
        try_files $uri $uri/ /index.html;
        
        # 缓存策略
        # HTML文件不缓存
        if ($request_filename ~* \.html$) {
            add_header Cache-Control "no-cache, no-store, must-revalidate";
        }
        
        # 静态资源长期缓存 (带hash的文件)
        if ($request_filename ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$) {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API代理转发到后端Gateway
    location /api/ {
        proxy_pass http://lab_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持 (如有需要)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;
        
        # Buffer设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Nginx状态监控 (仅限内网访问)
    location /nginx_status {
        stub_status on;
        allow 127.0.0.1;
        allow 192.168.0.0/16;  # 内网网段
        deny all;
    }
    
    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

#### HTTPS配置 (生产环境必须!)

```bash
# 申请SSL证书 (Let's Encrypt免费证书示例)
sudo apt install certbot python3-certbot-nginx -y  # Ubuntu
# 或 sudo yum install certbot python3-certbot-nginx -y  # CentOS

# 申请证书
sudo certbot --nginx -d your-lab-domain.com -d www.your-lab-domain.com

# 自动续期 (cron job)
echo "0 0 1 * * certbot renew --quiet" | sudo tee -a /etc/crontab
```

Nginx会自动添加HTTPS配置块。手动配置参考:

```nginx
# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name your-lab-domain.com;
    return 301 https://$host$request_uri;
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name your-lab-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-lab-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-lab-domain.com/privkey.pem;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS (强制HTTPS)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # ... 其余配置同上 ...
}
```

#### 启动Nginx

```bash
# 测试配置语法
sudo nginx -t

# 启动Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 验证
curl -I http://your-server-ip
# 应返回200 OK
```

---

## 6. 服务启动与验证

### 6.1 推荐启动顺序

```
启动顺序图:
1. MySQL      (3306)     ← 数据库基础
2. Redis      (6379)     ← 缓存基础  
3. Nacos      (8848)     ← 注册中心
4. Gateway    (8080)     ← API入口
5. UserSvc    (8081)     ← 认证服务
6. SampleSvc  (8082)     ← 标本服务
7. ReportSvc  (8083)     ← 报告服务
8. ExamSvc    (8084)     ← 项目服务
9. AI Service (8085)     ← AI服务(可选)
10. Nginx     (80/443)   ← 反向代理(最后)
```

### 6.2 一键启动脚本

创建 `/opt/lab-management/scripts/start-all.sh`:

```bash
#!/bin/bash
# ============================================================
# 实验室管理系统 - 一键启动脚本
# 用法: sudo ./start-all.sh [start|stop|restart|status]
# ============================================================

SERVICE_LIST=(
  "mysqld"
  "redis"
  "nacos"
  "lab-gateway"
  "lab-user-service"
  "lab-sample-service"
  "lab-report-service"
  "lab-exam-service"
  "nginx"
)

start_services() {
  echo "=========================================="
  echo "  开始启动实验室管理系统服务..."
  echo "=========================================="
  
  for service in "${SERVICE_LIST[@]}"; do
    echo -n "启动 $service ... "
    if systemctl is-active --quiet $service; then
      echo "[已运行]"
    else
      systemctl start $service
      sleep 2
      if systemctl is-active --quiet $service; then
        echo "[✓ 成功]"
      else
        echo "[✗ 失败] 请检查日志!"
      fi
    fi
  done
  
  echo ""
  echo "=========================================="
  echo "  所有服务启动完成!"
  echo "  访问地址: http://your-server-ip"
  echo "=========================================="
}

stop_services() {
  echo "=========================================="
  echo "  开始停止实验室管理系统服务..."
  echo "=========================================="
  
  # 反序停止 (先停依赖者)
  for (( i=${#SERVICE_LIST[@]}-1; i>=0; i-- )); do
    service=${SERVICE_LIST[$i]}
    echo -n "停止 $service ... "
    if systemctl is-active --quiet $service; then
      systemctl stop $service
      echo "[✓ 已停止]"
    else
      echo "[未运行]"
    fi
  done
  
  echo ""
  echo "所有服务已停止."
}

show_status() {
  echo "=========================================="
  echo "  服务状态总览"
  echo "=========================================="
  printf "%-25s %-10s %-8s\n" "服务名" "状态" "PID"
  printf "%-25s %-10s %-8s\n" "-------------------------" "----------" "--------"
  
  for service in "${SERVICE_LIST[@]}"; do
    if systemctl is-active --quiet $service; then
      pid=$(systemctl show --property=MainPID --value $service)
      printf "%-25s %-10s %-8s\n" $service "● 运行中" $pid
    else
      printf "%-25s %-10s %-8s\n" $service "○ 已停止" "-"
    fi
  done
}

case "$1" in
  start)
    start_services
    ;;
  stop)
    stop_services
    ;;
  restart)
    stop_services
    sleep 3
    start_services
    ;;
  status)
    show_status
    ;;
  *)
    echo "用法: $0 {start|stop|restart|status}"
    exit 1
esac
```

```bash
chmod +x /opt/lab-management/scripts/start-all.sh

# 使用示例
./start-all.sh start     # 启动所有服务
./start-all.sh status    # 查看状态
./start-all.sh stop      # 停止所有服务
./start-all.sh restart   # 重启所有服务
```

### 6.3 启动验证检查清单

启动完成后，执行以下验证:

```bash
# 1. 检查所有进程是否运行
ps aux | grep java | grep -v grep
# 应看到5-6个Java进程(Gateway + 4-5个微服务)

# 2. 检查端口监听
netstat -tlnp | grep -E ':(8080|8081|8082|8083|8084|8085|8848|3306|6379)'
# 所有端口都应在LISTEN状态

# 3. 检查Nacos注册中心
curl http://localhost:8848/nacos/v1/ns/service/list?pageNo=1&pageSize=50
# 应返回注册的服务列表JSON

# 4. 健康检查各服务
curl http://localhost:8080/actuator/health
curl http://localhost:8081/actuator/health
curl http://localhost:8082/actuator/health
# ... 其他服务
# 全部应返回 {"status":"UP",...}

# 5. 前端页面访问
curl -I http://localhost  # 或你的域名
# 应返回200 OK

# 6. 登录接口测试
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123456"}'
# 应返回200 + JWT Token
```

---

## 7. 配置文件详解

### 7.1 生产环境配置模板

创建 `/opt/lab-management/config/application-prod.yml`:

```yaml
# ============================================================
# 实验室管理系统 - 生产环境配置
# 文件路径: config/application-prod.yml
# 注意: 敏感信息请使用环境变量或加密配置中心
# ============================================================

server:
  port: ${SERVER_PORT:8080}
  servlet:
    context-path: /
  compression:
    enabled: true
    mime-types: application/json,text/html,text/xml,text/plain

spring:
  application:
    name: ${SPRING_APPLICATION_NAME:lab-management}
  
  profiles:
    active: prod
  
  # ======== 数据源配置 ========
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://${DB_HOST:localhost}:${DB_PORT:3306}/${DB_NAME:lab_management_db}?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
    username: ${DB_USER:lab_app}
    password: ${DB_PASSWORD:CHANGE_ME_IN_PRODUCTION}
    hikari:
      minimum-idle: 5
      maximum-pool-size: 20
      idle-timeout: 300000
      max-lifetime: 1800000
      connection-timeout: 30000
      pool-name: LabManagementHikariPool
  
  # ======== Redis配置 ========
  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: ${REDIS_PORT:6379}
      password: ${REDIS_PASSWORD:}
      database: 0
      lettuce:
        pool:
          max-active: 20
          max-idle: 10
          min-idle: 5
          max-wait: 3000ms
        shutdown-timeout: 200ms
  
  # ======== JPA/MyBatis配置 ========
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: Asia/Shanghai
    default-property-inclusion: non_null
    serialization:
      write-dates-as-timestamps: false

# ======== MyBatis-Plus配置 ========
mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml
  type-aliases-package: com.lab.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.slf4j.Slf4jImpl  # 生产环境用slf4j
  global-config:
    db-config:
      id-type: auto
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0

# ======== 日志配置 ========
logging:
  level:
    root: INFO
    com.lab: INFO         # 生产环境降低日志级别
    org.springframework.security: WARN
    org.springframework.web: WARN
  file:
    name: ${LOG_PATH:/opt/lab-management/logs}/${SPRING_APPLICATION_NAME:app}/application.log
  logback:
    rollingpolicy:
      max-file-size: 100MB
      max-history: 30
      total-size-cap: 3GB
      clean-history-on-start: true

# ======== JWT配置 ========
jwt:
  secret: ${JWT_SECRET:PLEASE_CHANGE_THIS_TO_A_VERY_LONG_SECRET_KEY_AT_LEAST_256_BITS_FOR_HMAC_SHA_ALGORITHM}
  expiration: ${JWT_EXPIRATION:86400000}  # 24小时

# ======== Actuator监控配置 ========
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
      base-path: /actuator
  endpoint:
    health:
      show-details: when-authorized
      roles: ADMIN
  metrics:
    tags:
      application: ${spring.application.name}
    export:
      prometheus:
        enabled: true

# ======== 业务配置 ========
lab:
  system:
    name: 实验室管理系统
    version: v1.6.0
    environment: production
  security:
    cors:
      allowed-origins:
        - ${FRONTEND_URL:http://localhost:5173}
        - ${FRONTEND_URL_ALT:https://your-lab-domain.com}
    token:
      expire-hours: 24
  hl7:
    his-host: ${HL7_HIS_HOST:localhost}
    his-port: ${HL7_HIS_PORT:2575}
    timeout: 30000
```

### 7.2 环境变量配置

创建 `/opt/lab-management/config/env.sh` (不提交到Git!):

```bash
#!/bin/bash
# ============================================================
# 生产环境敏感配置 (通过环境变量注入)
# 权限: chmod 700 env.sh (仅owner可读写执行)
# ============================================================

# 数据库
export DB_HOST="192.168.1.100"
export DB_PORT="3306"
export DB_NAME="lab_management_db"
export DB_USER="lab_app"
export DB_PASSWORD="YourSuperStrongPassword123!@#$"

# Redis
export REDIS_HOST="192.168.1.101"
export REDIS_PORT="6379"
export REDIS_PASSWORD="YourRedisPassword!"

# JWT密钥 (非常重要! 必须足够长且随机)
export JWT_SECRET="$(openssl rand -base64 64)"

# 前端URL
export FRONTEND_URL="https://your-lab-domain.com"

# HL7 HIS系统
export HL7_HIS_HOST="his.hospital.local"
export HL7_HIS_PORT="2575"
```

```bash
# 加载环境变量
source /opt/lab_management/config/env.sh

# 验证
echo $DB_PASSWORD  # 应显示密码
```

---

## 8. 健康检查与监控

### 8.1 Actuator健康端点

系统集成了Spring Boot Actuator，提供标准化的健康检查接口。

**各服务健康检查URL**:

| 服务 | URL | 说明 |
|------|-----|------|
| Gateway | `http://localhost:8080/actuator/health` | 网关健康 |
| User Service | `http://localhost:8081/actuator/health` | 用户服务健康 |
| Sample Service | `http://localhost:8082/actuator/health` | 标本服务健康 |
| Report Service | `http://localhost:8083/actuator/health` | 报告服务健康 |
| Exam Service | `http://localhost:8084/actuator/health` | 项目服务健康 |

**健康检查响应示例**:

```json
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": {
        "database": "MySQL",
        "validationQuery": "SELECT 1",
        "result": "UP"
      }
    },
    "redis": {
      "status": "UP",
      "details": {
        "version": "7.0.5"
      }
    },
    "diskSpace": {
      "status": "UP",
      "details": {
        "total": 500107782144,
        "free": 376541589504,
        "threshold": 10485760,
        "exists": true
      }
    },
    "ping": {
      "status": "UP"
    }
  }
}
```

### 8.2 自定义健康检查脚本

创建 `/opt/lab-management/scripts/health-check.sh`:

```bash
#!/bin/bash
# ============================================================
# 健康检查脚本 - 可集成到Zabbix/Prometheus/Nagios等监控系统
# 输出: 0=全部健康, 1=有警告, 2=有异常
# ============================================================

declare -A SERVICES=(
  ["Gateway"]="http://127.0.0.1:8080/actuator/health"
  ["UserSvc"]="http://127.0.0.1:8081/actuator/health"
  ["SampleSvc"]="http://127.0.0.1:8082/actuator/health"
  ["ReportSvc"]="http://127.0.0.1:8083/actuator/health"
  ["ExamSvc"]="http://127.0.0.1:8084/actuator/health"
)

WARNING_COUNT=0
ERROR_COUNT=0

echo "=========================================="
echo "  健康检查报告 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

for service in "${!SERVICES[@]}"; do
  url="${SERVICES[$service]}"
  response=$(curl -sf -w "\n%{http_code}" "$url" 2>/dev/null)
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')
  
  if [ "$http_code" == "200" ]; then
    status=$(echo "$body" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$status" == "UP" ]; then
      printf "  ✓ %-12s %s\n" "$service" "HEALTHY"
    else
      printf "  ⚠ %-12s %s (%s)\n" "$service" "DEGRADED" "$status"
      ((WARNING_COUNT++))
    fi
  else
    printf "  ✗ %-12s %s (HTTP %s)\n" "$service" "DOWN" "$http_code"
    ((ERROR_COUNT++))
  fi
done

echo ""
echo "------------------------------------------"
if [ $ERROR_COUNT -gt 0 ]; then
  echo "  结果: ❌ 异常 ($ERROR_COUNT 个服务宕机)"
  exit 2
elif [ $WARNING_COUNT -gt 0 ]; then
  echo "  结果: ⚠️  警告 ($WARNING_COUNT 个服务降级)"
  exit 1
else
  echo "  结果: ✅ 所有服务正常"
  exit 0
fi
```

```bash
chmod +x /opt/lab-management/scripts/health-check.sh

# 手动执行
/opt/lab-management/scripts/health-check.sh

# 设置定时任务 (每5分钟检查一次)
*/5 * * * * /opt/lab-management/scripts/health-check.sh >> /opt/lab-management/logs/health-check.log 2>&1
```

### 8.3 Prometheus + Grafana监控 (可选增强)

**Prometheus配置** (`prometheus.yml`):

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'lab-management'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['localhost:8080', 'localhost:8081', 'localhost:8082', 
                  'localhost:8083', 'localhost:8084']
        labels:
          env: production
```

**关键监控指标**:

| 指标名称 | 说明 | 告警阈值 |
|---------|------|----------|
| `jvm_memory_used_bytes` | JVM内存使用 | > 80% max |
| `http_server_requests_seconds_count` | API请求计数 | 错误率>1% |
| `hikaricp_connections_active` | 数据库连接数 | > 80% max |
| `process_cpu_usage` | CPU使用率 | > 85% |

---

## 9. 故障排查指南

### 9.1 常见问题速查表

| 问题现象 | 可能原因 | 解决方案 | 优先级 |
|---------|----------|----------|--------|
| **服务无法启动** | 端口被占用 | `lsof -i :端口号` 查找并释放 | P0 |
| **连接数据库失败** | 密码错误/网络不通 | 检查application.yml中的DB配置 | P0 |
| **注册中心连不上** | Nacos未启动或防火墙 | 先启动Nacos，检查8848端口 | P0 |
| **API返回401** | Token过期或无效 | 重新登录获取新Token | P1 |
| **API返回500** | 后端异常 | 查看`logs/*/error.log` | P0 |
| **前端白屏** | Nginx配置错误或构建失败 | 检查`nginx -t`和浏览器Console | P1 |
| **响应很慢** | 数据库慢查询/内存不足 | 开启慢查询日志，检查JVM参数 | P2 |
| **CORS跨域错误** | 域名未加入白名单 | 检查Gateway CORS配置 | P1 |

### 9.2 详细故障排查流程

#### 问题1: 微服务启动失败

```bash
# 步骤1: 查看启动日志
journalctl -u lab-user-service -f --no-pager

# 步骤2: 常见错误及解决
# 错误: "Failed to configure a DataSource"
# 原因: 数据库未启动或配置错误
# 解决: 
#   1. 确认MySQL运行: systemctl status mysqld
#   2. 测试连接: mysql -h DB_HOST -u DB_USER -p
#   3. 检查配置: cat config/application-prod.yml | grep datasource

# 错误: "Cannot connect to Nacos"
# 原因: Nacos未启动或网络不通
# 解决:
#   1. 确认Nacos运行: curl http://localhost:8848/nacos/
#   2. 检查防火墙: firewall-cmd --list-ports
#   3. telnet nacos-host 8848

# 错误: "Port already in use"
# 原因: 端口冲突
# 解决:
#   lsof -i :8081  # 查看占用进程
#   kill -9 <PID>  # 结束占用进程 (谨慎!)
```

#### 问题2: API请求超时或失败

```bash
# 步骤1: 检查服务是否运行
curl http://localhost:8080/actuator/health

# 步骤2: 直接测试目标服务 (绕过Gateway)
curl http://localhost:8081/actuator/health

# 步骤3: 检查Gateway路由配置
# 查看: config/application-prod.yml 的 spring.cloud.gateway.routes

# 步骤4: 检查网络连通性
telnet localhost 8080
telnet localhost 8081

# 步骤5: 分析慢请求
# 查看慢查询日志: tail -f /var/log/mysql/slow.log
# 查看应用日志: tail -f /opt/lab-management/logs/*/application.log
```

#### 问题3: 前端页面无法访问

```bash
# 步骤1: 检查Nginx状态
systemctl status nginx
nginx -t  # 测试配置

# 步骤2: 检查前端文件是否存在
ls -la /opt/lab-management/frontend/dist/index.html

# 步骤3: 检查Nginx错误日志
tail -f /var/log/nginx/lab-management.error.log

# 步骤4: 浏览器开发者工具检查
# F12 → Console: 查看JavaScript错误
# F12 → Network: 查看哪些请求失败(红色)
# F90 → Application: 检查localStorage/Cookie

# 常见修复:
# - 404: 检查try_files配置 (Vue Router history模式)
# - CORS: 检查nginx.conf的add_header配置
# - 白屏: 检查npm run build是否成功
```

### 9.3 日志分析技巧

```bash
# 实时查看日志 (最常用)
tail -f /opt/lab-management/logs/user-service/application.log

# 搜索错误关键字
grep -i "error\|exception\|failed" /opt/lab-management/logs/*/application.log

# 查看最近的错误
tail -n 500 /opt/lab-management/logs/gateway/application.log | grep -i error

# 按时间范围查看
grep "2026-04-05 14:" /opt/lab-management/logs/*/application.log

# 统计错误数量
grep -c "Exception" /opt/lab-management/logs/user-service/application.log

# 查看特定请求的完整日志链路 (如果有TraceId)
grep "trace-id=abc123" /opt/lab-management/logs/*/application.log
```

---

## 10. 备份恢复策略

### 10.1 数据库备份方案

#### 自动备份脚本

创建 `/opt/lab-management/scripts/backup-database.sh`:

```bash
#!/bin/bash
# ============================================================
# MySQL自动备份脚本
# 保留策略: 每日全量 + 保留30天
# ============================================================

BACKUP_DIR="/opt/lab-management/backup/database"
DB_NAME="lab_management_db"
DB_USER="lab_app"
DB_PASS="${DB_PASSWORD}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# 创建备份目录
mkdir -p "$BACKUP_DIR/daily"
mkdir -p "$BACKUP_DIR/monthly"

# 全量备份 (mysqldump)
BACKUP_FILE="$BACKUP_DIR/daily/${DB_NAME}_${DATE}.sql.gz"
echo "[$(date)] 开始备份数据库: $DB_NAME -> $BACKUP_FILE"

mysqldump -u"$DB_USER" -p"$DB_PASS" \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  --hex-blob \
  "$DB_NAME" | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo "[$(date)] 备份成功: $SIZE"
else
  echo "[$(date)] 备份失败!" >&2
  exit 1
fi

# �月1号额外保留一份月度备份
if [ "$(date +%d)" == "01" ]; then
  cp "$BACKUP_FILE" "$BACKUP_DIR/monthly/"
  echo "[$(date)] 月度备份已保存"
fi

# 清理过期备份 (保留最近30天)
find "$BACKUP_DIR/daily" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "[$(date)] 清理${RETENTION_DAYS}天前的旧备份完成"

echo "[$(date)] 备份任务结束"
```

```bash
chmod +x /opt/lab-management/scripts/backup-database.sh

# 设置定时任务 (每天凌晨3点执行)
crontab -e
# 添加:
0 3 * * * /opt/lab-management/scripts/backup-database.sh >> /opt/lab-management/logs/backup.log 2>&1
```

#### Binlog实时备份 (增量备份)

确保MySQL开启了binlog (见3.1节配置)，然后定期备份binlog:

```bash
# 手动刷新binlog并备份当前binlog
mysql -u root -p -e "FLUSH LOGS;"
cp /var/lib/mysql/mysql-bin.0* /opt/lab-management/backup/database/binlog/
```

### 10.2 配置文件备份

```bash
# 备份所有配置文件
tar -czvf /opt/lab-management/backup/config/config-backup-$(date +%Y%m%d).tar.gz \
  /opt/lab-management/config/*.yml \
  /etc/nginx/conf.d/*.conf \
  /etc/my.cnf.d/*.cnf \
  /etc/redis.conf
```

### 10.3 恢复演练

**重要**: 定期进行恢复演练，确保备份可用！

```bash
# 场景1: 从全量备份恢复整个数据库

# 1. 停止应用服务 (防止写入冲突)
sudo systemctl stop lab-*-service

# 2. 删除现有数据库 (谨慎!)
mysql -u root -p -e "DROP DATABASE lab_management_db; CREATE DATABASE lab_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 3. 解压并恢复备份
gunzip < /opt/lab-management/backup/database/daily/lab_management_db_20260405_030001.sql.gz | mysql -u root -p lab_management_db

# 4. 验证恢复
mysql -u root -p lab_management_db -e "SELECT COUNT(*) FROM t_user; SELECT COUNT(*) FROM t_sample;"

# 5. 重启服务
sudo systemctl start lab-*-service

# 场景2: 恢复单张误删表 (从全量+binlog)

# 1. 先恢复全量备份到临时库
mysql -u root -p -e "CREATE DATABASE restore_temp CHARACTER SET utf8mb4;"
gunzip < backup.sql.gz | mysql -u root -p restore_temp

# 2. 从临时库导出需要的表
mysqldump -u root -p restore_temp t_deleted_table > recover_table.sql

# 3. 导入到正式库
mysql -u root -p lab_management_db < recover_table.sql

# 4. 清理临时库
mysql -u root -p -e "DROP DATABASE restore_temp;"
```

---

## 11. 安全加固建议

### 11.1 操作系统层安全

```bash
# 1. 更新系统补丁
sudo yum update -y  # CentOS
sudo apt update && sudo apt upgrade -y  # Ubuntu

# 2. 配置防火墙
sudo firewall-cmd --permanent --add-port=22/tcp    # SSH
sudo firewall-cmd --permanent --add-port=80/tcp     # HTTP
sudo firewall-cmd --permanent --add-port=443/tcp    # HTTPS
sudo firewall-cmd --permanent --add-port=8080/tcp   # Gateway API (仅内网!)
sudo firewall-cmd --permanent --add-port=8848/tcp   # Nacos (仅内网!)
sudo firewall-cmd --permanent --remove-port=3306/tcp # MySQL禁止外网访问!
sudo firewall-cmd --permanent --remove-port=6379/tcp # Redis禁止外网访问!
sudo firewall-cmd --reload

# 3. 禁用root远程登录
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# 4. 安装Fail2Ban防暴力破解
sudo yum install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 11.2 应用层安全

| 安全措施 | 当前状态 | 建议 |
|---------|----------|------|
| 强密码策略 | ✅ BCrypt加密存储 | 定期轮换(90天) |
| JWT Token | ✅ 24小时过期 | 生产环境考虑更短(如8小时) |
| HTTPS | ⚠️ 需配置 | **生产环境必须启用** |
| SQL注入防护 | ✅ MyBatis-Plus预编译 | 保持现状 |
| XSS防护 | ✅ Vue自动转义 | 保持现状 |
| CSRF防护 | ✅ Stateless JWT天然免疫 | 保持现状 |
| 速率限制 | ⚠️ 未配置 | 建议添加Gateway限流 |
| 审计日志 | ✅ OperationLog表 | 定期归档分析 |

### 11.3 网络安全架构建议

```
                    Internet
                        │
                   ┌────▼────┐
                   │  WAF/DDoS│  (可选: 云WAF服务)
                   │  防护层  │
                   └────┬────┘
                        │
                   ┌────▼────┐
                   │  Nginx   │  (HTTPS终止 + 反向代理)
                   │ :443     │
                   └────┬────┘
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
         ┌────────┐ ┌────────┐ ┌────────┐
         │Frontend│ │API GW  │ │Static  │
         │(Vue.js)│ │:8080   │ │Assets  │
         └────────┘ └───┬────┘ └────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         ┌────────┐ ┌────────┐ ┌────────┐
         │MicroSvc│ │MicroSvc │ │MicroSvc │
         │:8081   │ │:8082    │ │:8083   │
         └───┬────┘ └───┬────┘ └───┬────┘
             │          │          │
             └──────────┼──────────┘
                        ▼
                ┌───────────────┐
                │  Internal Net │  (VPC/内网)
                │  MySQL :3306  │
                │  Redis :6379  │
                │  Nacos :8848  │
                └───────────────┘
```

---

## 12. 日常运维检查清单

### 每日检查 (自动化)

- [ ] 所有服务进程正常运行 (`systemctl status lab-*`)
- [ ] 健康检查全部通过 (`health-check.sh`)
- [ ] 磁盘空间充足 (>20% free)
- [ ] 数据库备份成功执行
- [ ] 无ERROR级别异常日志
- [ ] SSL证书未过期 (>30天有效期)

### 每周检查

- [ ] 分析慢查询日志并优化Top 10
- [ ] 检查系统资源使用趋势(CPU/Memory/Disk I/O)
- [ ] 审计操作日志(是否有异常操作)
- [ ] 检查安全补丁更新
- [ ] 验证备份恢复可行性 (可选)

### 每月检查

- [ ] 全面性能压测报告
- [ ] 安全扫描报告 (漏洞评估)
- [ ] 日志归档 (超过30天的压缩归档)
- [ ] 配置文件版本对比 (检测未授权变更)
- [ ] 容量规划评估 (未来3-6个月资源需求)

### 季度检查

- [ ] 灾难恢复演练 (模拟故障恢复)
- [ ] 安全渗透测试 (委托第三方)
- [ ] 架构评审会议 (技术债务清理)
- [ ] 成本优化评估 (云资源利用率)
- [ ] 文档更新 (本部署指南等)

---

## 📞 技术支持联系方式

| 场景 | 联系方式 | 响应时间 |
|------|----------|----------|
| **P0紧急故障** (系统宕机) | 电话: +86-xxx-xxxx-xxxx | < 30分钟 |
| **P1严重问题** (功能受损) | 企业微信/钉钉群 | < 2小时 |
| **P2一般问题** (非核心功能) | Issue Tracker | < 24小时 |
| **P3咨询建议** | Email: support@example.com | < 72小时 |

### 紧急联系人列表

| 角色 | 姓名 | 电话 | 邮箱 |
|------|------|------|------|
| 值班工程师A | 张工 | 138-xxxx-xxxx | zhang@example.com |
| 值班工程师B | 李工 | 139-xxxx-xxxx | li@example.com |
| DevOps负责人 | 王经理 | 186-xxxx-xxxx | wang@example.com |
| 技术总监 | 陈总 | 137-xxxx-xxxx | chen@example.com |

---

## 📚 附录

### A. 快速命令参考卡

```bash
# === 服务管理 ===
systemctl start/stop/restart/status lab-gateway
systemctl start/stop/restart/status lab-user-service
systemctl start/stop/restart/status lab-sample-service
systemctl start/stop/restart/status lab-report-service
systemctl start/stop/restart/status lab-exam-service

# === 日志查看 ===
journalctl -u lab-gateway -f            # 实时日志
tail -f /opt/lab-management/logs/*/application.log  # 应用日志

# === 健康检查 ===
curl http://localhost:8080/actuator/health
/opt/lab-management/scripts/health-check.sh

# === 备份恢复 ===
/opt/lab-management/scripts/backup-database.sh  # 手动备份
# 恢复见第10节

# === 性能监控 ===
curl http://localhost:8080/actuator/metrics/jvm_memory_used_bytes
curl http://localhost:8080/actuator/prometheus  # Prometheus格式
```

### B. 端口对照表

| 端口 | 服务 | 协议 | 外部访问 |
|------|------|------|----------|
| 22 | SSH | TCP | ✅ 管理 |
| 80 | HTTP (Nginx) | TCP | ✅ 用户 |
| 443 | HTTPS (Nginx) | TCP | ✅ 用户 |
| 3306 | MySQL | TCP | ❌ 仅内网 |
| 6379 | Redis | TCP | ❌ 仅内网 |
| 8080 | Gateway API | TCP | ❌ 仅内网/Nginx代理 |
| 8081 | User Service | TCP | ❌ 仅内网 |
| 8082 | Sample Service | TCP | ❌ 仅内网 |
| 8083 | Report Service | TCP | ❌ 仅内网 |
| 8084 | Exam Service | TCP | ❌ 仅内网 |
| 8085 | AI Service | TCP | ❌ 仅内网 |
| 8848 | Nacos Console | TCP | ❌ 仅内网 |
| 5173 | Vite Dev Server | TCP | ❌ 仅开发环境 |

---

**文档编制**: DevOps团队
**技术审核**: 系统架构师
**安全审核**: 安全专家
**生效日期**: 2026-04-05 23:00:00 UTC+8
**下次审查**: 2026-07-05 (3个月后)
**版本**: v1.0 Production Ready

---

*本文档为实验室管理系统v1.6.0 Final版本的官方部署指南，包含了从环境准备到生产运维的全流程指导。在生产环境部署前，请务必通读全文并根据实际情况调整配置。*
