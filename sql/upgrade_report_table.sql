-- =============================================
-- 报告表结构升级脚本（支持双层审核流程）
-- 在原有lab_report表基础上添加双层审核相关字段
-- =============================================

USE lab_management;

-- 为lab_report表添加双层审核相关字段
ALTER TABLE lab_report 
    -- 技术审核信息
    ADD COLUMN technical_reviewer_id BIGINT COMMENT '技术审核人ID',
    ADD COLUMN technical_reviewer_name VARCHAR(50) COMMENT '技术审核人姓名',
    ADD COLUMN technical_review_time DATETIME COMMENT '技术审核时间',
    ADD COLUMN technical_review_result VARCHAR(20) COMMENT '技术审核结果：APPROVED-通过，REJECTED-驳回',
    ADD COLUMN technical_review_comment TEXT COMMENT '技术审核意见',
    
    -- 临床审核信息
    ADD COLUMN clinical_reviewer_id BIGINT COMMENT '临床审核人ID',
    ADD COLUMN clinical_reviewer_name VARCHAR(50) COMMENT '临床审核人姓名',
    ADD COLUMN clinical_review_time DATETIME COMMENT '临床审核时间',
    ADD COLUMN clinical_review_result VARCHAR(20) COMMENT '临床审核结果：APPROVED-通过，REJECTED-驳回',
    ADD COLUMN clinical_review_comment TEXT COMMENT '临床审核意见',
    
    -- AI诊断增强信息
    ADD COLUMN ai_confidence INT COMMENT 'AI诊断置信度（0-100）',
    ADD COLUMN ai_model_version VARCHAR(50) COMMENT 'AI模型版本',
    ADD COLUMN ai_diagnosis_time DATETIME COMMENT 'AI诊断时间',
    
    -- 报告质量信息
    ADD COLUMN abnormal_indicator_count INT DEFAULT 0 COMMENT '异常指标数量',
    ADD COLUMN critical_indicator_count INT DEFAULT 0 COMMENT '危急值数量',
    
    -- 撤销信息
    ADD COLUMN revoked_by BIGINT COMMENT '撤销人ID',
    ADD COLUMN revoked_by_name VARCHAR(50) COMMENT '撤销人姓名',
    ADD COLUMN revoked_time DATETIME COMMENT '撤销时间',
    ADD COLUMN revoked_reason TEXT COMMENT '撤销原因',
    
    -- 归档信息
    ADD COLUMN archived_by BIGINT COMMENT '归档人ID',
    ADD COLUMN archived_by_name VARCHAR(50) COMMENT '归档人姓名',
    ADD COLUMN archived_time DATETIME COMMENT '归档时间';

-- 更新状态字段注释
ALTER TABLE lab_report 
    MODIFY COLUMN status VARCHAR(30) DEFAULT 'PENDING' COMMENT '状态：PENDING-待录入，TECHNICAL_REVIEWING-技术审核中，TECHNICAL_APPROVED-技术审核通过，TECHNICAL_REJECTED-技术审核驳回，CLINICAL_REVIEWING-临床审核中，CLINICAL_APPROVED-临床审核通过，CLINICAL_REJECTED-临床审核驳回，PUBLISHED-已发布，ARCHIVED-已归档，REVOKED-已撤销';

-- 更新现有数据的状态字段（将旧状态转换为新状态）
UPDATE lab_report SET 
    status = CASE 
        WHEN status = 'REVIEWING' THEN 'TECHNICAL_REVIEWING'
        WHEN status = 'APPROVED' THEN 'CLINICAL_APPROVED'
        WHEN status = 'REJECTED' THEN 'TECHNICAL_REJECTED'
        ELSE status
    END,
    -- 将原有审核信息迁移到技术审核字段
    technical_reviewer_id = reviewer_id,
    technical_reviewer_name = reviewer_name,
    technical_review_time = review_time,
    technical_review_result = CASE 
        WHEN status = 'APPROVED' THEN 'APPROVED'
        WHEN status = 'REJECTED' THEN 'REJECTED'
        ELSE NULL
    END,
    technical_review_comment = remark
WHERE status IN ('REVIEWING', 'APPROVED', 'REJECTED');

-- 添加索引以提高查询性能
ALTER TABLE lab_report 
    ADD INDEX idx_technical_reviewer (technical_reviewer_id),
    ADD INDEX idx_clinical_reviewer (clinical_reviewer_id),
    ADD INDEX idx_status_created (status, create_time),
    ADD INDEX idx_published_time (published_time),
    ADD INDEX idx_archived_time (archived_time);

