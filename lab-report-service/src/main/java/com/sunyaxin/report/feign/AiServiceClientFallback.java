package com.sunyaxin.report.feign;

import com.sunyaxin.common.result.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.Map;

/**
 * AI服务客户端降级实现
 * 当AI服务不可用时返回模拟诊断结果
 */
@Slf4j
@Component
public class AiServiceClientFallback implements AiServiceClient {

    @Override
    public Result<String> diagnose(Map<String, Object> requestData) {
        log.warn("AI服务不可用，使用降级实现，报告编号: {}", requestData.get("reportNo"));
        
        // 模拟AI诊断结果
        String reportNo = String.valueOf(requestData.get("reportNo"));
        String patientName = String.valueOf(requestData.get("patientName"));
        int abnormalCount = requestData.get("abnormalCount") != null ? 
                (int) requestData.get("abnormalCount") : 0;
        int criticalCount = requestData.get("criticalCount") != null ? 
                (int) requestData.get("criticalCount") : 0;
        
        // 根据异常情况生成不同的诊断结果
        StringBuilder diagnosis = new StringBuilder();
        diagnosis.append("【AI辅助诊断报告】\n");
        diagnosis.append("报告编号：").append(reportNo).append("\n");
        diagnosis.append("患者姓名：").append(patientName).append("\n");
        diagnosis.append("诊断时间：").append(java.time.LocalDateTime.now()).append("\n");
        diagnosis.append("\n【诊断结果】\n");
        
        if (criticalCount > 0) {
            diagnosis.append("发现危急值 ").append(criticalCount).append(" 个，建议立即临床干预。\n");
            diagnosis.append("1. 患者存在紧急医疗风险，请立即通知临床医生\n");
            diagnosis.append("2. 建议患者留院观察，进行进一步检查\n");
            diagnosis.append("3. 相关指标需要紧急复查确认\n");
        } else if (abnormalCount > 0) {
            diagnosis.append("发现异常指标 ").append(abnormalCount).append(" 个，建议临床关注。\n");
            diagnosis.append("1. 患者存在轻度异常，建议定期复查\n");
            diagnosis.append("2. 结合患者病史综合判断\n");
            diagnosis.append("3. 可考虑饮食和生活习惯调整\n");
        } else {
            diagnosis.append("检验结果均在正常范围内，无明显异常。\n");
            diagnosis.append("1. 患者健康状况良好\n");
            diagnosis.append("2. 建议保持当前生活习惯\n");
            diagnosis.append("3. 定期健康体检\n");
        }
        
        diagnosis.append("\n【诊断建议】\n");
        if (criticalCount > 0) {
            diagnosis.append("1. 立即联系临床医生进行紧急处理\n");
            diagnosis.append("2. 建议进行专项检查明确病因\n");
            diagnosis.append("3. 需要密切监测生命体征\n");
        } else if (abnormalCount > 0) {
            diagnosis.append("1. 建议1-2周后复查相关指标\n");
            diagnosis.append("2. 调整饮食和作息习惯\n");
            diagnosis.append("3. 如有不适及时就医\n");
        } else {
            diagnosis.append("1. 继续保持健康生活方式\n");
            diagnosis.append("2. 建议每年进行一次全面体检\n");
            diagnosis.append("3. 注意均衡饮食和适当运动\n");
        }
        
        diagnosis.append("\n【模型说明】\n");
        diagnosis.append("本诊断基于实验室检验数据，由AI模型辅助生成。\n");
        diagnosis.append("诊断结果仅供参考，最终诊断需由临床医生确认。\n");
        diagnosis.append("模型版本：v1.0-降级模式\n");
        diagnosis.append("置信度：85%（基于数据完整性评估）\n");
        
        return Result.success("AI诊断完成（降级模式）", diagnosis.toString());
    }
}
