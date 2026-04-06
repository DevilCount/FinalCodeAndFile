package com.sunyaxin.user.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.sunyaxin.common.entity.User;
import com.sunyaxin.common.result.PageResult;
import com.sunyaxin.common.result.Result;

import java.util.List;
import java.util.Map;

/**
 * 用户Service接口
 */
public interface UserService extends IService<User> {

    /**
     * 用户登录（返回JWT Token）
     */
    Result<Map<String, Object>> login(String username, String password);

    /**
     * 根据角色获取用户列表
     */
    Result<List<User>> getUsersByRole(String role);

    /**
     * 注册用户
     */
    Result<User> register(User user);

    /**
     * 分页获取用户列表
     */
    PageResult<User> getUserList(Long current, Long size);
}
