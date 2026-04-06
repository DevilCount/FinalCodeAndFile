package com.sunyaxin.report.dto;

import lombok.Data;

import java.io.Serializable;

/**
 * 检验医师/技师DTO
 */
@Data
public class TechnicianDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 技师ID
     */
    private Long id;

    /**
     * 技师姓名
     */
    private String name;

    /**
     * 所属科室
     */
    private String department;

    /**
     * 职称
     */
    private String title;

    /**
     * 联系方式
     */
    private String contact;
}
