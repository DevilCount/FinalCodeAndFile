-- =====================================================
-- 实验室管理系统 - 扩充数据库脚本
-- 参考成熟LIS系统数据字典设计
-- =====================================================

-- =====================================================
-- 1. 检验项目表 (lis_item)
-- =====================================================
CREATE TABLE IF NOT EXISTS lis_item (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    item_code       VARCHAR(20)     NOT NULL UNIQUE COMMENT '项目编码',
    item_name       VARCHAR(64)     NOT NULL COMMENT '项目名称',
    item_num        VARCHAR(20)     COMMENT '项目简码',
    eng_short_name  VARCHAR(20)     COMMENT '英文缩写',
    item_type_id    INT             COMMENT '项目分类ID',
    sample_code     VARCHAR(20)     COMMENT '标本类型编码',
    result_type     CHAR(1)         DEFAULT '0' COMMENT '结果类型: 0-数值 1-定性 2-计算公式',
    unit            VARCHAR(20)     COMMENT '单位',
    decimal_places  INT             DEFAULT 2 COMMENT '小数位数',
    price           DECIMAL(10,2)   COMMENT '价格',
    default_value   VARCHAR(20)     COMMENT '默认值',
    print_order     INT             DEFAULT 0 COMMENT '打印顺序',
    status          TINYINT         DEFAULT 1 COMMENT '状态: 0-停用 1-启用',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted         TINYINT         DEFAULT 0 COMMENT '删除标志: 0-未删除 1-已删除',
    INDEX idx_item_code (item_code),
    INDEX idx_item_name (item_name)
) COMMENT '检验项目表';

-- =====================================================
-- 2. 标本类型表 (lis_specimen_type)
-- =====================================================
CREATE TABLE IF NOT EXISTS lis_specimen_type (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    type_code       VARCHAR(20)     NOT NULL UNIQUE COMMENT '类型编码',
    type_name       VARCHAR(64)     NOT NULL COMMENT '类型名称',
    color           VARCHAR(20)     COMMENT '颜色标识',
    volume          VARCHAR(20)     COMMENT '采血量',
    additive        VARCHAR(100)    COMMENT '添加剂',
    storage_conditions VARCHAR(100) COMMENT '保存条件',
    barcode_prefix  VARCHAR(10)     COMMENT '条码前缀',
    print_order     INT             DEFAULT 0 COMMENT '显示顺序',
    status          TINYINT         DEFAULT 1 COMMENT '状态: 0-停用 1-启用',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted         TINYINT         DEFAULT 0 COMMENT '删除标志',
    INDEX idx_type_code (type_code)
) COMMENT '标本类型表';

-- =====================================================
-- 3. 参考值表 (lis_item_reference)
-- =====================================================
CREATE TABLE IF NOT EXISTS lis_item_reference (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    item_id         BIGINT          NOT NULL COMMENT '检验项目ID',
    reference_type  VARCHAR(20)     DEFAULT 'NORMAL' COMMENT '参考值类型: NORMAL-正常参考值 PANIC-危急值',
    min_value       DECIMAL(10,4)   COMMENT '最小值',
    max_value       DECIMAL(10,4)   COMMENT '最大值',
    reference_range VARCHAR(500)    COMMENT '参考范围描述',
    gender          VARCHAR(10)     COMMENT '性别: Male/Female/All',
    age_min         INT             COMMENT '最小年龄(岁)',
    age_max         INT             COMMENT '最大年龄(岁)',
    age_unit        VARCHAR(10)     COMMENT '年龄单位:岁/月/天',
    department      VARCHAR(50)     COMMENT '科室',
    sample_type     VARCHAR(20)     COMMENT '标本类型',
    print_range     VARCHAR(200)    COMMENT '打印显示范围',
    status          TINYINT         DEFAULT 1 COMMENT '状态: 0-停用 1-启用',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_item_id (item_id),
    INDEX idx_reference_type (reference_type)
) COMMENT '检验项目参考值表';

-- =====================================================
-- 4. 危急值记录表 (lis_panic_record)
-- =====================================================
CREATE TABLE IF NOT EXISTS lis_panic_record (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    report_id       BIGINT          COMMENT '报告ID',
    sample_no       VARCHAR(50)     COMMENT '标本编号',
    patient_id      BIGINT          COMMENT '患者ID',
    patient_name    VARCHAR(64)     COMMENT '患者姓名',
    item_code       VARCHAR(20)     COMMENT '检验项目编码',
    item_name       VARCHAR(64)     COMMENT '检验项目名称',
    result_value    VARCHAR(255)    COMMENT '检验结果',
    reference_range VARCHAR(500)    COMMENT '参考范围',
    panic_value     VARCHAR(100)    COMMENT '危急值',
    status          VARCHAR(20)     DEFAULT 'PENDING' COMMENT '状态: PENDING-待处理 NOTIFIED-已通知 CONFIRMED-已确认',
    notify_time     DATETIME        COMMENT '通知时间',
    notify_method   VARCHAR(20)     COMMENT '通知方式: 电话/短信/系统',
    notified_person VARCHAR(64)     COMMENT '被通知人',
    confirm_time    DATETIME        COMMENT '确认时间',
    confirm_person  VARCHAR(64)     COMMENT '确认人',
    remark          VARCHAR(500)   COMMENT '备注',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_sample_no (sample_no),
    INDEX idx_status (status)
) COMMENT '危急值记录表';

