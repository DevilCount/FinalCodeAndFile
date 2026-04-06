package com.sunyaxin.ai.controller;

import com.sunyaxin.ai.dto.DiagnosisRequestDTO;
import com.sunyaxin.ai.dto.DiagnosisResponseDTO;
import com.sunyaxin.ai.service.AiDiagnosisService;
import com.sunyaxin.common.result.Result;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * AI诊断Controller
 */
@RestController
@RequestMapping("/ai")
@RequiredArgsConstructor
@Validated
@Slf4j
public class AiController {

    private final AiDiagnosisService aiDiagnosisService;

    /**
     * AI辅助诊断（完整版）
     */
    @PostMapping("/diagnose")
    public Result<DiagnosisResponseDTO> diagnose(@Valid @RequestBody DiagnosisRequestDTO request) {
        return aiDiagnosisService.diagnose(request);
    }

    /**
     * 简化版诊断（供其他服务调用）
     */
    @PostMapping("/simple-diagnose")
    public Result<String> simpleDiagnose(@RequestBody Map<String, Object> testData) {
        return aiDiagnosisService.simpleDiagnose(testData);
    }

    /**
     * 血常规诊断
     */
    @PostMapping("/diagnose/blood-routine")
    public Result<DiagnosisResponseDTO> diagnoseBloodRoutine(@RequestBody Map<String, Object> results) {
        return aiDiagnosisService.diagnoseBloodRoutine(results);
    }

    /**
     * 尿常规诊断
     */
    @PostMapping("/diagnose/urine-routine")
    public Result<DiagnosisResponseDTO> diagnoseUrineRoutine(@RequestBody Map<String, Object> results) {
        return aiDiagnosisService.diagnoseUrineRoutine(results);
    }

    /**
     * 健康检查
     */
    @GetMapping("/health")
    public Result<String> health() {
        return Result.success("AI服务运行正常");
    }
}
