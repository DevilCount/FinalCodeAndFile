-- =============================================
-- Iter2 修复: 创建缺失的数据库表
-- =============================================

USE lab_management;

-- 1. 患者信息表 (lab_patient)
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
    card_no VARCHAR(50) COMMENT '就诊卡号',
    hosp_no VARCHAR(50) COMMENT '住院号',
    ward VARCHAR(50) COMMENT '病房',
    bed_no VARCHAR(20) COMMENT '床位号',
    department VARCHAR(50) COMMENT '科室',
    diagnosis VARCHAR(500) COMMENT '临床诊断',
    status TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_patient_no (patient_no),
    INDEX idx_id_num (id_num),
    INDEX idx_patient_name (patient_name),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='患者信息表';

-- 2. 检验项目表 (lab_test_item)
DROP TABLE IF EXISTS lab_test_item;
CREATE TABLE lab_test_item (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    item_code VARCHAR(20) NOT NULL COMMENT '项目编码',
    item_name VARCHAR(100) NOT NULL COMMENT '项目名称',
    item_short_name VARCHAR(50) COMMENT '项目简称',
    english_name VARCHAR(100) COMMENT '英文名称',
    category VARCHAR(50) COMMENT '项目分类：BLOOD-血常规，URINE-尿常规，BIOCHEM-生化，IMMUNE-免疫等',
    sample_type VARCHAR(20) COMMENT '适用标本类型',
    result_type VARCHAR(10) COMMENT '结果类型：NUMERIC-数值，TEXT-文本',
    unit VARCHAR(20) COMMENT '单位',
    decimal_places INT DEFAULT 2 COMMENT '小数位数',
    price DECIMAL(10,2) COMMENT '价格',
    is_critical TINYINT DEFAULT 0 COMMENT '是否危急值项目：0-否，1-是',
    critical_high DECIMAL(20,4) COMMENT '危急值上限',
    critical_low DECIMAL(20,4) COMMENT '危急值下限',
    status VARCHAR(10) DEFAULT 'ACTIVE' COMMENT '状态：ACTIVE-启用，INACTIVE-停用',
    remark VARCHAR(500) COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_item_code (item_code),
    INDEX idx_category (category),
    INDEX idx_item_name (item_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检验项目表';

-- 3. 检验结果明细表 (lab_test_result)
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
    unit VARCHAR(20) COMMENT '单位',
    reference_range VARCHAR(200) COMMENT '参考值范围',
    high_low_flag VARCHAR(10) COMMENT '高低标志：H-偏高，L-偏低，P-正常',
    is_abnormal TINYINT DEFAULT 0 COMMENT '是否异常：0-正常，1-异常',
    is_critical TINYINT DEFAULT 0 COMMENT '是否危急值：0-否，1-是',
    result_status VARCHAR(10) DEFAULT 'PENDING' COMMENT '结果状态',
    test_time DATETIME COMMENT '检验时间',
    operator_id BIGINT COMMENT '操作人ID',
    operator_name VARCHAR(50) COMMENT '操作人姓名',
    remark VARCHAR(500) COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_report_id (report_id),
    INDEX idx_sample_id (sample_id),
    INDEX idx_item_id (item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检验结果明细表';

-- =============================================
-- 插入初始测试数据
-- =============================================

-- 插入检验项目数据
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

-- 插入示例患者数据
INSERT INTO lab_patient (patient_no, patient_name, gender, gender_desc, birthday, age, age_unit, phone, address, patient_type, department, diagnosis, status) VALUES
('P20260405001', '张三', '1', '男', '1985-06-15', 40, '岁', '13800001001', '北京市朝阳区建设路123号', 'OUTPATIENT', '内科', '高血压', 1),
('P20260405002', '李四', '2', '女', '1990-03-22', 35, '岁', '13800001002', '上海市浦东新区世纪大道456号', 'INPATIENT', '外科', '胆结石', 1),
('P20260405003', '王五', '1', '男', '1978-11-08', 47, '岁', '13800001003', '广州市天河区珠江新城789号', 'OUTPATIENT', '内科', '糖尿病', 1);
