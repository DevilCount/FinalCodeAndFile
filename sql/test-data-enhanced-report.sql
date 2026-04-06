-- =============================================
-- 增强版报告服务测试数据脚本
-- 测试双层审核流程、AI诊断集成、统计分析等
-- =============================================

USE lab_management;

-- 清空相关表数据（谨慎操作，仅在测试环境使用）
TRUNCATE TABLE lab_report;
TRUNCATE TABLE lab_report_review_log;
TRUNCATE TABLE lab_report_abnormal_indicator;
TRUNCATE TABLE lab_report_test_result;

-- ==================== 插入测试报告数据 ====================

-- 1. 待录入结果的报告 (PENDING)
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        status, test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240326001', 1, 'SAMPLE001', 1, '张三', '血常规', 'PENDING', 
     '2024-03-26 08:30:00', '2024-03-26 08:30:00', '2024-03-26 08:30:00', 0),
    ('REP20240326002', 2, 'SAMPLE002', 2, '李四', '尿常规', 'PENDING', 
     '2024-03-26 09:15:00', '2024-03-26 09:15:00', '2024-03-26 09:15:00', 0),
    ('REP20240326003', 3, 'SAMPLE003', 3, '王五', '肝功能', 'PENDING', 
     '2024-03-26 10:00:00', '2024-03-26 10:00:00', '2024-03-26 10:00:00', 0);

-- 2. 技术审核中的报告 (TECHNICAL_REVIEWING)
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        technician_id, technician_name, status, test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240325001', 4, 'SAMPLE004', 4, '赵六', '血常规', 
     101, '技师张', 'TECHNICAL_REVIEWING', '2024-03-25 14:30:00', '2024-03-25 14:30:00', '2024-03-25 14:30:00', 0),
    ('REP20240325002', 5, 'SAMPLE005', 5, '钱七', '肾功能', 
     102, '技师王', 'TECHNICAL_REVIEWING', '2024-03-25 15:45:00', '2024-03-25 15:45:00', '2024-03-25 15:45:00', 0),
    ('REP20240325003', 6, 'SAMPLE006', 6, '孙八', '血脂', 
     103, '技师李', 'TECHNICAL_REVIEWING', '2024-03-25 16:20:00', '2024-03-25 16:20:00', '2024-03-25 16:20:00', 0);

-- 3. 技术审核通过的报告 (TECHNICAL_APPROVED) - 等待临床审核
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        technician_id, technician_name, technical_reviewer_id, technical_reviewer_name,
                        technical_review_time, technical_review_result, technical_review_comment,
                        status, test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240324001', 7, 'SAMPLE007', 7, '周九', '血糖', 
     104, '技师刘', 201, '技术审核员陈', '2024-03-24 11:20:00', 'APPROVED', '检验结果正常，符合标准',
     'TECHNICAL_APPROVED', '2024-03-24 10:30:00', '2024-03-24 10:30:00', '2024-03-24 11:20:00', 0),
    ('REP20240324002', 8, 'SAMPLE008', 8, '吴十', '心电图', 
     105, '技师赵', 202, '技术审核员林', '2024-03-24 13:45:00', 'APPROVED', '心电图波形正常',
     'TECHNICAL_APPROVED', '2024-03-24 13:00:00', '2024-03-24 13:00:00', '2024-03-24 13:45:00', 0),
    ('REP20240324003', 9, 'SAMPLE009', 9, '郑十一', 'B超', 
     106, '技师孙', 203, '技术审核员黄', '2024-03-24 16:10:00', 'APPROVED', 'B超图像清晰，未见异常',
     'TECHNICAL_APPROVED', '2024-03-24 15:30:00', '2024-03-24 15:30:00', '2024-03-24 16:10:00', 0);

