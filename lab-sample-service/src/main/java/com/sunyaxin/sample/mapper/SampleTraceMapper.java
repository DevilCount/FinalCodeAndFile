package com.sunyaxin.sample.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.sunyaxin.common.entity.SampleTrace;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 标本追踪Mapper
 */
@Mapper
public interface SampleTraceMapper extends BaseMapper<SampleTrace> {

    /**
     * 根据标本ID查询追踪记录
     */
    @Select("SELECT * FROM lab_sample_trace WHERE sample_id = #{sampleId} ORDER BY create_time ASC")
    List<SampleTrace> selectBySampleId(@Param("sampleId") Long sampleId);

    /**
     * 根据标本编号查询追踪记录
     */
    @Select("SELECT * FROM lab_sample_trace WHERE sample_no = #{sampleNo} ORDER BY create_time ASC")
    List<SampleTrace> selectBySampleNo(@Param("sampleNo") String sampleNo);
}
