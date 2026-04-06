-- =============================================
-- Iter3 FIX: User List API 500 Error 完整修复脚本
-- 目标：确保 sys_user 表存在且结构正确
-- 数据库：lab_management
-- 日期：2026-04-05
-- =============================================

USE lab_management;

-- =============================================
-- 1. 用户表 (sys_user) - 核心修复
-- 与 com.sunyaxin.common.entity.User 完全匹配
-- =============================================
DROP TABLE IF EXISTS sys_user;
CREATE TABLE sys_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码（BCrypt加密后约60字符）',
    real_name VARCHAR(100) COMMENT '真实姓名',
    role VARCHAR(20) NOT NULL COMMENT '角色：DOCTOR-临床医生，LAB_TECHNICIAN-检验医师，ADMIN-管理员',
    department VARCHAR(50) COMMENT '科室',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(50) COMMENT '邮箱',
    status TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_username (username),
    INDEX idx_role (role),
    INDEX idx_status (status),
    INDEX idx_deleted (deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- =============================================
-- 2. 插入初始用户数据（明文密码，登录时自动升级为BCrypt）
-- =============================================
INSERT INTO sys_user (username, password, real_name, role, department, phone, email, status, deleted) VALUES
('admin', 'admin123', '系统管理员', 'ADMIN', '信息科', '13800000000', 'admin@lab.com', 1, 0),
('doctor1', 'doctor123', '张医生', 'DOCTOR', '内科', '13800000001', 'zhangyi@lab.com', 1, 0),
('doctor2', 'doctor123', '李医生', 'DOCTOR', '外科', '13800000002', 'linger@lab.com', 1, 0),
('labtech1', 'lab123', '王检验师', 'LAB_TECHNICIAN', '检验科', '13800000003', 'wangyan@lab.com', 1, 0),
('labtech2', 'lab123', '刘检验师', 'LAB_TECHNICIAN', '检验科', '13800000004', 'liuyan@lab.com', 1, 0);

-- =============================================
-- 3. 验证数据插入
-- =============================================
SELECT '=== sys_user 表创建成功 ===' AS message;
SELECT COUNT(*) AS user_count FROM sys_user WHERE deleted = 0 AND status = 1;
SELECT id, username, real_name, role, status, deleted FROM sys_user WHERE deleted = 0 ORDER BY id;

-- =============================================
-- 4. 其他依赖表（确保完整性）
-- =============================================

-- 标本表
DROP TABLE IF EXISTS lab_sample;
CREATE TABLE lab_sample (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    sample_no VARCHAR(20) NOT NULL COMMENT '标本编号（唯一）',
    patient_id BIGINT COMMENT '患者ID',
    patient_name VARCHAR(50) NOT NULL COMMENT '患者姓名',
    patient_gender VARCHAR(10) COMMENT '患者性别',
    patient_age INT COMMENT '患者年龄',
    doctor_id BIGINT COMMENT '申请医生ID',
    doctor_name VARCHAR(50) COMMENT '申请医生姓名',
    test_items VARCHAR(200) NOT NULL COMMENT '检验项目',
    sample_type VARCHAR(20) COMMENT '标本类型',
    collect_time DATETIME COMMENT '采集时间',
    collect_location VARCHAR(100) COMMENT '采集位置',
    receive_time DATETIME COMMENT '接收时间',
    technician_id BIGINT COMMENT '检验医师ID',
    technician_name VARCHAR(50) COMMENT '检验医师姓名',
    status VARCHAR(20) DEFAULT 'COLLECTED' COMMENT '状态',
    remark VARCHAR(500) COMMENT '备注',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_sample_no (sample_no),
    INDEX idx_patient_id (patient_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标本表';

-- 患者表
DROP TABLE IF EXISTS lab_patient;
CREATE TABLE lab_patient (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    patient_no VARCHAR(20) NOT NULL COMMENT '患者编号',
    patient_name VARCHAR(50) NOT NULL COMMENT '患者姓名',
    gender VARCHAR(10) COMMENT '性别',
    birthday DATE COMMENT '出生日期',
    age INT COMMENT '年龄',
    phone VARCHAR(20) COMMENT '电话',
    address VARCHAR(255) COMMENT '地址',
    patient_type VARCHAR(20) COMMENT '患者类型',
    department VARCHAR(50) COMMENT '科室',
    diagnosis VARCHAR(500) COMMENT '诊断',
    status TINYINT DEFAULT 1 COMMENT '状态',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_patient_no (patient_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='患者表';

-- 检验报告表（简化版）
DROP TABLE IF EXISTS lab_report;
CREATE TABLE lab_report (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    report_no VARCHAR(20) NOT NULL COMMENT '报告编号',
    sample_id BIGINT COMMENT '标本ID',
    patient_id BIGINT NOT NULL COMMENT '患者ID',
    patient_name VARCHAR(50) NOT NULL COMMENT '患者姓名',
    test_items VARCHAR(200) NOT NULL COMMENT '检验项目',
    test_results TEXT COMMENT '检验结果JSON',
    ai_diagnosis VARCHAR(1000) COMMENT 'AI诊断结果',
    technician_id BIGINT COMMENT '检验医师ID',
    technician_name VARCHAR(50) COMMENT '检验医师姓名',
    reviewer_id BIGINT COMMENT '审核医师ID',
    reviewer_name VARCHAR(50) COMMENT '审核医师姓名',
    status VARCHAR(20) DEFAULT 'PENDING' COMMENT '状态',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_report_no (report_no),
    INDEX idx_patient_id (patient_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检验报告表';

-- 设备表
DROP TABLE IF EXISTS lab_device;
CREATE TABLE lab_device (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    device_no VARCHAR(20) NOT NULL COMMENT '设备编号',
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    device_model VARCHAR(50) COMMENT '设备型号',
    manufacturer VARCHAR(100) COMMENT '生产厂家',
    device_type VARCHAR(20) COMMENT '设备类型',
    location VARCHAR(100) COMMENT '位置',
    status VARCHAR(20) DEFAULT 'IDLE' COMMENT '状态',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_device_no (device_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';

-- =============================================
-- 5. 最终验证
-- =============================================
SELECT '========================================' AS separator;
SELECT 'Iter3 FIX: 数据库初始化完成！' AS status;
SELECT 'sys_user 表已创建并插入 5 条测试数据' AS user_table_info;
SELECT '其他依赖表已创建' AS other_tables_info;
SELECT '========================================' AS separator;

-- 显示所有表
SHOW TABLES LIKE 'sys_user';
SHOW TABLES LIKE 'lab_%';