-- 创建报告审核日志表（记录完整的审核历史）
CREATE TABLE IF NOT EXISTS lab_report_review_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    report_id BIGINT NOT NULL COMMENT '报告ID',
    report_no VARCHAR(20) NOT NULL COMMENT '报告编号',
    review_type VARCHAR(20) NOT NULL COMMENT '审核类型：TECHNICAL-技术审核，CLINICAL-临床审核',
    review_action VARCHAR(20) NOT NULL COMMENT '审核动作：SUBMIT-提交审核，REVIEW-进行审核，REVOKE-撤销，PUBLISH-发布，ARCHIVE-归档',
    reviewer_id BIGINT COMMENT '审核人ID',
    reviewer_name VARCHAR(50) COMMENT '审核人姓名',
    review_result VARCHAR(20) COMMENT '审核结果：APPROVED-通过，REJECTED-驳回，PENDING-待处理',
    review_comment TEXT COMMENT '审核意见',
    old_status VARCHAR(30) COMMENT '原状态',
    new_status VARCHAR(30) COMMENT '新状态',
    duration_seconds INT COMMENT '审核处理时长（秒）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_report_id (report_id),
    INDEX idx_report_no (report_no),
    INDEX idx_review_type (review_type),
    INDEX idx_review_action (review_action),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报告审核日志表';

-- 创建异常指标记录表（存储详细的异常指标信息）
CREATE TABLE IF NOT EXISTS lab_report_abnormal_indicator (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    report_id BIGINT NOT NULL COMMENT '报告ID',
    report_no VARCHAR(20) NOT NULL COMMENT '报告编号',
    indicator_name VARCHAR(100) NOT NULL COMMENT '指标名称',
    indicator_code VARCHAR(50) COMMENT '指标编码',
    result_value VARCHAR(50) NOT NULL COMMENT '检验结果值',
    unit VARCHAR(20) COMMENT '单位',
    reference_low VARCHAR(50) COMMENT '参考范围下限',
    reference_high VARCHAR(50) COMMENT '参考范围上限',
    abnormal_flag VARCHAR(20) NOT NULL COMMENT '异常标志：NORMAL-正常，LOW-偏低，HIGH-偏高，CRITICAL_LOW-危急值低，CRITICAL_HIGH-危急值高',
    abnormal_severity VARCHAR(20) COMMENT '异常程度：MILD-轻度，MODERATE-中度，SEVERE-重度',
    clinical_significance TEXT COMMENT '临床意义',
    ai_analysis TEXT COMMENT 'AI分析结果',
    technician_note TEXT COMMENT '技师备注',
    reviewer_note TEXT COMMENT '审核人备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_report_id (report_id),
    INDEX idx_indicator_name (indicator_name),
    INDEX idx_abnormal_flag (abnormal_flag),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报告异常指标记录表';

-- 创建检验结果结构化存储表（可选，用于存储详细的检验结果数据）
CREATE TABLE IF NOT EXISTS lab_report_test_result (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    report_id BIGINT NOT NULL COMMENT '报告ID',
    report_no VARCHAR(20) NOT NULL COMMENT '报告编号',
    item_name VARCHAR(100) NOT NULL COMMENT '检验项目名称',
    item_code VARCHAR(50) COMMENT '检验项目编码',
    result_value VARCHAR(200) NOT NULL COMMENT '检验结果值',
    unit VARCHAR(20) COMMENT '单位',
    reference_range VARCHAR(100) COMMENT '参考范围',
    abnormal_flag VARCHAR(20) DEFAULT 'NORMAL' COMMENT '异常标志',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_report_id (report_id),
    INDEX idx_item_name (item_name),
    INDEX idx_abnormal_flag (abnormal_flag)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检验结果结构化存储表';

-- 验证表结构更新结果
SELECT 
    '表结构更新完成' AS '状态',
    'lab_report' AS '表名',
    COUNT(*) AS '字段数量'
FROM information_schema.columns 
WHERE table_schema = 'lab_management' AND table_name = 'lab_report'
UNION ALL
SELECT 
    '新增表' AS '状态',
    table_name AS '表名',
    COUNT(*) AS '字段数量'
FROM information_schema.columns 
WHERE table_schema = 'lab_management' 
    AND table_name IN ('lab_report_review_log', 'lab_report_abnormal_indicator', 'lab_report_test_result')
GROUP BY table_name;

-- 显示更新后的字段信息
SELECT 
    column_name AS '字段名',
    column_type AS '字段类型',
    column_comment AS '字段说明'
FROM information_schema.columns 
WHERE table_schema = 'lab_management' AND table_name = 'lab_report'
    AND column_name IN ('technical_reviewer_id', 'clinical_reviewer_id', 'ai_confidence', 'abnormal_indicator_count')
ORDER BY ordinal_position;