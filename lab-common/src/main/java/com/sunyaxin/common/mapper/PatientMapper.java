package com.sunyaxin.common.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.sunyaxin.common.entity.Patient;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 患者信息Mapper
 */
@Mapper
public interface PatientMapper extends BaseMapper<Patient> {

    /**
     * 根据患者编号查询
     */
    @Select("SELECT * FROM lab_patient WHERE patient_no = #{patientNo}")
    Patient selectByPatientNo(@Param("patientNo") String patientNo);

    /**
     * 根据手机号查询
     */
    @Select("SELECT * FROM lab_patient WHERE phone = #{phone}")
    Patient selectByPhone(@Param("phone") String phone);

    /**
     * 根据身份证号查询
     */
    @Select("SELECT * FROM lab_patient WHERE id_card = #{idCard}")
    Patient selectByIdCard(@Param("idCard") String idCard);

    /**
     * 根据姓名模糊查询
     */
    @Select("SELECT * FROM lab_patient WHERE patient_name LIKE CONCAT('%', #{name}, '%')")
    List<Patient> selectByName(@Param("name") String name);
}