-- 4. 技术审核驳回的报告 (TECHNICAL_REJECTED) - 需要重新检验
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        technician_id, technician_name, technical_reviewer_id, technical_reviewer_name,
                        technical_review_time, technical_review_result, technical_review_comment,
                        status, test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240323001', 10, 'SAMPLE010', 10, '王十二', '血常规', 
     107, '技师周', 204, '技术审核员吴', '2024-03-23 09:30:00', 'REJECTED', '白细胞计数异常，建议重新采血检验',
     'TECHNICAL_REJECTED', '2024-03-23 08:45:00', '2024-03-23 08:45:00', '2024-03-23 09:30:00', 0),
    ('REP20240323002', 11, 'SAMPLE011', 11, '李十三', '尿常规', 
     108, '技师郑', 205, '技术审核员郑', '2024-03-23 14:15:00', 'REJECTED', '尿蛋白阳性，需复查确认',
     'TECHNICAL_REJECTED', '2024-03-23 13:30:00', '2024-03-23 13:30:00', '2024-03-23 14:15:00', 0);

-- 5. 临床审核中的报告 (CLINICAL_REVIEWING)
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        technician_id, technician_name, technical_reviewer_id, technical_reviewer_name,
                        technical_review_time, technical_review_result, technical_review_comment,
                        status, test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240322001', 12, 'SAMPLE012', 12, '张十四', '肝功能', 
     109, '技师王', 206, '技术审核员刘', '2024-03-22 10:40:00', 'APPROVED', '肝功能指标正常',
     'CLINICAL_REVIEWING', '2024-03-22 09:50:00', '2024-03-22 09:50:00', '2024-03-22 10:40:00', 0),
    ('REP20240322002', 13, 'SAMPLE013', 13, '陈十五', '肾功能', 
     110, '技师张', 207, '技术审核员陈', '2024-03-22 15:25:00', 'APPROVED', '肾功能指标正常',
     'CLINICAL_REVIEWING', '2024-03-22 14:35:00', '2024-03-22 14:35:00', '2024-03-22 15:25:00', 0);

-- 6. 临床审核通过的报告 (CLINICAL_APPROVED) - 等待发布
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        technician_id, technician_name, technical_reviewer_id, technical_reviewer_name,
                        technical_review_time, technical_review_result, technical_review_comment,
                        clinical_reviewer_id, clinical_reviewer_name, clinical_review_time, clinical_review_result, clinical_review_comment,
                        status, test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240321001', 14, 'SAMPLE014', 14, '林十六', '血脂', 
     111, '技师李', 208, '技术审核员林', '2024-03-21 11:15:00', 'APPROVED', '血脂指标正常',
     301, '临床医生张', '2024-03-21 14:30:00', 'APPROVED', '患者血脂水平正常，无需药物治疗',
     'CLINICAL_APPROVED', '2024-03-21 10:25:00', '2024-03-21 10:25:00', '2024-03-21 14:30:00', 0),
    ('REP20240321002', 15, 'SAMPLE015', 15, '黄十七', '血糖', 
     112, '技师周', 209, '技术审核员黄', '2024-03-21 13:50:00', 'APPROVED', '血糖值正常',
     302, '临床医生王', '2024-03-21 16:10:00', 'APPROVED', '空腹血糖正常，建议保持当前饮食',
     'CLINICAL_APPROVED', '2024-03-21 12:55:00', '2024-03-21 12:55:00', '2024-03-21 16:10:00', 0);

-- 7. 临床审核驳回的报告 (CLINICAL_REJECTED) - 需要返回技术审核
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        technician_id, technician_name, technical_reviewer_id, technical_reviewer_name,
                        technical_review_time, technical_review_result, technical_review_comment,
                        clinical_reviewer_id, clinical_reviewer_name, clinical_review_time, clinical_review_result, clinical_review_comment,
                        status, test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240320001', 16, 'SAMPLE016', 16, '吴十八', '血常规', 
     113, '技师郑', 210, '技术审核员吴', '2024-03-20 09:40:00', 'APPROVED', '血常规指标正常',
     303, '临床医生李', '2024-03-20 14:20:00', 'REJECTED', '血小板计数偏低，需重新检验确认',
     'CLINICAL_REJECTED', '2024-03-20 08:50:00', '2024-03-20 08:50:00', '2024-03-20 14:20:00', 0);

