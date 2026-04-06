-- =============================================
-- 实验室管理系统测试数据脚本（增强版）
-- 用于测试仪表盘统计、缓存等功能
-- =============================================

USE lab_management;

-- =============================================
-- 清理现有数据
-- =============================================
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM lab_sample;
DELETE FROM lab_sample_trace;
DELETE FROM lab_report;
DELETE FROM sys_user;
SET FOREIGN_KEY_CHECKS = 1;
ALTER TABLE lab_sample AUTO_INCREMENT = 1;
ALTER TABLE lab_sample_trace AUTO_INCREMENT = 1;
ALTER TABLE lab_report AUTO_INCREMENT = 1;
ALTER TABLE sys_user AUTO_INCREMENT = 1;

-- =============================================
-- 插入测试用户数据
-- =============================================
INSERT INTO sys_user (username, password, real_name, role, department, phone, email, status) VALUES
-- 临床医生
('doctor_zhang', '$2a$10$xxx', '张医生', 'DOCTOR', '内科', '13800138001', 'doctor_zhang@hospital.com', 1),
('doctor_wang', '$2a$10$xxx', '王医生', 'DOCTOR', '外科', '13800138002', 'doctor_wang@hospital.com', 1),
-- 检验医师
('tech_li', '$2a$10$xxx', '李技师', 'LAB_TECHNICIAN', '检验科', '13800138003', 'tech_li@hospital.com', 1),
('tech_zhao', '$2a$10$xxx', '赵技师', 'LAB_TECHNICIAN', '检验科', '13800138004', 'tech_zhao@hospital.com', 1),
-- 管理员
('admin', '$2a$10$xxx', '系统管理员', 'ADMIN', '信息科', '13800138000', 'admin@hospital.com', 1);

-- =============================================
-- 插入测试标本数据（用于仪表盘测试）
-- =============================================
-- 今日标本（测试仪表盘今日统计）
INSERT INTO lab_sample (sample_no, patient_name, patient_gender, patient_age, doctor_name, test_items, sample_type, status, create_time, collect_time) VALUES
-- 已采集标本（3个）
('S20240326001', '张三', '男', 30, '张医生', '血常规', 'BLOOD', 'COLLECTED', DATE_SUB(NOW(), INTERVAL 2 HOUR), DATE_SUB(NOW(), INTERVAL 2 HOUR)),
('S20240326002', '李四', '女', 25, '王医生', '尿常规,肝功能', 'URINE', 'COLLECTED', DATE_SUB(NOW(), INTERVAL 3 HOUR), DATE_SUB(NOW(), INTERVAL 3 HOUR)),
('S20240326003', '王五', '男', 45, '张医生', '血脂四项', 'BLOOD', 'COLLECTED', DATE_SUB(NOW(), INTERVAL 4 HOUR), DATE_SUB(NOW(), INTERVAL 4 HOUR)),

-- 运输中标本（2个）
('S20240326004', '赵六', '女', 35, '王医生', '血常规,血糖', 'BLOOD', 'IN_TRANSIT', DATE_SUB(NOW(), INTERVAL 1 HOUR), DATE_SUB(NOW(), INTERVAL 1 HOUR)),
('S20240326005', '孙七', '男', 50, '张医生', '肾功能', 'BLOOD', 'IN_TRANSIT', DATE_SUB(NOW(), INTERVAL 2 HOUR), DATE_SUB(NOW(), INTERVAL 2 HOUR)),

-- 已接收标本（4个）
('S20240326006', '周八', '女', 28, '王医生', '肝功能,肾功能', 'BLOOD', 'RECEIVED', DATE_SUB(NOW(), INTERVAL 3 HOUR), DATE_SUB(NOW(), INTERVAL 3 HOUR)),
('S20240326007', '吴九', '男', 32, '张医生', '甲状腺功能', 'BLOOD', 'RECEIVED', DATE_SUB(NOW(), INTERVAL 4 HOUR), DATE_SUB(NOW(), INTERVAL 4 HOUR)),
('S20240326008', '郑十', '女', 40, '王医生', '血常规,尿常规', 'BLOOD', 'RECEIVED', DATE_SUB(NOW(), INTERVAL 5 HOUR), DATE_SUB(NOW(), INTERVAL 5 HOUR)),
('S20240326009', '钱一', '男', 55, '张医生', '肿瘤标志物', 'BLOOD', 'RECEIVED', DATE_SUB(NOW(), INTERVAL 6 HOUR), DATE_SUB(NOW(), INTERVAL 6 HOUR)),

