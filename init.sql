-- 创建数据库
CREATE DATABASE IF NOT EXISTS lab_management DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE lab_management;

-- 创建用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL,
    department VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    status INT DEFAULT 1,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted INT DEFAULT 0
);

-- 创建索引
CREATE INDEX idx_username ON sys_user(username);
CREATE INDEX idx_role ON sys_user(role);
CREATE INDEX idx_status ON sys_user(status);

-- 插入测试数据
INSERT INTO sys_user (username, password, real_name, role, status) VALUES
('admin', 'admin123', '管理员', 'ADMIN', 1),
('doctor1', 'doctor123', '张医生', 'DOCTOR', 1),
('tech1', 'tech123', '李技术员', 'TECHNICIAN', 1),
('nurse1', 'nurse123', '王护士', 'NURSE', 1);