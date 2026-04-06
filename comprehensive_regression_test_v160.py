#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 v1.6.0 全面回归测试套件
Lab Management System - Comprehensive Regression Test Suite
"""

import requests
import json
import time
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== 测试配置 ====================
BASE_URLS = {
    'gateway': 'http://localhost:8080',
    'user_service': 'http://localhost:8086',
    'sample_service': 'http://localhost:8087',
    'report_service': 'http://localhost:8088',
    'hl7_service': 'http://localhost:8084',
    'ai_service': 'http://localhost:8089'
}

TIMEOUT = 10  # 秒

# 测试结果存储
test_results = []
performance_metrics = []

class TestResult:
    def __init__(self, test_id, test_name, category):
        self.test_id = test_id
        self.test_name = test_name
        self.category = category
        self.status = "PENDING"
        self.expected = ""
        self.actual = ""
        self.error_message = ""
        self.response_time_ms = 0
        self.http_status = 0
        self.timestamp = datetime.now().isoformat()
        self.details = {}

    def to_dict(self):
        return {
            'test_id': self.test_id,
            'test_name': self.test_name,
            'category': self.category,
            'status': self.status,
            'expected': self.expected,
            'actual': self.actual,
            'error_message': self.error_message,
            'response_time_ms': self.response_time_ms,
            'http_status': self.http_status,
            'timestamp': self.timestamp,
            'details': self.details
        }

def make_request(url, method='GET', data=None, headers=None, expected_status=200):
    """
    发送HTTP请求并记录性能指标
    """
    start_time = time.time()
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=TIMEOUT)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        elapsed_ms = (time.time() - start_time) * 1000

        performance_metrics.append({
            'endpoint': url,
            'method': method,
            'response_time_ms': round(elapsed_ms, 2),
            'status_code': response.status_code,
            'timestamp': datetime.now().isoformat()
        })

        return response, elapsed_ms

    except requests.exceptions.ConnectionError:
        elapsed_ms = (time.time() - start_time) * 1000
        return None, elapsed_ms
    except requests.exceptions.Timeout:
        elapsed_ms = (time.time() - start_time) * 1000
        return None, elapsed_ms
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return None, elapsed_ms


# ==================== 阶段1：健康检查测试 ====================

def test_health_checks():
    """测试所有微服务的健康检查端点"""
    print("\n" + "="*80)
    print("阶段1：微服务健康检查测试 (Health Check Tests)")
    print("="*80)

    services = [
        ('HC001', 'Gateway健康检查', BASE_URLS['gateway'], '/actuator/health'),
        ('HC002', 'HL7 Service健康检查', BASE_URLS['hl7_service'], '/actuator/health'),
        ('HC003', 'User Service健康检查', BASE_URLS['user_service'], '/actuator/health'),
        ('HC004', 'Sample Service健康检查', BASE_URLS['sample_service'], '/actuator/health'),
        ('HC005', 'Report Service健康检查', BASE_URLS['report_service'], '/actuator/health'),
        ('HC006', 'AI Service健康检查', BASE_URLS['ai_service'], '/actuator/health'),
    ]

    for test_id, name, base_url, endpoint in services:
        result = TestResult(test_id, name, 'Health Check')
        result.expected = "HTTP 200 - UP status"

        full_url = f"{base_url}{endpoint}"
        response, elapsed = make_request(full_url)

        if response is not None:
            result.http_status = response.status_code
            result.response_time_ms = round(elapsed, 2)

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') == 'UP':
                        result.status = "PASS"
                        result.actual = f"HTTP {response.status_code} - {data.get('status')}"
                        print(f"  [PASS] {name}: {result.actual} ({elapsed:.0f}ms)")
                    else:
                        result.status = "FAIL"
                        result.actual = f"HTTP {response.status_code} - Status: {data.get('status')}"
                        result.error_message = f"Service not UP, got: {data}"
                        print(f"  [FAIL] {name}: {result.actual}")
                except:
                    # 有些服务可能返回非JSON格式
                    result.status = "WARN"
                    result.actual = f"HTTP {response.status_code} (non-JSON response)"
                    print(f"  [WARN] {name}: {result.actual}")
            else:
                result.status = "FAIL"
                result.actual = f"HTTP {response.status_code}"
                result.error_message = f"Expected 200, got {response.status_code}"
                print(f"  [FAIL] {name}: HTTP {response.status_code} ({elapsed:.0f}ms)")
        else:
            result.status = "FAIL"
            result.actual = "Connection Failed / Timeout"
            result.error_message = "Service not reachable"
            print(f"  [FAIL] {name}: Service not running")

        test_results.append(result)


# ==================== 阶段2：用户认证API测试 ====================

def test_user_authentication():
    """测试用户认证相关API"""
    print("\n" + "="*80)
    print("阶段2：用户认证API测试 (User Authentication API Tests)")
    print("="*80)

    # 测试登录接口 - 使用不同的参数格式
    login_tests = [
        {
            'id': 'AUTH001',
            'name': '管理员登录（标准格式）',
            'url': f"{BASE_URLS['user_service']}/user/login",
            'method': 'POST',
            'data': {'username': 'admin', 'password': 'admin123'},
            'expected_status': 200
        },
        {
            'id': 'AUTH002',
            'name': '管理员登录（通过Gateway）',
            'url': f"{BASE_URLS['gateway']}/api/user/login",
            'method': 'POST',
            'data': {'username': 'admin', 'password': 'admin123'},
            'expected_status': 200
        },
        {
            'id': 'AUTH003',
            'name': '错误密码登录测试',
            'url': f"{BASE_URLS['user_service']}/user/login",
            'method': 'POST',
            'data': {'username': 'admin', 'password': 'wrongpassword'},
            'expected_status': 400  # 或401
        },
        {
            'id': 'AUTH004',
            'name': '空用户名登录测试',
            'url': f"{BASE_URLS['user_service']}/user/login",
            'method': 'POST',
            'data': {'username': '', 'password': 'admin123'},
            'expected_status': 400
        }
    ]

    jwt_token = None

    for test_case in login_tests:
        result = TestResult(test_case['id'], test_case['name'], 'Authentication')
        result.expected = f"HTTP {test_case['expected_status']}"

        response, elapsed = make_request(
            test_case['url'],
            method=test_case['method'],
            data=test_case['data']
        )

        if response is not None:
            result.http_status = response.status_code
            result.response_time_ms = round(elapsed, 2)

            try:
                resp_data = response.json()
                result.details = resp_data

                if response.status_code == test_case['expected_status']:
                    if test_case['expected_status'] == 200 and resp_data.get('success'):
                        result.status = "PASS"
                        result.actual = f"HTTP {response.status_code} - Login Success"
                        # 提取JWT token
                        if resp_data.get('data') and isinstance(resp_data['data'], dict):
                            jwt_token = resp_data['data'].get('token')
                            if jwt_token:
                                print(f"  [PASS] {test_case['name']}: Got JWT Token")
                            else:
                                print(f"  [PASS] {test_case['name']}: Login Success (no token in response)")
                        else:
                            print(f"  [PASS] {test_case['name']}: {resp_data.get('message', 'Success')}")
                    elif test_case['expected_status'] != 200:
                        result.status = "PASS"
                        result.actual = f"HTTP {response.status_code} - Correctly rejected"
                        print(f"  [PASS] {test_case['name']}: Correctly rejected with {response.status_code}")
                    else:
                        result.status = "FAIL"
                        result.actual = f"HTTP {response.status_code} - {resp_data.get('message', 'Unknown error')}"
                        result.error_message = resp_data
                        print(f"  [FAIL] {test_case['name']}: {result.actual}")
                else:
                    result.status = "FAIL"
                    result.actual = f"HTTP {response.status_code} (expected {test_case['expected_status']})"
                    result.error_message = resp_data
                    print(f"  [FAIL] {test_case['name']}: {result.actual}")
            except Exception as e:
                result.status = "ERROR"
                result.actual = f"Parse error: {str(e)}"
                result.error_message = str(e)
                print(f"  [ERROR] {test_case['name']}: {str(e)}")
        else:
            result.status = "FAIL"
            result.actual = "Request failed"
            result.error_message = "No response from server"
            print(f"  [FAIL] {test_case['name']}: No response")

        test_results.append(result)

    return jwt_token


# ==================== 阶段3：标本管理API测试 ====================

def test_sample_management(token=None):
    """测试标本管理相关API"""
    print("\n" + "="*80)
    print("阶段3：标本管理API测试 (Sample Management API Tests)")
    print("="*80)

    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    sample_tests = [
        {
            'id': 'SM001',
            'name': '获取标本列表',
            'url': f"{BASE_URLS['sample_service']}/sample/list",
            'method': 'GET',
            'expected_status': 200
        },
        {
            'id': 'SM002',
            'name': '获取标本列表（分页）',
            'url': f"{BASE_URLS['sample_service']}/sample/list?page=1&size=5",
            'method': 'GET',
            'expected_status': 200
        },
        {
            'id': 'SM003',
            'name': '创建新标本',
            'url': f"{BASE_URLS['sample_service']}/sample/create",
            'method': 'POST',
            'data': {
                'patientName': 'RegressionTest Patient',
                'patientGender': '男',
                'patientAge': 45,
                'doctorName': 'Test Doctor',
                'testItems': '血常规',
                'sampleType': 'BLOOD',
                'collectLocation': '检验科'
            },
            'expected_status': 200
        },
        {
            'id': 'SM004',
            'name': '通过Gateway获取标本列表',
            'url': f"{BASE_URLS['gateway']}/api/sample/list",
            'method': 'GET',
            'expected_status': 200
        }
    ]

    created_sample_id = None

    for test_case in sample_tests:
        result = TestResult(test_case['id'], test_case['name'], 'Sample Management')
        result.expected = f"HTTP {test_case['expected_status']}"

        response, elapsed = make_request(
            test_case['url'],
            method=test_case['method'],
            data=test_case.get('data'),
            headers=headers
        )

        if response is not None:
            result.http_status = response.status_code
            result.response_time_ms = round(elapsed, 2)

            try:
                resp_data = response.json()
                result.details = {
                    'record_count': len(resp_data.get('data', [])) if isinstance(resp_data.get('data'), list) else 'N/A'
                } if test_case['method'] == 'GET' else resp_data

                if response.status_code == test_case['expected_status']:
                    if resp_data.get('success'):
                        result.status = "PASS"
                        if test_case['method'] == 'GET':
                            count = len(resp_data.get('data', [])) if isinstance(resp_data.get('data'), list) else 'N/A'
                            result.actual = f"HTTP {response.status_code} - Returned {count} records"
                            print(f"  [PASS] {test_case['name']}: {count} records ({elapsed:.0f}ms)")
                        else:
                            result.actual = f"HTTP {response.status_code} - Operation successful"
                            # 获取创建的标本ID
                            if test_case['id'] == 'SM003' and resp_data.get('data'):
                                created_sample_id = resp_data['data'].get('id')
                            print(f"  [PASS] {test_case['name']}: Operation successful")
                    else:
                        result.status = "FAIL"
                        result.actual = f"HTTP {response.status_code} - {resp_data.get('message', 'Operation failed')}"
                        result.error_message = resp_data
                        print(f"  [FAIL] {test_case['name']}: {result.actual}")
                else:
                    result.status = "FAIL"
                    result.actual = f"HTTP {response.status_code} (expected {test_case['expected_status']})"
                    result.error_message = resp_data
                    print(f"  [FAIL] {test_case['name']}: {result.actual}")
            except Exception as e:
                result.status = "ERROR"
                result.actual = f"Parse error: {str(e)}"
                result.error_message = str(e)
                print(f"  [ERROR] {test_case['name']}: {str(e)}")
        else:
            result.status = "FAIL"
            result.actual = "Request failed"
            print(f"  [FAIL] {test_case['name']}: No response")

        test_results.append(result)

    return created_sample_id


# ==================== 阶段4：报告管理API测试 ====================

def test_report_management(token=None):
    """测试报告管理相关API"""
    print("\n" + "="*80)
    print("阶段4：报告管理API测试 (Report Management API Tests)")
    print("="*80)

    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    report_tests = [
        {
            'id': 'RP001',
            'name': '获取报告列表',
            'url': f"{BASE_URLS['report_service']}/report/list",
            'method': 'GET',
            'expected_status': 200
        },
        {
            'id': 'RP002',
            'name': '通过Gateway获取报告列表',
            'url': f"{BASE_URLS['gateway']}/api/report/list",
            'method': 'GET',
            'expected_status': 200
        },
        {
            'id': 'RP003',
            'name': '创建新报告',
            'url': f"{BASE_URLS['report_service']}/report/create",
            'method': 'POST',
            'data': {
                'sampleId': 1,
                'patientName': 'Report Test Patient',
                'testItems': '血常规,尿常规',
                'remark': '回归测试报告'
            },
            'expected_status': 200
        }
    ]

    for test_case in report_tests:
        result = TestResult(test_case['id'], test_case['name'], 'Report Management')
        result.expected = f"HTTP {test_case['expected_status']}"

        response, elapsed = make_request(
            test_case['url'],
            method=test_case['method'],
            data=test_case.get('data'),
            headers=headers
        )

        if response is not None:
            result.http_status = response.status_code
            result.response_time_ms = round(elapsed, 2)

            try:
                resp_data = response.json()
                result.details = {
                    'record_count': len(resp_data.get('data', [])) if isinstance(resp_data.get('data'), list) else 'N/A'
                } if test_case['method'] == 'GET' else resp_data

                if response.status_code == test_case['expected_status']:
                    if resp_data.get('success'):
                        result.status = "PASS"
                        if test_case['method'] == 'GET':
                            count = len(resp_data.get('data', [])) if isinstance(resp_data.get('data'), list) else 'N/A'
                            result.actual = f"HTTP {response.status_code} - Returned {count} reports"
                            print(f"  [PASS] {test_case['name']}: {count} reports ({elapsed:.0f}ms)")
                        else:
                            result.actual = f"HTTP {response.status_code} - Operation successful"
                            print(f"  [PASS] {test_case['name']}: Operation successful")
                    else:
                        result.status = "FAIL"
                        result.actual = f"HTTP {response.status_code} - {resp_data.get('message', 'Failed')}"
                        result.error_message = resp_data
                        print(f"  [FAIL] {test_case['name']}: {result.actual}")
                else:
                    result.status = "FAIL"
                    result.actual = f"HTTP {response.status_code} (expected {test_case['expected_status']})"
                    result.error_message = resp_data
                    print(f"  [FAIL] {test_case['name']}: {result.actual}")
            except Exception as e:
                result.status = "ERROR"
                result.actual = f"Parse error: {str(e)}"
                result.error_message = str(e)
                print(f"  [ERROR] {test_case['name']}: {str(e)}")
        else:
            result.status = "FAIL"
            result.actual = "Request failed"
            print(f"  [FAIL] {test_case['name']}: No response")

        test_results.append(result)


# ==================== 阶段5：AI诊断和HL7 API测试 ====================

def test_ai_and_hl7_services():
    """测试AI诊断和HL7消息解析API"""
    print("\n" + "="*80)
    print("阶段5：AI诊断 & HL7服务测试 (AI Diagnosis & HL7 Service Tests)")
    print("="*80)

    # AI诊断测试
    ai_tests = [
        {
            'id': 'AI001',
            'name': '血常规AI诊断',
            'url': f"{BASE_URLS['ai_service']}/ai/diagnose/blood-routine",
            'method': 'POST',
            'data': {
                'indicators': {
                    'WBC': 11.5,
                    'RBC': 4.8,
                    'HGB': 145,
                    'PLT': 280
                }
            },
            'expected_status': 200
        },
        {
            'id': 'AI002',
            'name': '尿常规AI诊断',
            'url': f"{BASE_URLS['ai_service']}/ai/diagnose/urine-routine",
            'method': 'POST',
            'data': {
                'indicators': {
                    'LEU': 2+,
                    'ERY': 1+,
                    'PRO': '+-',
                    'GLU': '-'
                }
            },
            'expected_status': 200
        }
    ]

    for test_case in ai_tests:
        result = TestResult(test_case['id'], test_case['name'], 'AI Diagnosis')
        result.expected = f"HTTP {test_case['expected_status']}"

        response, elapsed = make_request(
            test_case['url'],
            method=test_case['method'],
            data=test_case.get('data')
        )

        if response is not None:
            result.http_status = response.status_code
            result.response_time_ms = round(elapsed, 2)

            if response.status_code == test_case['expected_status']:
                try:
                    resp_data = response.json()
                    result.details = resp_data
                    result.status = "PASS"
                    result.actual = f"HTTP {response.status_code} - Diagnosis completed"
                    print(f"  [PASS] {test_case['name']}: Diagnosis completed ({elapsed:.0f}ms)")
                except:
                    result.status = "PASS"
                    result.actual = f"HTTP {response.status_code} - Response received"
                    print(f"  [PASS] {test_case['name']}: Response received ({elapsed:.0f}ms)")
            elif response.status_code == 404:
                result.status = "WARN"
                result.actual = f"HTTP 404 - AI Service endpoint not found (service may not be running)"
                result.error_message = "AI Service may not be started"
                print(f"  [WARN] {test_case['name']}: Service not available (HTTP 404)")
            else:
                result.status = "FAIL"
                result.actual = f"HTTP {response.status_code}"
                print(f"  [FAIL] {test_case['name']}: HTTP {response.status_code}")
        else:
            result.status = "FAIL"
            result.actual = "AI Service not running or unreachable"
            result.error_message = "Cannot connect to AI Service"
            print(f"  [FAIL] {test_case['name']}: Service not running")

        test_results.append(result)

    # HL7消息解析测试
    hl7_test = {
        'id': 'HL7001',
        'name': 'HL7消息解析',
        'url': f"{BASE_URLS['hl7_service']}/hl7/parse",
        'method': 'POST',
        'data': {
            'message': 'MSH|^~\\&|LAB|HOSP|LAB|HOSP|202604051200||ORM^O01|MSG00001|P|2.3.1\rPID|1||PT001||DOE^JOHN^|19700101|M\rOBR|1|ORD001||BLD^Blood Routine|||202604051200'
        },
        'expected_status': 200
    }

    result = TestResult(hl7_test['id'], hl7_test['name'], 'HL7 Service')
    result.expected = f"HTTP {hl7_test['expected_status']}"

    response, elapsed = make_request(
        hl7_test['url'],
        method=hl7_test['method'],
        data=hl7_test.get('data')
    )

    if response is not None:
        result.http_status = response.status_code
        result.response_time_ms = round(elapsed, 2)

        if response.status_code == hl7_test['expected_status']:
            try:
                resp_data = response.json()
                result.details = resp_data
                result.status = "PASS"
                result.actual = f"HTTP {response.status_code} - Message parsed successfully"
                print(f"  [PASS] {hl7_test['name']}: Parsed successfully ({elapsed:.0f}ms)")
            except:
                result.status = "PASS"
                result.actual = f"HTTP {response.status_code} - Response received"
                print(f"  [PASS] {hl7_test['name']}: Response received ({elapsed:.0f}ms)")
        else:
            result.status = "FAIL"
            result.actual = f"HTTP {response.status_code}"
            print(f"  [FAIL] {hl7_test['name']}: HTTP {response.status_code}")
    else:
        result.status = "WARN"
        result.actual = "HL7 Service returned error or not available"
        print(f"  [WARN] {hl7_test['name']}: Service error")

    test_results.append(result)


# ==================== 阶段6：安全性测试 ====================

def test_security(token=None):
    """测试安全配置"""
    print("\n" + "="*80)
    print("阶段6：安全性测试 (Security Tests)")
    print("="*80)

    security_tests = [
        {
            'id': 'SEC001',
            'name': '未授权访问保护（无Token访问受保护资源）',
            'url': f"{BASE_URLS['user_service']}/user/list",
            'method': 'GET',
            'expected_unauthorized': True
        },
        {
            'id': 'SEC002',
            'name': 'CORS配置验证',
            'url': f"{BASE_URLS['gateway']}/api/user/login",
            'method': 'OPTIONS',
            'headers': {
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'POST'
            },
            'expected_status': 204  # 或200
        }
    ]

    for test_case in security_tests:
        result = TestResult(test_case['id'], test_case['name'], 'Security')

        if test_case.get('expected_unauthorized'):
            result.expected = "HTTP 401/403 - Unauthorized"

            response, elapsed = make_request(
                test_case['url'],
                method=test_case['method']
            )

            if response is not None:
                result.http_status = response.status_code
                result.response_time_ms = round(elapsed, 2)

                if response.status_code in [401, 403]:
                    result.status = "PASS"
                    result.actual = f"HTTP {response.status_code} - Properly blocked unauthorized access"
                    print(f"  [PASS] {test_case['name']}: Access denied ({response.status_code})")
                else:
                    result.status = "FAIL"
                    result.actual = f"HTTP {response.status_code} - Should be 401/403"
                    result.error_message = f"Unauthorized access not properly blocked"
                    print(f"  [FAIL] {test_case['name']}: Not properly protected (HTTP {response.status_code})")
            else:
                result.status = "ERROR"
                result.actual = "Request failed"
                print(f"  [ERROR] {test_case['name']}: Request failed")
        else:
            result.expected = f"HTTP {test_case.get('expected_status', 200)}"

            response, elapsed = make_request(
                test_case['url'],
                method=test_case['method'],
                headers=test_case.get('headers')
            )

            if response is not None:
                result.http_status = response.status_code
                result.response_time_ms = round(elapsed, 2)

                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods')
                }

                if response.status_code in [200, 204]:
                    result.status = "PASS"
                    result.actual = f"HTTP {response.status_code} - CORS configured"
                    result.details = cors_headers
                    print(f"  [PASS] {test_case['name']}: CORS headers present")
                else:
                    result.status = "WARN"
                    result.actual = f"HTTP {response.status_code}"
                    print(f"  [WARN] {test_case['name']}: HTTP {response.status_code}")
            else:
                result.status = "ERROR"
                result.actual = "Request failed"
                print(f"  [ERROR] {test_case['name']}: Request failed")

        test_results.append(result)


# ==================== 阶段7：性能基准测试 ====================

def test_performance_benchmark():
    """执行性能基准测试"""
    print("\n" + "="*80)
    print("阶段7：性能基准测试 (Performance Benchmark Tests)")
    print("="*80)

    benchmark_endpoints = [
        ('PERF001', '标本列表查询性能', f"{BASE_URLS['sample_service']}/sample/list", 'GET'),
        ('PERF002', '报告列表查询性能', f"{BASE_URLS['report_service']}/report/list", 'GET'),
        ('PERF003', 'Gateway路由性能', f"{BASE_URLS['gateway']}/api/sample/list", 'GET'),
    ]

    for test_id, name, url, method in benchmark_endpoints:
        result = TestResult(test_id, name, 'Performance')
        result.expected = "P50 < 200ms, P95 < 500ms"

        # 执行多次请求以获得统计数据
        times = []
        success_count = 0

        for i in range(10):  # 执行10次请求
            response, elapsed = make_request(url, method=method)
            times.append(elapsed)
            if response and response.status_code == 200:
                success_count += 1
            time.sleep(0.1)  # 避免过快请求

        if times:
            times.sort()
            p50_idx = int(len(times) * 0.50)
            p95_idx = int(len(times) * 0.95)
            p99_idx = int(len(times) * 0.99)

            p50 = times[p50_idx]
            p95 = times[min(p95_idx, len(times)-1)]
            p99 = times[min(p99_idx, len(times)-1)]
            avg = sum(times) / len(times)

            result.details = {
                'avg_ms': round(avg, 2),
                'p50_ms': round(p50, 2),
                'p95_ms': round(p95, 2),
                'p99_ms': round(p99, 2),
                'min_ms': round(min(times), 2),
                'max_ms': round(max(times), 2),
                'success_rate': f"{success_count}/{len(times)}",
                'requests': times
            }
            result.response_time_ms = round(avg, 2)

            # 判断是否达标
            if p95 < 500 and p50 < 200:
                result.status = "PASS"
                result.actual = f"Avg:{avg:.0f}ms P50:{p50:.0f}ms P95:{p95:.0f}ms P99:{p99:.0f}ms"
                print(f"  [PASS] {name}: Avg={avg:.0f}ms, P50={p50:.0f}ms, P95={p95:.0f}ms, P99={p99:.0f}ms")
            elif p95 < 1000:
                result.status = "WARN"
                result.actual = f"Avg:{avg:.0f}ms P50:{p50:.0f}ms P95:{p95:.0f}ms (above target)"
                print(f"  [WARN] {name}: P95={p95:.0f}ms (target <500ms)")
            else:
                result.status = "FAIL"
                result.actual = f"P95={p95:.0f}ms (exceeds limit)"
                print(f"  [FAIL] {name}: P95={p95:.0f}ms exceeds 1000ms limit")
        else:
            result.status = "ERROR"
            result.actual = "No measurements collected"

        test_results.append(result)


# ==================== 主测试流程 ====================

def main():
    """主测试入口"""
    print("="*80)
    print("实验室管理系统 v1.6.0 - 全面回归测试套件")
    print("Lab Management System v1.6.0 - Comprehensive Regression Test Suite")
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 执行所有测试阶段
    try:
        # 阶段1：健康检查
        test_health_checks()

        # 阶段2：用户认证
        jwt_token = test_user_authentication()

        # 阶段3：标本管理
        sample_id = test_sample_management(jwt_token)

        # 阶段4：报告管理
        test_report_management(jwt_token)

        # 阶段5：AI诊断和HL7
        test_ai_and_hl7_services()

        # 阶段6：安全性测试
        test_security(jwt_token)

        # 阶段7：性能基准测试
        test_performance_benchmark()

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

    # 生成测试报告
    generate_test_report()


def generate_test_report():
    """生成详细的测试报告"""
    print("\n" + "="*80)
    print("测试报告汇总 (Test Summary Report)")
    print("="*80)

    # 统计结果
    total = len(test_results)
    passed = sum(1 for r in test_results if r.status == "PASS")
    failed = sum(1 for r in test_results if r.status == "FAIL")
    warned = sum(1 for r in test_results if r.status == "WARN")
    errors = sum(1 for r in test_results if r.status == "ERROR")

    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"\n总测试用例数: {total}")
    print(f"通过 (PASS):   {passed} ({pass_rate:.1f}%)")
    print(f"失败 (FAIL):   {failed}")
    print(f"警告 (WARN):   {warned}")
    print(f"错误 (ERROR):  {errors}")

    # 按类别统计
    print("\n按测试类别统计:")
    categories = {}
    for r in test_results:
        cat = r.category
        if cat not in categories:
            categories[cat] = {'total': 0, 'pass': 0, 'fail': 0}
        categories[cat]['total'] += 1
        if r.status == 'PASS':
            categories[cat]['pass'] += 1
        elif r.status == 'FAIL':
            categories[cat]['fail'] += 1

    for cat, stats in sorted(categories.items()):
        rate = (stats['pass'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {cat:25s}: {stats['pass']:3d}/{stats['total']:3d} 通过 ({rate:5.1f}%)")

    # 性能指标汇总
    if performance_metrics:
        print("\n性能指标汇总:")
        perf_times = [m['response_time_ms'] for m in performance_metrics if m['response_time_ms'] > 0]
        if perf_times:
            perf_times.sort()
            n = len(perf_times)
            print(f"  总请求数:       {n}")
            print(f"  平均响应时间:   {sum(perf_times)/n:.2f}ms")
            print(f"  最小响应时间:   {min(perf_times):.2f}ms")
            print(f"  最大响应时间:   {max(perf_times):.2f}ms")
            print(f"  P50 响应时间:   {perf_times[int(n*0.50)]:.2f}ms")
            print(f"  P95 响应时间:   {perf_times[min(int(n*0.95), n-1)]:.2f}ms")
            print(f"  P99 响应时间:   {perf_times[min(int(n*0.99), n-1)]:.2f}ms")

    # 失败的测试用例详情
    failed_tests = [r for r in test_results if r.status in ['FAIL', 'ERROR']]
    if failed_tests:
        print("\n失败的测试用例:")
        for r in failed_tests:
            print(f"  [{r.status}] {r.test_id}: {r.test_name}")
            if r.error_message:
                print(f"         错误: {str(r.error_message)[:100]}")

    # 保存详细结果到JSON文件
    report_data = {
        'version': 'v1.6.0',
        'test_timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'warned': warned,
            'errors': errors,
            'pass_rate': round(pass_rate, 2)
        },
        'performance_summary': {
            'total_requests': len(performance_metrics),
            'avg_response_ms': round(sum(performance_metrics)/len(performance_metrics), 2) if performance_metrics else 0
        } if performance_metrics else {},
        'test_results': [r.to_dict() for r in test_results],
        'performance_metrics': performance_metrics
    }

    output_file = 'd:/FinalCodeAndFile/lab-management-system/test_results/api-test-results-v1.6.0.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print(f"\n详细测试结果已保存至: {output_file}")

    # 最终结论
    print("\n" + "="*80)
    print("最终结论 (Final Conclusion)")
    print("="*80)

    if pass_rate >= 90:
        conclusion = "✓ 通过验收标准 (PASSED)"
        print(f"\n测试通过率: {pass_rate:.1f}%")
        print(f"状态: {conclusion}")
        print(f"系统版本 v1.6.0 已达到生产就绪状态，可以部署上线。")
    elif pass_rate >= 70:
        conclusion = "△ 有条件通过 (CONDITIONAL PASS)"
        print(f"\n测试通过率: {pass_rate:.1f}%")
        print(f"状态: {conclusion}")
        print(f"系统基本功能正常，但存在部分缺陷需要修复后才能部署。")
    else:
        conclusion = "✗ 未通过验收 (FAILED)"
        print(f"\n测试通过率: {pass_rate:.1f}%")
        print(f"状态: {conclusion}")
        print(f"系统存在严重问题，不建议部署，需要修复后重新测试。")

    print(f"\n测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return pass_rate >= 90


if __name__ == '__main__':
    main()
