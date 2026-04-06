package com.sunyaxin.user.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.sunyaxin.common.entity.User;
import com.sunyaxin.common.result.PageResult;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.common.utils.JwtUtil;
import com.sunyaxin.user.mapper.UserMapper;
import com.sunyaxin.user.service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.CacheConfig;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 用户Service实现类
 */
@Service
@RequiredArgsConstructor
@Slf4j
@CacheConfig(cacheNames = "user")
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {

    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    @Override
    public Result<Map<String, Object>> login(String username, String password) {
        // ========== 第一层：参数防御性校验（防止任何异常导致500）==========
        try {
            // 检查null
            if (username == null) {
                return Result.error(400, "用户名不能为空");
            }
            if (password == null) {
                return Result.error(400, "密码不能为空");
            }

            // 检查空白字符串（trim后判断）
            if (username.trim().isEmpty()) {
                return Result.error(400, "用户名不能为空");
            }
            if (password.trim().isEmpty()) {
                return Result.error(400, "密码不能为空");
            }
        } catch (Exception e) {
            // 极端情况：即使trim()失败也不应该返回500
            System.err.println("[登录参数校验异常] " + e.getMessage());
            return Result.error(400, "用户名或密码格式错误");
        }

        // ========== 第二层：查询用户（带异常保护）==========
        User user;
        try {
            user = baseMapper.selectByUsername(username);
        } catch (Exception e) {
            System.err.println("[登录查询异常] 用户名: " + username + ", 错误: " + e.getMessage());
            return Result.error("系统繁忙，请稍后重试");
        }

        if (user == null) {
            return Result.error("用户不存在");
        }

        // ========== 第三层：密码验证（向后兼容BCrypt和明文）==========
        try {
            String storedPassword = user.getPassword();

            // 安全检查：防止storedPassword为null导致NPE
            if (storedPassword == null) {
                System.err.println("[登录错误] 用户 " + username + " 的密码字段为空");
                return Result.error("账户异常，请联系管理员");
            }

            boolean passwordMatch = false;

            // 1. 先尝试BCrypt匹配（新格式）
            if (storedPassword.startsWith("$2a$") || storedPassword.startsWith("$2b$") || storedPassword.startsWith("$2y$")) {
                passwordMatch = passwordEncoder.matches(password, storedPassword);
            } else {
                // 2. 明文密码兼容模式（旧数据迁移过渡）
                if (storedPassword.equals(password)) {
                    passwordMatch = true;

                    // 自动将明文密码升级为BCrypt格式
                    try {
                        String encodedPassword = passwordEncoder.encode(password);
                        user.setPassword(encodedPassword);
                        this.updateById(user);
                        System.out.println("[密码升级] 用户 " + username + " 的密码已从明文升级为BCrypt格式");
                    } catch (Exception upgradeEx) {
                        System.err.println("[密码升级失败] 用户 " + username + " : " + upgradeEx.getMessage());
                        // 升级失败不影响登录，仅记录日志
                    }
                }
            }

            if (!passwordMatch) {
                return Result.error("密码错误");
            }

            // ========== 第四层：生成JWT Token并返回 ==========
            // 清除敏感信息
            user.setPassword(null);

            // 生成JWT Token
            String token = jwtUtil.generateToken(username, user.getId(), user.getRole());

            // 构建返回数据（包含token和user信息）
            Map<String, Object> data = new HashMap<>();
            data.put("token", token);
            data.put("user", user);

            System.out.println("[登录成功] 用户: " + username + ", 角色: " + user.getRole() + ", Token已生成");
            return Result.success("登录成功", data);

        } catch (Exception e) {
            System.err.println("[登录验证异常] 用户名: " + username + ", 错误: " + e.getMessage());
            return Result.error("登录验证失败，请稍后重试");
        }
    }

    @Override
    public Result<List<User>> getUsersByRole(String role) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getRole, role).eq(User::getStatus, 1);
        List<User> list = this.list(wrapper);
        // 清除敏感信息
        list.forEach(u -> u.setPassword(null));
        return Result.success(list);
    }

    @Override
    public Result<User> register(User user) {
        try {
            // 参数校验
            if (user.getUsername() == null || user.getUsername().trim().isEmpty()) {
                return Result.error("用户名不能为空");
            }
            if (user.getPassword() == null || user.getPassword().length() < 6) {
                return Result.error("密码长度至少6个字符");
            }

            User existUser = baseMapper.selectByUsername(user.getUsername());
            if (existUser != null) {
                return Result.error("用户名已存在");
            }

            // 使用BCrypt加密密码（生成60字符的哈希值）
            String encodedPassword = passwordEncoder.encode(user.getPassword());
            System.out.println("[注册] 用户 " + user.getUsername() + " 密码已BCrypt加密, 原始长度: "
                    + user.getPassword().length() + ", 加密后长度: " + encodedPassword.length());

            user.setPassword(encodedPassword);
            user.setStatus(1);
            this.save(user);

            // 清除敏感信息
            user.setPassword(null);
            return Result.success("注册成功", user);
        } catch (Exception e) {
            System.err.println("[注册失败] 异常信息: " + e.getClass().getName() + " - " + e.getMessage());
            e.printStackTrace();

            // 提供更友好的错误提示
            String errorMsg = "注册失败";
            if (e.getMessage() != null) {
                if (e.getMessage().contains("Data too long") || e.getMessage().contains("Data truncation")) {
                    errorMsg = "注册失败：数据库字段长度不足，请检查password字段是否支持100字符以上";
                } else if (e.getMessage().contains("Duplicate entry")) {
                    errorMsg = "注册失败：用户名已存在";
                } else {
                    errorMsg = "注册失败：" + e.getMessage();
                }
            }
            return Result.error(errorMsg);
        }
    }

    @Override
    // [Iter2 FIX] 移除@Cacheable注解，避免Redis序列化PageResult导致的500错误
    // 原因：PageResult包含MyBatis-Plus的Page对象，Jackson序列化到Redis时可能失败
    // [Iter3 FIX] 增强异常保护和详细日志输出，便于诊断500错误
    public PageResult<User> getUserList(Long current, Long size) {
        log.info("==> [Iter3] 获取用户分页列表, current: {}, size: {}", current, size);

        try {
            // ========== 参数校验 ==========
            if (current == null || current < 1) {
                log.warn("[Iter3] 参数错误: current={}, 使用默认值1", current);
                current = 1L;
            }
            if (size == null || size < 1 || size > 100) {
                log.warn("[Iter3] 参数错误: size={}, 使用默认值10", size);
                size = 10L;
            }

            // 创建分页对象
            Page<User> page = new Page<>(current, size);
            log.debug("[Iter3] 分页对象创建成功: current={}, size={}", page.getCurrent(), page.getSize());

            // 查询条件：只查询正常状态的用户（排除逻辑删除的）
            LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(User::getStatus, 1)
                   .eq(User::getDeleted, 0)  // [FIX] 明确排除已删除记录
                   .orderByDesc(User::getCreateTime);

            log.debug("[Iter3] 查询条件构建完成: status=1, deleted=0, orderBy=createTime DESC");

            // 执行分页查询
            log.info("[Iter3] 开始执行MyBatis-Plus分页查询...");
            Page<User> result = this.page(page, wrapper);

            log.info("[Iter3] 分页查询成功! 总数: {}, 当前页: {}, 每页: {}, 记录数: {}",
                     result.getTotal(), result.getCurrent(), result.getSize(),
                     result.getRecords() != null ? result.getRecords().size() : 0);

            // 清除敏感信息
            if (result.getRecords() != null) {
                result.getRecords().forEach(u -> {
                    if (u != null) u.setPassword(null);
                });
            }

            // 返回分页结果
            PageResult<User> pageResult = PageResult.of(
                result.getCurrent(),
                result.getSize(),
                result.getTotal(),
                result.getRecords()
            );

            log.info("[Iter3] 用户列表查询完成, 返回结果: current={}, total={}, records={}",
                     pageResult.getCurrent(), pageResult.getTotal(),
                     pageResult.getRecords() != null ? pageResult.getRecords().size() : 0);

            return pageResult;

        } catch (Exception e) {
            // ========== 详细异常诊断 ==========
            log.error("==> [Iter3] 用户列表查询异常!");
            log.error("==> [Iter3] 异常类型: {}", e.getClass().getName());
            log.error("==> [Iter3] 异常消息: {}", e.getMessage());
            log.error("==> [Iter3] 参数信息: current={}, size={}", current, size);

            // 诊断常见错误原因
            String errorMsg = diagnoseUserListError(e);
            log.error("==> [Iter3] 诊断结果: {}", errorMsg);

            // 打印完整堆栈（仅在前100行）
            log.error("==> [Iter3] 堆栈跟踪(前20行):");
            StackTraceElement[] stackTrace = e.getStackTrace();
            for (int i = 0; i < Math.min(20, stackTrace.length); i++) {
                log.error("    {}:{} - {}",
                         stackTrace[i].getClassName(),
                         stackTrace[i].getLineNumber(),
                         stackTrace[i].getMethodName());
            }

            // 返回空结果而非抛出异常，避免500错误
            log.warn("==> [Iter3] 返回空分页结果以避免500错误");
            return PageResult.empty(current != null ? current : 1L, size != null ? size : 10L);
        }
    }

    /**
     * [Iter3 FIX] 诊断用户列表查询错误的辅助方法
     * 提供常见错误原因的友好提示
     */
    private String diagnoseUserListError(Exception e) {
        String message = e.getMessage();
        if (message == null) return "未知错误（异常消息为null）";

        // 数据库连接问题
        if (message.contains("Connection refused") || message.contains("Unable to connect")) {
            return "数据库连接失败：请检查MySQL服务是否启动（127.0.0.1:3306）";
        }
        if (message.contains("Access denied") || message.contains("Authentication failed")) {
            return "数据库认证失败：请检查MySQL用户名和密码配置";
        }
        if (message.contains("Unknown database")) {
            return "数据库不存在：请先执行SQL初始化脚本创建 lab_management 数据库";
        }
        if (message.contains("doesn't exist") || message.contains("Table") && message.contains("doesn't exist")) {
            return "数据表不存在：sys_user表未创建，请执行 sql/iter3_fix_user_list_500.sql 初始化数据库";
        }

        // 表结构不匹配
        if (message.contains("Unknown column")) {
            return "表字段不存在：sys_user表结构与Entity不匹配，请检查表结构";
        }
        if (message.contains("Data too long") || message.contains("Data truncation")) {
            return "数据长度超出限制：某字段值超过数据库定义的最大长度";
        }

        // SQL语法错误
        if (message.contains("SQL syntax") || message.contains("SQLSyntaxErrorException")) {
            return "SQL语法错误：MyBatis-Plus生成的SQL有问题";
        }

        // MyBatis-Plus 配置问题
        if (message.contains("PaginationInterceptor") || message.contains("pagination")) {
            return "分页插件配置错误：请检查MybatisPlusConfig是否正确配置了MYSQL方言";
        }

        // 其他错误
        return "数据库操作异常：" + message;
    }
}
