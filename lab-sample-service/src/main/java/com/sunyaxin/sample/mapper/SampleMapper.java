package com.sunyaxin.sample.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.sunyaxin.common.entity.Sample;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * 标本Mapper（性能优化版）
 * 优化查询语句，避免使用DATE()函数以便更好地利用索引
 */
@Mapper
public interface SampleMapper extends BaseMapper<Sample> {

    /**
     * 根据标本编号查询
     */
    @Select("SELECT * FROM lab_sample WHERE sample_no = #{sampleNo} AND deleted = 0")
    Sample selectBySampleNo(@Param("sampleNo") String sampleNo);

    /**
     * 按状态统计今日标本数量（优化版：使用时间范围代替DATE()函数）
     */
    @Select("SELECT status, COUNT(*) as count FROM lab_sample " +
            "WHERE deleted = 0 AND create_time >= #{startOfDay} AND create_time < #{endOfDay} " +
            "GROUP BY status")
    List<Map<String, Object>> countByStatusToday(@Param("startOfDay") LocalDateTime startOfDay, 
                                                   @Param("endOfDay") LocalDateTime endOfDay);

    /**
     * 按状态统计指定日期的标本数量（优化版）
     */
    @Select("SELECT status, COUNT(*) as count FROM lab_sample " +
            "WHERE deleted = 0 AND create_time >= #{startOfDay} AND create_time < #{endOfDay} " +
            "GROUP BY status")
    List<Map<String, Object>> countByStatusByDate(@Param("startOfDay") LocalDateTime startOfDay, 
                                                    @Param("endOfDay") LocalDateTime endOfDay);

    /**
     * 统计指定日期范围的标本数量（按天）（优化版）
     */
    @Select("SELECT DATE(create_time) as date, COUNT(*) as count FROM lab_sample " +
            "WHERE deleted = 0 AND create_time >= #{startDateTime} AND create_time < #{endDateTime} " +
            "GROUP BY DATE(create_time) ORDER BY date")
    List<Map<String, Object>> countByDateRange(@Param("startDateTime") LocalDateTime startDateTime,
                                                @Param("endDateTime") LocalDateTime endDateTime);

    /**
     * 统计今日标本总数（优化版）
     */
    @Select("SELECT COUNT(*) FROM lab_sample WHERE deleted = 0 " +
            "AND create_time >= #{startOfDay} AND create_time < #{endOfDay}")
    Long countToday(@Param("startOfDay") LocalDateTime startOfDay, 
                    @Param("endOfDay") LocalDateTime endOfDay);

    /**
     * 统计指定日期的标本总数（优化版）
     */
    @Select("SELECT COUNT(*) FROM lab_sample WHERE deleted = 0 " +
            "AND create_time >= #{startOfDay} AND create_time < #{endOfDay}")
    Long countByDate(@Param("startOfDay") LocalDateTime startOfDay, 
                     @Param("endOfDay") LocalDateTime endOfDay);

    /**
     * 查询待处理标本（已采集+运输中）
     */
    @Select("SELECT * FROM lab_sample WHERE deleted = 0 AND status IN ('COLLECTED', 'IN_TRANSIT', 'RECEIVED') " +
            "ORDER BY create_time DESC LIMIT #{limit}")
    List<Sample> selectPendingSamples(@Param("limit") int limit);

    /**
     * 按检验项目统计热度（今日）（优化版）
     */
    @Select("SELECT test_items as itemName, COUNT(*) as count FROM lab_sample " +
            "WHERE deleted = 0 AND create_time >= #{startOfDay} AND create_time < #{endOfDay} " +
            "GROUP BY test_items ORDER BY count DESC LIMIT 10")
    List<Map<String, Object>> hotTestItemsToday(@Param("startOfDay") LocalDateTime startOfDay, 
                                                  @Param("endOfDay") LocalDateTime endOfDay);

    /**
     * 查询异常标本
     */
    @Select("SELECT * FROM lab_sample WHERE deleted = 0 AND status = 'ABNORMAL' " +
            "ORDER BY update_time DESC LIMIT #{limit}")
    List<Sample> selectAbnormalSamples(@Param("limit") int limit);

    /**
     * 分页查询标本列表（支持条件筛选）（优化版）
     */
    @Select("<script>" +
            "SELECT * FROM lab_sample WHERE deleted = 0 " +
            "<if test='keyword != null and keyword != \"\"'> " +
            "  AND (sample_no LIKE CONCAT('%',#{keyword},'%') " +
            "  OR patient_name LIKE CONCAT('%',#{keyword},'%') " +
            "  OR doctor_name LIKE CONCAT('%',#{keyword},'%')) " +
            "</if>" +
            "<if test='status != null and status != \"\"'> " +
            "  AND status = #{status} " +
            "</if>" +
            "<if test='sampleType != null and sampleType != \"\"'> " +
            "  AND sample_type = #{sampleType} " +
            "</if>" +
            "<if test='startDate != null'> " +
            "  AND create_time &gt;= #{startDateTime} " +
            "</if>" +
            "<if test='endDate != null'> " +
            "  AND create_time &lt; #{endDateTime} " +
            "</if>" +
            " ORDER BY create_time DESC " +
            "</script>")
    List<Sample> selectSampleList(@Param("keyword") String keyword,
                                   @Param("status") String status,
                                   @Param("sampleType") String sampleType,
                                   @Param("startDate") LocalDate startDate,
                                   @Param("endDate") LocalDate endDate,
                                   @Param("startDateTime") LocalDateTime startDateTime,
                                   @Param("endDateTime") LocalDateTime endDateTime);
}