-- 8. 已发布的报告 (PUBLISHED)
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        technician_id, technician_name, technical_reviewer_id, technical_reviewer_name,
                        technical_review_time, technical_review_result, technical_review_comment,
                        clinical_reviewer_id, clinical_reviewer_name, clinical_review_time, clinical_review_result, clinical_review_comment,
                        status, published_time, published_by, published_by_name, test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240319001', 17, 'SAMPLE017', 17, '郑十九', '心电图', 
     114, '技师刘', 211, '技术审核员郑', '2024-03-19 10:35:00', 'APPROVED', '心电图正常',
     304, '临床医生周', '2024-03-19 14:55:00', 'APPROVED', '心电图正常，无心律失常',
     'PUBLISHED', '2024-03-19 16:00:00', 401, '发布员张', '2024-03-19 09:40:00', '2024-03-19 09:40:00', '2024-03-19 16:00:00', 0),
    ('REP20240319002', 18, 'SAMPLE018', 18, '刘二十', 'B超', 
     115, '技师陈', 212, '技术审核员刘', '2024-03-19 13:20:00', 'APPROVED', 'B超图像清晰',
     305, '临床医生陈', '2024-03-19 17:10:00', 'APPROVED', 'B超检查正常，未见异常回声',
     'PUBLISHED', '2024-03-19 18:00:00', 402, '发布员王', '2024-03-19 12:25:00', '2024-03-19 12:25:00', '2024-03-19 18:00:00', 0),
    ('REP20240319003', 19, 'SAMPLE019', 19, '陈二一', 'CT', 
     116, '技师林', 213, '技术审核员陈', '2024-03-19 15:45:00', 'APPROVED', 'CT扫描正常',
     306, '临床医生林', '2024-03-19 19:30:00', 'APPROVED', 'CT检查未见异常病变',
     'PUBLISHED', '2024-03-19 20:00:00', 403, '发布员李', '2024-03-19 14:50:00', '2024-03-19 14:50:00', '2024-03-19 20:00:00', 0);

-- 9. 已归档的报告 (ARCHIVED)
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        technician_id, technician_name, technical_reviewer_id, technical_reviewer_name,
                        technical_review_time, technical_review_result, technical_review_comment,
                        clinical_reviewer_id, clinical_reviewer_name, clinical_review_time, clinical_review_result, clinical_review_comment,
                        status, published_time, published_by, published_by_name, archived_time, archived_by, archived_by_name,
                        test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240301001', 20, 'SAMPLE020', 20, '黄二二', '血常规', 
     117, '技师黄', 214, '技术审核员黄', '2024-03-01 11:10:00', 'APPROVED', '血常规正常',
     307, '临床医生黄', '2024-03-01 15:25:00', 'APPROVED', '血常规指标均在正常范围',
     'ARCHIVED', '2024-03-01 16:30:00', 404, '发布员周', '2024-04-01 10:00:00', 501, '归档员张',
     '2024-03-01 10:15:00', '2024-03-01 10:15:00', '2024-04-01 10:00:00', 0),
    ('REP20240301002', 21, 'SAMPLE021', 21, '周二三', '尿常规', 
     118, '技师周', 215, '技术审核员周', '2024-03-01 14:40:00', 'APPROVED', '尿常规正常',
     308, '临床医生周', '2024-03-01 18:10:00', 'APPROVED', '尿常规检查正常',
     'ARCHIVED', '2024-03-01 19:00:00', 405, '发布员郑', '2024-04-01 10:30:00', 502, '归档员王',
     '2024-03-01 13:50:00', '2024-03-01 13:50:00', '2024-04-01 10:30:00', 0);

