package com.sunyaxin.sample.service.impl;

import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.RandomUtil;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.sunyaxin.common.entity.Patient;
import com.sunyaxin.common.mapper.PatientMapper;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.sample.service.PatientService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.CacheConfig;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;

/**
 * 患者Service实现类
 */
@Slf4j
@Service
@RequiredArgsConstructor
@CacheConfig(cacheNames = "patient")
public class PatientServiceImpl extends ServiceImpl<PatientMapper, Patient> implements PatientService {

    @Override
    @Transactional(rollbackFor = Exception.class)
    @CacheEvict(allEntries = true)
    public Result<Patient> createPatient(Patient patient) {
        log.info("==> 开始创建患者，姓名: {}", patient.getPatientName());

        // ========== 参数校验 ==========
        if (patient.getPatientName() == null || patient.getPatientName().trim().isEmpty()) {
            log.warn("创建患者失败：患者姓名为空");
            return Result.badRequest("患者姓名不能为空");
        }

        try {
            // 生成患者编号：P + yyyyMMdd + 4位随机数
            String patientNo = "P" + DateUtil.today().replace("-", "") + RandomUtil.randomNumbers(4);
            patient.setPatientNo(patientNo);
            patient.setStatus(1);

            // 如果没有设置生日，根据年龄计算
            if (patient.getBirthday() == null && patient.getAge() != null) {
                patient.setBirthday(LocalDate.now().minusYears(patient.getAge()));
            }

            // 设置默认值
            if (patient.getAgeUnit() == null || patient.getAgeUnit().isEmpty()) {
                patient.setAgeUnit("岁");
            }
            if (patient.getPatientType() == null || patient.getPatientType().isEmpty()) {
                patient.setPatientType("OUTPATIENT");
            }

            log.info("==> 保存患者信息, 编号: {}", patient.getPatientNo());
            this.save(patient);

            if (patient.getId() == null) {
                log.error("患者保存后ID为空");
                throw new RuntimeException("患者保存失败：未获取到患者ID");
            }

            log.info("==> 患者保存成功, ID: {}, 编号: {}", patient.getId(), patient.getPatientNo());
            return Result.success("创建成功", patient);

        } catch (Exception e) {
            log.error("创建患者异常: {}", e.getMessage(), e);
            return Result.error("创建患者失败: " + e.getMessage());
        }
    }

    @Override
    @Cacheable(key = "'id:' + #id")
    public Result<Patient> getPatientById(Long id) {
        Patient patient = this.getById(id);
        if (patient == null) {
            return Result.notFound("患者不存在");
        }
        return Result.success(patient);
    }

    @Override
    @Cacheable(key = "'no:' + #patientNo")
    public Result<Patient> getPatientByNo(String patientNo) {
        Patient patient = baseMapper.selectByPatientNo(patientNo);
        if (patient == null) {
            return Result.notFound("患者不存在");
        }
        return Result.success(patient);
    }

    @Override
    @Cacheable(key = "'list'")
    public Result<List<Patient>> listPatients() {
        try {
            List<Patient> list = this.lambdaQuery()
                    .eq(Patient::getStatus, 1)
                    .orderByDesc(Patient::getCreateTime)
                    .list();
            return Result.success(list);
        } catch (Exception e) {
            log.error("查询患者列表异常: {}", e.getMessage(), e);
            return Result.success(List.of());
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    @CacheEvict(allEntries = true)
    public Result<Patient> updatePatient(Long id, Patient patient) {
        Patient existingPatient = this.getById(id);
        if (existingPatient == null) {
            return Result.notFound("患者不存在");
        }

        patient.setId(id);
        // 保留不允许修改的字段
        patient.setPatientNo(existingPatient.getPatientNo());
        patient.setCreateTime(existingPatient.getCreateTime());

        this.updateById(patient);
        return Result.success("更新成功", patient);
    }
}
