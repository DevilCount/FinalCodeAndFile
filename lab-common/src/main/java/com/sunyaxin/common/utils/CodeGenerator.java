package com.sunyaxin.common.utils;

import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.RandomUtil;

/**
 * 编号生成工具类
 */
public class CodeGenerator {

    /**
     * 生成标本编号：SP + yyyyMMdd + 4位随机数
     */
    public static String generateSampleNo() {
        return "SP" + DateUtil.today().replace("-", "") + RandomUtil.randomNumbers(4);
    }

    /**
     * 生成报告编号：RP + yyyyMMdd + 4位随机数
     */
    public static String generateReportNo() {
        return "RP" + DateUtil.today().replace("-", "") + RandomUtil.randomNumbers(4);
    }

    /**
     * 生成设备编号：DE + yyyyMMdd + 4位随机数
     */
    public static String generateDeviceNo() {
        return "DE" + DateUtil.today().replace("-", "") + RandomUtil.randomNumbers(4);
    }
}
