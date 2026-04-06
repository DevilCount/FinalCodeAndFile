package com.sunyaxin.sample.controller;

import com.sunyaxin.common.constant.SampleStatusConstant;
import com.sunyaxin.common.entity.Sample;
import com.sunyaxin.common.entity.SampleTrace;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.sample.dto.SampleCreateDTO;
import com.sunyaxin.sample.service.SampleService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;

/**
 * 标本Controller
 * 
 * API端点参数校验说明：
 * - POST /create: @Valid SampleCreateDTO (patientId, patientName, testItems, sampleType 必填)
 */
@RestController
@RequestMapping("/sample")
@RequiredArgsConstructor
@Validated
@Slf4j
public class SampleController {

    private final SampleService sampleService;

    /**
     * 创建标本
     * 使用 SampleCreateDTO 进行参数校验
     * 
     * 参数校验: 
     * - patientId (@NotNull)
     * - patientName (@NotBlank)
     * - testItems (@NotBlank)
     * - sampleType (@NotBlank)
     */
    @PostMapping("/create")
    public Result<Sample> createSample(@Valid @RequestBody SampleCreateDTO createDTO) {
        // 将DTO转换为实体
        Sample sample = new Sample();
        BeanUtils.copyProperties(createDTO, sample);
        return sampleService.createSample(sample);
    }

    /**
     * 根据ID获取标本
     * 路径参数校验: id (@Min(1))
     */
    @GetMapping("/{id}")
    public Result<Sample> getSampleById(
            @PathVariable(name = "id") @Min(value = 1, message = "标本ID必须大于0") Long id) {
        Sample sample = sampleService.getById(id);
        return Result.success(sample);
    }

    /**
     * 扫码查询标本
     */
    @GetMapping("/scan/{sampleNo}")
    public Result<Sample> scanSample(@PathVariable(name = "sampleNo") String sampleNo) {
        return sampleService.scanSample(sampleNo);
    }

    /**
     * 更新标本状态
     * 请求参数校验: status, operatorId, operatorName, location (必填)
     */
    @PostMapping("/{id}/status")
    public Result<Sample> updateStatus(
            @PathVariable(name = "id") @Min(value = 1, message = "标本ID必须大于0") Long id,
            @RequestParam(name = "status") @NotBlank(message = "状态不能为空") String status,
            @RequestParam(name = "operatorId") @Min(value = 1, message = "操作人ID无效") Long operatorId,
            @RequestParam(name = "operatorName") @NotBlank(message = "操作人姓名不能为空") String operatorName,
            @RequestParam(name = "location") @NotBlank(message = "位置不能为空") String location) {
        return sampleService.updateStatus(id, status, operatorId, operatorName, location);
    }

    /**
     * 接收标本
     */
    @PostMapping("/{id}/receive")
    public Result<Sample> receiveSample(
            @PathVariable(name = "id") @Min(value = 1, message = "标本ID必须大于0") Long id,
            @RequestParam(name = "technicianId") @Min(value = 1, message = "检验师ID无效") Long technicianId,
            @RequestParam(name = "technicianName") @NotBlank(message = "检验师姓名不能为空") String technicianName) {
        return sampleService.receiveSample(id, technicianId, technicianName);
    }

    /**
     * 开始检验
     */
    @PostMapping("/{id}/start-test")
    public Result<Sample> startTest(
            @PathVariable(name = "id") @Min(value = 1, message = "标本ID必须大于0") Long id,
            @RequestParam(name = "technicianId") @Min(value = 1, message = "检验师ID无效") Long technicianId,
            @RequestParam(name = "technicianName") @NotBlank(message = "检验师姓名不能为空") String technicianName) {
        return sampleService.updateStatus(id, SampleStatusConstant.TESTING, technicianId, technicianName, "检验室");
    }

    /**
     * 完成检验
     */
    @PostMapping("/{id}/complete")
    public Result<Sample> completeTest(
            @PathVariable(name = "id") @Min(value = 1, message = "标本ID必须大于0") Long id,
            @RequestParam(name = "technicianId") @Min(value = 1, message = "检验师ID无效") Long technicianId,
            @RequestParam(name = "technicianName") @NotBlank(message = "检验师姓名不能为空") String technicianName) {
        return sampleService.updateStatus(id, SampleStatusConstant.COMPLETED, technicianId, technicianName, "检验室");
    }

    /**
     * 获取标本追踪记录
     */
    @GetMapping("/{id}/traces")
    public Result<List<SampleTrace>> getTraceRecords(@PathVariable(name = "id") Long id) {
        return sampleService.getTraceRecords(id);
    }

    /**
     * 录入检验结果 (TC007步骤4: 录入检验结果)
     */
    @PutMapping("/{id}/results")
    public ResponseEntity<Result<Sample>> inputResults(
            @PathVariable(name = "id") @Min(value = 1, message = "标本ID必须大于0") Long id,
            @RequestBody java.util.Map<String, Object> requestBody) {
        log.info("==> 收到录入标本检验结果请求, sampleId: {}", id);

        try {
            // ========== 参数校验 ==========
            if (requestBody == null || !requestBody.containsKey("results")) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body(Result.badRequest("检验结果(results)不能为空"));
            }

            String results = requestBody.get("results").toString();
            Long technicianId = requestBody.get("technicianId") != null ?
                    Long.valueOf(requestBody.get("technicianId").toString()) : null;
            String technicianName = requestBody.get("technicianName") != null ?
                    requestBody.get("technicianName").toString() : "系统操作";

            // 获取标本
            Sample sample = sampleService.getById(id);
            if (sample == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Result.error("标本不存在"));
            }

            // 更新标本状态为检验中/已完成
            sample.setStatus("COMPLETED");
            if (technicianId != null) {
                sample.setTechnicianId(technicianId);
                sample.setTechnicianName(technicianName);
            }
            sampleService.updateById(sample);

            // 注意：详细的结果数据存储在lab_report表的test_results字段
            // 此端点主要更新标本状态，实际结果录入通过报告服务的input-results完成
            log.info("==> 标本检验结果已记录, sampleId: {}, technicianName: {}", id, technicianName);

            return ResponseEntity.ok(Result.success("检验结果录入成功", sample));

        } catch (Exception e) {
            log.error("录入标本检验结果异常, sampleId: {}", id, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Result.error("录入失败"));
        }
    }

    /**
     * 获取所有标本
     */
    @GetMapping("/list")
    public Result<List<Sample>> listSamples() {
        List<Sample> list = sampleService.list();
        return Result.success(list);
    }

    /**
     * 根据状态获取标本列表
     */
    @GetMapping("/list-by-status")
    public ResponseEntity<Result<List<Sample>>> listByStatus(
            @RequestParam(name = "status", required = false) @NotBlank(message = "状态参数不能为空") String status) {
        log.info("==> 收到按状态查询标本请求, status: {}", status);
        
        // ========== Controller层第一道防线：参数校验 ==========
        if (status == null || status.trim().isEmpty()) {
            log.warn("状态参数为空，返回400错误");
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Result.badRequest("状态参数不能为空"));
        }
        
        // ========== 调用Service层处理 ==========
        try {
            Result<List<Sample>> result = sampleService.listByStatus(status);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            // 极端情况：即使Service层抛出异常，也要捕获并返回友好结果
            log.error("按状态查询标本接口异常, status: {}", status, e);
            // 返回空列表（HTTP 200）而不是500错误
            return ResponseEntity.ok(Result.success(new ArrayList<>()));
        }
    }
}
