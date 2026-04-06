package com.sunyaxin.sample.controller;

import com.sunyaxin.common.entity.Patient;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.sample.service.PatientService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 患者Controller
 * 提供患者CRUD接口，支持TC007全流程测试
 */
@RestController
@RequestMapping("/patient")
@RequiredArgsConstructor
@Validated
@Slf4j
public class PatientController {

    private final PatientService patientService;

    /**
     * 创建患者 (TC007步骤2: 创建患者)
     * POST /api/patients -> /patient (after StripPrefix)
     */
    @PostMapping
    public ResponseEntity<Result<Patient>> createPatient(@Valid @RequestBody Patient patient) {
        log.info("==> 收到创建患者请求, 姓名: {}", patient.getPatientName());
        try {
            Result<Patient> result = patientService.createPatient(patient);
            return ResponseEntity.status(HttpStatus.CREATED).body(result);
        } catch (Exception e) {
            log.error("创建患者接口异常", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Result.error("系统异常，请稍后重试"));
        }
    }

    /**
     * 根据ID获取患者
     */
    @GetMapping("/{id}")
    public ResponseEntity<Result<Patient>> getPatientById(@PathVariable Long id) {
        try {
            Result<Patient> result = patientService.getPatientById(id);
            if (result.getData() == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(result);
            }
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("查询患者异常, id: {}", id, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Result.error("查询失败"));
        }
    }

    /**
     * 根据患者编号查询
     */
    @GetMapping("/no/{patientNo}")
    public ResponseEntity<Result<Patient>> getPatientByNo(@PathVariable String patientNo) {
        try {
            Result<Patient> result = patientService.getPatientByNo(patientNo);
            if (result.getData() == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(result);
            }
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("按编号查询患者异常, patientNo: {}", patientNo, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Result.error("查询失败"));
        }
    }

    /**
     * 获取所有患者列表
     */
    @GetMapping("/list")
    public ResponseEntity<Result<List<Patient>>> listPatients() {
        log.info("==> 收到获取患者列表请求");
        try {
            Result<List<Patient>> result = patientService.listPatients();
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("获取患者列表异常", e);
            // 返回空列表而非500错误
            return ResponseEntity.ok(Result.success(List.of()));
        }
    }

    /**
     * 更新患者信息
     */
    @PutMapping("/{id}")
    public ResponseEntity<Result<Patient>> updatePatient(
            @PathVariable Long id,
            @Valid @RequestBody Patient patient) {
        log.info("==> 收到更新患者请求, id: {}", id);
        try {
            Result<Patient> result = patientService.updatePatient(id, patient);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            log.error("更新患者异常, id: {}", id, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Result.error("更新失败"));
        }
    }
}
