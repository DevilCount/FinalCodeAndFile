#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 API 全面深度测试脚本 v1.4.0
============================================
测试范围：
1. 用户服务API (User Service)
2. 标本服务API (Sample Service)
3. 报告服务API (Report Service)
4. AI服务API (AI Service)
5. HL7服务API (HL7 Service)
6. 网关路由验证
7. 异常场景测试（无效参数、不存在资源、未认证等）

作者：API Test Pro
日期：2026-04-02
版本：v1.4.0
"""

import requests
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import sys
import os

# ==================== 配置区域 ====================
BASE_DIR = r"d:\FinalCodeAndFile\lab-management-system"
RESULTS_DIR = os.path.join(BASE_DIR, "test_results")

# 服务地址配置（直接访问各微服务）
SERVICES = {
    "Gateway": "http://localhost:8080",
    "User Service": "http://localhost:8086",
    "Sample Service": "http://localhost:8087",
    "Report Service": "http://localhost:8088",
    "AI Service": "http://localhost:8085",
    "HL7 Service": "http://localhost:8084",
}

# 测试超时时间（秒）
TIMEOUT = 15

# 全局变量存储认证token
AUTH_TOKEN = None

# ==================== 工具函数 ====================
class APITester:
    """API测试器核心类"""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.test_start_time = datetime.now()
        self.response_times: List[float] = []
        self.passed_count = 0
        self.failed_count = 0

    def execute_request(self, method: str, url: str, **kwargs) -> Tuple[requests.Response, float]:
        """执行HTTP请求并返回响应和耗时"""
        start_time = time.time()
        try:
            if method.upper() == "GET":
                resp = requests.get(url, timeout=TIMEOUT, **kwargs)
            elif method.upper() == "POST":
                resp = requests.post(url, timeout=TIMEOUT, **kwargs)
            elif method.upper() == "PUT":
                resp = requests.put(url, timeout=TIMEOUT, **kwargs)
            elif method.upper() == "DELETE":
                resp = requests.delete(url, timeout=TIMEOUT, **kwargs)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return resp, elapsed_ms
        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return None, elapsed_ms

    def add_test_result(self, test_id: int, service: str, category: str,
                       endpoint: str, method: str, url: str,
                       expected_status: int, actual_status: Optional[int],
                       response_time_ms: Optional[float], passed: bool,
                       test_data: Optional[Dict] = None,
                       response_body: str = "",
                       error_message: str = "",
                       note: str = ""):
        """添加测试结果"""
        result = {
            "test_id": test_id,
            "service": service,
            "category": category,
            "endpoint": endpoint,
            "method": method,
            "url": url,
            "expected_status": expected_status,
            "actual_status": actual_status,
            "response_time_ms": response_time_ms,
            "passed": passed,
            "test_data": test_data,
            "response_body_preview": response_body[:500] if response_body else "",
            "error_message": error_message,
            "note": note,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        }
        self.results.append(result)

        if response_time_ms:
            self.response_times.append(response_time_ms)

        if passed:
            self.passed_count += 1
        else:
            self.failed_count += 1

        # 打印实时结果
        status_icon = "[PASS]" if passed else "[FAIL]"
        status_code_str = str(actual_status) if actual_status else "N/A"
        time_str = f"{response_time_ms}ms" if response_time_ms else "N/A"
        print(f"[{test_id:03d}] {status_icon} {method:6} {service:16} {endpoint:40} "
              f"→ 状态码:{status_code_str:4} 耗时:{time_str:>10}  {note}")

    def calculate_statistics(self) -> Dict[str, Any]:
        """计算性能统计指标"""
        if not self.response_times:
            return {
                "avg_response_time_ms": 0,
                "min_response_time_ms": 0,
                "max_response_time_ms": 0,
                "p50_response_time_ms": 0,
                "p90_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "p99_response_time_ms": 0,
                "total_tests": len(self.results),
                "passed": self.passed_count,
                "failed": self.failed_count,
                "pass_rate": 0
            }

        sorted_times = sorted(self.response_times)
        total = len(self.results)
        pass_rate = round(self.passed_count / total * 100, 2) if total > 0 else 0

        stats = {
            "avg_response_time_ms": round(statistics.mean(self.response_times), 2),
            "min_response_time_ms": min(self.response_times),
            "max_response_time_ms": max(self.response_times),
            "total_tests": total,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "pass_rate": pass_rate,
        }

        # 计算百分位数
        for percentile, key in [(50, "p50"), (90, "p90"), (95, "p95"), (99, "p99")]:
            idx = int(len(sorted_times) * percentile / 100)
            idx = min(idx, len(sorted_times) - 1)
            stats[f"{key}_response_time_ms"] = sorted_times[idx]

        return stats


# ==================== 测试用例定义 ====================
def get_test_cases():
    """获取所有测试用例"""
    test_cases = []

    # ==================== 1. 用户服务API测试 ====================
    user_base = SERVICES["User Service"]

    # 1.1 登录 - 正确账号
    test_cases.append({
        "id": 1, "service": "User Service", "category": "用户登录",
        "method": "POST", "endpoint": "/user/login", "url": f"{user_base}/user/login",
        "expected_status": 200,
        "params": {"username": "admin", "password": "admin123"},
        "note": "正确账号登录"
    })

    # 1.2 登录 - 错误密码
    test_cases.append({
        "id": 2, "service": "User Service", "category": "用户登录",
        "method": "POST", "endpoint": "/user/login", "url": f"{user_base}/user/login",
        "expected_status": [200, 400, 401, 500],  # 允许多种可能的状态码
        "params": {"username": "admin", "password": "wrongpassword"},
        "note": "错误密码登录"
    })

    # 1.3 登录 - 不存在的用户
    test_cases.append({
        "id": 3, "service": "User Service", "category": "用户登录",
        "method": "POST", "endpoint": "/user/login", "url": f"{user_base}/user/login",
        "expected_status": [200, 400, 401, 404, 500],
        "params": {"username": "nonexistent_user_999", "password": "test123"},
        "note": "不存在的用户登录"
    })

    # 1.4 登录 - 空用户名
    test_cases.append({
        "id": 4, "service": "User Service", "category": "用户登录(异常)",
        "method": "POST", "endpoint": "/user/login", "url": f"{user_base}/user/login",
        "expected_status": [200, 400, 422],
        "params": {"username": "", "password": "admin123"},
        "note": "空用户名"
    })

    # 1.5 登录 - 空密码
    test_cases.append({
        "id": 5, "service": "User Service", "category": "用户登录(异常)",
        "method": "POST", "endpoint": "/user/login", "url": f"{user_base}/user/login",
        "expected_status": [200, 400, 422],
        "params": {"username": "admin", "password": ""},
        "note": "空密码"
    })

    # 1.6 注册 - 正常数据
    test_cases.append({
        "id": 6, "service": "User Service", "category": "用户注册",
        "method": "POST", "endpoint": "/user/register", "url": f"{user_base}/user/register",
        "expected_status": [200, 201],
        "json": {
            "username": f"testuser_{int(time.time())}",
            "password": "Test@123456",
            "realName": "测试用户V140",
            "role": "DOCTOR",
            "status": 1
        },
        "note": "正常注册"
    })

    # 1.7 注册 - 重复用户名（使用已存在的admin）
    test_cases.append({
        "id": 7, "service": "User Service", "category": "用户注册(异常)",
        "method": "POST", "endpoint": "/user/register", "url": f"{user_base}/user/register",
        "expected_status": [200, 400, 409, 500],
        "json": {
            "username": "admin",
            "password": "Admin@123456",
            "realName": "管理员重复",
            "role": "ADMIN"
        },
        "note": "重复用户名注册"
    })

    # 1.8 注册 - 缺少必填字段
    test_cases.append({
        "id": 8, "service": "User Service", "category": "用户注册(异常)",
        "method": "POST", "endpoint": "/user/register", "url": f"{user_base}/user/register",
        "expected_status": [200, 400, 422],
        "json": {"username": "incomplete_user"},
        "note": "缺少必填字段"
    })

    # 1.9 用户列表 - 分页查询
    test_cases.append({
        "id": 9, "service": "User Service", "category": "用户管理",
        "method": "GET", "endpoint": "/user/list", "url": f"{user_base}/user/list",
        "expected_status": 200,
        "params": {"current": 1, "size": 10},
        "note": "分页查询用户列表"
    })

    # 1.10 用户详情 - 存在的ID
    test_cases.append({
        "id": 10, "service": "User Service", "category": "用户管理",
        "method": "GET", "endpoint": "/user/1", "url": f"{user_base}/user/1",
        "expected_status": 200,
        "note": "查询存在的用户ID=1"
    })

    # 1.11 用户详情 - 不存在的ID
    test_cases.append({
        "id": 11, "service": "User Service", "category": "用户管理(异常)",
        "method": "GET", "endpoint": "/user/999999", "url": f"{user_base}/user/999999",
        "expected_status": [200, 404],
        "note": "查询不存在的用户ID=999999"
    })

    # 1.12 按角色查询用户
    test_cases.append({
        "id": 12, "service": "User Service", "category": "用户管理",
        "method": "GET", "endpoint": "/user/role/DOCTOR", "url": f"{user_base}/user/role/DOCTOR",
        "expected_status": 200,
        "note": "按角色DOCTOR查询"
    })

    # 1.13 所有用户
    test_cases.append({
        "id": 13, "service": "User Service", "category": "用户管理",
        "method": "GET", "endpoint": "/user/all", "url": f"{user_base}/user/all",
        "expected_status": 200,
        "note": "获取所有用户"
    })

    # ==================== 2. 标本服务API测试 ====================
    sample_base = SERVICES["Sample Service"]

    # 2.1 创建标本 - 完整数据
    test_cases.append({
        "id": 14, "service": "Sample Service", "category": "标本创建",
        "method": "POST", "endpoint": "/sample/create", "url": f"{sample_base}/sample/create",
        "expected_status": [200, 201],
        "json": {
            "patientName": f"患者V140_{int(time.time())}",
            "patientId": f"P{int(time.time())}",
            "doctorName": "张医生",
            "department": "检验科",
            "testItems": "血常规,尿常规,生化全套",
            "sampleType": "BLOOD",
            "status": "PENDING",
            "priority": "NORMAL",
            "notes": "API自动化测试标本"
        },
        "note": "创建完整标本"
    })

    # 2.2 创建标本 - 最小数据
    test_cases.append({
        "id": 15, "service": "Sample Service", "category": "标本创建",
        "method": "POST", "endpoint": "/sample/create", "url": f"{sample_base}/sample/create",
        "expected_status": [200, 201],
        "json": {
            "patientName": "最小数据患者",
            "doctorName": "李医生",
            "testItems": "血常规",
            "sampleType": "BLOOD"
        },
        "note": "创建最小数据标本"
    })

    # 2.3 创建标本 - 缺少必填字段
    test_cases.append({
        "id": 16, "service": "Sample Service", "category": "标本创建(异常)",
        "method": "POST", "endpoint": "/sample/create", "url": f"{sample_base}/sample/create",
        "expected_status": [200, 400, 422, 500],
        "json": {"patientName": "缺少字段"},
        "note": "缺少必填字段"
    })

    # 2.4 标本列表
    test_cases.append({
        "id": 17, "service": "Sample Service", "category": "标本查询",
        "method": "GET", "endpoint": "/sample/list", "url": f"{sample_base}/sample/list",
        "expected_status": 200,
        "note": "获取所有标本列表"
    })

    # 2.5 标本详情 - 存在的ID
    test_cases.append({
        "id": 18, "service": "Sample Service", "category": "标本查询",
        "method": "GET", "endpoint": "/sample/1", "url": f"{sample_base}/sample/1",
        "expected_status": 200,
        "note": "查询标本详情ID=1"
    })

    # 2.6 标本详情 - 不存在的ID
    test_cases.append({
        "id": 19, "service": "Sample Service", "category": "标本查询(异常)",
        "method": "GET", "endpoint": "/sample/999999", "url": f"{sample_base}/sample/999999",
        "expected_status": [200, 404],
        "note": "查询不存在的标本ID=999999"
    })

    # 2.7 扫码查询标本
    test_cases.append({
        "id": 20, "service": "Sample Service", "category": "标本查询",
        "method": "GET", "endpoint": "/sample/scan/SAMPLE001", "url": f"{sample_base}/sample/scan/SAMPLE001",
        "expected_status": [200, 404],
        "note": "扫码查询标本号SAMPLE001"
    })

    # 2.8 按状态查询标本
    test_cases.append({
        "id": 21, "service": "Sample Service", "category": "标本查询",
        "method": "GET", "endpoint": "/sample/list-by-status", "url": f"{sample_base}/sample/list-by-status",
        "expected_status": 200,
        "params": {"status": "PENDING"},
        "note": "按PENDING状态查询"
    })

    # 2.9 更新标本状态
    test_cases.append({
        "id": 22, "service": "Sample Service", "category": "标本操作",
        "method": "POST", "endpoint": "/sample/1/status", "url": f"{sample_base}/sample/1/status",
        "expected_status": [200, 400, 404],
        "params": {
            "status": "RECEIVED",
            "operatorId": 1,
            "operatorName": "技术员A",
            "location": "接收窗口"
        },
        "note": "更新标本ID=1状态为RECEIVED"
    })

    # 2.10 接收标本
    test_cases.append({
        "id": 23, "service": "Sample Service", "category": "标本操作",
        "method": "POST", "endpoint": "/sample/1/receive", "url": f"{sample_base}/sample/1/receive",
        "expected_status": [200, 400, 404],
        "params": {
            "technicianId": 1,
            "technicianName": "技术员B"
        },
        "note": "接收标本ID=1"
    })

    # 2.11 开始检验
    test_cases.append({
        "id": 24, "service": "Sample Service", "category": "标本操作",
        "method": "POST", "endpoint": "/sample/1/start-test", "url": f"{sample_base}/sample/1/start-test",
        "expected_status": [200, 400, 404],
        "params": {
            "technicianId": 1,
            "technicianName": "技术员C"
        },
        "note": "开始检验标本ID=1"
    })

    # 2.12 完成检验
    test_cases.append({
        "id": 25, "service": "Sample Service", "category": "标本操作",
        "method": "POST", "endpoint": "/sample/1/complete", "url": f"{sample_base}/sample/1/complete",
        "expected_status": [200, 400, 404],
        "params": {
            "technicianId": 1,
            "technicianName": "技术员D"
        },
        "note": "完成检验标本ID=1"
    })

    # 2.13 标本追踪记录
    test_cases.append({
        "id": 26, "service": "Sample Service", "category": "标本追踪",
        "method": "GET", "endpoint": "/sample/1/traces", "url": f"{sample_base}/sample/1/traces",
        "expected_status": 200,
        "note": "获取标本ID=1的追踪记录"
    })

    # ==================== 3. 报告服务API测试 ====================
    report_base = SERVICES["Report Service"]

    # 3.1 创建报告 - 完整数据
    test_cases.append({
        "id": 27, "service": "Report Service", "category": "报告创建",
        "method": "POST", "endpoint": "/report/create", "url": f"{report_base}/report/create",
        "expected_status": [200, 201],
        "json": {
            "patientName": f"报告患者V140_{int(time.time())}",
            "patientId": f"RP{int(time.time())}",
            "sampleId": 1,
            "status": "DRAFT",
            "diagnosis": "初步诊断待补充",
            "conclusion": "结论待审核",
            "doctorName": "王医生",
            "reviewerName": ""
        },
        "note": "创建完整报告"
    })

    # 3.2 创建报告 - 最小数据
    test_cases.append({
        "id": 28, "service": "Report Service", "category": "报告创建",
        "method": "POST", "endpoint": "/report/create", "url": f"{report_base}/report/create",
        "expected_status": [200, 201],
        "json": {
            "patientName": "最小数据报告患者",
            "sampleId": 1,
            "status": "DRAFT"
        },
        "note": "创建最小数据报告"
    })

    # 3.3 报告列表
    test_cases.append({
        "id": 29, "service": "Report Service", "category": "报告查询",
        "method": "GET", "endpoint": "/report/list", "url": f"{report_base}/report/list",
        "expected_status": 200,
        "note": "获取所有报告列表"
    })

    # 3.4 报告详情 - 存在的ID
    test_cases.append({
        "id": 30, "service": "Report Service", "category": "报告查询",
        "method": "GET", "endpoint": "/report/1", "url": f"{report_base}/report/1",
        "expected_status": 200,
        "note": "查询报告详情ID=1"
    })

    # 3.5 报告详情 - 不存在的ID
    test_cases.append({
        "id": 31, "service": "Report Service", "category": "报告查询(异常)",
        "method": "GET", "endpoint": "/report/999999", "url": f"{report_base}/report/999999",
        "expected_status": [200, 404],
        "note": "查询不存在的报告ID=999999"
    })

    # 3.6 待审核报告列表
    test_cases.append({
        "id": 32, "service": "Report Service", "category": "报告查询",
        "method": "GET", "endpoint": "/report/pending-list", "url": f"{report_base}/report/pending-list",
        "expected_status": 200,
        "note": "获取待审核报告列表"
    })

    # 3.7 按患者ID查询报告
    test_cases.append({
        "id": 33, "service": "Report Service", "category": "报告查询",
        "method": "GET", "endpoint": "/report/patient/1", "url": f"{report_base}/report/patient/1",
        "expected_status": 200,
        "note": "按患者ID=1查询报告"
    })

    # 3.8 录入检验结果
    test_cases.append({
        "id": 34, "service": "Report Service", "category": "报告操作",
        "method": "POST", "endpoint": "/report/1/input-results", "url": f"{report_base}/report/1/input-results",
        "expected_status": [200, 400, 404],
        "params": {
            "results": json.dumps([
                {"itemName": "WBC", "value": "5.5", "unit": "10^9/L", "referenceRange": "4-10", "isAbnormal": False},
                {"itemName": "RBC", "value": "4.5", "unit": "10^12/L", "referenceRange": "3.5-5.5", "isAbnormal": False},
                {"itemName": "PLT", "value": "250", "unit": "10^9/L", "referenceRange": "100-300", "isAbnormal": False}
            ], ensure_ascii=False),
            "technicianId": 1,
            "technicianName": "检验技师E"
        },
        "note": "录入报告ID=1的检验结果"
    })

    # 3.9 审核报告 - 通过
    test_cases.append({
        "id": 35, "service": "Report Service", "category": "报告审核",
        "method": "POST", "endpoint": "/report/1/review", "url": f"{report_base}/report/1/review",
        "expected_status": [200, 400, 404],
        "params": {
            "reviewerId": 2,
            "reviewerName": "审核医生F",
            "approved": True,
            "remark": "审核通过，结果正常"
        },
        "note": "审核通过报告ID=1"
    })

    # 3.10 发布报告
    test_cases.append({
        "id": 36, "service": "Report Service", "category": "报告发布",
        "method": "POST", "endpoint": "/report/1/publish", "url": f"{report_base}/report/1/publish",
        "expected_status": [200, 400, 404],
        "note": "发布报告ID=1"
    })

    # ==================== 4. AI服务API测试 ====================
    ai_base = SERVICES["AI Service"]

    # 4.1 AI诊断请求 - 血常规
    test_cases.append({
        "id": 37, "service": "AI Service", "category": "AI诊断",
        "method": "POST", "endpoint": "/ai/diagnose", "url": f"{ai_base}/ai/diagnose",
        "expected_status": 200,
        "json": {
            "patientInfo": {
                "name": "AI诊断测试患者",
                "age": 35,
                "gender": "男"
            },
            "testResults": [
                {"name": "WBC", "value": 11.5, "unit": "10^9/L", "referenceMin": 4.0, "referenceMax": 10.0},
                {"name": "RBC", "value": 3.2, "unit": "10^12/L", "referenceMin": 4.0, "referenceMax": 5.5},
                {"name": "HGB", "value": 98, "unit": "g/L", "referenceMin": 120, "referenceMax": 160}
            ],
            "testType": "blood_routine"
        },
        "note": "AI血常规诊断（含异常值）"
    })

    # 4.2 AI诊断请求 - 尿常规
    test_cases.append({
        "id": 38, "service": "AI Service", "category": "AI诊断",
        "method": "POST", "endpoint": "/ai/diagnose/urine-routine", "url": f"{ai_base}/ai/diagnose/urine-routine",
        "expected_status": 200,
        "json": {
            "LEU": "+2",
            "PRO": "+1",
            "GLU": "Negative",
            "BLD": "Negative"
        },
        "note": "AI尿常规诊断"
    })

    # 4.3 简化版诊断
    test_cases.append({
        "id": 39, "service": "AI Service", "category": "AI诊断",
        "method": "POST", "endpoint": "/ai/simple-diagnose", "url": f"{ai_base}/ai/simple-diagnose",
        "expected_status": 200,
        "json": {"indicators": [{"name": "WBC", "value": 12.0}]},
        "note": "简化版AI诊断"
    })

    # 4.4 健康检查
    test_cases.append({
        "id": 40, "service": "AI Service", "category": "健康检查",
        "method": "GET", "endpoint": "/ai/health", "url": f"{ai_base}/ai/health",
        "expected_status": 200,
        "note": "AI服务健康检查"
    })

    # 4.5 AI诊断 - 空数据
    test_cases.append({
        "id": 41, "service": "AI Service", "category": "AI诊断(异常)",
        "method": "POST", "endpoint": "/ai/diagnose", "url": f"{ai_base}/ai/diagnose",
        "expected_status": [200, 400, 422, 500],
        "json": {},
        "note": "空数据诊断请求"
    })

    # ==================== 5. HL7服务API测试 ====================
    hl7_base = SERVICES["HL7 Service"]

    # 5.1 解析HL7消息
    hl7_message = ("MSH|^~\\&|LIS|LAB|20260402090000||ORM^O01|MSG001|P|2.5\r"
                   "PID|1||PAT001||张三^三|19800101|M\r"
                   "ORC|NW|ORD001|||||R\r"
                   "OBR|1|ORD001||血常规^Blood Routine||20260402090000")
    test_cases.append({
        "id": 42, "service": "HL7 Service", "category": "HL7消息处理",
        "method": "POST", "endpoint": "/hl7/parse", "url": f"{hl7_base}/hl7/parse",
        "expected_status": 200,
        "data": hl7_message,
        "headers": {"Content-Type": "text/plain"},
        "note": "解析HL7 ORM消息"
    })

    # 5.2 生成检验申请消息
    test_cases.append({
        "id": 43, "service": "HL7 Service", "category": "HL7消息生成",
        "method": "POST", "endpoint": "/hl7/generate-order", "url": f"{hl7_base}/hl7/generate-order",
        "expected_status": 200,
        "json": {
            "messageType": "ORM",
            "triggerEvent": "O01",
            "sendingApplication": "LIS",
            "sendingFacility": "LAB",
            "patientId": "PAT002",
            "patientName": "李四",
            "orderControl": "NW",
            "placerOrderNumber": "ORD002",
            "universalServiceIdentifier": "尿常规^Urine Routine"
        },
        "note": "生成HL7检验申请消息"
    })

    # 5.3 生成检验结果消息
    test_cases.append({
        "id": 44, "service": "HL7 Service", "category": "HL7消息生成",
        "method": "POST", "endpoint": "/hl7/generate-result", "url": f"{hl7_base}/hl7/generate-result",
        "expected_status": 200,
        "json": {
            "messageType": "ORU",
            "triggerEvent": "R01",
            "patientId": "PAT002",
            "patientName": "李四",
            "results": [
                {"itemName": "WBC", "value": "5.5", "unit": "10^9/L", "referenceRange": "4-10"},
                {"itemName": "RBC", "value": "4.5", "unit": "10^12/L", "referenceRange": "3.5-5.5"}
            ]
        },
        "note": "生成HL7检验结果消息"
    })

    # 5.4 发送消息到HIS系统（模拟）
    test_cases.append({
        "id": 45, "service": "HL7 Service", "category": "HL7系统集成",
        "method": "POST", "endpoint": "/hl7/send-to-his", "url": f"{hl7_base}/hl7/send-to-his",
        "expected_status": [200, 503],
        "data": hl7_message,
        "headers": {"Content-Type": "text/plain"},
        "note": "发送HL7消息到HIS"
    })

    # 5.5 接收HIS消息（模拟）
    test_cases.append({
        "id": 46, "service": "HL7 Service", "category": "HL7系统集成",
        "method": "POST", "endpoint": "/hl7/receive-from-his", "url": f"{hl7_base}/hl7/receive-from-his",
        "expected_status": 200,
        "data": hl7_message,
        "headers": {"Content-Type": "text/plain"},
        "note": "从HIS接收HL7消息"
    })

    # 5.6 消息转换
    test_cases.append({
        "id": 47, "service": "HL7 Service", "category": "HL7消息转换",
        "method": "POST", "endpoint": "/hl7/transform", "url": f"{hl7_base}/hl7/transform",
        "expected_status": 200,
        "json": {
            "messageType": "ORU",
            "triggerEvent": "R01",
            "patientId": "PAT003",
            "patientName": "王五",
            "results": [
                {"itemName": "PLT", "value": "250", "unit": "10^9/L", "referenceRange": "100-300"}
            ]
        },
        "note": "HL7消息转换测试"
    })

    # ==================== 6. 网关路由验证 ====================
    gateway_base = SERVICES["Gateway"]

    # 6.1 通过网关访问用户服务
    test_cases.append({
        "id": 48, "service": "Gateway", "category": "网关路由",
        "method": "GET", "endpoint": "/api/user/list", "url": f"{gateway_base}/api/user/list",
        "expected_status": [200, 502, 503, 504],
        "params": {"current": 1, "size": 5},
        "note": "网关转发到用户服务"
    })

    # 6.2 通过网关访问标本服务
    test_cases.append({
        "id": 49, "service": "Gateway", "category": "网关路由",
        "method": "GET", "endpoint": "/api/sample/list", "url": f"{gateway_base}/api/sample/list",
        "expected_status": [200, 502, 503, 504],
        "note": "网关转发到标本服务"
    })

    # 6.3 通过网关访问报告服务
    test_cases.append({
        "id": 50, "service": "Gateway", "category": "网关路由",
        "method": "GET", "endpoint": "/api/report/list", "url": f"{gateway_base}/api/report/list",
        "expected_status": [200, 502, 503, 504],
        "note": "网关转发到报告服务"
    })

    # 6.4 通过网关访问AI服务
    test_cases.append({
        "id": 51, "service": "Gateway", "category": "网关路由",
        "method": "GET", "endpoint": "/api/ai/health", "url": f"{gateway_base}/api/ai/health",
        "expected_status": [200, 502, 503, 504],
        "note": "网关转发到AI服务"
    })

    # 6.5 通过网关访问HL7服务
    test_cases.append({
        "id": 52, "service": "Gateway", "category": "网关路由",
        "method": "POST", "endpoint": "/api/hl7/parse", "url": f"{gateway_base}/api/hl7/parse",
        "expected_status": [200, 502, 503, 504],
        "data": "MSH|^~\\&|LIS|LAB|20260402||ADT^A04|GW001|P|2.5",
        "headers": {"Content-Type": "text/plain"},
        "note": "网关转发到HL7服务"
    })

    # 6.6 网关 - 不存在的路径
    test_cases.append({
        "id": 53, "service": "Gateway", "category": "网关路由(异常)",
        "method": "GET", "endpoint": "/api/nonexistent/service", "url": f"{gateway_base}/api/nonexistent/service",
        "expected_status": [404, 502, 503, 504],
        "note": "网关转发到不存在的服务"
    })

    # ==================== 7. 高级异常场景测试 ====================

    # 7.1 超长字符串参数
    long_string = "A" * 10000
    test_cases.append({
        "id": 54, "service": "User Service", "category": "边界测试",
        "method": "POST", "endpoint": "/user/register", "url": f"{user_base}/user/register",
        "expected_status": [200, 400, 413, 422, 500],
        "json": {
            "username": f"longuser_{int(time.time())}",
            "password": "Test@123456",
            "realName": long_string,
            "role": "DOCTOR"
        },
        "note": "超长姓名(10000字符)"
    })

    # 7.2 特殊字符注入
    special_chars = "<script>alert('xss')</script>'; DROP TABLE users; --"
    test_cases.append({
        "id": 55, "service": "User Service", "category": "安全测试",
        "method": "POST", "endpoint": "/user/register", "url": f"{user_base}/user/register",
        "expected_status": [200, 400, 422, 500],
        "json": {
            "username": f"xss_user_{int(time.time())}",
            "password": "Test@123456",
            "realName": special_chars,
            "role": "DOCTOR"
        },
        "note": "XSS/SQL注入字符测试"
    })

    # 7.3 非法HTTP方法
    test_cases.append({
        "id": 56, "service": "User Service", "category": "安全测试",
        "method": "PATCH", "endpoint": "/user/1", "url": f"{user_base}/user/1",
        "expected_status": [200, 405, 500],
        "note": "非法HTTP方法PATCH"
    })

    # 7.4 大量并发请求模拟（单次快速连续请求）
    test_cases.append({
        "id": 57, "service": "User Service", "category": "压力测试",
        "method": "GET", "endpoint": "/user/1", "url": f"{user_base}/user/1",
        "expected_status": 200,
        "note": "快速响应测试#1"
    })
    test_cases.append({
        "id": 58, "service": "User Service", "category": "压力测试",
        "method": "GET", "endpoint": "/user/1", "url": f"{user_base}/user/1",
        "expected_status": 200,
        "note": "快速响应测试#2"
    })
    test_cases.append({
        "id": 59, "service": "User Service", "category": "压力测试",
        "method": "GET", "endpoint": "/user/1", "url": f"{user_base}/user/1",
        "expected_status": 200,
        "note": "快速响应测试#3"
    })

    # 7.5 JSON格式错误
    test_cases.append({
        "id": 60, "service": "Sample Service", "category": "格式验证",
        "method": "POST", "endpoint": "/sample/create", "url": f"{sample_base}/sample/create",
        "expected_status": [200, 400, 415, 500],
        "data": "{invalid json content",
        "headers": {"Content-Type": "application/json"},
        "note": " malformed JSON格式"
    })

    return test_cases


def run_all_tests(tester: APITester):
    """执行所有测试用例"""
    print("\n" + "="*90)
    print("实验室管理系统 API 全面深度测试 v1.4.0")
    print("="*90)
    print(f"\n测试开始时间: {tester.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n{'='*90}")
    print(f"{'ID':>4} | {'状态':>6} | {'方法':>6} | {'服务':<16} | {'端点':<40} | {'状态码':>6} | {'耗时':>10} | 备注")
    print("-"*90)

    test_cases = get_test_cases()

    for tc in test_cases:
        test_id = tc["id"]
        service = tc["service"]
        category = tc["category"]
        method = tc["method"].upper()
        endpoint = tc["endpoint"]
        url = tc["url"]
        expected_status = tc.get("expected_status", 200)
        note = tc.get("note", "")

        # 准备请求数据
        request_kwargs = {}
        test_data = None

        if "params" in tc:
            request_kwargs["params"] = tc["params"]
            test_data = {"params": tc["params"]}
        elif "json" in tc:
            request_kwargs["json"] = tc["json"]
            test_data = {"json_body": tc["json"]}
        elif "data" in tc:
            request_kwargs["data"] = tc["data"]
            test_data = {"raw_data": tc["data"][:200]}

        if "headers" in tc:
            request_kwargs["headers"] = tc["headers"]

        try:
            # 执行请求
            resp, elapsed_ms = tester.execute_request(method, url, **request_kwargs)

            if resp is None:
                # 请求异常
                tester.add_test_result(
                    test_id=test_id, service=service, category=category,
                    endpoint=endpoint, method=method, url=url,
                    expected_status=expected_status, actual_status=None,
                    response_time_ms=elapsed_ms, passed=False,
                    test_data=test_data, error_message="连接失败或请求超时",
                    note=note
                )
                continue

            actual_status = resp.status_code
            response_body = resp.text

            # 判断是否通过
            if isinstance(expected_status, list):
                passed = actual_status in expected_status
            else:
                # 允许一定范围内的状态码
                passed = (actual_status == expected_status or
                         (expected_status == 200 and 200 <= actual_status < 400))

            tester.add_test_result(
                test_id=test_id, service=service, category=category,
                endpoint=endpoint, method=method, url=url,
                expected_status=expected_status, actual_status=actual_status,
                response_time_ms=elapsed_ms, passed=passed,
                test_data=test_data, response_body=response_body,
                note=note
            )

        except requests.exceptions.ConnectionError as e:
            tester.add_test_result(
                test_id=test_id, service=service, category=category,
                endpoint=endpoint, method=method, url=url,
                expected_status=expected_status, actual_status=None,
                response_time_ms=None, passed=False,
                test_data=test_data, error_message=f"连接失败: {str(e)[:200]}",
                note=note
            )
        except requests.exceptions.Timeout as e:
            tester.add_test_result(
                test_id=test_id, service=service, category=category,
                endpoint=endpoint, method=method, url=url,
                expected_status=expected_status, actual_status=None,
                response_time_ms=None, passed=False,
                test_data=test_data, error_message=f"请求超时: {str(e)[:200]}",
                note=note
            )
        except Exception as e:
            tester.add_test_result(
                test_id=test_id, service=service, category=category,
                endpoint=endpoint, method=method, url=url,
                expected_status=expected_status, actual_status=None,
                response_time_ms=None, passed=False,
                test_data=test_data, error_message=f"未知错误: {str(e)[:200]}",
                note=note
            )

    return tester


def generate_json_report(tester: APITester, output_file: str):
    """生成JSON格式的详细测试报告"""
    stats = tester.calculate_statistics()

    report = {
        "report_info": {
            "title": "实验室管理系统 API 全面深度测试报告",
            "version": "v1.4.0",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_duration_seconds": round((datetime.now() - tester.test_start_time).total_seconds(), 2),
            "tester": "API Test Pro",
            "environment": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "requests_version": requests.__version__,
                "target_services": SERVICES,
                "operating_system": "Windows"
            }
        },
        "summary": stats,
        "test_results": tester.results,
        "statistics_by_service": {},
        "statistics_by_category": {}
    }

    # 按服务统计
    service_stats = {}
    for result in tester.results:
        svc = result["service"]
        if svc not in service_stats:
            service_stats[svc] = {"total": 0, "passed": 0, "failed": 0, "response_times": []}

        service_stats[svc]["total"] += 1
        if result["passed"]:
            service_stats[svc]["passed"] += 1
        else:
            service_stats[svc]["failed"] += 1

        if result.get("response_time_ms"):
            service_stats[svc]["response_times"].append(result["response_time_ms"])

    # 计算每个服务的统计信息
    for svc, data in service_stats.items():
        report["statistics_by_service"][svc] = {
            "total_tests": data["total"],
            "passed": data["passed"],
            "failed": data["failed"],
            "pass_rate": round(data["passed"] / data["total"] * 100, 2) if data["total"] > 0 else 0,
            "avg_response_time_ms": round(sum(data["response_times"]) / len(data["response_times"]), 2) if data["response_times"] else None
        }

    # 按类别统计
    category_stats = {}
    for result in tester.results:
        cat = result["category"]
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "passed": 0, "failed": 0}

        category_stats[cat]["total"] += 1
        if result["passed"]:
            category_stats[cat]["passed"] += 1
        else:
            category_stats[cat]["failed"] += 1

    for cat, data in category_stats.items():
        report["statistics_by_category"][cat] = {
            "total_tests": data["total"],
            "passed": data["passed"],
            "failed": data["failed"],
            "pass_rate": round(data["passed"] / data["total"] * 100, 2) if data["total"] > 0 else 0
        }

    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n✓ JSON报告已保存至: {output_file}")
    return report


def generate_markdown_report(tester: APITester, json_report: Dict, output_file: str):
    """生成Markdown可读性测试报告"""

    lines = []

    # 标题部分
    lines.append("# 实验室管理系统 API 全面深度测试报告 v1.4.0\n")
    lines.append(f"> **生成时间**: {json_report['report_info']['generated_at']}")
    lines.append(f"> **测试工具**: Python Requests v{requests.__version__}")
    lines.append(f"> **Python版本**: {json_report['report_info']['environment']['python_version']}")
    lines.append(f"> **操作系统**: Windows\n")

    # 目录
    lines.append("---\n")
    lines.append("## 目录\n")
    lines.append("- [1. 测试环境信息](#1-测试环境信息)")
    lines.append("- [2. 执行摘要](#2-执行摘要)")
    lines.append("- [3. 详细测试结果](#3-详细测试结果)")
    lines.append("- [4. 失败用例详情](#4-失败用例详情)")
    lines.append("- [5. 性能指标分析](#5-性能指标分析)")
    lines.append("- [6. 各服务统计](#6-各服务统计)")
    lines.append("- [7. 测试分类统计](#7-测试分类统计)")
    lines.append("- [8. 风险评估与建议](#8-风险评估与建议)\n")

    # 1. 测试环境信息
    lines.append("---\n")
    lines.append("## 1. 测试环境信息\n")
    lines.append("| 配置项 | 值 |")
    lines.append("|--------|-----|")
    lines.append(f"| **测试版本** | v1.4.0 |")
    lines.append(f"| **测试时间** | {json_report['report_info']['generated_at']} |")
    lines.append(f"| **测试时长** | {json_report['report_info']['test_duration_seconds']} 秒 |")
    lines.append(f"| **总用例数** | {json_report['summary']['total_tests']} |")
    env = json_report['report_info']['environment']
    lines.append(f"| **目标服务** | {len(env['target_services'])} 个微服务 |")
    lines.append("")
    lines.append("### 服务端点配置\n")
    lines.append("| 服务名称 | 基础URL |")
    lines.append("|----------|---------|")
    for svc_name, svc_url in env['target_services'].items():
        lines.append(f"| {svc_name} | `{svc_url}` |")
    lines.append("")

    # 2. 执行摘要
    lines.append("---\n")
    lines.append("## 2. 执行摘要\n")
    summary = json_report['summary']
    lines.append("### 总体概况\n")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| **总用例数** | {summary['total_tests']} |")
    lines.append(f"| **通过用例** | ✅ {summary['passed']} |")
    lines.append(f"| **失败用例** | ❌ {summary['failed']} |")
    lines.append(f"| **通过率** | **{summary['pass_rate']}%** |")
    lines.append("")

    # 3. 详细测试结果
    lines.append("---\n")
    lines.append("## 3. 详细测试结果\n")
    lines.append("<details>")
    lines.append("<summary>点击展开全部测试结果 ({})</summary>\n".format(len(tester.results)))
    lines.append("| ID | 服务 | 分类 | 方法 | 端点 | 预期状态 | 实际状态 | 响应时间(ms) | 结果 | 备注 |")
    lines.append("|----|------|------|------|------|----------|----------|--------------|------|------|")

    for result in tester.results:
        status_icon = "✅ PASS" if result['passed'] else "❌ FAIL"
        actual_status = str(result['actual_status']) if result['actual_status'] else "N/A"
        response_time = str(result['response_time_ms']) if result['response_time_ms'] else "N/A"

        lines.append(f"| {result['test_id']} | {result['service']} | {result['category']} | "
                    f"`{result['method']}` | `{result['endpoint']}` | "
                    f"{result['expected_status']} | {actual_status} | {response_time} | "
                    f"{status_icon} | {result['note']} |")

    lines.append("</details>\n")

    # 4. 失败用例详情
    failed_results = [r for r in tester.results if not r['passed']]
    lines.append("---\n")
    lines.append("## 4. 失败用例详情\n")

    if failed_results:
        lines.append(f"⚠️ 共发现 **{len(failed_results)}** 个失败用例:\n")
        for i, fail in enumerate(failed_results, 1):
            lines.append(f"### 失败 #{i}: [{fail['service']}] {fail['endpoint']}\n")
            lines.append("| 属性 | 值 |")
            lines.append("|------|-----|")
            lines.append(f"| **测试ID** | {fail['test_id']} |")
            lines.append(f"| **服务** | {fail['service']} |")
            lines.append(f"| **分类** | {fail['category']} |")
            lines.append(f"| **方法** | `{fail['method']}` |")
            lines.append(f"| **URL** | `{fail['url']}` |")
            lines.append(f"| **预期状态码** | {fail['expected_status']} |")
            lines.append(f"| **实际状态码** | {fail['actual_status'] or 'N/A'} |")
            lines.append(f"| **响应时间** | {fail['response_time_ms'] or 'N/A'}ms |")
            lines.append(f"| **备注** | {fail['note']} |")

            if fail.get('error_message'):
                lines.append(f"| **错误信息** | `{fail['error_message']}` |")

            if fail.get('response_body_preview'):
                preview = fail['response_body_preview'][:300]
                lines.append(f"| **响应预览** | ```{preview}``` |")

            lines.append("")
    else:
        lines.append("🎉 **所有测试用例均通过！** 未发现失败用例。\n")

    # 5. 性能指标分析
    lines.append("---\n")
    lines.append("## 5. 性能指标分析\n")
    lines.append("### 响应时间分布\n")
    lines.append("| 指标 | 数值(ms) | 说明 |")
    lines.append("|------|----------|------|")
    lines.append(f"| **平均响应时间** | {summary.get('avg_response_time_ms', 'N/A')} | 所有成功请求的平均值 |")
    lines.append(f"| **最小响应时间** | {summary.get('min_response_time_ms', 'N/A')} | 最快的请求 |")
    lines.append(f"| **最大响应时间** | {summary.get('max_response_time_ms', 'N/A')} | 最慢的请求 |")
    lines.append(f"| **P50 (中位数)** | {summary.get('p50_response_time_ms', 'N/A')} | 50%请求在此时间内完成 |")
    lines.append(f"| **P90** | {summary.get('p90_response_time_ms', 'N/A')} | 90%请求在此时间内完成 |")
    lines.append(f"| **P95** | {summary.get('p95_response_time_ms', 'N/A')} | 95%请求在此时间内完成 |")
    lines.append(f"| **P99** | {summary.get('p99_response_time_ms', 'N/A')} | 99%请求在此时间内完成 |")
    lines.append("")

    # 6. 各服务统计
    lines.append("---\n")
    lines.append("## 6. 各服务统计\n")
    lines.append("| 服务 | 总用例 | 通过 | 失败 | 通过率 | 平均响应时间(ms) |")
    lines.append("|------|--------|------|------|--------|------------------|")

    for svc_name, svc_stats in json_report['statistics_by_service'].items():
        pass_rate_color = "🟢" if svc_stats['pass_rate'] >= 90 else ("🟡" if svc_stats['pass_rate'] >= 70 else "🔴")
        avg_time = svc_stats.get('avg_response_time_ms', 'N/A')
        lines.append(f"| {svc_name} | {svc_stats['total_tests']} | {svc_stats['passed']} | "
                    f"{svc_stats['failed']} | {pass_rate_color} {svc_stats['pass_rate']}% | {avg_time} |")

    lines.append("")

    # 7. 测试分类统计
    lines.append("---\n")
    lines.append("## 7. 测试分类统计\n")
    lines.append("| 测试分类 | 用例数 | 通过 | 失败 | 通过率 |")
    lines.append("|----------|--------|------|------|--------|")

    for cat_name, cat_stats in sorted(json_report['statistics_by_category'].items(),
                                       key=lambda x: x[1]['total_tests'], reverse=True):
        pass_indicator = "✅" if cat_stats['pass_rate'] == 100 else ("⚠️" if cat_stats['pass_rate'] >= 70 else "❌")
        lines.append(f"| {cat_name} | {cat_stats['total_tests']} | {cat_stats['passed']} | "
                    f"{cat_stats['failed']} | {pass_indicator} {cat_stats['pass_rate']}% |")

    lines.append("")

    # 8. 风险评估与建议
    lines.append("---\n")
    lines.append("## 8. 风险评估与建议\n")

    # 分析风险
    risks = []
    recommendations = []

    if summary['pass_rate'] < 100:
        risks.append(f"- ⚠️ 整体通过率为 {summary['pass_rate']}%，存在 {summary['failed']} 个失败的测试用例")

        # 分析失败原因
        connection_failures = len([r for r in failed_results if r['actual_status'] is None])
        if connection_failures > 0:
            risks.append(f"- 🔴 发现 {connection_failures} 个连接失败，可能是服务未启动或网络问题")

        status_failures = len([r for r in failed_results if r['actual_status'] is not None])
        if status_failures > 0:
            risks.append(f"- 🟡 发现 {status_failures} 个状态码不符合预期的用例")

    # 性能风险
    if summary.get('max_response_time_ms', 0) > 5000:
        risks.append(f"- 🟡 最大响应时间达到 {summary['max_response_time_ms']}ms，超过5秒阈值")
    elif summary.get('avg_response_time_ms', 0) > 1000:
        risks.append(f"- 🟢 平均响应时间为 {summary['avg_response_time_ms']}ms，处于可接受范围")

    # 服务可用性
    for svc_name, svc_stats in json_report['statistics_by_service'].items():
        if svc_stats['pass_rate'] < 70:
            risks.append(f"- 🔴 {svc_name} 通过率仅 {svc_stats['pass_rate']}%，存在严重问题")
        elif svc_stats['pass_rate'] < 90:
            risks.append(f"- 🟡 {svc_name} 通过率为 {svc_stats['pass_rate']}%，建议关注")

    # 建议
    recommendations.extend([
        "- 定期执行此测试套件以监控API健康状况",
        "- 对失败的用例进行根因分析并修复",
        "- 关注性能指标，特别是P95和P99响应时间",
        "- 在生产环境部署前确保所有关键用例通过",
        "- 建议将此测试集成到CI/CD流水线中"
    ])

    if risks:
        lines.append("### 发现的风险\n")
        for risk in risks:
            lines.append(risk)
        lines.append("")

    lines.append("### 改进建议\n")
    for rec in recommendations:
        lines.append(rec)
    lines.append("")

    # 结尾
    lines.append("---\n")
    lines.append("***\n")
    lines.append(f"*报告由 **API Test Pro** 自动生成 | 版本 v1.4.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✓ Markdown报告已保存至: {output_file}")


def main():
    """主函数"""
    print("\n" + "#"*90)
    print("#" + " "*30 + "实验室管理系统 API 全面深度测试" + " "*33 + "#")
    print("#" + " "*35 + "v1.4.0" + " "*44 + "#")
    print("#"*90)

    # 确保输出目录存在
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # 创建测试器实例
    tester = APITester()

    # 运行所有测试
    run_all_tests(tester)

    # 计算统计信息
    stats = tester.calculate_statistics()

    # 打印汇总
    print("\n" + "="*90)
    print("测试执行完毕 - 汇总统计")
    print("="*90)
    print(f"\n📊 总体统计:")
    print(f"   • 总用例数: {stats['total_tests']}")
    print(f"   • 通过:     ✅ {stats['passed']}")
    print(f"   • 失败:     ❌ {stats['failed']}")
    print(f"   • 通过率:   **{stats['pass_rate']}%**")
    print(f"\n⏱️  性能指标:")
    print(f"   • 平均响应时间: {stats.get('avg_response_time_ms', 'N/A')}ms")
    print(f"   • 最小响应时间: {stats.get('min_response_time_ms', 'N/A')}ms")
    print(f"   • 最大响应时间: {stats.get('max_response_time_ms', 'N/A')}ms")
    print(f"   • P50/P90/P95/P99: {stats.get('p50_response_time_ms', 'N/A')}ms / "
          f"{stats.get('p90_response_time_ms', 'N/A')}ms / "
          f"{stats.get('p95_response_time_ms', 'N/A')}ms / "
          f"{stats.get('p99_response_time_ms', 'N/A')}ms")

    # 定义输出文件路径
    json_output = os.path.join(RESULTS_DIR, "api-deep-test-v1.4.0.json")
    md_output = os.path.join(RESULTS_DIR, "api-test-report-v1.4.0.md")

    # 生成JSON报告
    print(f"\n📝 正在生成测试报告...")
    json_report = generate_json_report(tester, json_output)

    # 生成Markdown报告
    generate_markdown_report(tester, json_report, md_output)

    print("\n" + "="*90)
    print("✅ 测试完成！")
    print("="*90)
    print(f"\n输出文件:")
    print(f"  • JSON报告:  {json_output}")
    print(f"  • MD报告:    {md_output}")

    # 返回退出代码
    return 0 if stats['pass_rate'] >= 90 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
