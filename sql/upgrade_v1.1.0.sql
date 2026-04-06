-- =============================================
-- 实验室管理系统数据库升级脚本
-- 版本: 1.1.0
-- 日期: 2026-03-22
-- =============================================

USE lab_management;

-- 1. 操作日志表（如果不存在）
CREATE TABLE IF NOT EXISTS operation_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    user_id BIGINT COMMENT '操作用户ID',
    username VARCHAR(50) COMMENT '操作用户名',
    real_name VARCHAR(50) COMMENT '操作人真实姓名',
    module VARCHAR(50) NOT NULL COMMENT '操作模块',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    operation_desc VARCHAR(500) COMMENT '操作描述',
    target_type VARCHAR(50) COMMENT '操作对象类型',
    target_id BIGINT COMMENT '操作对象ID',
    target_no VARCHAR(50) COMMENT '操作对象编号',
    request_ip VARCHAR(50) COMMENT '请求IP',
    request_method VARCHAR(10) COMMENT '请求方法',
    request_params TEXT COMMENT '请求参数',
    response_result TEXT COMMENT '返回结果',
    status VARCHAR(20) DEFAULT 'SUCCESS' COMMENT '操作状态',
    error_msg VARCHAR(500) COMMENT '错误信息',
    cost_time_ms INT COMMENT '耗时',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_user_id (user_id),
    INDEX idx_module (module),
    INDEX idx_operation_type (operation_type),
    INDEX idx_target_id (target_id),
    INDEX idx_target_no (target_no),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- 2. 患者信息表
CREATE TABLE IF NOT EXISTS patient_info (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    patient_no VARCHAR(20) NOT NULL COMMENT '患者编号',
    patient_name VARCHAR(50) NOT NULL COMMENT '患者姓名',
    id_card VARCHAR(18) COMMENT '身份证号',
    phone VARCHAR(20) COMMENT '联系电话',
    gender VARCHAR(10) COMMENT '性别',
    birth_date DATE COMMENT '出生日期',
    age INT COMMENT '年龄',
    address VARCHAR(200) COMMENT '地址',
    medical_history VARCHAR(500) COMMENT '病史',
    allergy_info VARCHAR(200) COMMENT '过敏信息',
    status TINYINT DEFAULT 1 COMMENT '状态',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_patient_no (patient_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='患者信息表';

-- 3. 标本类型字典表
CREATE TABLE IF NOT EXISTS sample_type (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    type_code VARCHAR(20) NOT NULL COMMENT '类型编码',
    type_name VARCHAR(50) NOT NULL COMMENT '类型名称',
    type_alias VARCHAR(50) COMMENT '类型别名',
    container_type VARCHAR(50) COMMENT '容器类型',
    storage_condition VARCHAR(50) COMMENT '存储条件',
    sort_order INT DEFAULT 0 COMMENT '排序',
    status TINYINT DEFAULT 1 COMMENT '状态',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_type_code (type_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标本类型字典表';

-- 4. 检验项目字典表
CREATE TABLE IF NOT EXISTS test_item (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    item_code VARCHAR(20) NOT NULL COMMENT '项目编码',
    item_name VARCHAR(100) NOT NULL COMMENT '项目名称',
    item_alias VARCHAR(50) COMMENT '项目别名',
    category VARCHAR(50) COMMENT '类别',
    unit VARCHAR(20) COMMENT '单位',
    reference_min DECIMAL(10,2) COMMENT '参考值最小值',
    reference_max DECIMAL(10,2) COMMENT '参考值最大值',
    reference_range VARCHAR(100) COMMENT '参考范围描述',
    price DECIMAL(10,2) COMMENT '价格',
    status TINYINT DEFAULT 1 COMMENT '状态',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_item_code (item_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检验项目字典表';

-- 5. 给lab_sample表添加字段
ALTER TABLE lab_sample ADD COLUMN barcode_no VARCHAR(50) COMMENT '条码号';
ALTER TABLE lab_sample ADD COLUMN sample_type_id BIGINT COMMENT '标本类型ID';
ALTER TABLE lab_sample ADD COLUMN priority TINYINT DEFAULT 0 COMMENT '优先级';
ALTER TABLE lab_sample ADD COLUMN abnormal_flag TINYINT DEFAULT 0 COMMENT '异常标志';
ALTER TABLE lab_sample ADD COLUMN abnormal_reason VARCHAR(200) COMMENT '异常原因';

-- 6. 给lab_report表添加字段
ALTER TABLE lab_report ADD COLUMN print_count INT DEFAULT 0 COMMENT '打印次数';
ALTER TABLE lab_report ADD COLUMN print_time DATETIME COMMENT '打印时间';
ALTER TABLE lab_report ADD COLUMN published_time DATETIME COMMENT '发布时间';
ALTER TABLE lab_report ADD COLUMN published_by BIGINT COMMENT '发布人ID';
ALTER TABLE lab_report ADD COLUMN published_by_name VARCHAR(50) COMMENT '发布人姓名';

-- 7. 给lab_sample_trace表添加字段
ALTER TABLE lab_sample_trace ADD COLUMN device_id BIGINT COMMENT '设备ID';
ALTER TABLE lab_sample_trace ADD COLUMN device_name VARCHAR(50) COMMENT '设备名称';
ALTER TABLE lab_sample_trace ADD COLUMN remark VARCHAR(200) COMMENT '备注';

-- 8. 添加初始数据
INSERT INTO sample_type (type_code, type_name, type_alias, container_type, storage_condition, sort_order, status) VALUES
('BLOOD', '血液', '血', '真空采血管', '室温/冷藏', 1, 1),
('URINE', '尿液', '尿', '尿杯', '冷藏', 2, 1),
('STOOL', '粪便', '粪', '便盒', '冷藏', 3, 1),
('SPUTUM', '痰液', '痰', '痰盒', '冷藏', 4, 1),
('SERUM', '血清', '血清', '离心管', '冷藏', 5, 1),
('PLASMA', '血浆', '血浆', '离心管', '冷藏', 6, 1);

INSERT INTO test_item (item_code, item_name, item_alias, category, unit, reference_min, reference_max, reference_range, price, status) VALUES
('WBC', '白细胞计数', 'WBC', '血常规', '10^9/L', 4.0, 10.0, '4.0-10.0', 25.00, 1),
('RBC', '红细胞计数', 'RBC', '血常规', '10^12/L', 4.0, 5.5, '4.0-5.5', 20.00, 1),
('HGB', '血红蛋白', 'HGB', '血常规', 'g/L', 120, 160, '120-160', 15.00, 1),
('HCT', '红细胞压积', 'HCT', '血常规', '%', 36, 50, '36-50', 15.00, 1),
('PLT', '血小板计数', 'PLT', '血常规', '10^9/L', 100, 300, '100-300', 25.00, 1),
('MCV', '平均红细胞体积', 'MCV', '血常规', 'fL', 80, 100, '80-100', 15.00, 1),
('MCH', '平均红细胞血红蛋白含量', 'MCH', '血常规', 'pg', 27, 34, '27-34', 15.00, 1),
('MCHC', '平均红细胞血红蛋白浓度', 'MCHC', '血常规', 'g/L', 320, 360, '320-360', 15.00, 1);

INSERT INTO patient_info (patient_no, patient_name, gender, age, phone, id_card, status) VALUES
('P20240001', '张三', '男', 35, '13800138001', '410101199001011234', 1),
('P20240002', '李四', '女', 28, '13800138002', '410101199601021234', 1),
('P20240003', '王五', '男', 45, '13800138003', '410101198101031234', 1);

SELECT '数据库升级完成!' AS result;
