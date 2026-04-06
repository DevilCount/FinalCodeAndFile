package com.sunyaxin.common.utils;

/**
 * 敏感数据脱敏工具类
 * 
 * 功能说明：
 * - 密码字段: 用 *** 替代完整内容
 * - Token/JWT: 只显示前8位...后4位
 * - 手机号: 138****1234 格式
 * - 身份证号: 110***********1234 格式
 * - 银行卡号: 6222****1234 格式
 * - 邮箱: t***@example.com 格式
 */
public final class SensitiveDataUtil {

    private SensitiveDataUtil() {
        // 工具类禁止实例化
    }

    /**
     * 脱敏密码
     * 示例: "mypassword" -> "***"
     */
    public static String desensitizePassword(String password) {
        if (password == null || password.isEmpty()) {
            return password;
        }
        return "***";
    }

    /**
     * 脱敏Token/JWT
     * 只显示前8位和后4位
     * 示例: "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
     *      -> "eyJhbGci...RsR8U"
     */
    public static String desensitizeToken(String token) {
        if (token == null || token.isEmpty()) {
            return token;
        }
        if (token.length() <= 12) {
            return "***";
        }
        return token.substring(0, 8) + "..." + token.substring(token.length() - 4);
    }

    /**
     * 脱敏手机号
     * 保留前3位和后4位，中间用*替代
     * 示例: "13812345678" -> "138****5678"
     */
    public static String desensitizePhone(String phone) {
        if (phone == null || phone.isEmpty()) {
            return phone;
        }
        if (phone.length() < 7) {
            return "***";
        }
        return phone.substring(0, 3) + "****" + phone.substring(phone.length() - 4);
    }

    /**
     * 脱敏身份证号
     * 保留前3位和后4位，中间用*替代
     * 示例: "110101199001011234" -> "110***********1234"
     */
    public static String desensitizeIdCard(String idCard) {
        if (idCard == null || idCard.isEmpty()) {
            return idCard;
        }
        if (idCard.length() < 8) {
            return "***";
        }
        int maskLength = idCard.length() - 7;
        StringBuilder masked = new StringBuilder(idCard.substring(0, 3));
        for (int i = 0; i < maskLength; i++) {
            masked.append("*");
        }
        masked.append(idCard.substring(idCard.length() - 4));
        return masked.toString();
    }

    /**
     * 脱敏银行卡号
     * 保留前4位和后4位，中间用*替代
     * 示例: "6222021234567890123" -> "6222******90123"
     */
    public static String desensitizeBankCard(String bankCard) {
        if (bankCard == null || bankCard.isEmpty()) {
            return bankCard;
        }
        if (bankCard.length() < 8) {
            return "***";
        }
        int maskLength = bankCard.length() - 8;
        StringBuilder masked = new StringBuilder(bankCard.substring(0, 4));
        for (int i = 0; i < maskLength; i++) {
            masked.append("*");
        }
        masked.append(bankCard.substring(bankCard.length() - 4));
        return masked.toString();
    }

    /**
     * 脱敏邮箱
     * 用户名只显示首字符，@后面保持不变
     * 示例: "test@example.com" -> "t***@example.com"
     */
    public static String desensitizeEmail(String email) {
        if (email == null || email.isEmpty()) {
            return email;
        }
        int atIndex = email.indexOf("@");
        if (atIndex <= 1) {
            return email;
        }
        return email.charAt(0) + "***" + email.substring(atIndex);
    }

    /**
     * 脱敏姓名
     * 只显示姓氏，名字用*替代（2个字的名字只显示1个*）
     * 示例: "张三" -> "张*", "张三丰" -> "张**", "欧阳锋" -> "欧**"
     */
    public static String desensitizeName(String name) {
        if (name == null || name.isEmpty()) {
            return name;
        }
        if (name.length() <= 1) {
            return "*";
        }
        StringBuilder masked = new StringBuilder(name.charAt(0));
        for (int i = 1; i < name.length(); i++) {
            masked.append("*");
        }
        return masked.toString();
    }

    /**
     * 通用脱敏方法
     * 根据字段类型自动选择脱敏策略
     *
     * @param fieldName 字段名（用于判断类型）
     * @param value 原始值
     * @return 脱敏后的值
     */
    public static String desensitize(String fieldName, String value) {
        if (value == null || value.isEmpty()) {
            return value;
        }
        
        String lowerFieldName = fieldName.toLowerCase();
        
        // 密码相关字段
        if (lowerFieldName.contains("password") || 
            lowerFieldName.contains("passwd") || 
            lowerFieldName.contains("pwd")) {
            return desensitizePassword(value);
        }
        
        // Token/JWT相关字段
        if (lowerFieldName.contains("token") || 
            lowerFieldName.contains("jwt") ||
            lowerFieldName.contains("authorization") ||
            lowerFieldName.contains("access_token")) {
            return desensitizeToken(value);
        }
        
        // 手机号相关字段
        if (lowerFieldName.contains("phone") || 
            lowerFieldName.contains("mobile") ||
            lowerFieldName.contains("tel")) {
            return desensitizePhone(value);
        }
        
        // 身份证相关字段
        if (lowerFieldName.contains("idcard") || 
            lowerFieldName.contains("id_card") ||
            lowerFieldName.contains("identity")) {
            return desensitizeIdCard(value);
        }
        
        // 银行卡相关字段
        if (lowerFieldName.contains("bank") || 
            lowerFieldName.contains("card")) {
            return desensitizeBankCard(value);
        }
        
        // 邮箱相关字段
        if (lowerFieldName.contains("email") || 
            lowerFieldName.contains("mail")) {
            return desensitizeEmail(value);
        }
        
        // 姓名相关字段
        if (lowerFieldName.contains("name") && !lowerFieldName.contains("username")) {
            return desensitizeName(value);
        }
        
        // 默认不脱敏
        return value;
    }
}
