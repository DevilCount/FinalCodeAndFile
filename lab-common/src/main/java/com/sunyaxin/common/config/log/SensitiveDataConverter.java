package com.sunyaxin.common.config.log;

import ch.qos.logback.classic.pattern.MessageConverter;
import ch.qos.logback.classic.spi.ILoggingEvent;
import com.sunyaxin.common.utils.SensitiveDataUtil;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 日志脱敏转换器
 * 
 * 用于在Logback输出日志时自动对敏感数据进行脱敏处理
 * 支持的脱敏类型：
 * - password=xxx -> password=***
 * - token=xxx / jwt=xxx / authorization=xxx -> token=xxx...xxxx (前8后4)
 * - 手机号: 13812345678 -> 138****5678
 * - 身份证号: 110101199001011234 -> 110***********1234
 * - 银行卡号: 6222021234567890123 -> 6222******90123
 */
public class SensitiveDataConverter extends MessageConverter {

    // 密码模式: password=xxx, pwd=xxx 等
    private static final Pattern PASSWORD_PATTERN = Pattern.compile(
            "(password|pwd|passwd)\\s*[=:：]\\s*['\"]?([^'\"\\s,}]+)['\"]?", 
            Pattern.CASE_INSENSITIVE);
    
    // Token/JWT模式: token=xxx, authorization=xxx, Bearer xxx
    private static final Pattern TOKEN_PATTERN = Pattern.compile(
            "(token|jwt|authorization|access_token)\\s*[=:：]\\s*['\"]?([^'\"\\s,}]{12,})['\"]?|Bearer\\s+([A-Za-z0-9_-]+\\.?[A-Za-z0-9_-]+)", 
            Pattern.CASE_INSENSITIVE);
    
    // 手机号模式: 11位数字，以1开头
    private static final Pattern PHONE_PATTERN = Pattern.compile(
            "(?<![\\d])(1[3-9]\\d{9})(?![\\d])");
    
    // 身份证号模式: 15位或18位数字
    private static final Pattern ID_CARD_PATTERN = Pattern.compile(
            "(?<![\\d])(\\d{15}|\\d{17}[\\dXx])(?![\\d])");
    
    // 银行卡号模式: 16-19位数字
    private static final Pattern BANK_CARD_PATTERN = Pattern.compile(
            "(?<![\\d])(\\d{16,19})(?![\\d])");

    @Override
    public String convert(ILoggingEvent event) {
        String originalMessage = super.convert(event);
        return desensitize(originalMessage);
    }

    /**
     * 对日志消息进行脱敏处理
     */
    public static String desensitize(String message) {
        if (message == null || message.isEmpty()) {
            return message;
        }

        String result = message;
        
        // 1. 脱敏密码
        Matcher passwordMatcher = PASSWORD_PATTERN.matcher(result);
        if (passwordMatcher.find()) {
            StringBuffer sb = new StringBuffer();
            do {
                passwordMatcher.appendReplacement(sb, 
                    passwordMatcher.group(1) + "=" + SensitiveDataUtil.desensitizePassword(passwordMatcher.group(2)));
            } while (passwordMatcher.find());
            passwordMatcher.appendTail(sb);
            result = sb.toString();
        }
        
        // 2. 脱敏Token/JWT
        Matcher tokenMatcher = TOKEN_PATTERN.matcher(result);
        if (tokenMatcher.find()) {
            StringBuffer sb = new StringBuffer();
            do {
                String key = tokenMatcher.group(1) != null ? tokenMatcher.group(1) : "token";
                String value = tokenMatcher.group(2) != null ? tokenMatcher.group(2) : tokenMatcher.group(3);
                if (value != null && !value.isEmpty()) {
                    tokenMatcher.appendReplacement(sb, 
                        key + "=" + SensitiveDataUtil.desensitizeToken(value));
                }
            } while (tokenMatcher.find());
            tokenMatcher.appendTail(sb);
            result = sb.toString();
        }
        
        // 3. 脱敏手机号
        Matcher phoneMatcher = PHONE_PATTERN.matcher(result);
        if (phoneMatcher.find()) {
            StringBuffer sb = new StringBuffer();
            do {
                phoneMatcher.appendReplacement(sb, 
                    SensitiveDataUtil.desensitizePhone(phoneMatcher.group(1)));
            } while (phoneMatcher.find());
            phoneMatcher.appendTail(sb);
            result = sb.toString();
        }
        
        // 4. 脱敏身份证号
        Matcher idCardMatcher = ID_CARD_PATTERN.matcher(result);
        if (idCardMatcher.find()) {
            StringBuffer sb = new StringBuffer();
            do {
                idCardMatcher.appendReplacement(sb, 
                    SensitiveDataUtil.desensitizeIdCard(idCardMatcher.group(1)));
            } while (idCardMatcher.find());
            idCardMatcher.appendTail(sb);
            result = sb.toString();
        }
        
        // 5. 脱敏银行卡号
        Matcher bankCardMatcher = BANK_CARD_PATTERN.matcher(result);
        if (bankCardMatcher.find()) {
            StringBuffer sb = new StringBuffer();
            do {
                bankCardMatcher.appendReplacement(sb, 
                    SensitiveDataUtil.desensitizeBankCard(bankCardMatcher.group(1)));
            } while (bankCardMatcher.find());
            bankCardMatcher.appendTail(sb);
            result = sb.toString();
        }

        return result;
    }
}
