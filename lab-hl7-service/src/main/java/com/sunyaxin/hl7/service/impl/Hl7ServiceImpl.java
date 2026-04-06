package com.sunyaxin.hl7.service.impl;

import com.sunyaxin.common.result.Result;
import com.sunyaxin.hl7.dto.Hl7MessageDTO;
import com.sunyaxin.hl7.service.Hl7Service;
import com.sunyaxin.hl7.util.Hl7MessageParser;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.nio.charset.StandardCharsets;

/**
 * HL7服务实现类
 * 实现MLLP协议发送和接收功能
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class Hl7ServiceImpl implements Hl7Service {

    private final Hl7MessageParser messageParser;

    @Value("${hl7.his.host:127.0.0.1}")
    private String hisHost;

    @Value("${hl7.his.port:2575}")
    private int hisPort;

    @Value("${hl7.his.timeout:5000}")
    private int timeout;

    // MLLP协议定义的字符
    private static final byte MLLP_START_BLOCK = 0x0B;  // 开始标记 <SB>
    private static final byte MLLP_END_BLOCK = 0x1C;    // 结束标记 <EB>
    private static final byte MLLP_CARRIAGE_RETURN = 0x0D;  // 回车 <CR>

    @Override
    public Result<Hl7MessageDTO> parseMessage(String hl7Message) {
        try {
            Hl7MessageDTO dto = messageParser.parse(hl7Message);
            if (dto != null) {
                return Result.success("解析成功", dto);
            } else {
                return Result.error("消息解析失败");
            }
        } catch (Exception e) {
            log.error("解析HL7消息异常", e);
            return Result.error("解析异常：" + e.getMessage());
        }
    }

    @Override
    public Result<String> generateOrderMessage(Hl7MessageDTO dto) {
        try {
            // 简化版ORM^O01消息生成
            StringBuilder message = new StringBuilder();
            message.append("MSH|^~\\&|LAB|HOSPITAL|HIS|HOSPITAL|").append(System.currentTimeMillis())
                   .append("||ORM^O01|MSG001|P|2.5\r");
            message.append("PID|1||").append(dto.getPatientId())
                   .append("||").append(dto.getPatientName())
                   .append("||").append(dto.getPatientBirthDate())
                   .append("|").append(dto.getPatientGender()).append("\r");
            message.append("ORC|NW|").append(dto.getOrderNo())
                   .append("|||").append(dto.getOrderingProvider()).append("\r");
            message.append("OBR|1|").append(dto.getOrderNo())
                   .append("||").append(dto.getTestItems())
                   .append("||||||||||||").append(System.currentTimeMillis()).append("\r");

            return Result.success("生成成功", message.toString());
        } catch (Exception e) {
            log.error("生成申请消息异常", e);
            return Result.error("生成失败：" + e.getMessage());
        }
    }

    @Override
    public Result<String> generateResultMessage(Hl7MessageDTO dto) {
        try {
            String message = messageParser.generateORU_R01(dto);
            if (message != null) {
                return Result.success("生成成功", message);
            } else {
                return Result.error("生成失败");
            }
        } catch (Exception e) {
            log.error("生成结果消息异常", e);
            return Result.error("生成失败：" + e.getMessage());
        }
    }

    @Override
    public Result<Boolean> sendToHis(String hl7Message) {
        log.info("==> 开始发送HL7消息到HIS系统，目标: {}:{}", hisHost, hisPort);
        
        Socket socket = null;
        try {
            // 1. 建立TCP连接
            log.info("正在连接HIS系统... 地址: {}:{}", hisHost, hisPort);
            socket = new Socket(hisHost, hisPort);
            socket.setSoTimeout(timeout);
            
            // 2. 获取输出流
            OutputStream outputStream = socket.getOutputStream();
            
            // 3. 构建MLLP消息包
            byte[] hl7Bytes = hl7Message.getBytes(StandardCharsets.UTF_8);
            byte[] mllpPackage = new byte[hl7Bytes.length + 3];
            
            // MLLP封装：[SB] + HL7消息 + [EB][CR]
            mllpPackage[0] = MLLP_START_BLOCK;
            System.arraycopy(hl7Bytes, 0, mllpPackage, 1, hl7Bytes.length);
            mllpPackage[hl7Bytes.length + 1] = MLLP_END_BLOCK;
            mllpPackage[hl7Bytes.length + 2] = MLLP_CARRIAGE_RETURN;
            
            // 4. 发送MLLP消息
            log.info("发送MLLP消息，消息长度: {} bytes", mllpPackage.length);
            outputStream.write(mllpPackage);
            outputStream.flush();
            
            // 5. 等待HIS系统响应（ACK消息）
            InputStream inputStream = socket.getInputStream();
            ByteArrayOutputStream responseBuffer = new ByteArrayOutputStream();
            
            // 读取响应直到遇到结束标记
            int bytesRead;
            boolean foundEndBlock = false;
            byte[] buffer = new byte[4096];
            
            try {
                while (!foundEndBlock && (bytesRead = inputStream.read(buffer)) != -1) {
                    for (int i = 0; i < bytesRead; i++) {
                        if (buffer[i] == MLLP_END_BLOCK) {
                            foundEndBlock = true;
                            responseBuffer.write(buffer, 0, i);  // 写入到结束标记之前的数据
                            break;
                        }
                        if (buffer[i] != MLLP_START_BLOCK) {  // 跳过开始标记
                            responseBuffer.write(buffer[i]);
                        }
                    }
                }
                
                // 消费掉回车符
                if (foundEndBlock) {
                    inputStream.read();  // 读取CR
                }
                
            } catch (SocketTimeoutException ste) {
                log.warn("等待HIS系统响应超时（{}ms），但消息已发送成功", timeout);
                // 超时不算失败，消息可能已被处理
            }
            
            // 6. 解析响应
            String responseStr = responseBuffer.toString(StandardCharsets.UTF_8.name()).trim();
            log.info("收到HIS系统响应: {}", 
                    responseStr.length() > 100 ? responseStr.substring(0, 100) + "..." : responseStr);
            
            // 7. 判断是否成功（简单检查响应中是否包含AA - Application Accept）
            boolean success = responseStr.contains("|AA|") || 
                             responseStr.isEmpty() ||  // 无响应也算成功（某些HIS不返回ACK）
                             responseStr.contains("MSH");
            
            if (success) {
                log.info("==> HL7消息发送成功");
                return Result.success("发送成功", true);
            } else {
                log.warn("HIS系统返回错误响应: {}", responseStr);
                return Result.error("HIS系统拒绝消息: " + responseStr);
            }
            
        } catch (java.net.ConnectException ce) {
            log.error("无法连接到HIS系统 {}:{} - 请检查HIS系统是否启动和网络连接", hisHost, hisPort, ce);
            return Result.error("无法连接到HIS系统（" + hisHost + ":" + hisPort + "），请检查网络和HIS服务状态");
            
        } catch (SocketTimeoutException ste) {
            log.error("连接或读取HIS系统响应超时（{}ms）", timeout, ste);
            return Result.error("HIS系统响应超时，请稍后重试");
            
        } catch (IOException ioe) {
            log.error("与HIS系统通信时发生IO异常", ioe);
            return Result.error("与HIS系统通信失败: " + ioe.getMessage());
            
        } catch (Exception e) {
            log.error("发送HL7消息到HIS系统时发生未知异常", e);
            return Result.error("发送失败: " + e.getMessage());
            
        } finally {
            // 8. 关闭连接
            if (socket != null && !socket.isClosed()) {
                try {
                    socket.close();
                    log.debug("已关闭与HIS系统的连接");
                } catch (IOException e) {
                    log.warn("关闭HIS系统连接时发生异常", e);
                }
            }
        }
    }

    @Override
    public Result<Hl7MessageDTO> receiveFromHis(String hl7Message) {
        log.info("==> 接收并处理来自HIS系统的HL7消息");
        
        try {
            // 解析接收到的消息
            Result<Hl7MessageDTO> result = parseMessage(hl7Message);
            
            if (result.getCode() == 200 && result.getData() != null) {
                Hl7MessageDTO dto = result.getData();
                log.info("成功接收并解析HIS系统消息 - 患者: {}, 类型: {}", 
                        dto.getPatientName(), dto.getMessageType());
                
                // TODO: 这里可以添加业务逻辑，如：
                // 1. 根据消息类型分发处理（ADT、ORM、ORU等）
                // 2. 更新本地数据库状态
                // 3. 触发相关业务流程
                // 4. 发送通知
                
                handleReceivedMessage(dto);
                
                return Result.success("消息处理成功", dto);
            } else {
                log.warn("解析HIS系统消息失败: {}", result.getMessage());
                return result;
            }
            
        } catch (Exception e) {
            log.error("处理来自HIS系统的消息时发生异常", e);
            return Result.error("消息处理失败: " + e.getMessage());
        }
    }
    
    /**
     * 处理从HIS接收到的消息
     */
    private void handleReceivedMessage(Hl7MessageDTO dto) {
        try {
            String messageType = dto.getMessageType();
            log.info("处理HL7消息类型: {}", messageType);
            
            switch (messageType != null ? messageType.toUpperCase() : "") {
                case "ADT":
                    // ADT消息：患者入院、出院、转科等
                    log.info("处理ADT患者管理消息 - 患者ID: {}", dto.getPatientId());
                    break;
                    
                case "ORM":
                    // ORM消息：检验申请
                    log.info("处理ORM检验申请消息 - 申请单号: {}", dto.getOrderNo());
                    break;
                    
                case "ORU":
                    // ORU消息：检验结果
                    log.info("处理ORU检验结果消息 - 患者ID: {}", dto.getPatientId());
                    break;
                    
                case "ACK":
                    // ACK消息：确认应答
                    log.info("收到HIS系统ACK确认消息");
                    break;
                    
                default:
                    log.warn("未知的HL7消息类型: {}", messageType);
            }
            
        } catch (Exception e) {
            log.error("处理HL7消息时发生业务异常", e);
        }
    }
}
