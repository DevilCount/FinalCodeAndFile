#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 - 修正后的API测试脚本
使用正确的参数格式（登录接口使用表单参数）
"""

import requests
import json
import time
from datetime import datetime

# 服务配置
SERVICES = {
    "Gateway": "http://localhost:8080",
    "User Service": "http://localhost:8086",
    "Sample Service": "http://localhost:8087",
    "Report Service": "http://localhost:8088",
    "HL7 Service": "http://localhost:8084",
    "AI Service": "http://localhost:8085"
}

REPORT_FILE = r"d:\FinalCodeAndFile\lab-management-system\API_TEST_REPORT_FINAL_FIXED.md"
RESULTS_FILE = r"d:\FinalCodeAndFile\lab-management-system\api_test_results_final_fixed.json"

test_results = []


def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_test_result(index, name, status, status_code, response_time, note=""):
    icon = "✅" if status == "PASS" else "❌"
    rt_str = f"{response_time:.2f}ms" if response_time else "N/A"
    sc_str = str(status_code) if status_code else "N/A"
    print(f"[{index:02d}] {icon} {name:50} → {sc_str:>4} ({rt_str:>10}) {note}")


def test_endpoint(service_name, method, endpoint, params=None, json_data=None, form_data=None, expected_status=200, test_name="", note=""):
    base_url = SERVICES[service_name]
    url = base_url + endpoint
    
    result = {
        "test_name": test_name,
        "service": service_name,
        "method": method,
        "endpoint": endpoint,
        "url": url,
        "expected_status": expected_status,
        "note": note
    }
    
    start_time = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            if form_data:
                response = requests.post(url, data=form_data, timeout=10)
            elif json_data:
                response = requests.post(url, json=json_data, timeout=10)
            elif params:
                response = requests.post(url, params=params, timeout=10)
            else:
                response = requests.post(url, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=json_data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        
        elapsed_ms = (time.time() - start_time) * 1000
        status_code = response.status_code
        
        is_pass = status_code == expected_status
        
        result.update({
            "status": "PASS" if is_pass else "FAIL",
            "actual_status": status_code,
            "response_time_ms": round(elapsed_ms, 2),
            "response_body": response.text[:500] if response.text else ""
        })
        
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        result.update({
            "status": "FAIL",
            "actual_status": None,
            "response_time_ms": round(elapsed_ms, 2),
            "error": str(e)
        })
    
    test_results.append(result)
    return result


def run_tests():
    print_header("实验室管理系统 - 修正后的API测试")
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 用户服务测试 - 登录接口 (重点)
    print_header("第一部分: 用户服务 - 登录接口测试 (重点)")
    
    # 测试1: 登录接口 - 空参数验证 (期望HTTP 400) - 使用表单参数
    print("\n【重点测试1】登录接口空参数验证 (期望HTTP 400)")
    result = test_endpoint(
        "User Service", "POST", "/user/login",
        form_data={},
        expected_status=400,
        test_name="登录接口 - 空参数验证 (表单格式)",
        note="重点测试: 空登录参数应返回HTTP 400"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms"),
        f"期望: {result['expected_status']}, 实际: {result.get('actual_status')}"
    )
    
    # 测试2: 登录接口 - 缺少用户名
    result = test_endpoint(
        "User Service", "POST", "/user/login",
        form_data={"password": "admin123"},
        expected_status=400,
        test_name="登录接口 - 缺少用户名 (表单格式)",
        note="缺少用户名参数验证"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )
    
    # 测试3: 登录接口 - 缺少密码
    result = test_endpoint(
        "User Service", "POST", "/user/login",
        form_data={"username": "admin"},
        expected_status=400,
        test_name="登录接口 - 缺少密码 (表单格式)",
        note="缺少密码参数验证"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )
    
    # 测试4: 登录接口 - 正常登录
    result = test_endpoint(
        "User Service", "POST", "/user/login",
        form_data={"username": "admin", "password": "admin123"},
        expected_status=200,
        test_name="登录接口 - 正常登录 (表单格式)",
        note="正常登录测试"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )
    
    # 2. 标本服务测试 - 按状态查询 (重点)
    print_header("第二部分: 标本服务 - 按状态查询测试 (重点)")
    
    # 测试1: 标本列表
    result = test_endpoint(
        "Sample Service", "GET", "/sample/list",
        expected_status=200,
        test_name="标本服务 - 获取标本列表",
        note="获取所有标本"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )
    
    # 【重点测试2】标本按状态查询接口 (期望HTTP 200)
    print("\n【重点测试2】标本按状态查询接口 (期望HTTP 200)")
    statuses = ["PENDING", "RECEIVED", "TESTING", "COMPLETED", "REPORTED"]
    
    for status in statuses:
        result = test_endpoint(
            "Sample Service", "GET", "/sample/list-by-status",
            params={"status": status},
            expected_status=200,
            test_name=f"标本服务 - 按状态查询 ({status})",
            note=f"查询状态为 {status} 的标本"
        )
        print_test_result(
            len(test_results),
            result["test_name"],
            result["status"],
            result.get("actual_status"),
            result.get("response_time_ms"),
            f"状态: {status}"
        )
    
    # 3. 其他服务快速测试
    print_header("第三部分: 其他服务测试")
    
    result = test_endpoint(
        "User Service", "GET", "/user/list",
        expected_status=200,
        test_name="用户服务 - 获取用户列表",
        note="获取所有用户"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )
    
    result = test_endpoint(
        "Report Service", "GET", "/report/list",
        expected_status=200,
        test_name="报告服务 - 获取报告列表",
        note="获取所有报告"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )
    
    result = test_endpoint(
        "AI Service", "GET", "/ai/health",
        expected_status=200,
        test_name="AI服务 - 健康检查",
        note="AI服务健康检查"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )


def generate_report():
    print_header("生成测试报告")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r["status"] == "PASS")
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # 生成Markdown报告
    report_content = []
    report_content.append("# 实验室管理系统 - 修正后的API测试报告\n")
    report_content.append(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    report_content.append("## 测试摘要\n\n")
    report_content.append(f"- **总测试用例**: {total_tests}\n")
    report_content.append(f"- **通过**: {passed_tests} ({pass_rate:.1f}%)\n")
    report_content.append(f"- **失败**: {failed_tests}\n\n")
    
    # 重点测试结果
    report_content.append("## 重点测试结果\n\n")
    report_content.append("### 1. 登录接口空参数验证 (使用表单参数)\n")
    login_test = next((r for r in test_results if "空参数验证" in r["test_name"]), None)
    if login_test:
        report_content.append(f"- **测试名称**: {login_test['test_name']}\n")
        report_content.append(f"- **期望状态码**: {login_test['expected_status']}\n")
        report_content.append(f"- **实际状态码**: {login_test.get('actual_status', 'N/A')}\n")
        report_content.append(f"- **测试结果**: {login_test['status']}\n")
        report_content.append(f"- **响应时间**: {login_test.get('response_time_ms', 'N/A')}ms\n")
        if "response_body" in login_test:
            report_content.append(f"- **响应内容**: {login_test['response_body']}\n")
    
    report_content.append("\n### 2. 标本按状态查询接口\n")
    status_tests = [r for r in test_results if "按状态查询" in r["test_name"]]
    for test in status_tests:
        report_content.append(f"- **{test['test_name']}**: {test['status']} (状态码: {test.get('actual_status', 'N/A')})\n")
    
    # 详细测试结果
    report_content.append("\n## 详细测试结果\n\n")
    report_content.append("| 序号 | 测试名称 | 服务 | 方法 | 端点 | 期望 | 实际 | 结果 | 响应时间(ms) |\n")
    report_content.append("|------|---------|------|------|------|------|------|------|-------------|\n")
    
    for idx, result in enumerate(test_results, 1):
        expected = result['expected_status']
        actual = result.get('actual_status', 'N/A')
        rt = result.get('response_time_ms', 'N/A')
        report_content.append(f"| {idx} | {result['test_name']} | {result['service']} | {result['method']} | {result['endpoint']} | {expected} | {actual} | {result['status']} | {rt} |\n")
    
    # 保存报告
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_content))
    
    # 保存JSON结果
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": pass_rate,
            "results": test_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 测试报告已生成: {REPORT_FILE}")
    print(f"✅ JSON结果已保存: {RESULTS_FILE}")
    print(f"\n📊 测试统计: {passed_tests}/{total_tests} 通过 ({pass_rate:.1f}%)")
    
    return passed_tests, failed_tests, total_tests


if __name__ == "__main__":
    # 检查requests库
    try:
        import requests
    except ImportError:
        print("正在安装requests库...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    # 运行测试
    run_tests()
    
    # 生成报告
    passed, failed, total = generate_report()
    
    print_header("测试完成")
