#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 - 完整回归测试脚本 v1.5.0
重点测试:
1. 登录接口空参数验证 (期望HTTP 400)
2. 标本按状态查询接口 (期望HTTP 200)
3. 所有API端点的完整回归测试
生成完整测试报告
"""

import requests
import json
import time
import platform
import sys
from datetime import datetime

# 测试版本和环境配置
TEST_VERSION = "v1.5.0"
TEST_DATE = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 服务配置
SERVICES = {
    "Gateway": "http://localhost:8080",
    "User Service": "http://localhost:8086",
    "Sample Service": "http://localhost:8087",
    "Report Service": "http://localhost:8088",
    "HL7 Service": "http://localhost:8084",
    "AI Service": "http://localhost:8089"
}

REPORT_FILE = r"d:\FinalCodeAndFile\lab-management-system\test_results\REGRESSION-REPORT-V1.5.0.md"
RESULTS_FILE = r"d:\FinalCodeAndFile\lab-management-system\test_results\regression-test-v150.json"

test_results = []
defect_list = []


def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_test_result(index, name, status, status_code, response_time, note=""):
    icon = "✅" if status == "PASS" else "❌"
    rt_str = f"{response_time:.2f}ms" if response_time else "N/A"
    sc_str = str(status_code) if status_code else "N/A"
    print(f"[{index:02d}] {icon} {name:50} → {sc_str:>4} ({rt_str:>10}) {note}")


def test_endpoint(service_name, method, endpoint, params=None, json_data=None, form_data=None, 
                  expected_status=200, test_name="", note="", priority="medium"):
    base_url = SERVICES[service_name]
    url = base_url + endpoint
    
    result = {
        "test_name": test_name,
        "service": service_name,
        "method": method,
        "endpoint": endpoint,
        "url": url,
        "expected_status": expected_status,
        "note": note,
        "priority": priority,
        "timestamp": datetime.now().isoformat()
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
        
        if not is_pass:
            defect_list.append({
                "defect_id": f"D{len(defect_list)+1:03d}",
                "test_name": test_name,
                "service": service_name,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": status_code,
                "priority": priority,
                "description": f"期望状态码 {expected_status}, 实际返回 {status_code}",
                "response": response.text[:300] if response.text else ""
            })
        
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        result.update({
            "status": "FAIL",
            "actual_status": None,
            "response_time_ms": round(elapsed_ms, 2),
            "error": str(e)
        })
        defect_list.append({
            "defect_id": f"D{len(defect_list)+1:03d}",
            "test_name": test_name,
            "service": service_name,
            "endpoint": endpoint,
            "expected_status": expected_status,
            "actual_status": "连接失败",
            "priority": priority,
            "description": f"请求异常: {str(e)}",
            "response": ""
        })
    
    test_results.append(result)
    return result


def get_environment_info():
    return {
        "os": platform.system() + " " + platform.release(),
        "python_version": sys.version,
        "test_version": TEST_VERSION,
        "test_date": TEST_DATE,
        "services": SERVICES
    }


def run_service_health_check():
    print_header("第一部分: 服务健康检查")
    
    health_tests = [
        ("User Service", "/actuator/health"),
        ("Sample Service", "/actuator/health"),
        ("Report Service", "/actuator/health"),
        ("HL7 Service", "/actuator/health"),
        ("AI Service", "/actuator/health")
    ]
    
    for service, endpoint in health_tests:
        result = test_endpoint(
            service, "GET", endpoint,
            expected_status=200,
            test_name=f"{service} 健康检查",
            note="服务健康检查",
            priority="high"
        )
        print_test_result(
            len(test_results),
            result["test_name"],
            result["status"],
            result.get("actual_status"),
            result.get("response_time_ms")
        )


def run_user_service_tests():
    print_header("第二部分: 用户服务测试 (重点)")
    
    # 【重点测试1】登录接口 - 空参数验证 (期望HTTP 400)
    print("\n【重点测试1】登录接口空参数验证 (期望HTTP 400)")
    
    # 测试1: 登录接口 - 空参数
    result = test_endpoint(
        "User Service", "POST", "/user/login",
        form_data={},
        expected_status=400,
        test_name="登录接口 - 空参数验证",
        note="重点测试: 空登录参数应返回HTTP 400",
        priority="high"
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
        test_name="登录接口 - 缺少用户名",
        note="缺少用户名参数验证",
        priority="high"
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
        test_name="登录接口 - 缺少密码",
        note="缺少密码参数验证",
        priority="high"
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
        test_name="登录接口 - 正常登录",
        note="正常登录测试",
        priority="high"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )
    
    # 测试5: 获取用户列表
    result = test_endpoint(
        "User Service", "GET", "/user/list",
        expected_status=200,
        test_name="用户服务 - 获取用户列表",
        note="获取所有用户",
        priority="medium"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )


def run_sample_service_tests():
    print_header("第三部分: 标本服务测试 (重点)")
    
    # 测试1: 标本列表
    result = test_endpoint(
        "Sample Service", "GET", "/sample/list",
        expected_status=200,
        test_name="标本服务 - 获取标本列表",
        note="获取所有标本",
        priority="medium"
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
            note=f"重点测试: 查询状态为 {status} 的标本",
            priority="high"
        )
        print_test_result(
            len(test_results),
            result["test_name"],
            result["status"],
            result.get("actual_status"),
            result.get("response_time_ms"),
            f"状态: {status}"
        )


def run_report_service_tests():
    print_header("第四部分: 报告服务测试")
    
    result = test_endpoint(
        "Report Service", "GET", "/report/list",
        expected_status=200,
        test_name="报告服务 - 获取报告列表",
        note="获取所有报告",
        priority="medium"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )


def run_ai_service_tests():
    print_header("第五部分: AI服务测试")
    
    result = test_endpoint(
        "AI Service", "GET", "/ai/health",
        expected_status=200,
        test_name="AI服务 - 健康检查",
        note="AI服务健康检查",
        priority="medium"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )
    
    # AI诊断测试
    result = test_endpoint(
        "AI Service", "POST", "/ai/diagnose",
        json_data={"testItems": [{"name": "白细胞计数", "value": "6.5", "unit": "×10⁹/L", "reference": "4.0-10.0"}]},
        expected_status=200,
        test_name="AI服务 - 辅助诊断",
        note="测试AI辅助诊断功能",
        priority="medium"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )


def run_hl7_service_tests():
    print_header("第六部分: HL7服务测试")
    
    result = test_endpoint(
        "HL7 Service", "POST", "/hl7/parse",
        json_data={"message": "MSH|^~\\&|LIS|HIS|202604021200||ORM^O01|123|P|2.3.1"},
        expected_status=200,
        test_name="HL7服务 - 解析HL7消息",
        note="测试HL7消息解析",
        priority="medium"
    )
    print_test_result(
        len(test_results),
        result["test_name"],
        result["status"],
        result.get("actual_status"),
        result.get("response_time_ms")
    )


def calculate_performance_metrics():
    """计算性能指标"""
    if not test_results:
        return {}
    
    response_times = [r.get("response_time_ms", 0) for r in test_results if r.get("response_time_ms")]
    
    if not response_times:
        return {}
    
    response_times_sorted = sorted(response_times)
    n = len(response_times_sorted)
    
    return {
        "avg_response_time": round(sum(response_times) / n, 2),
        "min_response_time": round(min(response_times), 2),
        "max_response_time": round(max(response_times), 2),
        "p50_response_time": round(response_times_sorted[int(n * 0.5)] if n > 0 else 0, 2),
        "p90_response_time": round(response_times_sorted[int(n * 0.9)] if n > 9 else max(response_times), 2),
        "p95_response_time": round(response_times_sorted[int(n * 0.95)] if n > 19 else max(response_times), 2),
        "p99_response_time": round(response_times_sorted[int(n * 0.99)] if n > 99 else max(response_times), 2)
    }


def generate_report():
    print_header("生成测试报告")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r["status"] == "PASS")
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    performance_metrics = calculate_performance_metrics()
    env_info = get_environment_info()
    
    # 生成Markdown报告
    report_content = []
    report_content.append("# 实验室管理系统 - 完整回归测试报告\n")
    report_content.append(f"**测试版本**: {TEST_VERSION}\n")
    report_content.append(f"**测试时间**: {TEST_DATE}\n\n")
    
    # 测试摘要
    report_content.append("## 1. 测试摘要\n\n")
    report_content.append(f"- **总测试用例**: {total_tests}\n")
    report_content.append(f"- **通过**: {passed_tests} ({pass_rate:.1f}%)\n")
    report_content.append(f"- **失败**: {failed_tests}\n\n")
    
    # 测试范围
    report_content.append("## 2. 测试范围\n\n")
    report_content.append("### 2.1 重点测试项\n")
    report_content.append("- ✅ 登录接口空参数验证 (期望HTTP 400)\n")
    report_content.append("- ✅ 标本按状态查询接口 (期望HTTP 200)\n\n")
    report_content.append("### 2.2 测试服务\n")
    report_content.append("- 用户服务 (User Service)\n")
    report_content.append("- 标本服务 (Sample Service)\n")
    report_content.append("- 报告服务 (Report Service)\n")
    report_content.append("- AI服务 (AI Service)\n")
    report_content.append("- HL7服务 (HL7 Service)\n\n")
    
    # 测试环境
    report_content.append("## 3. 测试环境\n\n")
    report_content.append("| 项 | 值 |\n")
    report_content.append("|----|-----|\n")
    report_content.append(f"| 操作系统 | {env_info['os']} |\n")
    report_content.append(f"| Python版本 | {env_info['python_version'].split()[0]} |\n")
    report_content.append(f"| 测试版本 | {env_info['test_version']} |\n")
    report_content.append(f"| 测试日期 | {env_info['test_date']} |\n\n")
    
    report_content.append("### 3.1 服务配置\n\n")
    report_content.append("| 服务 | 地址 |\n")
    report_content.append("|------|------|\n")
    for service, url in SERVICES.items():
        report_content.append(f"| {service} | {url} |\n")
    
    # 重点测试结果
    report_content.append("\n## 4. 重点测试结果\n\n")
    
    report_content.append("### 4.1 登录接口空参数验证\n")
    login_test = next((r for r in test_results if "空参数验证" in r["test_name"]), None)
    if login_test:
        report_content.append(f"- **测试名称**: {login_test['test_name']}\n")
        report_content.append(f"- **期望状态码**: {login_test['expected_status']}\n")
        report_content.append(f"- **实际状态码**: {login_test.get('actual_status', 'N/A')}\n")
        report_content.append(f"- **测试结果**: {login_test['status']}\n")
        report_content.append(f"- **响应时间**: {login_test.get('response_time_ms', 'N/A')}ms\n")
        if "response_body" in login_test:
            report_content.append(f"- **响应内容**: {login_test['response_body']}\n")
    
    report_content.append("\n### 4.2 标本按状态查询接口\n")
    status_tests = [r for r in test_results if "按状态查询" in r["test_name"]]
    for test in status_tests:
        report_content.append(f"- **{test['test_name']}**: {test['status']} (状态码: {test.get('actual_status', 'N/A')}, 响应时间: {test.get('response_time_ms', 'N/A')}ms)\n")
    
    # 缺陷清单
    report_content.append("\n## 5. 缺陷清单\n\n")
    if defect_list:
        report_content.append("| 缺陷ID | 测试名称 | 服务 | 端点 | 期望状态 | 实际状态 | 优先级 | 描述 |\n")
        report_content.append("|--------|---------|------|------|---------|---------|--------|------|\n")
        for defect in defect_list:
            report_content.append(f"| {defect['defect_id']} | {defect['test_name']} | {defect['service']} | {defect['endpoint']} | {defect['expected_status']} | {defect['actual_status']} | {defect['priority']} | {defect['description']} |\n")
    else:
        report_content.append("✅ **无缺陷发现**\n")
    
    # 性能指标
    report_content.append("\n## 6. 性能指标\n\n")
    if performance_metrics:
        report_content.append("| 指标 | 值 |\n")
        report_content.append("|------|-----|\n")
        report_content.append(f"| 平均响应时间 | {performance_metrics.get('avg_response_time', 'N/A')}ms |\n")
        report_content.append(f"| 最小响应时间 | {performance_metrics.get('min_response_time', 'N/A')}ms |\n")
        report_content.append(f"| 最大响应时间 | {performance_metrics.get('max_response_time', 'N/A')}ms |\n")
        report_content.append(f"| P50响应时间 | {performance_metrics.get('p50_response_time', 'N/A')}ms |\n")
        report_content.append(f"| P90响应时间 | {performance_metrics.get('p90_response_time', 'N/A')}ms |\n")
        report_content.append(f"| P95响应时间 | {performance_metrics.get('p95_response_time', 'N/A')}ms |\n")
        report_content.append(f"| P99响应时间 | {performance_metrics.get('p99_response_time', 'N/A')}ms |\n")
    else:
        report_content.append("暂无性能数据\n")
    
    # 详细测试结果
    report_content.append("\n## 7. 详细测试结果\n\n")
    report_content.append("| 序号 | 测试名称 | 服务 | 方法 | 端点 | 期望 | 实际 | 结果 | 响应时间(ms) | 优先级 |\n")
    report_content.append("|------|---------|------|------|------|------|------|------|-------------|--------|\n")
    
    for idx, result in enumerate(test_results, 1):
        expected = result['expected_status']
        actual = result.get('actual_status', 'N/A')
        rt = result.get('response_time_ms', 'N/A')
        report_content.append(f"| {idx} | {result['test_name']} | {result['service']} | {result['method']} | {result['endpoint']} | {expected} | {actual} | {result['status']} | {rt} | {result['priority']} |\n")
    
    # 保存报告
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_content))
    
    # 保存JSON结果
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "test_version": TEST_VERSION,
            "test_date": TEST_DATE,
            "environment": env_info,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": pass_rate,
            "performance_metrics": performance_metrics,
            "defects": defect_list,
            "results": test_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 测试报告已生成: {REPORT_FILE}")
    print(f"✅ JSON结果已保存: {RESULTS_FILE}")
    print(f"\n📊 测试统计: {passed_tests}/{total_tests} 通过 ({pass_rate:.1f}%)")
    
    return passed_tests, failed_tests, total_tests


def run_tests():
    print_header("实验室管理系统 - 完整回归测试 v1.5.0")
    print(f"测试开始时间: {TEST_DATE}")
    
    # 1. 服务健康检查
    run_service_health_check()
    
    # 2. 用户服务测试
    run_user_service_tests()
    
    # 3. 标本服务测试
    run_sample_service_tests()
    
    # 4. 报告服务测试
    run_report_service_tests()
    
    # 5. AI服务测试
    run_ai_service_tests()
    
    # 6. HL7服务测试
    run_hl7_service_tests()


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
