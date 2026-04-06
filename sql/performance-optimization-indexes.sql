-- =============================================
-- 实验室管理系统性能优化 - 数据库索引脚本
-- 创建时间: 2026-04-01
-- 描述: 添加关键索引以优化查询性能
-- =============================================

USE lab_management;

-- =============================================
-- 用户表索引优化
-- =============================================
-- 已有的索引: uk_username, idx_role
-- 添加复合索引优化常见查询
CREATE INDEX IF NOT EXISTS idx_user_role_status ON sys_user(role, status);
CREATE INDEX IF NOT EXISTS idx_user_create_time ON sys_user(create_time);

-- =============================================
-- 标本表索引优化
-- =============================================
-- 已有的索引: uk_sample_no, idx_patient_id, idx_status, idx_create_time

-- 优化按日期范围查询
CREATE INDEX IF NOT EXISTS idx_sample_create_time_deleted ON lab_sample(create_time, deleted);

-- 优化状态+日期的复合查询
CREATE INDEX IF NOT EXISTS idx_sample_status_create_time ON lab_sample(status, create_time);

-- 优化患者+状态查询
CREATE INDEX IF NOT EXISTS idx_sample_patient_status ON lab_sample(patient_id, status);

-- 优化搜索查询 (sample_no, patient_name, doctor_name)
CREATE INDEX IF NOT EXISTS idx_sample_patient_name ON lab_sample(patient_name);
CREATE INDEX IF NOT EXISTS idx_sample_doctor_name ON lab_sample(doctor_name);

-- 优化标本类型查询
CREATE INDEX IF NOT EXISTS idx_sample_type ON lab_sample(sample_type);

-- 优化复合筛选查询
CREATE INDEX IF NOT EXISTS idx_sample_status_type_create ON lab_sample(status, sample_type, create_time);

-- =============================================
-- 标本追踪记录表索引优化
-- =============================================
-- 已有的索引: idx_sample_id, idx_sample_no

-- 优化按操作类型查询
CREATE INDEX IF NOT EXISTS idx_sample_trace_operation ON lab_sample_trace(operation_type);

-- 优化按操作人和时间查询
CREATE INDEX IF NOT EXISTS idx_sample_trace_operator_time ON lab_sample_trace(operator_id, create_time);

-- 复合索引优化标本+操作查询
CREATE INDEX IF NOT EXISTS idx_sample_trace_sample_operation ON lab_sample_trace(sample_id, operation_type, create_time);

-- =============================================
-- 检验报告表索引优化
-- =============================================
-- 已有的索引: uk_report_no, idx_sample_id, idx_patient_id, idx_status, idx_create_time

-- 优化状态+时间查询
CREATE INDEX IF NOT EXISTS idx_report_status_create_time ON lab_report(status, create_time);

-- 优化患者+状态查询
CREATE INDEX IF NOT EXISTS idx_report_patient_status ON lab_report(patient_id, status);

-- 优化检验医师查询
CREATE INDEX IF NOT EXISTS idx_report_technician ON lab_report(technician_id);

-- 优化审核医师查询
CREATE INDEX IF NOT EXISTS idx_report_reviewer ON lab_report(reviewer_id);

-- 优化复合查询：状态+检验医师
CREATE INDEX IF NOT EXISTS idx_report_status_technician ON lab_report(status, technician_id);

-- 优化复合查询：状态+审核医师
CREATE INDEX IF NOT EXISTS idx_report_status_reviewer ON lab_report(status, reviewer_id);

-- 优化标本编号查询
CREATE INDEX IF NOT EXISTS idx_report_sample_no ON lab_report(sample_no);

-- =============================================
-- 设备表索引优化
-- =============================================
-- 已有的索引: uk_device_no, idx_status

-- 优化设备类型查询
CREATE INDEX IF NOT EXISTS idx_device_type ON lab_device(device_type);

-- 优化位置查询
CREATE INDEX IF NOT EXISTS idx_device_location ON lab_device(location);

-- 优化状态+类型查询
CREATE INDEX IF NOT EXISTS idx_device_status_type ON lab_device(status, device_type);

-- =============================================
-- 查询性能分析提示
-- =============================================
-- 执行以下命令查看索引使用情况:
-- SHOW INDEX FROM lab_sample;
-- SHOW INDEX FROM lab_report;
-- 
-- 执行以下命令分析慢查询:
-- SET GLOBAL slow_query_log = 'ON';
-- SET GLOBAL long_query_time = 1;
-- 
-- 使用EXPLAIN分析具体查询:
-- EXPLAIN SELECT * FROM lab_sample WHERE status = 'COLLECTED' AND DATE(create_time) = CURDATE();
-- 
-- 注意事项:
-- 1. 索引会增加写入操作的开销，请根据实际读写比例调整
-- 2. 定期使用 ANALYZE TABLE 更新表统计信息
-- 3. 监控索引使用情况，删除未使用的索引
-- 4. 对于大表，考虑使用pt-online-schema-change等工具在线添加索引
