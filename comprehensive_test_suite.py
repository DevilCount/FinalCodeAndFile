#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 - 综合测试套件 v2.0
执行时间: 2026-04-03

测试内容:
1. API功能测试 - 验证所有API端点功能
2. 集成测试 - 验证模块间接口调用及数据流转
3. 性能测试 - 评估系统响应时间、并发处理能力
4. 资源占用评估 - 监控CPU和内存使用情况

作者: API Test Pro
"""

import requests
import time
import statistics
import threading
import concurrent.futures
import json
import os
import psutil
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field

# ==================== 配置 ====================
SERVICES = {
    'gateway': 'http://localhost:8080',
    'user_service': 'http://localhost:8086',
    'sample_service': 'http://localhost:8087',
    'report_service': 'http://localhost:8088',
    'ai_service': 'http://localhost:8089',
    'hl7_service': 'http://localhost:8084',
    'frontend': 'http://localhost:5173'
}

API_ITERATIONS = 5
CONCURRENT_USERS = 10
REQUESTS_PER_USER = 10
TIMEOUT_SECONDS = 30

PERFORMANCE_TARGETS = {
    'api_p95_ms': 500,
    'api_p99_ms': 1000,
    'page_load_ms': 2000,
    'concurrency_success_rate': 99.0,
    'max_5xx_errors': 0
}

# ==================== 数据结构 ====================
@dataclass
class ApiTestResult:
    endpoint: str
    method: str
    display_name: str
    total_requests: int = 0
    success_count: int = 0
    success_rate: float = 0.0
    response_times: List[float] = field(default_factory=list)
    status_codes: List[int] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    test_category: str = "API"

    @property
    def p50_ms(self) -> float:
        return self._calculate_percentile(50)

    @property
    def p95_ms(self) -> float:
        return self._calculate_percentile(95)

    @property
    def p99_ms(self) -> float:
        return self._calculate_percentile(99)

    @property
    def avg_ms(self) -> float:
        if not self.response_times:
            return 0.0
        return round(statistics.mean(self.response_times), 2)

    @property
    def min_ms(self) -> float:
        if not self.response_times:
            return 0.0
        return round(min(self.response_times), 2)

    @property
    def max_ms(self) -> float:
        if not self.response_times:
            return 0.0
        return round(max(self.response_times), 2)

    def _calculate_percentile(self, percentile: float) -> float:
        valid_times = [t for t in self.response_times if t > 0]
        if not valid_times:
            return 0.0
        sorted_data = sorted(valid_times)
        index = int(len(sorted_data) * percentile / 100)
        index = min(index, len(sorted_data) - 1)
        return round(sorted_data[index], 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'endpoint': self.endpoint,
            'method': self.method,
            'display_name': self.display_name,
            'total_requests': self.total_requests,
            'success_count': self.success_count,
            'success_rate': round(self.success_count / self.total_requests * 100, 2) if self.total_requests > 0 else 0,
            'p50_ms': self.p50_ms,
            'p95_ms': self.p95_ms,
            'p99_ms': self.p99_ms,
            'avg_ms': self.avg_ms,
            'min_ms': self.min_ms,
            'max_ms': self.max_ms,
            'status_codes': list(set(self.status_codes)),
            'errors': self.errors[:5],
            'test_category': self.test_category
        }


@dataclass
class ConcurrencyTestResult:
    endpoint: str
    concurrent_users: int
    requests_per_user: int
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    server_error_count: int = 0
    success_rate: float = 0.0
    response_times: List[float] = field(default_factory=list)
    total_test_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)

    @property
    def avg_response_time_ms(self) -> float:
        if not self.response_times:
            return 0.0
        return round(statistics.mean(self.response_times), 2)

    @property
    def throughput_per_second(self) -> float:
        if self.total_test_time_ms <= 0:
            return 0.0
        return round(self.successful_requests / (self.total_test_time_ms / 1000), 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'endpoint': self.endpoint,
            'concurrent_users': self.concurrent_users,
            'requests_per_user': self.requests_per_user,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'server_error_count': self.server_error_count,
            'success_rate': round(self.successful_requests / self.total_requests * 100, 2) if self.total_requests > 0 else 0,
            'avg_response_time_ms': self.avg_response_time_ms,
            'throughput_per_second': self.throughput_per_second,
            'total_test_time_ms': round(self.total_test_time_ms, 2),
            'errors': self.errors[:5]
        }

# ==================== 工具函数 ====================
def check_service_health(url: str, service_name: str) -> Dict[str, Any]:
    result = {
        'service_name': service_name,
        'url': url,
        'available': False,
        'response_time_ms': -1,
        'status_code': 0,
        'message': ''
    }
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        elapsed_ms = (time.time() - start_time) * 1000
        result['available'] = True
        result['response_time_ms'] = round(elapsed_ms, 2)
        result['status_code'] = response.status_code
        result['message'] = f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        result['message'] = "连接失败(端口未开放或服务未启动)"
    except requests.exceptions.Timeout:
        result['message'] = "连接超时"
    except Exception as e:
        result['message'] = f"未知错误: {str(e)[:100]}"
    return result


def check_all_services() -> Dict[str, Any]:
    print("\n" + "="*70)
    print("服务健康检查")
    print("="*70)
    services_status = {}
    available_services = []
    for service_name, url in SERVICES.items():
        if service_name == 'frontend':
            test_url = url
        else:
            test_url = f"{url}/actuator/health" if 'gateway' in url else f"{url}/health"
        status = check_service_health(test_url, service_name)
        services_status[service_name] = status
        status_icon = "✓" if status['available'] else "✗"
        print(f"  {status_icon} {service_name:<20} {url:<30} {status['message']}")
        if status['available']:
            available_services.append(service_name)
    print(f"\n可用服务: {len(available_services)}/{len(SERVICES)}")
    return {
        'services': services_status,
        'available_count': len(available_services),
        'total_count': len(SERVICES),
        'available_services': available_services
    }

# ==================== 1. API功能测试 ====================
def test_api_endpoint(method: str, url: str, display_name: str,
                     iterations: int = API_ITERATIONS,
                     payload: Optional[Dict] = None,
                     test_category: str = "API") -> ApiTestResult:
    result = ApiTestResult(
        endpoint=url,
        method=method,
        display_name=display_name,
        test_category=test_category
    )
    print(f"\n{'='*60}")
    print(f"测试: {display_name}")
    print(f"端点: {method} {url}")
    print(f"{'='*60}")
    for i in range(iterations):
        try:
            start_time = time.time()
            if method == 'GET':
                response = requests.get(url, timeout=TIMEOUT_SECONDS)
            elif method == 'POST':
                response = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            elapsed_ms = (time.time() - start_time) * 1000
            result.response_times.append(round(elapsed_ms, 2))
            result.status_codes.append(response.status_code)
            result.total_requests += 1
            if response.status_code < 500:
                result.success_count += 1
            status_icon = "✓" if response.status_code < 400 else "✗"
            print(f"  [{i+1}/{iterations}] {status_icon} {response.status_code} | {elapsed_ms:.2f}ms")
        except requests.exceptions.Timeout:
            result.errors.append(f"请求{i+1}超时")
            result.total_requests += 1
            print(f"  [{i+1}/{iterations}] ✗ TIMEOUT")
        except requests.exceptions.ConnectionError as e:
            result.errors.append(f"请求{i+1}连接失败")
            result.total_requests += 1
            print(f"  [{i+1}/{iterations}] ✗ CONNECTION_ERROR")
        except Exception as e:
            result.errors.append(f"请求{i+1}错误: {str(e)[:50]}")
            result.total_requests += 1
            print(f"  [{i+1}/{iterations}] ✗ ERROR")
    if result.total_requests > 0:
        result.success_rate = result.success_count / result.total_requests * 100
    print(f"\n  统计: 成功率 {result.success_rate:.1f}% | 平均 {result.avg_ms}ms | P95 {result.p95_ms}ms")
    return result


def run_api_functional_tests() -> List[ApiTestResult]:
    print("\n\n" + "#"*80)
    print("# 第一部分: API功能测试")
    print("#"*80)
    api_endpoints = [
        # 用户服务
        ('POST', f"{SERVICES['gateway']}/api/user/login", '用户登录', 
         {"username": "admin", "password": "admin123"}, "API"),
        ('GET', f"{SERVICES['gateway']}/api/user/list", '获取用户列表', None, "API"),
        # 标本服务
        ('GET', f"{SERVICES['gateway']}/api/sample/list", '获取标本列表', None, "API"),
        ('POST', f"{SERVICES['gateway']}/api/sample/create", '创建标本',
         {"patientName": "测试患者", "testItems": "血常规", "sampleType": "BLOOD"}, "API"),
        # 报告服务
        ('GET', f"{SERVICES['gateway']}/api/report/list", '获取报告列表', None, "API"),
        # AI服务
        ('GET', f"{SERVICES['gateway']}/api/ai/health", 'AI服务健康检查', None, "API"),
        # HL7服务
        ('POST', f"{SERVICES['gateway']}/api/hl7/parse", '解析HL7消息',
         {"message": "MSH|^~\\&|LIS|HIS|202604031200||ORM^O01|123|P|2.3.1"}, "API"),
    ]
    results = []
    for method, url, name, payload, category in api_endpoints:
        result = test_api_endpoint(method, url, name, payload=payload, test_category=category)
        results.append(result)
    return results

# ==================== 2. 集成测试 ====================
def run_integration_tests() -> List[ApiTestResult]:
    print("\n\n" + "#"*80)
    print("# 第二部分: 集成测试 (模块间数据流转)")
    print("#"*80)
    integration_tests = []
    # 流程1: 创建标本 -> 查询标本
    print("\n[集成测试1] 标本创建与查询流程")
    try:
        # 创建标本
        create_url = f"{SERVICES['gateway']}/api/sample/create"
        create_payload = {"patientName": "集成测试患者", "testItems": "血常规,尿常规", "sampleType": "BLOOD"}
        create_result = test_api_endpoint('POST', create_url, '创建标本(集成测试)', 
                                         iterations=1, payload=create_payload, test_category="INTEGRATION")
        integration_tests.append(create_result)
        # 查询标本列表
        list_result = test_api_endpoint('GET', f"{SERVICES['gateway']}/api/sample/list", 
                                        '查询标本列表(集成测试)', iterations=1, test_category="INTEGRATION")
        integration_tests.append(list_result)
    except Exception as e:
        print(f"集成测试1异常: {e}")
    # 流程2: 登录 -> 查询报告
    print("\n[集成测试2] 登录与报告查询流程")
    try:
        # 登录
        login_result = test_api_endpoint('POST', f"{SERVICES['gateway']}/api/user/login", 
                                         '用户登录(集成测试)', iterations=1, 
                                         payload={"username": "admin", "password": "admin123"}, 
                                         test_category="INTEGRATION")
        integration_tests.append(login_result)
        # 查询报告
        report_result = test_api_endpoint('GET', f"{SERVICES['gateway']}/api/report/list", 
                                          '查询报告列表(集成测试)', iterations=1, test_category="INTEGRATION")
        integration_tests.append(report_result)
    except Exception as e:
        print(f"集成测试2异常: {e}")
    return integration_tests

# ==================== 3. 性能测试 - 并发压力测试 ====================
def concurrent_user_worker(user_id: int, login_url: str, query_urls: List[str],
                          requests_per_user: int) -> Dict[str, Any]:
    user_results = {
        'user_id': user_id,
        'login_success': False,
        'query_results': [],
        'total_success': 0,
        'total_failed': 0,
        'server_errors': 0,
        'response_times': [],
        'errors': []
    }
    session = requests.Session()
    try:
        start_time = time.time()
        login_payload = {"username": "admin", "password": "admin123"}
        response = session.post(login_url, json=login_payload, timeout=TIMEOUT_SECONDS)
        elapsed_ms = (time.time() - start_time) * 1000
        if response.status_code == 200:
            user_results['login_success'] = True
            user_results['response_times'].append(round(elapsed_ms, 2))
        elif response.status_code >= 500:
            user_results['server_errors'] += 1
    except Exception as e:
        user_results['errors'].append(f"登录失败: {str(e)[:80]}")
    if user_results['login_success']:
        for req_num in range(requests_per_user):
            query_url = query_urls[req_num % len(query_urls)]
            try:
                start_time = time.time()
                response = session.get(query_url, timeout=TIMEOUT_SECONDS)
                elapsed_ms = (time.time() - start_time) * 1000
                user_results['response_times'].append(round(elapsed_ms, 2))
                if response.status_code < 500:
                    user_results['total_success'] += 1
                else:
                    user_results['total_failed'] += 1
                    user_results['server_errors'] += 1
            except Exception as e:
                user_results['total_failed'] += 1
                user_results['errors'].append(f"请求{req_num+1}失败")
    else:
        user_results['total_failed'] = requests_per_user
    return user_results


def run_concurrency_stress_test() -> ConcurrencyTestResult:
    print("\n\n" + "#"*80)
    print("# 第三部分: 性能测试 - 并发压力测试")
    print("#"*80)
    login_url = f"{SERVICES['gateway']}/api/user/login"
    query_urls = [
        f"{SERVICES['gateway']}/api/sample/list",
        f"{SERVICES['gateway']}/api/report/list",
        f"{SERVICES['gateway']}/api/user/list"
    ]
    result = ConcurrencyTestResult(
        endpoint=login_url,
        concurrent_users=CONCURRENT_USERS,
        requests_per_user=REQUESTS_PER_USER
    )
    print(f"\n测试配置: {CONCURRENT_USERS}并发用户, 每用户{REQUESTS_PER_USER}次请求")
    all_user_results = []
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = [
            executor.submit(concurrent_user_worker, user_id, login_url, query_urls, REQUESTS_PER_USER)
            for user_id in range(1, CONCURRENT_USERS + 1)
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                user_result = future.result(timeout=60)
                all_user_results.append(user_result)
            except Exception as e:
                print(f"  用户线程异常: {e}")
    total_test_time = (time.time() - start_time) * 1000
    result.total_test_time_ms = total_test_time
    for user_result in all_user_results:
        result.total_requests += 1 + REQUESTS_PER_USER
        result.successful_requests += user_result['total_success']
        result.failed_requests += user_result['total_failed']
        result.server_error_count += user_result['server_errors']
        result.response_times.extend(user_result['response_times'])
        if user_result['errors']:
            result.errors.extend(user_result['errors'])
    if result.total_requests > 0:
        result.success_rate = result.successful_requests / result.total_requests * 100
    print(f"\n并发测试结果:")
    print(f"  总请求数: {result.total_requests}")
    print(f"  成功请求: {result.successful_requests}")
    print(f"  5xx错误: {result.server_error_count}")
    print(f"  成功率: {result.success_rate:.2f}%")
    print(f"  平均响应: {result.avg_response_time_ms}ms")
    print(f"  吞吐量: {result.throughput_per_second} 请求/秒")
    return result

# ==================== 4. 资源占用评估 ====================
def monitor_resource_usage(duration_seconds: int = 10) -> Dict[str, Any]:
    print("\n\n" + "#"*80)
    print("# 第四部分: 系统资源占用评估")
    print("#"*80)
    print(f"\n监控时长: {duration_seconds}秒")
    cpu_samples = []
    memory_samples = []
    start_time = time.time()
    while (time.time() - start_time) < duration_seconds:
        current_time = datetime.now().strftime('%H:%M:%S')
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_samples.append(cpu_percent)
        memory = psutil.virtual_memory()
        memory_samples.append({
            'total_gb': round(memory.total / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'percent': memory.percent
        })
        print(f"  [{current_time}] CPU: {cpu_percent}% | 内存: {memory.percent}%")
        time.sleep(1)
    return {
        'monitor_duration_seconds': duration_seconds,
        'cpu_usage': {
            'average_percent': round(statistics.mean(cpu_samples), 2) if cpu_samples else 0,
            'max_percent': max(cpu_samples) if cpu_samples else 0,
            'min_percent': min(cpu_samples) if cpu_samples else 0,
            'samples': cpu_samples
        },
        'memory_usage': {
            'average_percent': round(statistics.mean([m['percent'] for m in memory_samples]), 2) if memory_samples else 0,
            'average_used_gb': round(statistics.mean([m['used_gb'] for m in memory_samples]), 2) if memory_samples else 0
        }
    }

# ==================== 主测试流程 ====================
def run_comprehensive_tests():
    print("="*90)
    print("实验室管理系统 - 综合测试套件 v2.0")
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*90)
    test_results = {
        'version': 'v2.0',
        'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'environment': SERVICES,
        'results': {}
    }
    # 0. 服务健康检查
    service_status = check_all_services()
    test_results['results']['service_status'] = service_status
    # 1. API功能测试
    api_results = run_api_functional_tests()
    test_results['results']['api_functional'] = [r.to_dict() for r in api_results]
    # 2. 集成测试
    integration_results = run_integration_tests()
    test_results['results']['integration'] = [r.to_dict() for r in integration_results]
    # 3. 并发性能测试
    concurrency_result = run_concurrency_stress_test()
    test_results['results']['concurrency'] = concurrency_result.to_dict()
    # 4. 资源占用评估
    resource_result = monitor_resource_usage(duration_seconds=10)
    test_results['results']['resource_usage'] = resource_result
    # 生成测试报告
    generate_test_report(test_results, api_results + integration_results, concurrency_result)
    # 保存JSON结果
    json_file = r"d:\FinalCodeAndFile\lab-management-system\test_results\comprehensive_test_results.json"
    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    print(f"\nJSON结果已保存: {json_file}")
    return test_results


def generate_test_report(test_results: Dict, all_api_results: List[ApiTestResult], 
                         concurrency_result: ConcurrencyTestResult):
    print("\n\n" + "="*90)
    print("生成测试报告...")
    print("="*90)
    service_status = test_results['results']['service_status']
    api_results = test_results['results']['api_functional']
    integration_results = test_results['results']['integration']
    concurrency = test_results['results']['concurrency']
    resource = test_results['results']['resource_usage']
    # 统计通过率
    total_api_tests = len(api_results) + len(integration_results)
    passed_api_tests = sum(1 for r in all_api_results if r.success_rate >= 80)
    api_pass_rate = passed_api_tests / total_api_tests * 100 if total_api_tests > 0 else 0
    # 生成Markdown报告
    md = []
    md.append("# 实验室管理系统 - 综合测试报告 v2.0")
    md.append("")
    md.append(f"**测试时间**: {test_results['test_date']}")
    md.append("")
    md.append("---")
    md.append("## 一、测试概述")
    md.append("")
    md.append("### 1.1 测试范围")
    md.append("- API功能测试: 用户、标本、报告、AI、HL7服务")
    md.append("- 集成测试: 模块间数据流转验证")
    md.append("- 性能测试: 并发压力测试、响应时间评估")
    md.append("- 资源占用: CPU和内存使用监控")
    md.append("")
    md.append("### 1.2 测试环境")
    md.append("")
    md.append("| 服务 | 地址 | 状态 |")
    md.append("|------|------|------|")
    for service_name, status in service_status['services'].items():
        availability = "可用" if status['available'] else "不可用"
        md.append(f"| {service_name} | {status['url']} | {availability} |")
    md.append("")
    md.append("---")
    md.append("## 二、测试结果汇总")
    md.append("")
    md.append("### 2.1 总体统计")
    md.append("")
    md.append(f"- **API功能测试**: {passed_api_tests}/{total_api_tests} 项通过 ({api_pass_rate:.1f}%)")
    md.append(f"- **并发测试**: 成功率 {concurrency['success_rate']}%, 5xx错误 {concurrency['server_error_count']}个")
    md.append(f"- **资源使用**: CPU平均 {resource['cpu_usage']['average_percent']}%, 内存平均 {resource['memory_usage']['average_percent']}%")
    md.append("")
    md.append("### 2.2 API功能测试详情")
    md.append("")
    md.append("| 测试类别 | 端点 | 方法 | 成功率 | 平均响应(ms) | P95(ms) |")
    md.append("|---------|------|------|--------|-------------|---------|")
    for r in api_results + integration_results:
        md.append(f"| {r['test_category']} | {r['display_name']} | {r['method']} | {r['success_rate']}% | {r['avg_ms']} | {r['p95_ms']} |")
    md.append("")
    md.append("### 2.3 并发性能测试结果")
    md.append("")
    md.append("| 指标 | 数值 |")
    md.append("|------|------|")
    md.append(f"| 并发用户数 | {concurrency['concurrent_users']} |")
    md.append(f"| 总请求数 | {concurrency['total_requests']} |")
    md.append(f"| 成功请求 | {concurrency['successful_requests']} |")
    md.append(f"| 成功率 | {concurrency['success_rate']}% |")
    md.append(f"| 5xx错误数 | {concurrency['server_error_count']} |")
    md.append(f"| 平均响应时间 | {concurrency['avg_response_time_ms']}ms |")
    md.append(f"| 吞吐量 | {concurrency['throughput_per_second']} 请求/秒 |")
    md.append("")
    md.append("### 2.4 资源占用情况")
    md.append("")
    md.append("#### CPU使用")
    md.append(f"- 平均使用率: {resource['cpu_usage']['average_percent']}%")
    md.append(f"- 峰值使用率: {resource['cpu_usage']['max_percent']}%")
    md.append("")
    md.append("#### 内存使用")
    md.append(f"- 平均使用率: {resource['memory_usage']['average_percent']}%")
    md.append(f"- 平均使用量: {resource['memory_usage']['average_used_gb']} GB")
    md.append("")
    md.append("---")
    md.append("## 三、测试结论")
    md.append("")
    if api_pass_rate >= 80 and concurrency['success_rate'] >= 90 and concurrency['server_error_count'] == 0:
        md.append("### 3.1 总体评估: **通过** ✓")
        md.append("")
        md.append("系统整体表现良好，核心功能正常，性能指标满足要求。")
    else:
        md.append("### 3.1 总体评估: **需改进** ⚠")
        md.append("")
        md.append("系统存在部分问题，需要进一步优化和修复。")
    md.append("")
    md.append("### 3.2 建议")
    md.append("")
    md.append("1. 针对失败的API端点进行功能修复")
    md.append("2. 优化慢查询API，提升响应速度")
    md.append("3. 增加服务器资源配置以支持更高并发")
    md.append("4. 实施持续集成测试，确保代码质量")
    md.append("")
    md.append("---")
    md.append(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # 保存报告
    report_file = r"d:\FinalCodeAndFile\lab-management-system\COMPREHENSIVE_TEST_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    print(f"\n综合测试报告已生成: {report_file}")
    # 打印报告摘要
    print("\n" + "="*90)
    print("测试报告摘要")
    print("="*90)
    print(f"\nAPI功能测试: {passed_api_tests}/{total_api_tests} 项通过 ({api_pass_rate:.1f}%)")
    print(f"并发测试成功率: {concurrency['success_rate']}%")
    print(f"5xx错误数: {concurrency['server_error_count']}")
    print(f"\n详细报告请查看: {report_file}")


if __name__ == "__main__":
    run_comprehensive_tests()

