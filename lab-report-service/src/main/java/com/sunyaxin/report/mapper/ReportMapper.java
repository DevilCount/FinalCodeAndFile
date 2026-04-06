package com.sunyaxin.report.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.sunyaxin.common.entity.Report;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 报告Mapper
 */
@Mapper
public interface ReportMapper extends BaseMapper<Report> {

    /**
     * 根据报告编号查询
     */
    @Select("SELECT * FROM lab_report WHERE report_no = #{reportNo}")
    Report selectByReportNo(String reportNo);

    /**
     * 根据患者ID查询报告列表
     */
    @Select("SELECT * FROM lab_report WHERE patient_id = #{patientId} ORDER BY create_time DESC")
    List<Report> selectByPatientId(@Param("patientId") Long patientId);

    /**
     * 根据状态查询报告列表
     */
    @Select("SELECT * FROM lab_report WHERE status = #{status} ORDER BY create_time DESC")
    List<Report> selectByStatus(@Param("status") String status);
}