-- 10. 已撤销的报告 (REVOKED)
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        technician_id, technician_name, status, revoked_time, revoked_by, revoked_by_name, revoked_reason,
                        test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240318001', 22, 'SAMPLE022', 22, '吴二四', '肝功能', 
     119, '技师吴', 'REVOKED', '2024-03-18 16:20:00', 503, '撤销员李', '患者信息录入错误，需重新创建报告',
     '2024-03-18 15:00:00', '2024-03-18 15:00:00', '2024-03-18 16:20:00', 0);

-- 11. 带有AI诊断的报告（异常报告）
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        technician_id, technician_name, technical_reviewer_id, technical_reviewer_name,
                        technical_review_time, technical_review_result, technical_review_comment,
                        clinical_reviewer_id, clinical_reviewer_name, clinical_review_time, clinical_review_result, clinical_review_comment,
                        ai_diagnosis, ai_confidence, ai_model_version, ai_diagnosis_time, abnormal_indicator_count, critical_indicator_count,
                        status, published_time, published_by, published_by_name,
                        test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240317001', 23, 'SAMPLE023', 23, '郑二五', '血常规', 
     120, '技师郑', 216, '技术审核员吴', '2024-03-17 10:25:00', 'APPROVED', '白细胞异常偏高',
     309, '临床医生吴', '2024-03-17 14:40:00', 'APPROVED', '符合感染表现，建议抗感染治疗',
     '【AI辅助诊断报告】\n报告编号：REP20240317001\n患者姓名：郑二五\n诊断时间：2024-03-17T14:30:00\n\n【诊断结果】\n白细胞计数显著升高（18.5×10⁹/L），中性粒细胞比例增加，符合急性感染表现。红细胞计数、血红蛋白浓度正常。血小板计数正常。\n\n【诊断建议】\n1. 结合临床表现考虑急性感染\n2. 建议进行病原学检查\n3. 考虑抗感染治疗\n4. 建议1周后复查血常规\n\n【模型说明】\n本诊断基于实验室检验数据，由AI模型辅助生成。诊断结果仅供参考，最终诊断需由临床医生确认。',
     88, 'v1.0', '2024-03-17 14:30:00', 2, 1,
     'PUBLISHED', '2024-03-17 16:00:00', 406, '发布员刘',
     '2024-03-17 09:35:00', '2024-03-17 09:35:00', '2024-03-17 16:00:00', 0),
     
    ('REP20240317002', 24, 'SAMPLE024', 24, '刘二六', '肾功能', 
     121, '技师刘', 217, '技术审核员郑', '2024-03-17 13:55:00', 'APPROVED', '肌酐、尿素氮异常',
     310, '临床医生郑', '2024-03-17 17:20:00', 'APPROVED', '肾功能损害，建议进一步检查',
     '【AI辅助诊断报告】\n报告编号：REP20240317002\n患者姓名：刘二六\n诊断时间：2024-03-17T17:10:00\n\n【诊断结果】\n血肌酐升高（156μmol/L），尿素氮升高（9.8mmol/L），提示肾功能损害。肾小球滤过率估算值降低。电解质检查显示血钾偏高。\n\n【诊断建议】\n1. 肾功能损害（慢性肾脏病可能）\n2. 建议24小时尿蛋白定量检查\n3. 建议肾脏B超检查\n4. 控制蛋白质摄入，监测血压\n\n【模型说明】\n本诊断基于实验室检验数据，由AI模型辅助生成。诊断结果仅供参考，最终诊断需由临床医生确认。',
     92, 'v1.0', '2024-03-17 17:10:00', 3, 0,
     'PUBLISHED', '2024-03-17 18:30:00', 407, '发布员陈',
     '2024-03-17 12:45:00', '2024-03-17 12:45:00', '2024-03-17 18:30:00', 0);

-- 12. 今日报告（用于统计测试）
INSERT INTO lab_report (report_no, sample_id, sample_no, patient_id, patient_name, test_items, 
                        technician_id, technician_name, status, test_time, create_time, update_time, deleted)
