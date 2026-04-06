-- =============================================
-- 实验室管理系统数据库升级脚本
-- 升级日期：2026-03-19
-- 目的：扩容数据库，参考成熟LIS系统数据字典
-- =============================================

USE lab_management;

-- =============================================
-- 1. 患者信息表 (lab_patient) - 参考LIS_LIST简化版
-- =============================================
DROP TABLE IF EXISTS lab_patient;
CREATE TABLE lab_patient (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    patient_no VARCHAR(20) NOT NULL COMMENT '患者唯一编号',
    patient_name VARCHAR(50) NOT NULL COMMENT '患者姓名',
    id_num VARCHAR(20) COMMENT '身份证号',
    gender VARCHAR(10) COMMENT '性别：1-男，2-女，3-未知',
    gender_desc VARCHAR(20) COMMENT '性别描述',
    birthday DATE COMMENT '出生日期',
    age INT COMMENT '年龄',
    age_unit VARCHAR(10) COMMENT '年龄单位：岁、月、天',
    phone VARCHAR(20) COMMENT '联系电话',
    address VARCHAR(255) COMMENT '联系地址',
    patient_type VARCHAR(20) COMMENT '患者类型：OUTPATIENT-门诊，INPATIENT-住院，EMERGENCY-急诊',
    ward VARCHAR(50) COMMENT '病房',
    bed_no VARCHAR(20) COMMENT '床位号',
    diagnosis VARCHAR(500) COMMENT '临床诊断',
    allergy_info VARCHAR(500) COMMENT '过敏信息',
    status VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '状态：ACTIVE-活跃，INACTIVE-不活跃',
    remark VARCHAR(500) COMMENT '备注',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_patient_no (patient_no),
    INDEX idx_id_num (id_num),
    INDEX idx_patient_name (patient_name),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='患者信息表';

-- =============================================
-- 2. 检验项目表 (lab_test_item) - 参考LIS_ITEM
-- =============================================
DROP TABLE IF EXISTS lab_test_item;
CREATE TABLE lab_test_item (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    item_code VARCHAR(20) NOT NULL COMMENT '项目编码',
    item_name VARCHAR(100) NOT NULL COMMENT '项目名称',
    item_short_name VARCHAR(50) COMMENT '项目简称',
    english_name VARCHAR(100) COMMENT '英文名称',
    loinc_code VARCHAR(20) COMMENT 'LOINC编码',
    category VARCHAR(50) COMMENT '项目分类：BLOOD-血常规，URINE-尿常规，BIOCHEM-生化，IMMUNE-免疫等',
    sample_type VARCHAR(20) COMMENT '适用标本类型',
    result_type VARCHAR(10) COMMENT '结果类型：NUMERIC-数值，TEXT-文本，FORMULA-公式',
    unit VARCHAR(20) COMMENT '单位',
    decimal_places INT DEFAULT 2 COMMENT '小数位数',
    default_value VARCHAR(50) COMMENT '默认值',
    price DECIMAL(10,2) COMMENT '价格',
    report_sort INT DEFAULT 0 COMMENT '报告排序',
    test_method VARCHAR(50) COMMENT '检验方法',
    status VARCHAR(10) DEFAULT 'ACTIVE' COMMENT '状态：ACTIVE-启用，INACTIVE-停用',
    is_critical TINYINT DEFAULT 0 COMMENT '是否危急值项目：0-否，1-是',
    critical_high DECIMAL(20,4) COMMENT '危急值上限',
    critical_low DECIMAL(20,4) COMMENT '危急值下限',
    remark VARCHAR(500) COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_item_code (item_code),
    INDEX idx_category (category),
    INDEX idx_item_name (item_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检验项目表';

-- =============================================
-- 3. 检验结果明细表 (lab_test_result) - 参考LIS_RESULT
-- =============================================
DROP TABLE IF EXISTS lab_test_result;
CREATE TABLE lab_test_result (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    report_id BIGINT NOT NULL COMMENT '报告ID',
    report_no VARCHAR(20) NOT NULL COMMENT '报告编号',
    sample_id BIGINT NOT NULL COMMENT '标本ID',
    sample_no VARCHAR(20) NOT NULL COMMENT '标本编号',
    item_id BIGINT NOT NULL COMMENT '检验项目ID',
    item_code VARCHAR(20) NOT NULL COMMENT '项目编码',
    item_name VARCHAR(100) NOT NULL COMMENT '项目名称',
    result_value VARCHAR(100) COMMENT '结果值',
    result_text VARCHAR(500) COMMENT '结果描述',
    unit VARCHAR(20) COMMENT '单位',
    reference_range VARCHAR(200) COMMENT '参考值范围',
    high_low_flag VARCHAR(10) COMMENT '高低标志：H-偏高，L-偏低，HH-严重偏高，LL-严重偏低，P-正常',
    is_abnormal TINYINT DEFAULT 0 COMMENT '是否异常：0-正常，1-异常',
    is_critical TINYINT DEFAULT 0 COMMENT '是否危急值：0-否，1-是',
    result_status VARCHAR(10) DEFAULT 'PENDING' COMMENT '结果状态：PENDING-待审核，CONFIRMED-已确认，REPORTED-已报告',
    instrument_id BIGINT COMMENT '检验仪器ID',
    instrument_name VARCHAR(100) COMMENT '仪器名称',
    test_time DATETIME COMMENT '检验时间',
    result_time DATETIME COMMENT '结果时间',
    operator_id BIGINT COMMENT '操作人ID',
    operator_name VARCHAR(50) COMMENT '操作人姓名',
    remark VARCHAR(500) COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_report_id (report_id),
    INDEX idx_sample_id (sample_id),
    INDEX idx_item_id (item_id),
    INDEX idx_sample_no (sample_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检验结果明细表';

-- =============================================
-- 4. 参考值配置表 (lab_item_reference) - 参考LIS_ITEMREFERANCE
-- =============================================
DROP TABLE IF EXISTS lab_item_reference;
CREATE TABLE lab_item_reference (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    item_id BIGINT NOT NULL COMMENT '检验项目ID',
    item_code VARCHAR(20) NOT NULL COMMENT '项目编码',
    item_name VARCHAR(100) COMMENT '项目名称',
    reference_type VARCHAR(20) DEFAULT 'NORMAL' COMMENT '参考值类型：NORMAL-正常参考值，PANIC-危急值',
    gender VARCHAR(10) COMMENT '性别：MALE-男，FEMALE-女，ALL-通用',
    age_min INT COMMENT '最小年龄',
    age_max INT COMMENT '最大年龄',
    age_unit VARCHAR(10) COMMENT '年龄单位：岁、月、天',
    low_limit DECIMAL(20,4) COMMENT '下限',
    high_limit DECIMAL(20,4) COMMENT '上限',
    low_warn DECIMAL(20,4) COMMENT '警告下限',
    high_warn DECIMAL(20,4) COMMENT '警告上限',
    reference_text VARCHAR(200) COMMENT '参考值文本描述',
    sample_type VARCHAR(20) COMMENT '标本类型',
    status VARCHAR(10) DEFAULT 'ACTIVE' COMMENT '状态：ACTIVE-启用，INACTIVE-停用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_item_id (item_id),
    INDEX idx_item_code (item_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='参考值配置表';

-- =============================================
-- 5. 危急值记录表 (lab_panic_record) - 参考Lab_PanicRepTrace
-- =============================================
DROP TABLE IF EXISTS lab_panic_record;
CREATE TABLE lab_panic_record (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    report_id BIGINT COMMENT '报告ID',
    report_no VARCHAR(20) COMMENT '报告编号',
    sample_no VARCHAR(20) COMMENT '标本编号',
    patient_id BIGINT COMMENT '患者ID',
    patient_name VARCHAR(50) COMMENT '患者姓名',
    item_code VARCHAR(20) NOT NULL COMMENT '项目编码',
    item_name VARCHAR(100) NOT NULL COMMENT '项目名称',
    result_value VARCHAR(100) COMMENT '危急值结果',
    reference_range VARCHAR(100) COMMENT '参考值范围',
    unit VARCHAR(20) COMMENT '单位',
    panic_type VARCHAR(20) DEFAULT 'CRITICAL' COMMENT '危急值类型：CRITICAL-危急值，WARNING-警告值',
    status VARCHAR(20) DEFAULT 'PENDING' COMMENT '状态：PENDING-待处理，NOTIFIED-已通知，CONFIRMED-已确认，HANDLED-已处理',
    notify_time DATETIME COMMENT '通知时间',
    notify_method VARCHAR(20) COMMENT '通知方式：PHONE-电话，SMS-短信，SYSTEM-系统',
    notifier_id BIGINT COMMENT '通知人ID',
    notifier_name VARCHAR(50) COMMENT '通知人姓名',
    receiver_id BIGINT COMMENT '接收人ID',
    receiver_name VARCHAR(50) COMMENT '接收人姓名',
    receiver_phone VARCHAR(20) COMMENT '接收人电话',
    confirm_time DATETIME COMMENT '确认时间',
    handle_time DATETIME COMMENT '处理时间',
    handle_desc VARCHAR(500) COMMENT '处理描述',
    remark VARCHAR(500) COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_report_id (report_id),
    INDEX idx_sample_no (sample_no),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='危急值记录表';

-- =============================================
-- 6. 优化现有标本表 (lab_sample)
-- =============================================
ALTER TABLE lab_sample
    ADD COLUMN patient_no VARCHAR(20) COMMENT '患者编号' AFTER patient_id,
    ADD COLUMN patient_id_num VARCHAR(20) COMMENT '身份证号' AFTER patient_name,
    ADD COLUMN patient_phone VARCHAR(20) COMMENT '患者电话' AFTER patient_age,
    ADD COLUMN patient_type VARCHAR(20) COMMENT '患者类型：OUTPATIENT-门诊，INPATIENT-住院' AFTER patient_phone,
    ADD COLUMN ward VARCHAR(50) COMMENT '病房' AFTER patient_type,
    ADD COLUMN bed_no VARCHAR(20) COMMENT '床位号' AFTER ward,
    ADD COLUMN barcode VARCHAR(50) COMMENT '条码号' AFTER sample_no,
    ADD COLUMN collector_id BIGINT COMMENT '采集人ID' AFTER collect_location,
    ADD COLUMN collector_name VARCHAR(50) COMMENT '采集人姓名' AFTER collector_id,
    ADD COLUMN nurse_id BIGINT COMMENT '护士ID' AFTER collector_name,
    ADD COLUMN nurse_name VARCHAR(50) COMMENT '护士姓名' AFTER nurse_id,
    ADD COLUMN receive_location VARCHAR(100) COMMENT '接收地点' AFTER receive_time,
    ADD COLUMN section VARCHAR(50) COMMENT '检验科室' AFTER status,
    ADD COLUMN priority TINYINT DEFAULT 0 COMMENT '优先级：0-普通，1-紧急' AFTER section,
    ADD COLUMN is_abnormal TINYINT DEFAULT 0 COMMENT '是否异常：0-否，1-是' AFTER priority,
    ADD COLUMN reject_reason VARCHAR(500) COMMENT '拒收原因' AFTER is_abnormal,
    ADD INDEX idx_patient_no (patient_no),
    ADD INDEX idx_barcode (barcode),
    ADD INDEX idx_section (section);

-- =============================================
-- 7. 优化现有报告表 (lab_report)
-- =============================================
ALTER TABLE lab_report
    ADD COLUMN patient_no VARCHAR(20) COMMENT '患者编号' AFTER patient_name,
    ADD COLUMN patient_phone VARCHAR(20) COMMENT '患者电话' AFTER patient_no,
    ADD COLUMN patient_type VARCHAR(20) COMMENT '患者类型' AFTER patient_phone,
    ADD COLUMN diagnosis VARCHAR(500) COMMENT '临床诊断' AFTER patient_type,
    ADD COLUMN sample_barcode VARCHAR(50) COMMENT '标本条码' AFTER sample_no,
    ADD COLUMN section VARCHAR(50) COMMENT '检验科室' AFTER test_items,
    ADD COLUMN report_title VARCHAR(100) COMMENT '报告标题' AFTER section,
    ADD COLUMN print_count INT DEFAULT 0 COMMENT '打印次数' AFTER remark,
    ADD COLUMN print_time DATETIME COMMENT '最后打印时间' AFTER print_count,
    ADD COLUMN publish_time DATETIME COMMENT '发布时间' AFTER review_time,
    ADD COLUMN report_path VARCHAR(255) COMMENT '报告文件路径' AFTER publish_time,
    ADD COLUMN is_repeat TINYINT DEFAULT 0 COMMENT '是否复查：0-否，1-是' AFTER report_path,
    ADD COLUMN tat_minutes INT COMMENT 'TAT时间（分钟）' AFTER is_repeat,
    ADD INDEX idx_patient_no (patient_no),
    ADD INDEX idx_sample_barcode (sample_barcode),
    ADD INDEX idx_publish_time (publish_time);

-- =============================================
-- 8. 优化现有标本追踪表 (lab_sample_trace)
-- =============================================
ALTER TABLE lab_sample_trace
    ADD COLUMN operation_time DATETIME COMMENT '操作时间' AFTER operation_desc,
    ADD COLUMN device_id BIGINT COMMENT '设备ID' AFTER operator_name,
    ADD COLUMN device_name VARCHAR(100) COMMENT '设备名称' AFTER device_id,
    ADD COLUMN result_value VARCHAR(100) COMMENT '结果值' AFTER device_name,
    ADD COLUMN remark VARCHAR(500) COMMENT '备注' AFTER result_value;

-- =============================================
-- 9. 科室表 (lab_section) - 新增
-- =============================================
DROP TABLE IF EXISTS lab_section;
CREATE TABLE lab_section (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    section_code VARCHAR(20) NOT NULL COMMENT '科室编码',
    section_name VARCHAR(50) NOT NULL COMMENT '科室名称',
    section_type VARCHAR(20) COMMENT '科室类型：LAB-检验科，CLINICAL-临床科室',
    parent_id BIGINT COMMENT '父科室ID',
    sort_order INT DEFAULT 0 COMMENT '排序',
    status VARCHAR(10) DEFAULT 'ACTIVE' COMMENT '状态',
    remark VARCHAR(500) COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_section_code (section_code),
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='科室表';

-- =============================================
-- 10. 仪器表 (lab_instrument) - 替代原有lab_device，更详细
-- =============================================
DROP TABLE IF EXISTS lab_instrument;
CREATE TABLE lab_instrument (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    instrument_code VARCHAR(20) NOT NULL COMMENT '仪器编码',
    instrument_name VARCHAR(100) NOT NULL COMMENT '仪器名称',
    instrument_model VARCHAR(50) COMMENT '仪器型号',
    manufacturer VARCHAR(100) COMMENT '生产厂家',
    serial_no VARCHAR(50) COMMENT '序列号',
    instrument_type VARCHAR(20) COMMENT '仪器类型：ANALYZER-生化分析仪，HEMATOLOGY-血球仪，URINE-尿分析仪等',
    section_id BIGINT COMMENT '所属科室ID',
    section_name VARCHAR(50) COMMENT '所属科室名称',
    location VARCHAR(100) COMMENT '放置位置',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    comm_type VARCHAR(20) COMMENT '通讯类型：TCP，UDP，COM，HL7',
    comm_params VARCHAR(500) COMMENT '通讯参数',
    status VARCHAR(20) DEFAULT 'IDLE' COMMENT '状态：IDLE-空闲，RUNNING-运行，MAINTENANCE-维护，OFFLINE-离线',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用：0-否，1-是',
    last_connect_time DATETIME COMMENT '最后连接时间',
    last_maintenance_date DATE COMMENT '最后维护日期',
    next_maintenance_date DATE COMMENT '下次维护日期',
    purchase_date DATE COMMENT '购买日期',
    warranty_end_date DATE COMMENT '保修截止日期',
    remark VARCHAR(500) COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_instrument_code (instrument_code),
    INDEX idx_status (status),
    INDEX idx_section_id (section_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='仪器表';

-- 迁移旧设备数据到新仪器表（可选）
-- INSERT INTO lab_instrument (instrument_code, instrument_name, instrument_model, manufacturer, instrument_type, location, status)
-- SELECT device_no, device_name, device_model, manufacturer, device_type, location, status FROM lab_device WHERE deleted = 0;

-- =============================================
-- 插入初始检验项目数据（示例）
-- =============================================
INSERT INTO lab_test_item (item_code, item_name, item_short_name, category, sample_type, result_type, unit, decimal_places, price, is_critical, critical_high, critical_low) VALUES
('WBC', '白细胞计数', 'WBC', 'BLOOD', 'BLOOD', 'NUMERIC', '10^9/L', 2, 25.00, 1, 30.00, 2.00),
('RBC', '红细胞计数', 'RBC', 'BLOOD', 'BLOOD', 'NUMERIC', '10^12/L', 2, 20.00, 0, NULL, NULL),
('HGB', '血红蛋白', 'HGB', 'BLOOD', 'BLOOD', 'NUMERIC', 'g/L', 1, 15.00, 1, 200.00, 60.00),
('HCT', '红细胞压积', 'HCT', 'BLOOD', 'BLOOD', 'NUMERIC', '%', 1, 15.00, 0, NULL, NULL),
('PLT', '血小板计数', 'PLT', 'BLOOD', 'BLOOD', 'NUMERIC', '10^9/L', 1, 25.00, 1, 1000.00, 30.00),
('GLU', '葡萄糖', 'GLU', 'BIOCHEM', 'BLOOD', 'NUMERIC', 'mmol/L', 2, 12.00, 1, 27.80, 2.20),
('ALT', '丙氨酸氨基转移酶', 'ALT', 'BIOCHEM', 'BLOOD', 'NUMERIC', 'U/L', 0, 15.00, 0, NULL, NULL),
('AST', '天门冬氨酸氨基转移酶', 'AST', 'BIOCHEM', 'BLOOD', 'NUMERIC', 'U/L', 0, 15.00, 0, NULL, NULL),
('CREA', '肌酐', 'CREA', 'BIOCHEM', 'BLOOD', 'NUMERIC', 'umol/L', 0, 20.00, 1, 707.00, 44.00),
('BUN', '尿素氮', 'BUN', 'BIOCHEM', 'BLOOD', 'NUMERIC', 'mmol/L', 2, 15.00, 1, 35.70, 3.10);

-- 插入初始科室数据
INSERT INTO lab_section (section_code, section_name, section_type, sort_order) VALUES
('LAB', '检验科', 'LAB', 1),
('BLOOD', '血常规室', 'LAB', 2),
('BIOCHEM', '生化室', 'LAB', 3),
('IMMUNE', '免疫室', 'LAB', 4),
('INNER', '内科', 'CLINICAL', 10),
('SURGERY', '外科', 'CLINICAL', 11),
('PEDIATRICS', '儿科', 'CLINICAL', 12);

-- 插入初始用户（密码: admin123）
INSERT INTO sys_user (username, password, real_name, role, department, status) VALUES
('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '系统管理员', 'ADMIN', '信息中心', 1),
('doctor1', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '张医生', 'DOCTOR', '内科', 1),
('tech1', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '李技师', 'LAB_TECHNICIAN', '检验科', 1);

SELECT 'Database upgrade completed successfully!' AS message;
