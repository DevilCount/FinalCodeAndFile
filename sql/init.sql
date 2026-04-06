-- =============================================
-- 实验室管理系统数据库初始化脚本
-- 数据库：lab_management
-- =============================================

CREATE DATABASE IF NOT EXISTS lab_management DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE lab_management;

-- =============================================
-- 用户表
-- =============================================
DROP TABLE IF EXISTS sys_user;
CREATE TABLE sys_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
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
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- =============================================
-- 标本表
-- =============================================
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
    sample_type VARCHAR(20) COMMENT '标本类型：BLOOD-血液，URINE-尿液，STOOL-粪便等',
    collect_time DATETIME COMMENT '采集时间',
    collect_location VARCHAR(100) COMMENT '采集位置',
    receive_time DATETIME COMMENT '接收时间',
    technician_id BIGINT COMMENT '检验医师ID',
    technician_name VARCHAR(50) COMMENT '检验医师姓名',
    status VARCHAR(20) DEFAULT 'COLLECTED' COMMENT '状态：COLLECTED-已采集，IN_TRANSIT-运输中，RECEIVED-已接收，TESTING-检验中，COMPLETED-已完成，ARCHIVED-已归档，ABNORMAL-异常',
    remark VARCHAR(500) COMMENT '备注',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_sample_no (sample_no),
    INDEX idx_patient_id (patient_id),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标本表';

