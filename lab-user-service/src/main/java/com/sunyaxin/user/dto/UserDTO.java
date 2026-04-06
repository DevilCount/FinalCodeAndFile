package com.sunyaxin.user.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 用户创建/更新请求DTO
 * 专门用于接收前端传入的用户数据，与数据库实体分离
 */
@Data
public class UserDTO {

    /**
     * 用户名
     */
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度必须在3-20个字符之间")
    private String username;

    /**
     * 密码（明文，存储时会加密）
     */
    @NotBlank(message = "密码不能为空", groups = {Create.class})
    @Size(min = 6, max = 100, message = "密码长度必须在6-100个字符之间")
    private String password;

    /**
     * 真实姓名
     */
    @NotBlank(message = "真实姓名不能为空")
    @Size(max = 50, message = "真实姓名长度不能超过50个字符")
    private String realName;

    /**
     * 角色：DOCTOR-临床医生，LAB_TECHNICIAN-检验医师，ADMIN-管理员
     */
    @NotBlank(message = "角色不能为空")
    private String role;

    /**
     * 科室
     */
    @Size(max = 50, message = "科室名称长度不能超过50个字符")
    private String department;

    /**
     * 手机号
     */
    @Pattern(regexp = "^$|^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;

    /**
     * 邮箱
     */
    // @Email(message = "邮箱格式不正确")  // 可选字段，允许为空
    private String email;

    /**
     * 状态：0-禁用，1-启用
     */
    private Integer status;

    /**
     * 校验分组接口 - 创建时需要密码
     */
    public interface Create {}
    
    /**
     * 校验分组接口 - 更新时不需要密码
     */
    public interface Update {}
}