-- 检验中标本（5个）
('S20240326010', '孙二', '女', 22, '王医生', '血常规', 'BLOOD', 'TESTING', DATE_SUB(NOW(), INTERVAL 1 HOUR), DATE_SUB(NOW(), INTERVAL 1 HOUR)),
('S20240326011', '李三', '男', 38, '张医生', '尿常规', 'URINE', 'TESTING', DATE_SUB(NOW(), INTERVAL 2 HOUR), DATE_SUB(NOW(), INTERVAL 2 HOUR)),
('S20240326012', '王四', '女', 29, '王医生', '肝功能', 'BLOOD', 'TESTING', DATE_SUB(NOW(), INTERVAL 3 HOUR), DATE_SUB(NOW(), INTERVAL 3 HOUR)),
('S20240326013', '赵五', '男', 47, '张医生', '肾功能', 'BLOOD', 'TESTING', DATE_SUB(NOW(), INTERVAL 4 HOUR), DATE_SUB(NOW(), INTERVAL 4 HOUR)),
('S20240326014', '周六', '女', 33, '王医生', '血脂', 'BLOOD', 'TESTING', DATE_SUB(NOW(), INTERVAL 5 HOUR), DATE_SUB(NOW(), INTERVAL 5 HOUR)),

-- 已完成标本（6个）
('S20240326015', '吴七', '男', 41, '张医生', '血常规,尿常规', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 6 HOUR), DATE_SUB(NOW(), INTERVAL 6 HOUR)),
('S20240326016', '郑八', '女', 27, '王医生', '肝功能,肾功能', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 7 HOUR), DATE_SUB(NOW(), INTERVAL 7 HOUR)),
('S20240326017', '王九', '男', 52, '张医生', '甲状腺功能', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 8 HOUR), DATE_SUB(NOW(), INTERVAL 8 HOUR)),
('S20240326018', '李十', '女', 36, '王医生', '肿瘤标志物', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 9 HOUR), DATE_SUB(NOW(), INTERVAL 9 HOUR)),
('S20240326019', '张一', '男', 44, '张医生', '血常规,血糖', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 10 HOUR), DATE_SUB(NOW(), INTERVAL 10 HOUR)),
('S20240326020', '刘二', '女', 31, '王医生', '血脂四项', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 11 HOUR), DATE_SUB(NOW(), INTERVAL 11 HOUR)),

-- 异常标本（2个）
('S20240326021', '陈三', '男', 58, '张医生', '血常规', 'BLOOD', 'ABNORMAL', DATE_SUB(NOW(), INTERVAL 12 HOUR), DATE_SUB(NOW(), INTERVAL 12 HOUR)),
('S20240326022', '林四', '女', 26, '王医生', '尿常规', 'URINE', 'ABNORMAL', DATE_SUB(NOW(), INTERVAL 13 HOUR), DATE_SUB(NOW(), INTERVAL 13 HOUR));

