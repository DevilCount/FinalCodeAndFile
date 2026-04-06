package com.sunyaxin.hl7.util;

import ca.uhn.hl7v2.HL7Exception;
import ca.uhn.hl7v2.model.Message;
import ca.uhn.hl7v2.model.v25.message.ORU_R01;
import ca.uhn.hl7v2.parser.PipeParser;
import ca.uhn.hl7v2.parser.Parser;
import com.sunyaxin.hl7.dto.Hl7MessageDTO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * HL7消息解析工具类
 */
@Slf4j
@Component
public class Hl7MessageParser {

    private final Parser parser = new PipeParser();

    /**
     * 解析HL7消息
     */
    public Hl7MessageDTO parse(String hl7Message) {
        try {
            Message message = parser.parse(hl7Message);
            Hl7MessageDTO dto = new Hl7MessageDTO();
            dto.setRawMessage(hl7Message);

            // 获取消息类型
            String messageType = message.getName();
            dto.setMessageType(messageType);

            // 根据消息类型解析
            if ("ORU_R01".equals(messageType)) {
                parseORU_R01((ORU_R01) message, dto);
            }

            return dto;
        } catch (HL7Exception e) {
            log.error("HL7消息解析失败", e);
            return null;
        }
    }

    /**
     * 解析检验结果消息(ORU_R01)
     */
    private void parseORU_R01(ORU_R01 message, Hl7MessageDTO dto) throws HL7Exception {
        // 解析患者信息
        dto.setPatientId(message.getPATIENT_RESULT().getPATIENT().getPID().getPatientIdentifierList(0).getIDNumber().getValue());
        dto.setPatientName(message.getPATIENT_RESULT().getPATIENT().getPID().getPatientName(0).getFamilyName().getSurname().getValue());
        dto.setPatientGender(message.getPATIENT_RESULT().getPATIENT().getPID().getAdministrativeSex().getValue());

        // 解析检验结果
        StringBuilder results = new StringBuilder();
        int obsCount = message.getPATIENT_RESULT().getORDER_OBSERVATIONReps();
        for (int i = 0; i < obsCount; i++) {
            var orderObs = message.getPATIENT_RESULT().getORDER_OBSERVATION(i);
            int obxCount = orderObs.getOBSERVATIONReps();
            for (int j = 0; j < obxCount; j++) {
                var obx = orderObs.getOBSERVATION(j).getOBX();
                String itemCode = obx.getObservationIdentifier().getIdentifier().getValue();
                String value = obx.getObservationValue(0).getData().toString();
                String unit = obx.getUnits().getIdentifier().getValue();
                results.append(itemCode).append(": ").append(value).append(" ").append(unit).append("; ");
            }
        }
        dto.setTestResults(results.toString());
    }

    /**
     * 生成HL7检验结果消息
     */
    public String generateORU_R01(Hl7MessageDTO dto) {
        try {
            ORU_R01 message = new ORU_R01();
            message.initQuickstart("ORU", "R01", "P");

            // 设置患者信息
            var patient = message.getPATIENT_RESULT().getPATIENT();
            patient.getPID().getPatientIdentifierList(0).getIDNumber().setValue(dto.getPatientId());
            patient.getPID().getPatientName(0).getFamilyName().getSurname().setValue(dto.getPatientName());
            patient.getPID().getAdministrativeSex().setValue(dto.getPatientGender());

            // 设置检验结果
            var orderObs = message.getPATIENT_RESULT().getORDER_OBSERVATION(0);
            orderObs.getOBR().getSetIDOBR().setValue("1");
            orderObs.getOBR().getUniversalServiceIdentifier().getIdentifier().setValue(dto.getTestItems());

            // 简化处理：直接返回字符串格式的HL7消息
            StringBuilder sb = new StringBuilder();
            sb.append("MSH|^~\\&|LAB|HOSPITAL|HIS|HOSPITAL|").append(System.currentTimeMillis())
              .append("||ORU^R01|MSG001|P|2.5\r");
            sb.append("PID|1||").append(dto.getPatientId())
              .append("||").append(dto.getPatientName())
              .append("||").append(dto.getPatientGender()).append("\r");
            sb.append("OBR|1|||").append(dto.getTestItems()).append("\r");
            sb.append("OBX|1|ST|RESULT||").append(dto.getTestResults()).append("||||||F\r");
            
            return sb.toString();
        } catch (Exception e) {
            log.error("生成HL7消息失败", e);
            return null;
        }
    }
}