-- =====================================================
-- 5. 检验组合/套餐表 (lis_test_group)
-- =====================================================
CREATE TABLE IF NOT EXISTS lis_test_group (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    group_code      VARCHAR(20)     NOT NULL UNIQUE COMMENT '组合编码',
    group_name      VARCHAR(64)     NOT NULL COMMENT '组合名称',
    price           DECIMAL(10,2)   COMMENT '价格',
    specimen_type   VARCHAR(20)     COMMENT '默认标本类型',
    report_days     INT             DEFAULT 1 COMMENT '报告天数',
    department      VARCHAR(50)     COMMENT '适用科室',
    description     VARCHAR(500)    COMMENT '说明',
    print_order     INT             DEFAULT 0 COMMENT '打印顺序',
    status          TINYINT         DEFAULT 1 COMMENT '状态: 0-停用 1-启用',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted         TINYINT         DEFAULT 0 COMMENT '删除标志',
    INDEX idx_group_code (group_code)
) COMMENT '检验组合/套餐表';

-- =====================================================
-- 6. 组合项目明细表 (lis_group_item)
-- =====================================================
CREATE TABLE IF NOT EXISTS lis_group_item (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    group_id        BIGINT          NOT NULL COMMENT '组合ID',
    item_id         BIGINT          NOT NULL COMMENT '项目ID',
    print_order     INT             DEFAULT 0 COMMENT '打印顺序',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_group_id (group_id),
    INDEX idx_item_id (item_id)
) COMMENT '组合项目明细表';

-- =====================================================
-- 7. 设备表 (lab_device) - 扩充字段
-- =====================================================
ALTER TABLE lab_device 
ADD COLUMN device_brand VARCHAR(50) COMMENT '设备品牌' AFTER device_name,
ADD COLUMN device_model VARCHAR(50) COMMENT '设备型号' AFTER device_brand,
ADD COLUMN device_sn VARCHAR(50) COMMENT '设备序列号' AFTER device_model,
ADD COLUMN ip_address VARCHAR(50) COMMENT 'IP地址' AFTER device_sn,
ADD COLUMN port INT COMMENT '通讯端口' AFTER ip_address,
ADD COLUMN last_comm_time DATETIME COMMENT '最后通讯时间' AFTER port,
ADD COLUMN comm_status VARCHAR(20) DEFAULT 'OFFLINE' COMMENT '通讯状态: ONLINE/OFFLINE/ERROR' AFTER last_comm_time;

-- =====================================================
-- 8. 系统操作日志表 (sys_log)
-- =====================================================
CREATE TABLE IF NOT EXISTS sys_log (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    log_type        VARCHAR(20)     COMMENT '日志类型: OPERATE-操作日志 LOGIN-登录日志 EXCEPTION-异常日志',
    operation       VARCHAR(50)     COMMENT '操作名称',
    request_method  VARCHAR(10)     COMMENT '请求方法',
    request_url     VARCHAR(255)    COMMENT '请求URL',
    request_params  TEXT            COMMENT '请求参数',
    response_result TEXT            COMMENT '返回结果',
    request_time    BIGINT          COMMENT '请求耗时(毫秒)',
    ip_address      VARCHAR(50)    COMMENT 'IP地址',
    user_agent      VARCHAR(500)   COMMENT '用户代理',
    user_id         BIGINT          COMMENT '操作用户ID',
    username        VARCHAR(50)     COMMENT '操作用户名',
    operation_time  DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    error_message   TEXT            COMMENT '异常信息',
    INDEX idx_log_type (log_type),
    INDEX idx_operation (operation),
    INDEX idx_user_id (user_id),
    INDEX idx_operation_time (operation_time)
) COMMENT '系统操作日志表';

-- =====================================================
-- 9. 登录日志表 (sys_login_log)
-- =====================================================
CREATE TABLE IF NOT EXISTS sys_login_log (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    username        VARCHAR(50)     COMMENT '用户名',
    login_status    VARCHAR(10)     COMMENT '登录状态: SUCCESS/FAIL',
    login_type      VARCHAR(20)     COMMENT '登录类型: PASSWORD/WECHAT/QRCODE',
    ip_address      VARCHAR(50)    COMMENT 'IP地址',
    user_agent      VARCHAR(500)   COMMENT '用户代理',
    login_time      DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    error_message   VARCHAR(255)    COMMENT '错误信息',
    session_id      VARCHAR(100)   COMMENT 'Session ID',
    INDEX idx_username (username),
    INDEX idx_login_time (login_time)
) COMMENT '系统登录日志表';

