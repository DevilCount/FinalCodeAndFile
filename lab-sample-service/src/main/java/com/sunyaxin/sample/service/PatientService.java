package com.sunyaxin.sample.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.sunyaxin.common.entity.Patient;
import com.sunyaxin.common.result.Result;

import java.util.List;

/**
 * 患者Service接口
 */
public interface PatientService extends IService<Patient> {

    /**
     * 创建患者
     */
    Result<Patient> createPatient(Patient patient);

    /**
     * 根据ID获取患者
     */
    Result<Patient> getPatientById(Long id);

    /**
     * 根据患者编号查询
     */
    Result<Patient> getPatientByNo(String patientNo);

    /**
     * 获取所有患者列表
     */
    Result<List<Patient>> listPatients();

    /**
     * 更新患者信息
     */
    Result<Patient> updatePatient(Long id, Patient patient);
}
