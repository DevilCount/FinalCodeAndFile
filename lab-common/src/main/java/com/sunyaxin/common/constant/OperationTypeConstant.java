package com.sunyaxin.common.constant;

/**
 * 操作类型常量 - 定义所有可记录的操作类型
 */
public class OperationTypeConstant {

    // ========== 标本模块 ==========
    public static final String SAMPLE_CREATE = "CREATE";           // 创建标本
    public static final String SAMPLE_RECEIVE = "RECEIVE";         // 签收标本
    public static final String SAMPLE_START_TEST = "START_TEST";    // 开始检验
    public static final String SAMPLE_COMPLETE = "COMPLETE";       // 完成检验
    public static final String SAMPLE_ARCHIVE = "ARCHIVE";         // 归档标本
    public static final String SAMPLE_ABNORMAL = "ABNORMAL";      // 标本异常
    public static final String SAMPLE_REJECT = "REJECT";           // 拒收标本

    // ========== 报告模块 ==========
    public static final String REPORT_CREATE = "REPORT_CREATE";           // 创建报告
    public static final String REPORT_CREATE_ENHANCED = "REPORT_CREATE_ENHANCED"; // 创建增强版报告
    
    public static final String REPORT_INPUT = "INPUT";                     // 录入结果
    public static final String REPORT_INPUT_STRUCTURED = "INPUT_STRUCTURED"; // 录入结构化结果
    
    public static final String REPORT_AI_DIAGNOSE = "AI_DIAGNOSE";         // AI诊断
    public static final String REPORT_AI_DIAGNOSE_INVOKE = "AI_DIAGNOSE_INVOKE"; // 调用AI诊断
    
    public static final String REPORT_REVIEW = "REVIEW";                   // 审核报告
    
    // 双层审核流程
    public static final String REPORT_TECHNICAL_SUBMIT = "TECHNICAL_SUBMIT";   // 提交技术审核
    public static final String REPORT_TECHNICAL_APPROVE = "TECHNICAL_APPROVE"; // 技术审核通过
    public static final String REPORT_TECHNICAL_REJECT = "TECHNICAL_REJECT";   // 技术审核驳回
    
    public static final String REPORT_CLINICAL_SUBMIT = "CLINICAL_SUBMIT";     // 提交临床审核
    public static final String REPORT_CLINICAL_APPROVE = "CLINICAL_APPROVE";   // 临床审核通过
    public static final String REPORT_CLINICAL_REJECT = "CLINICAL_REJECT";     // 临床审核驳回
    
    public static final String REPORT_REJECT = "REPORT_REJECT";            // 驳回报告（兼容旧版）
    public static final String REPORT_PUBLISH = "PUBLISH";                // 发布报告
    public static final String REPORT_RECALL = "RECALL";                  // 撤回报告
    public static final String REPORT_REVOKE = "REVOKE";                  // 撤销报告
    public static final String REPORT_ARCHIVE = "ARCHIVE";                // 归档报告
    public static final String REPORT_PRINT = "PRINT";                    // 打印报告
    
    // 批量操作
    public static final String REPORT_BATCH_TECHNICAL_SUBMIT = "BATCH_TECHNICAL_SUBMIT";   // 批量提交技术审核
    public static final String REPORT_BATCH_TECHNICAL_REVIEW = "BATCH_TECHNICAL_REVIEW";   // 批量技术审核
    public static final String REPORT_BATCH_CLINICAL_SUBMIT = "BATCH_CLINICAL_SUBMIT";     // 批量提交临床审核
    public static final String REPORT_BATCH_CLINICAL_REVIEW = "BATCH_CLINICAL_REVIEW";     // 批量临床审核
    public static final String REPORT_BATCH_PUBLISH = "BATCH_PUBLISH";                     // 批量发布
    public static final String REPORT_BATCH_ARCHIVE = "BATCH_ARCHIVE";                     // 批量归档
    
    // 数据导入导出
    public static final String REPORT_EXPORT_EXCEL = "EXPORT_EXCEL";      // 导出Excel
    public static final String REPORT_IMPORT_EXCEL = "IMPORT_EXCEL";      // 导入Excel
    public static final String REPORT_EXPORT_PDF = "EXPORT_PDF";          // 导出PDF
    
    // 批量操作（通用）
    public static final String BATCH_OPERATION = "BATCH_OPERATION";      // 批量操作
    public static final String BATCH_DELETE = "BATCH_DELETE";            // 批量删除
    public static final String BATCH_IMPORT = "BATCH_IMPORT";            // 批量导入

    // ========== 用户模块 ==========
    public static final String USER_LOGIN = "LOGIN";              // 用户登录
    public static final String USER_LOGOUT = "LOGOUT";            // 用户登出
    public static final String USER_REGISTER = "REGISTER";        // 用户注册
    public static final String USER_UPDATE = "UPDATE";            // 更新用户
    public static final String USER_DELETE = "DELETE";            // 删除用户
    public static final String USER_PASSWORD_CHANGE = "PWD_CHANGE"; // 修改密码

    // ========== 设备模块 ==========
    public static final String DEVICE_UPDATE_STATUS = "DEV_STATUS"; // 更新设备状态
    public static final String DEVICE_MAINTENANCE = "MAINTENANCE";  // 设备维护

    // ========== 模块名称 ==========
    public static final String MODULE_SAMPLE = "标本管理";
    public static final String MODULE_REPORT = "报告管理";
    public static final String MODULE_USER = "用户管理";
    public static final String MODULE_DEVICE = "设备管理";
    public static final String MODULE_SYSTEM = "系统管理";
}
