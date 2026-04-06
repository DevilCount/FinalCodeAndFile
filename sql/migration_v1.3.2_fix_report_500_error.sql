-- =============================================
-- Report Service 500错误修复 - 数据库迁移脚本
-- 版本: v1.3.2
-- 日期: 2026-04-02
-- 问题: lab_report表缺少30个字段，导致MyBatis-Plus操作失败
-- =============================================

USE lab_management;

-- =============================================
-- 1. AI诊断相关字段（3个）
-- =============================================
ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS ai_confidence INT COMMENT 'AI诊断置信度（0-100）' AFTER ai_diagnosis;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS ai_model_version VARCHAR(50) COMMENT 'AI模型版本' AFTER ai_confidence;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS ai_diagnosis_time DATETIME COMMENT 'AI诊断时间' AFTER ai_model_version;

-- =============================================
-- 2. 技术审核相关字段（5个）
-- =============================================
ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS technical_reviewer_id BIGINT COMMENT '技术审核人ID' AFTER reviewer_name;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS technical_reviewer_name VARCHAR(50) COMMENT '技术审核人姓名' AFTER technical_reviewer_id;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS technical_review_time DATETIME COMMENT '技术审核时间' AFTER technical_reviewer_name;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS technical_review_result VARCHAR(20) COMMENT '技术审核结果：APPROVED-通过，REJECTED-驳回' AFTER technical_review_time;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS technical_review_comment VARCHAR(500) COMMENT '技术审核意见' AFTER technical_review_result;

-- =============================================
-- 3. 临床审核相关字段（5个）
-- =============================================
ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS clinical_reviewer_id BIGINT COMMENT '临床审核人ID' AFTER technical_review_comment;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS clinical_reviewer_name VARCHAR(50) COMMENT '临床审核人姓名' AFTER clinical_reviewer_id;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS clinical_review_time DATETIME COMMENT '临床审核时间' AFTER clinical_reviewer_name;

ALTER TABLE lab_report 
ADD COLUMN IF NOT exists clinical_review_result VARCHAR(20) COMMENT '临床审核结果：APPROVED-通过，REJECTED-驳回' AFTER clinical_review_time;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS clinical_review_comment VARCHAR(500) COMMENT '临床审核意见' AFTER clinical_review_result;

-- =============================================
-- 4. 异常指标字段（2个）
-- =============================================
ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS abnormal_indicator_count INT DEFAULT 0 COMMENT '异常指标数量' AFTER remark;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS critical_indicator_count INT DEFAULT 0 COMMENT '危急值数量' AFTER abnormal_indicator_count;

-- =============================================
-- 5. 撤销相关字段（4个）
-- =============================================
ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS revoked_by BIGINT COMMENT '撤销人ID' AFTER critical_indicator_count;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS revoked_by_name VARCHAR(50) COMMENT '撤销人姓名' AFTER revoked_by;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS revoked_time DATETIME COMMENT '撤销时间' AFTER revoked_by_name;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS revoked_reason VARCHAR(500) COMMENT '撤销原因' AFTER revoked_time;

-- =============================================
-- 6. 归档相关字段（3个）
-- =============================================
ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS archived_by BIGINT COMMENT '归档人ID' AFTER revoked_reason;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS archived_by_name VARCHAR(50) COMMENT '归档人姓名' AFTER archived_by;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS archived_time DATETIME COMMENT '归档时间' AFTER archived_by_name;

-- =============================================
-- 7. 打印相关字段（2个）
-- =============================================
ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS print_count INT DEFAULT 0 COMMENT '打印次数' AFTER archived_time;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS print_time DATETIME COMMENT '首次打印时间' AFTER print_count;

-- =============================================
-- 8. 发布相关字段（2个）
-- =============================================
ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS published_by BIGINT COMMENT '发布人ID' AFTER published_time;

ALTER TABLE lab_report 
ADD COLUMN IF NOT EXISTS published_by_name VARCHAR(50) COMMENT '发布人姓名' AFTER published_by;

-- =============================================
-- 9. 添加索引优化查询性能
-- =============================================
CREATE INDEX IF NOT EXISTS idx_technical_reviewer_id ON lab_report(technical_reviewer_id);
CREATE INDEX IF NOT EXISTS idx_clinical_reviewer_id ON lab_report(clinical_reviewer_id);

-- =============================================
-- 验证：检查表结构是否完整
-- =============================================
SELECT COUNT(*) AS total_columns 
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'lab_management' 
AND TABLE_NAME = 'lab_report';

-- 预期结果：48-50个字段（包含id, deleted, create_time, update_time等系统字段）