-- 昨日标本（用于对比）
INSERT INTO lab_sample (sample_no, patient_name, patient_gender, patient_age, doctor_name, test_items, sample_type, status, create_time, collect_time) VALUES
('S20240325001', '昨日患者1', '男', 35, '张医生', '血常规', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
('S20240325002', '昨日患者2', '女', 28, '王医生', '尿常规', 'URINE', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
('S20240325003', '昨日患者3', '男', 42, '张医生', '肝功能', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY));

-- 近7天标本数据（用于趋势分析）
INSERT INTO lab_sample (sample_no, patient_name, patient_gender, patient_age, doctor_name, test_items, sample_type, status, create_time, collect_time) VALUES
-- 7天前
('S20240320001', '趋势患者1', '男', 30, '张医生', '血常规', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
('S20240320002', '趋势患者2', '女', 25, '王医生', '尿常规', 'URINE', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
-- 6天前
('S20240321001', '趋势患者3', '男', 40, '张医生', '肝功能', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY)),
('S20240321002', '趋势患者4', '女', 35, '王医生', '肾功能', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY)),
('S20240321003', '趋势患者5', '男', 45, '张医生', '血脂', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY)),
-- 5天前
('S20240322001', '趋势患者6', '女', 28, '王医生', '血常规', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
('S20240322002', '趋势患者7', '男', 32, '张医生', '尿常规', 'URINE', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
('S20240322003', '趋势患者8', '女', 38, '王医生', '肝功能', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
('S20240322004', '趋势患者9', '男', 50, '张医生', '肾功能', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
-- 4天前
('S20240323001', '趋势患者10', '女', 27, '王医生', '血常规,尿常规', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),
('S20240323002', '趋势患者11', '男', 33, '张医生', '肝功能,肾功能', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),
('S20240323003', '趋势患者12', '女', 29, '王医生', '甲状腺功能', 'BLOOD', 'COMPLETED', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY));

-- =============================================
-- 插入标本追踪记录
-- =============================================
-- 为每个标本插入相应的追踪记录
INSERT INTO lab_sample_trace (sample_id, sample_no, operation_type, operation_desc, operator_id, operator_name, location)
SELECT 
    id, sample_no, 
    CASE status 
        WHEN 'COLLECTED' THEN 'COLLECT'
        WHEN 'IN_TRANSIT' THEN 'TRANSPORT'
        WHEN 'RECEIVED' THEN 'RECEIVE'
        WHEN 'TESTING' THEN 'TEST'
        WHEN 'COMPLETED' THEN 'COMPLETE'
        WHEN 'ARCHIVED' THEN 'ARCHIVE'
        WHEN 'ABNORMAL' THEN 'ABNORMAL'
        ELSE 'OTHER'
    END,
    CONCAT('标本', CASE status 
        WHEN 'COLLECTED' THEN '采集'
        WHEN 'IN_TRANSIT' THEN '运输'
        WHEN 'RECEIVED' THEN '接收'
        WHEN 'TESTING' THEN '开始检验'
        WHEN 'COMPLETED' THEN '检验完成'
        WHEN 'ARCHIVED' THEN '归档'
        WHEN 'ABNORMAL' THEN '标记异常'
        ELSE '操作'
    END),
    1, '系统管理员',
    CASE 
        WHEN status = 'COLLECTED' THEN '门诊采集点'
        WHEN status = 'IN_TRANSIT' THEN '运输途中'
        WHEN status IN ('RECEIVED', 'TESTING', 'COMPLETED', 'ABNORMAL') THEN '检验科'
        ELSE '未知位置'
    END
FROM lab_sample;

-- =============================================
-- 插入测试报告数据
-- =============================================
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_name, test_items, status, test_time) VALUES
-- 待审核报告
('R20240326001', 15, 'S20240326015', '吴七', '血常规,尿常规', 'REVIEWING', DATE_SUB(NOW(), INTERVAL 6 HOUR)),
('R20240326002', 16, 'S20240326016', '郑八', '肝功能,肾功能', 'REVIEWING', DATE_SUB(NOW(), INTERVAL 7 HOUR)),
-- 已通过报告
('R20240326003', 17, 'S20240326017', '王九', '甲状腺功能', 'APPROVED', DATE_SUB(NOW(), INTERVAL 8 HOUR)),
('R20240326004', 18, 'S20240326018', '李十', '肿瘤标志物', 'APPROVED', DATE_SUB(NOW(), INTERVAL 9 HOUR)),
-- 已发布报告
('R20240326005', 19, 'S20240326019', '张一', '血常规,血糖', 'PUBLISHED', DATE_SUB(NOW(), INTERVAL 10 HOUR));

-- =============================================
-- 数据验证查询
-- =============================================
SELECT '数据统计:' AS '===== 数据验证 =====';

-- 标本状态统计
SELECT 
    '标本状态统计' AS '统计类型',
    status AS '状态',
    COUNT(*) AS '数量',
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM lab_sample), 2) AS '百分比'
FROM lab_sample 
GROUP BY status 
ORDER BY COUNT(*) DESC;

-- 今日标本统计
SELECT 
    '今日标本统计' AS '统计类型',
    DATE(create_time) AS '日期',
    COUNT(*) AS '数量'
FROM lab_sample 
WHERE DATE(create_time) = CURDATE()
GROUP BY DATE(create_time);

-- 检验项目热度排行
SELECT 
    '热门检验项目' AS '统计类型',
    test_items AS '检验项目',
    COUNT(*) AS '标本数量'
FROM lab_sample 
WHERE DATE(create_time) = CURDATE()
GROUP BY test_items 
ORDER BY COUNT(*) DESC 
LIMIT 5;

-- 标本采集趋势（最近7天）
SELECT 
    '近7天趋势' AS '统计类型',
    DATE(create_time) AS '日期',
    COUNT(*) AS '标本数量'
FROM lab_sample 
WHERE create_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY DATE(create_time)
ORDER BY DATE(create_time);

-- 待办事项统计
SELECT 
    '待办事项' AS '统计类型',
    '待接收标本' AS '待办类型',
    COUNT(*) AS '数量'
FROM lab_sample 
WHERE status IN ('COLLECTED', 'IN_TRANSIT') 
AND DATE(create_time) = CURDATE()
UNION ALL
SELECT 
    '待办事项',
    '检验中标本',
    COUNT(*)
FROM lab_sample 
WHERE status = 'TESTING'
UNION ALL
SELECT 
    '待办事项',
    '异常标本',
    COUNT(*)
FROM lab_sample 
WHERE status = 'ABNORMAL';

-- 报告状态统计
SELECT 
    '报告状态' AS '统计类型',
    status AS '状态',
    COUNT(*) AS '数量'
FROM lab_report 
GROUP BY status;

SELECT '===== 测试数据插入完成 =====' AS '完成状态';