-- =====================================================
-- 10. 字典数据表 (sys_dict_data)
-- =====================================================
CREATE TABLE IF NOT EXISTS sys_dict_data (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    dict_type       VARCHAR(50)     NOT NULL COMMENT '字典类型',
    dict_label      VARCHAR(100)    NOT NULL COMMENT '字典标签',
    dict_value      VARCHAR(100)    NOT NULL COMMENT '字典键值',
    dict_sort       INT             DEFAULT 0 COMMENT '字典排序',
    status          TINYINT         DEFAULT 1 COMMENT '状态: 0-停用 1-启用',
    default_flag    CHAR(1)         DEFAULT 'N' COMMENT '是否默认: Y-是 N-否',
    remark          VARCHAR(500)    COMMENT '备注',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_dict_type (dict_type),
    INDEX idx_dict_label (dict_label)
) COMMENT '字典数据表';

-- =====================================================
-- 初始化字典数据
-- =====================================================
-- 标本状态字典
INSERT INTO sys_dict_data (dict_type, dict_label, dict_value, dict_sort, default_flag) VALUES
('specimen_status', '已创建', 'CREATED', 1, 'Y'),
('specimen_status', '已采集', 'COLLECTED', 2, 'N'),
('specimen_status', '运输中', 'IN_TRANSIT', 3, 'N'),
('specimen_status', '已接收', 'RECEIVED', 4, 'N'),
('specimen_status', '检验中', 'TESTING', 5, 'N'),
('specimen_status', '已完成', 'COMPLETED', 6, 'N'),
('specimen_status', '已归档', 'ARCHIVED', 7, 'N'),
('specimen_status', '异常', 'ABNORMAL', 8, 'N');

-- 报告状态字典
INSERT INTO sys_dict_data (dict_type, dict_label, dict_value, dict_sort, default_flag) VALUES
('report_status', '待审核', 'PENDING', 1, 'Y'),
('report_status', '审核中', 'REVIEWING', 2, 'N'),
('report_status', '已通过', 'APPROVED', 3, 'N'),
('report_status', '已拒绝', 'REJECTED', 4, 'N'),
('report_status', '已发布', 'PUBLISHED', 5, 'N');

-- 危急值状态字典
INSERT INTO sys_dict_data (dict_type, dict_label, dict_value, dict_sort, default_flag) VALUES
('panic_status', '待处理', 'PENDING', 1, 'Y'),
('panic_status', '已通知', 'NOTIFIED', 2, 'N'),
('panic_status', '已确认', 'CONFIRMED', 3, 'N');

-- 用户角色字典
INSERT INTO sys_dict_data (dict_type, dict_label, dict_value, dict_sort, default_flag) VALUES
('user_role', '管理员', 'ADMIN', 1, 'N'),
('user_role', '医生', 'DOCTOR', 2, 'N'),
('user_role', '检验技师', 'LAB_TECHNICIAN', 3, 'N'),
('user_role', '护士', 'NURSE', 4, 'N');

-- =====================================================
-- 11. 缓存管理表 (sys_cache)
-- =====================================================
CREATE TABLE IF NOT EXISTS sys_cache (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    cache_key       VARCHAR(100)    NOT NULL UNIQUE COMMENT '缓存Key',
    cache_value     TEXT            COMMENT '缓存Value',
    expire_time     DATETIME        COMMENT '过期时间',
    cache_type      VARCHAR(50)     DEFAULT 'DEFAULT' COMMENT '缓存类型',
    description     VARCHAR(255)    COMMENT '描述',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_cache_key (cache_key),
    INDEX idx_expire_time (expire_time)
) COMMENT '缓存管理表';

-- =====================================================
-- 12. 定时任务调度表 (sys_job)
-- =====================================================
CREATE TABLE IF NOT EXISTS sys_job (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    job_name        VARCHAR(50)     NOT NULL COMMENT '任务名称',
    job_group       VARCHAR(50)     DEFAULT 'DEFAULT' COMMENT '任务分组',
    job_type        VARCHAR(20)     COMMENT '任务类型: QUARTZ/SPRING_BEAN',
    cron_expression VARCHAR(50)     COMMENT 'Cron表达式',
    bean_class      VARCHAR(255)    COMMENT 'Bean类名',
    method_name     VARCHAR(50)     COMMENT '方法名',
    method_params   VARCHAR(255)   COMMENT '方法参数',
    description     VARCHAR(255)    COMMENT '任务描述',
    status          VARCHAR(20)     DEFAULT 'PAUSED' COMMENT '状态: RUNNING/PAUSED',
    concurrent      CHAR(1)         DEFAULT 'Y' COMMENT '是否并发: Y-是 N-否',
    create_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_job_name (job_name),
    INDEX idx_job_group (job_group),
    INDEX idx_status (status)
) COMMENT '定时任务调度表';
