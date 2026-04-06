package com.sunyaxin.hl7.service;

import com.sunyaxin.common.result.Result;
import com.sunyaxin.hl7.dto.Hl7MessageDTO;

/**
 * HL7服务接口
 */
public interface Hl7Service {

    /**
     * 解析HL7消息
     */
    Result<Hl7MessageDTO> parseMessage(String hl7Message);

    /**
     * 生成检验申请消息
     */
    Result<String> generateOrderMessage(Hl7MessageDTO dto);

    /**
     * 生成检验结果消息
     */
    Result<String> generateResultMessage(Hl7MessageDTO dto);

    /**
     * 发送消息到HIS系统
     */
    Result<Boolean> sendToHis(String hl7Message);

    /**
     * 从HIS系统接收消息
     */
    Result<Hl7MessageDTO> receiveFromHis(String hl7Message);
}