-- =============================================
-- 标本追踪记录表
-- =============================================
DROP TABLE IF EXISTS lab_sample_trace;
CREATE TABLE lab_sample_trace (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    sample_id BIGINT NOT NULL COMMENT '标本ID',
    sample_no VARCHAR(20) NOT NULL COMMENT '标本编号',
    operation_type VARCHAR(20) NOT NULL COMMENT '操作类型：COLLECT-采集，TRANSPORT-运输，RECEIVE-接收，TEST-检验，COMPLETE-完成，ARCHIVE-归档',
    operation_desc VARCHAR(200) COMMENT '操作描述',
    operator_id BIGINT COMMENT '操作人ID',
    operator_name VARCHAR(50) COMMENT '操作人姓名',
    location VARCHAR(100) COMMENT '操作位置',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_sample_id (sample_id),
    INDEX idx_sample_no (sample_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标本追踪记录表';

-- =============================================
-- 检验报告表
-- =============================================
DROP TABLE IF EXISTS lab_report;
CREATE TABLE lab_report (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    report_no VARCHAR(20) NOT NULL COMMENT '报告编号',
    sample_id BIGINT COMMENT '标本ID',
    sample_no VARCHAR(20) COMMENT '标本编号',
    patient_id BIGINT NOT NULL COMMENT '患者ID',
    patient_name VARCHAR(50) NOT NULL COMMENT '患者姓名',
    test_items VARCHAR(200) NOT NULL COMMENT '检验项目',
    test_results TEXT COMMENT '检验结果（JSON格式）',
    ai_diagnosis VARCHAR(1000) COMMENT 'AI辅助诊断结果',
    ai_confidence INT COMMENT 'AI诊断置信度（0-100）',
    ai_model_version VARCHAR(50) COMMENT 'AI模型版本',
    ai_diagnosis_time DATETIME COMMENT 'AI诊断时间',
    technician_id BIGINT COMMENT '检验医师ID',
    technician_name VARCHAR(50) COMMENT '检验医师姓名',
    reviewer_id BIGINT COMMENT '审核医师ID（兼容旧版）',
    reviewer_name VARCHAR(50) COMMENT '审核医师姓名（兼容旧版）',
    technical_reviewer_id BIGINT COMMENT '技术审核人ID',
    technical_reviewer_name VARCHAR(50) COMMENT '技术审核人姓名',
    technical_review_time DATETIME COMMENT '技术审核时间',
    technical_review_result VARCHAR(20) COMMENT '技术审核结果：APPROVED-通过，REJECTED-驳回',
    technical_review_comment VARCHAR(500) COMMENT '技术审核意见',
    clinical_reviewer_id BIGINT COMMENT '临床审核人ID',
    clinical_reviewer_name VARCHAR(50) COMMENT '临床审核人姓名',
    clinical_review_time DATETIME COMMENT '临床审核时间',
    clinical_review_result VARCHAR(20) COMMENT '临床审核结果：APPROVED-通过，REJECTED-驳回',
    clinical_review_comment VARCHAR(500) COMMENT '临床审核意见',
    status VARCHAR(20) DEFAULT 'PENDING' COMMENT '状态：PENDING-待审核，REVIEWING-审核中，APPROVED-已通过，REJECTED-已驳回，PUBLISHED-已发布',
    test_time DATETIME COMMENT '检验时间',
    review_time DATETIME COMMENT '审核时间',
    remark VARCHAR(500) COMMENT '备注',
    abnormal_indicator_count INT DEFAULT 0 COMMENT '异常指标数量',
    critical_indicator_count INT DEFAULT 0 COMMENT '危急值数量',
    revoked_by BIGINT COMMENT '撤销人ID',
    revoked_by_name VARCHAR(50) COMMENT '撤销人姓名',
    revoked_time DATETIME COMMENT '撤销时间',
    revoked_reason VARCHAR(500) COMMENT '撤销原因',
    archived_by BIGINT COMMENT '归档人ID',
    archived_by_name VARCHAR(50) COMMENT '归档人姓名',
    archived_time DATETIME COMMENT '归档时间',
    print_count INT DEFAULT 0 COMMENT '打印次数',
    print_time DATETIME COMMENT '首次打印时间',
    published_time DATETIME COMMENT '发布时间',
    published_by BIGINT COMMENT '发布人ID',
    published_by_name VARCHAR(50) COMMENT '发布人姓名',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_report_no (report_no),
    INDEX idx_sample_id (sample_id),
    INDEX idx_patient_id (patient_id),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time),
    INDEX idx_technical_reviewer_id (technical_reviewer_id),
    INDEX idx_clinical_reviewer_id (clinical_reviewer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检验报告表';

-- =============================================
-- 设备表
-- =============================================
DROP TABLE IF EXISTS lab_device;
CREATE TABLE lab_device (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    device_no VARCHAR(20) NOT NULL COMMENT '设备编号',
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    device_model VARCHAR(50) COMMENT '设备型号',
    manufacturer VARCHAR(100) COMMENT '生产厂家',
    device_type VARCHAR(20) COMMENT '设备类型：ANALYZER-分析仪，MICROSCOPE-显微镜，CENTRIFUGE-离心机等',
    location VARCHAR(100) COMMENT '所在位置',
    status VARCHAR(20) DEFAULT 'IDLE' COMMENT '状态：IDLE-空闲，RUNNING-运行中，MAINTENANCE-维护中，FAULT-故障',
    purchase_date DATE COMMENT '购买日期',
    last_maintenance_date DATE COMMENT '最后维护日期',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_device_no (device_no),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';

-- =============================================
-- 插入初始数据
-- =============================================

-- 初始化管理员账户（密码：admin123）
INSERT INTO sys_user (username, password, real_name, role, department, phone, status) VALUES
('admin', 'admin123', '管理员', 'ADMIN', '信息科', '13800000000', 1),
('doctor1', 'doctor123', '张医生', 'DOCTOR', '内科', '13800000001', 1),
('doctor2', 'doctor123', '李医生', 'DOCTOR', '外科', '13800000002', 1),
('labtech1', 'lab123', '王检验师', 'LAB_TECHNICIAN', '检验科', '13800000003', 1),
('labtech2', 'lab123', '刘检验师', 'LAB_TECHNICIAN', '检验科', '13800000004', 1);

-- 初始化设备数据
INSERT INTO lab_device (device_no, device_name, device_model, manufacturer, device_type, location, status) VALUES
('DE202402240001', '全自动血细胞分析仪', 'BC-6000', '迈瑞', 'ANALYZER', '检验科1室', 'IDLE'),
('DE202402240002', '尿液分析仪', 'UA-5800', '迪瑞', 'ANALYZER', '检验科2室', 'IDLE'),
('DE202402240003', '离心机', 'TDZ5-WS', '湘仪', 'CENTRIFUGE', '检验科准备室', 'IDLE');

-- =============================================
-- 查询示例
-- =============================================

-- 查询所有用户
-- SELECT * FROM sys_user WHERE status = 1 AND deleted = 0;

-- 查询标本追踪记录
-- SELECT * FROM lab_sample_trace WHERE sample_no = 'SPxxx' ORDER BY create_time ASC;

-- 查询患者报告
-- SELECT * FROM lab_report WHERE patient_id = 1 ORDER BY create_time DESC;