VALUES 
    ('REP20240326004', 25, 'SAMPLE025', 25, '张二七', '血常规', 
     122, '技师张', 'PENDING', NOW(), NOW(), NOW(), 0),
    ('REP20240326005', 26, 'SAMPLE026', 26, '王二八', '尿常规', 
     123, '技师王', 'PENDING', NOW(), NOW(), NOW(), 0),
    ('REP20240326006', 27, 'SAMPLE027', 27, '李二九', '肝功能', 
     124, '技师李', 'TECHNICAL_REVIEWING', NOW(), NOW(), NOW(), 0),
    ('REP20240326007', 28, 'SAMPLE028', 28, '赵三十', '肾功能', 
     125, '技师赵', 'CLINICAL_REVIEWING', NOW(), NOW(), NOW(), 0),
    ('REP20240326008', 29, 'SAMPLE029', 29, '钱三一', '血糖', 
     126, '技师钱', 'CLINICAL_APPROVED', NOW(), NOW(), NOW(), 0),
    ('REP20240326009', 30, 'SAMPLE030', 30, '孙三二', '血脂', 
     127, '技师孙', 'PUBLISHED', NOW(), NOW(), NOW(), 0);

-- ==================== 插入异常指标记录 ====================

-- 为AI诊断报告插入异常指标记录
INSERT INTO lab_report_abnormal_indicator (report_id, report_no, indicator_name, indicator_code, result_value, unit, 
                                           reference_low, reference_high, abnormal_flag, abnormal_severity, clinical_significance)
VALUES 
    -- REP20240317001 的异常指标
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240317001'), 'REP20240317001', 
     '白细胞计数', 'WBC', '18.5', '×10⁹/L', '4.0', '10.0', 'HIGH', 'SEVERE', '急性感染可能'),
     
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240317001'), 'REP20240317001', 
     '中性粒细胞比例', 'NEUT%', '85', '%', '40', '75', 'HIGH', 'MODERATE', '细菌感染表现'),
     
    -- REP20240317002 的异常指标
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240317002'), 'REP20240317002', 
     '血肌酐', 'CREA', '156', 'μmol/L', '44', '97', 'HIGH', 'SEVERE', '肾功能损害'),
     
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240317002'), 'REP20240317002', 
     '尿素氮', 'BUN', '9.8', 'mmol/L', '2.5', '7.5', 'HIGH', 'MODERATE', '肾功能减退'),
     
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240317002'), 'REP20240317002', 
     '血钾', 'K', '5.6', 'mmol/L', '3.5', '5.5', 'HIGH', 'MILD', '高钾血症');

-- ==================== 插入检验结果结构化数据 ====================

-- 为部分报告插入结构化检验结果
INSERT INTO lab_report_test_result (report_id, report_no, item_name, item_code, result_value, unit, reference_range, abnormal_flag, sort_order)
VALUES 
    -- REP20240326004 血常规结果
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240326004'), 'REP20240326004', 
     '白细胞计数', 'WBC', '7.2', '×10⁹/L', '4.0-10.0', 'NORMAL', 1),
     
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240326004'), 'REP20240326004', 
     '红细胞计数', 'RBC', '4.5', '×10¹²/L', '4.0-5.5', 'NORMAL', 2),
     
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240326004'), 'REP20240326004', 
     '血红蛋白', 'HGB', '135', 'g/L', '120-160', 'NORMAL', 3),
     
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240326004'), 'REP20240326004', 
     '血小板计数', 'PLT', '210', '×10⁹/L', '100-300', 'NORMAL', 4);

-- ==================== 插入审核日志 ====================

-- 为部分报告插入审核日志记录
INSERT INTO lab_report_review_log (report_id, report_no, review_type, review_action, reviewer_id, reviewer_name, 
                                   review_result, old_status, new_status, duration_seconds, create_time)
