package com.sunyaxin.hl7.controller;

import com.sunyaxin.common.result.Result;
import com.sunyaxin.hl7.dto.Hl7MessageDTO;
import com.sunyaxin.hl7.service.Hl7Service;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * HL7接口Controller
 */
@RestController
@RequestMapping("/hl7")
@RequiredArgsConstructor
@Validated
@Slf4j
public class Hl7Controller {

    private final Hl7Service hl7Service;

    /**
     * 解析HL7消息
     */
    @PostMapping("/parse")
    public Result<Hl7MessageDTO> parseMessage(@RequestBody String hl7Message) {
        return hl7Service.parseMessage(hl7Message);
    }

    /**
     * 生成检验申请消息
     */
    @PostMapping("/generate-order")
    public Result<String> generateOrderMessage(@Valid @RequestBody Hl7MessageDTO dto) {
        return hl7Service.generateOrderMessage(dto);
    }

    /**
     * 生成检验结果消息
     */
    @PostMapping("/generate-result")
    public Result<String> generateResultMessage(@Valid @RequestBody Hl7MessageDTO dto) {
        return hl7Service.generateResultMessage(dto);
    }

    /**
     * 发送消息到HIS系统
     */
    @PostMapping("/send-to-his")
    public Result<Boolean> sendToHis(@RequestBody String hl7Message) {
        return hl7Service.sendToHis(hl7Message);
    }

    /**
     * 从HIS系统接收消息（模拟接口）
     */
    @PostMapping("/receive-from-his")
    public Result<Hl7MessageDTO> receiveFromHis(@RequestBody String hl7Message) {
        return hl7Service.receiveFromHis(hl7Message);
    }

    /**
     * 消息转换测试
     */
    @PostMapping("/transform")
    public Result<String> transformMessage(@Valid @RequestBody Hl7MessageDTO dto) {
        // 生成ORU_R01消息
        return hl7Service.generateResultMessage(dto);
    }
}
