package com.sunyaxin.ai.service.impl;

import com.sunyaxin.ai.dto.DiagnosisRequestDTO;
import com.sunyaxin.ai.dto.DiagnosisResponseDTO;
import com.sunyaxin.ai.service.AiDiagnosisService;
import com.sunyaxin.common.result.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;

/**
 * AI诊断服务实现类
 * 
 * 简化版实现：基于规则的辅助诊断，不调用外部AI API
 * 实际项目中可替换为调用第三方AI API（如百度、阿里、OpenAI等）
 */
@Slf4j
@Service
public class AiDiagnosisServiceImpl implements AiDiagnosisService {

    // 血常规参考范围
    private static final Map<String, double[]> BLOOD_ROUTINE_RANGE = new HashMap<>();
    static {
        BLOOD_ROUTINE_RANGE.put("WBC", new double[]{4.0, 10.0});      // 白细胞
        BLOOD_ROUTINE_RANGE.put("RBC", new double[]{3.5, 5.5});       // 红细胞
        BLOOD_ROUTINE_RANGE.put("HGB", new double[]{110.0, 160.0});   // 血红蛋白
        BLOOD_ROUTINE_RANGE.put("PLT", new double[]{100.0, 300.0});   // 血小板
        BLOOD_ROUTINE_RANGE.put("NEUT%", new double[]{50.0, 70.0});   // 中性粒细胞百分比
        BLOOD_ROUTINE_RANGE.put("LYMPH%", new double[]{20.0, 40.0});  // 淋巴细胞百分比
    }

    // 尿常规参考范围
    private static final Map<String, String> URINE_ROUTINE_NORMAL = new HashMap<>();
    static {
        URINE_ROUTINE_NORMAL.put("LEU", "阴性");
        URINE_ROUTINE_NORMAL.put("NIT", "阴性");
        URINE_ROUTINE_NORMAL.put("PRO", "阴性");
        URINE_ROUTINE_NORMAL.put("GLU", "阴性");
        URINE_ROUTINE_NORMAL.put("KET", "阴性");
        URINE_ROUTINE_NORMAL.put("UBG", "阴性或弱阳性");
        URINE_ROUTINE_NORMAL.put("BIL", "阴性");
        URINE_ROUTINE_NORMAL.put("ERY", "阴性");
    }

    @Override
    public Result<DiagnosisResponseDTO> diagnose(DiagnosisRequestDTO request) {
        try {
            DiagnosisResponseDTO response = new DiagnosisResponseDTO();
            StringBuilder diagnosis = new StringBuilder();
            StringBuilder abnormal = new StringBuilder();
            List<String> recommendations = new ArrayList<>();

            if ("BLOOD_ROUTINE".equals(request.getTestType())) {
                @SuppressWarnings("unchecked")
                Map<String, Object> results = request.getTestResults();
                processBloodRoutine(results, diagnosis, abnormal, recommendations);
            } else if ("URINE_ROUTINE".equals(request.getTestType())) {
                @SuppressWarnings("unchecked")
                Map<String, Object> results = request.getTestResults();
                processUrineRoutine(results, diagnosis, abnormal, recommendations);
            }

            response.setDiagnosis(diagnosis.toString());
            response.setAbnormalIndicators(abnormal.toString());
            response.setRecommendedTests(String.join("；", recommendations));
            response.setConfidence(0.85);
            response.setReferenceNotes("以上参考范围适用于成年人，具体参考范围可能因实验室和个体情况而异。");

            return Result.success("诊断完成", response);
        } catch (Exception e) {
            log.error("AI诊断异常", e);
            return Result.error("诊断失败：" + e.getMessage());
        }
    }

    @Override
    public Result<DiagnosisResponseDTO> diagnoseBloodRoutine(Map<String, Object> results) {
        DiagnosisRequestDTO request = new DiagnosisRequestDTO();
        request.setTestType("BLOOD_ROUTINE");
        request.setTestResults(results);
        return diagnose(request);
    }

    @Override
    public Result<DiagnosisResponseDTO> diagnoseUrineRoutine(Map<String, Object> results) {
        DiagnosisRequestDTO request = new DiagnosisRequestDTO();
        request.setTestType("URINE_ROUTINE");
        request.setTestResults(results);
        return diagnose(request);
    }