VALUES 
    -- REP20240319001 的审核流程
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240319001'), 'REP20240319001', 
     'TECHNICAL', 'REVIEW', 211, '技术审核员郑', 'APPROVED', 'TECHNICAL_REVIEWING', 'TECHNICAL_APPROVED', 1800, '2024-03-19 10:35:00'),
     
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240319001'), 'REP20240319001', 
     'CLINICAL', 'REVIEW', 304, '临床医生周', 'APPROVED', 'CLINICAL_REVIEWING', 'CLINICAL_APPROVED', 3600, '2024-03-19 14:55:00'),
     
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240319001'), 'REP20240319001', 
     'PUBLISH', 'PUBLISH', 401, '发布员张', 'PUBLISHED', 'CLINICAL_APPROVED', 'PUBLISHED', 0, '2024-03-19 16:00:00'),
     
    -- REP20240323001 的技术审核驳回流程
    ((SELECT id FROM lab_report WHERE report_no = 'REP20240323001'), 'REP20240323001', 
     'TECHNICAL', 'REVIEW', 204, '技术审核员吴', 'REJECTED', 'TECHNICAL_REVIEWING', 'TECHNICAL_REJECTED', 1200, '2024-03-23 09:30:00');

-- ==================== 统计验证 ====================

SELECT '报告总数' AS '统计项', COUNT(*) AS '数量' FROM lab_report WHERE deleted = 0
UNION ALL
SELECT '今日报告数', COUNT(*) FROM lab_report WHERE deleted = 0 AND DATE(create_time) = CURDATE()
UNION ALL
SELECT '待技术审核数', COUNT(*) FROM lab_report WHERE deleted = 0 AND status = 'TECHNICAL_REVIEWING'
UNION ALL
SELECT '待临床审核数', COUNT(*) FROM lab_report WHERE deleted = 0 AND status = 'CLINICAL_REVIEWING'
UNION ALL
SELECT '今日已发布数', COUNT(*) FROM lab_report WHERE deleted = 0 AND status = 'PUBLISHED' AND DATE(published_time) = CURDATE()
UNION ALL
SELECT 'AI诊断报告数', COUNT(*) FROM lab_report WHERE deleted = 0 AND ai_diagnosis IS NOT NULL
UNION ALL
SELECT '异常报告数', COUNT(*) FROM lab_report WHERE deleted = 0 AND abnormal_indicator_count > 0
UNION ALL
SELECT '已归档报告数', COUNT(*) FROM lab_report WHERE deleted = 0 AND status = 'ARCHIVED';

-- 按状态统计报告数量
SELECT status, COUNT(*) AS count, 
       CASE status
           WHEN 'PENDING' THEN '待录入结果'
           WHEN 'TECHNICAL_REVIEWING' THEN '技术审核中'
           WHEN 'TECHNICAL_APPROVED' THEN '技术审核通过'
           WHEN 'TECHNICAL_REJECTED' THEN '技术审核驳回'
           WHEN 'CLINICAL_REVIEWING' THEN '临床审核中'
           WHEN 'CLINICAL_APPROVED' THEN '临床审核通过'
           WHEN 'CLINICAL_REJECTED' THEN '临床审核驳回'
           WHEN 'PUBLISHED' THEN '已发布'
           WHEN 'ARCHIVED' THEN '已归档'
           WHEN 'REVOKED' THEN '已撤销'
           ELSE status
       END AS '状态描述'
FROM lab_report WHERE deleted = 0
GROUP BY status
ORDER BY FIELD(status, 'PENDING', 'TECHNICAL_REVIEWING', 'TECHNICAL_APPROVED', 'TECHNICAL_REJECTED',
                      'CLINICAL_REVIEWING', 'CLINICAL_APPROVED', 'CLINICAL_REJECTED',
                      'PUBLISHED', 'ARCHIVED', 'REVOKED');

-- 近7天报告趋势（测试数据）
SELECT DATE(create_time) AS report_date, COUNT(*) AS report_count
FROM lab_report 
WHERE deleted = 0 AND create_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY DATE(create_time)
ORDER BY report_date;