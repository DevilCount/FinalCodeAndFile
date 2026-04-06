package com.sunyaxin.ai.service;

import com.sunyaxin.ai.dto.DiagnosisRequestDTO;
import com.sunyaxin.ai.dto.DiagnosisResponseDTO;
import com.sunyaxin.common.result.Result;

import java.util.Map;

/**
 * AI诊断服务接口
 */
public interface AiDiagnosisService {

    /**
     * 根据检验结果进行AI辅助诊断
     */
    Result<DiagnosisResponseDTO> diagnose(DiagnosisRequestDTO request);

    /**
     * 血常规诊断
     */
    Result<DiagnosisResponseDTO> diagnoseBloodRoutine(Map<String, Object> results);

    /**
     * 尿常规诊断
     */
    Result<DiagnosisResponseDTO> diagnoseUrineRoutine(Map<String, Object> results);

    /**
     * 简化版诊断（直接传入检验数据）
     */
    Result<String> simpleDiagnose(Map<String, Object> testData);
}