    @Override
    public Result<String> simpleDiagnose(Map<String, Object> testData) {
        try {
            String testType = (String) testData.getOrDefault("testItems", "BLOOD_ROUTINE");
            @SuppressWarnings("unchecked")
            Map<String, Object> results = (Map<String, Object>) testData.get("testResults");
            
            if (results == null) {
                return Result.success("暂无法提供诊断建议，检验数据不完整");
            }

            StringBuilder diagnosis = new StringBuilder();
            
            // 简化处理：根据关键词判断
            if (testType.contains("血常规") || testType.contains("BLOOD")) {
                diagnosis.append("【血常规初步分析】\n");
                
                // 检查白细胞
                if (results.containsKey("WBC")) {
                    double wbc = parseDouble(results.get("WBC"));
                    if (wbc > 10.0) {
                        diagnosis.append("白细胞偏高，可能存在感染或炎症反应。\n");
                    } else if (wbc < 4.0) {
                        diagnosis.append("白细胞偏低，注意免疫力状况。\n");
                    }
                }
                
                // 检查血红蛋白
                if (results.containsKey("HGB")) {
                    double hgb = parseDouble(results.get("HGB"));
                    if (hgb < 110.0) {
                        diagnosis.append("血红蛋白偏低，建议关注是否贫血。\n");
                    }
                }
                
                diagnosis.append("建议：请结合临床症状由专业医师进行综合判断。");
            } else {
                diagnosis.append("【检验结果分析】\n");
                diagnosis.append("已收到检验数据，建议由专业医师进行详细解读。\n");
            }

            return Result.success("诊断建议：\n" + diagnosis.toString());
        } catch (Exception e) {
            log.error("简单诊断异常", e);
            return Result.success("AI诊断暂时无法处理该数据，请稍后重试或咨询专业医师。");
        }
    }

    /**
     * 处理血常规结果
     */
    private void processBloodRoutine(Map<String, Object> results, StringBuilder diagnosis, 
                                      StringBuilder abnormal, List<String> recommendations) {
        diagnosis.append("血常规检验结果分析：\n");
        int abnormalCount = 0;

        for (Map.Entry<String, double[]> entry : BLOOD_ROUTINE_RANGE.entrySet()) {
            String item = entry.getKey();
            double[] range = entry.getValue();
            
            if (results.containsKey(item)) {
                double value = parseDouble(results.get(item));
                if (value < range[0]) {
                    abnormal.append(item).append("偏低(").append(value).append("); ");
                    abnormalCount++;
                } else if (value > range[1]) {
                    abnormal.append(item).append("偏高(").append(value).append("); ");
                    abnormalCount++;
                }
            }
        }

        // 生成诊断建议
        if (abnormalCount == 0) {
            diagnosis.append("各项指标基本正常，无显著异常。");
        } else {
            diagnosis.append("发现").append(abnormalCount).append("项指标异常，建议结合临床症状进行综合评估。");
            
            if (abnormal.toString().contains("WBC")) {
                diagnosis.append("白细胞异常提示可能存在感染或免疫相关问题。");
                recommendations.add("必要时进行C反应蛋白检查");
            }
            if (abnormal.toString().contains("HGB") || abnormal.toString().contains("RBC")) {
                diagnosis.append("红细胞或血红蛋白异常提示可能存在贫血相关状况。");
                recommendations.add("建议进行贫血相关进一步检查");
            }
        }

        recommendations.add("建议定期复查");
        recommendations.add("如有不适请及时就医");
    }

    /**
     * 处理尿常规结果
     */
    private void processUrineRoutine(Map<String, Object> results, StringBuilder diagnosis,
                                      StringBuilder abnormal, List<String> recommendations) {
        diagnosis.append("尿常规检验结果分析：\n");
        int abnormalCount = 0;

        for (Map.Entry<String, String> entry : URINE_ROUTINE_NORMAL.entrySet()) {
            String item = entry.getKey();
            String normalValue = entry.getValue();
            
            if (results.containsKey(item)) {
                String value = String.valueOf(results.get(item));
                if (!normalValue.contains(value) && !"阴性".equals(value)) {
                    abnormal.append(item).append("(").append(value).append("); ");
                    abnormalCount++;
                }
            }
        }

        if (abnormalCount == 0) {
            diagnosis.append("尿常规各项指标正常。");
        } else {
            diagnosis.append("发现").append(abnormalCount).append("项指标异常。");
            
            if (abnormal.toString().contains("LEU")) {
                recommendations.add("建议进行尿培养检查");
            }
            if (abnormal.toString().contains("GLU")) {
                recommendations.add("建议检测血糖水平");
            }
            if (abnormal.toString().contains("PRO")) {
                recommendations.add("建议进行肾功能检查");
            }
        }

        recommendations.add("建议复查尿常规");
    }

    /**
     * 安全解析Double
     */
    private double parseDouble(Object value) {
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        try {
            return Double.parseDouble(String.valueOf(value));
        } catch (NumberFormatException e) {
            return 0.0;
        }
    }
}
