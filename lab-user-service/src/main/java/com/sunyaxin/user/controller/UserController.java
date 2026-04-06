package com.sunyaxin.user.controller;

import com.sunyaxin.common.entity.User;
import com.sunyaxin.common.result.PageResult;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.user.dto.LoginDTO;
import com.sunyaxin.user.dto.UserDTO;
import com.sunyaxin.user.service.UserService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 用户Controller
 * 
 * API端点参数校验说明：
 * - POST /login: @Valid LoginDTO (username, password 必填)
 * - POST /register: @Valid UserDTO.Create (所有必填字段)
 * - PUT /{id}: @Valid UserDTO.Update (更新时密码可选)
 */
@RestController
@RequestMapping("/user")
@RequiredArgsConstructor
@Validated
@Slf4j
public class UserController {

    private final UserService userService;

    /**
     * 用户登录
     * 接收JSON格式的请求体，返回JWT Token和用户信息
     *
     * [DEF-001 FIX] 修复P0 Critical BUG：
     * - 原因：原代码使用@RequestParam无法解析JSON Body
     * - 修复：改用@RequestBody + LoginDTO接收JSON请求
     * 
     * 参数校验: username(@NotBlank), password(@NotBlank)
     */
    @PostMapping("/login")
    public ResponseEntity<Result<Map<String, Object>>> login(@Valid @RequestBody LoginDTO loginDTO) {
        try {
            Result<Map<String, Object>> result = userService.login(loginDTO.getUsername(), loginDTO.getPassword());
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            // 极端情况：即使Service层抛出异常，也要捕获并返回友好错误
            log.error("[登录接口异常] {}: {}", e.getClass().getName(), e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Result.error("系统繁忙，请稍后重试"));
        }
    }

    /**
     * 用户注册
     * 使用 UserDTO 进行参数校验（Create分组）
     * 
     * 参数校验: username(@NotBlank, @Size), password(@NotBlank, @Size), realName(@NotBlank), role(@NotBlank)
     */
    @PostMapping("/register")
    public Result<User> register(@Validated(UserDTO.Create.class) @RequestBody UserDTO userDTO) {
        // 将DTO转换为实体
        User user = new User();
        BeanUtils.copyProperties(userDTO, user);
        return userService.register(user);
    }

    /**
     * 根据ID获取用户
     * 
     * 路径参数校验: id (@Min(1))
     */
    @GetMapping("/{id}")
    public Result<User> getUserById(
            @PathVariable(name = "id") @Min(value = 1, message = "用户ID必须大于0") Long id) {
        User user = userService.getById(id);
        if (user != null) {
            user.setPassword(null);
        }
        return Result.success(user);
    }

    /**
     * 根据角色获取用户列表
     */
    @GetMapping("/role/{role}")
    public Result<List<User>> getUsersByRole(@PathVariable(name = "role") String role) {
        return userService.getUsersByRole(role);
    }

    /**
     * 分页获取用户列表
     * 
     * 查询参数校验: current (默认1), size (默认10)
     */
    @GetMapping("/list")
    public Result<PageResult<User>> listUsers(
            @RequestParam(name = "current", defaultValue = "1") Long current,
            @RequestParam(name = "size", defaultValue = "10") Long size) {
        return Result.success(userService.getUserList(current, size));
    }

    /**
     * 获取所有用户
     */
    @GetMapping("/all")
    public Result<List<User>> listUsers() {
        List<User> list = userService.list();
        list.forEach(user -> user.setPassword(null));
        return Result.success(list);
    }

    /**
     * 更新用户
     * 使用 UserDTO 进行参数校验（Update分组）
     * 
     * 参数校验: username(@NotBlank), realName(@NotBlank), role(@NotBlank)
     * 注意：Update分组下password不是必填项
     */
    @PutMapping("/{id}")
    public Result<User> updateUser(
            @PathVariable(name = "id") @Min(value = 1, message = "用户ID必须大于0") Long id,
            @Validated(UserDTO.Update.class) @RequestBody UserDTO userDTO) {
        // 将DTO转换为实体
        User user = new User();
        BeanUtils.copyProperties(userDTO, user);
        user.setId(id);
        userService.updateById(user);
        return Result.success("更新成功", user);
    }

    /**
     * 删除用户（逻辑删除）
     * 
     * 路径参数校验: id (@Min(1))
     */
    @DeleteMapping("/{id}")
    public Result<Void> deleteUser(
            @PathVariable(name = "id") @Min(value = 1, message = "用户ID必须大于0") Long id) {
        User user = new User();
        user.setId(id);
        user.setStatus(0);
        userService.updateById(user);
        return Result.success("删除成功");
    }
}
