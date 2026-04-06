#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 - 性能基准测试 v1.3.0
任务2.3: 性能基准测试
执行时间: 2026-04-02

测试内容:
- A1. API响应时间基准测试 (P50/P95/P99)
- A2. 前端页面加载性能测试
- A3. 并发能力测试 (5并发)
"""

import requests
import time
import statistics
import concurrent.futures
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any

# ==================== 配置 ====================
GATEWAY_URL = "http://localhost:8080"
FRONTEND_URLS = {
    "登录页": "http://localhost:3001/login",
    "仪表盘": "http://localhost:3001/",
    "标本列表": "http://localhost:3001/sample",
    "报告列表": "http://localhost:3001/report",
    "AI诊断": "http://localhost:3001/ai",
    "用户管理": "http://localhost:3001/user"
}

API_ENDPOINTS = [
    ('GET', f'{GATEWAY_URL}/api/user/list'),
    ('GET', f'{GATEWAY_URL}/api/sample/list'),
    ('GET', f'{GATEWAY_URL}/api/report/list'),
    ('GET', f'{GATEWAY_URL}/api/ai/health'),
]

TEST_ITERATIONS = 10  # 每个接口测试次数
CONCURRENT_USERS = 5  # 并发用户数
TIMEOUT_SECONDS = 10  # 超时时间(秒)

# ==================== 工具函数 ====================
def calculate_percentile(data: List[float], percentile: float) -> float:
    """计算百分位数"""
    if not data:
        return 0.0
    sorted_data = sorted([x for x in data if x > 0])
    if not sorted_data:
        return 0.0
    index = int(len(sorted_data) * percentile / 100)
    index = min(index, len(sorted_data) - 1)
    return sorted_data[index]

def test_api_endpoint(method: str, url: str, iterations: int = TEST_ITERATIONS) -> Dict[str, Any]:
    """
    测试单个API端点的响应时间
    返回包含P50/P95/P99/平均响应时间等指标的字典
    """
    times = []
    status_codes = []
    errors = []

    for i in range(iterations):
        try:
            start_time = time.time()
            if method == 'GET':
                response = requests.get(url, timeout=TIMEOUT_SECONDS)
            elif method == 'POST':
                response = requests.post(url, json={}, timeout=TIMEOUT_SECONDS)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            elapsed_ms = (time.time() - start_time) * 1000
            times.append(elapsed_ms)
            status_codes.append(response.status_code)

        except requests.exceptions.Timeout:
            times.append(-1)
            status_codes.append(0)
            errors.append(f"请求超时 (>{TIMEOUT_SECONDS}s)")
        except requests.exceptions.ConnectionError as e:
            times.append(-1)
            status_codes.append(0)
            errors.append(f"连接失败: {str(e)[:50]}")
        except Exception as e:
            times.append(-1)
            status_codes.append(0)
            errors.append(f"未知错误: {str(e)[:50]}")

    # 计算统计指标
    valid_times = [t for t in times if t > 0]
    success_count = len(valid_times)

    result = {
        'endpoint': url,
        'method': method,
        'total_requests': iterations,
        'success_count': success_count,
        'success_rate': round(success_count / iterations * 100, 2) if iterations > 0 else 0,
        'p50_ms': round(calculate_percentile(valid_times, 50), 2),
        'p95_ms': round(calculate_percentile(valid_times, 95), 2),
        'p99_ms': round(calculate_percentile(valid_times, 99), 2),
        'avg_ms': round(sum(valid_times) / len(valid_times), 2) if valid_times else 0,
        'min_ms': round(min(valid_times), 2) if valid_times else 0,
        'max_ms': round(max(valid_times), 2) if valid_times else 0,
        'status_codes': list(set(status_codes)),
        'errors': errors[:3]  # 只保留前3个错误
    }

    return result

def test_page_load(url: str) -> Dict[str, Any]:
    """
    测试前端页面加载时间
    """
    try:
        start_time = time.time()
        response = requests.get(url, timeout=30)
        elapsed_ms = (time.time() - start_time) * 1000

        return {
            'url': url,
            'status_code': response.status_code,
            'load_time_ms': round(elapsed_ms, 2),
            'content_size_bytes': len(response.content),
            'success': response.status_code == 200,
            'error': None
        }
    except Exception as e:
        return {
            'url': url,
            'status_code': 0,
            'load_time_ms': -1,
            'content_size_bytes': 0,
            'success': False,
            'error': str(e)[:100]
        }

def concurrent_request_worker(url: str) -> Dict[str, Any]:
    """
    并发请求工作函数
    """
    try:
        start_time = time.time()
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        elapsed_ms = (time.time() - start_time) * 1000

        return {
            'time_ms': round(elapsed_ms, 2),
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'error': None
        }
    except Exception as e:
        return {
            'time_ms': -1,
            'status_code': 0,
            'success': False,
            'error': str(e)[:100]
        }

def test_concurrent_requests(url: str, num_users: int = CONCURRENT_USERS) -> Dict[str, Any]:
    """
    测试并发请求能力
    """
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(concurrent_request_worker, url) for _ in range(num_users)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    # 统计结果
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    response_times = [r['time_ms'] for r in successful if r['time_ms'] > 0]

    return {
        'endpoint': url,
        'concurrent_users': num_users,
        'total_requests': len(results),
        'successful_requests': len(successful),
        'failed_requests': len(failed),
        'success_rate': round(len(successful) / len(results) * 100, 2) if results else 0,
        'avg_response_time_ms': round(sum(response_times) / len(response_times), 2) if response_times else 0,
        'min_response_time_ms': round(min(response_times), 2) if response_times else 0,
        'max_response_time_ms': round(max(response_times), 2) if response_times else 0,
        'errors': [r['error'] for r in failed if r['error']][:3]
    }

# ==================== 主测试流程 ====================
def run_performance_tests():
    """
    执行所有性能测试
    """
    print("=" * 80)
    print("实验室管理系统 - 性能基准测试 v1.3.0")
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    test_results = {
        'test_version': 'v1.3.0',
        'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'environment': {
            'gateway_url': GATEWAY_URL,
            'frontend_base_url': 'http://localhost:3001',
            'test_iterations': TEST_ITERATIONS,
            'concurrent_users': CONCURRENT_USERS,
            'timeout_seconds': TIMEOUT_SECONDS
        },
        'results': {}
    }

    # ===== A1. API响应时间测试 =====
    print("\n" + "=" * 80)
    print("A1. API响应时间基准测试 (P50/P95/P99)")
    print("=" * 80)

    api_results = []
    for method, url in API_ENDPOINTS:
        print(f"\n测试: {method} {url}")
        result = test_api_endpoint(method, url)
        api_results.append(result)

        print(f"  成功率: {result['success_rate']}% ({result['success_count']}/{result['total_requests']})")
        print(f"  P50: {result['p50_ms']}ms | P95: {result['p95_ms']}ms | P99: {result['p99_ms']}ms")
        print(f"  平均: {result['avg_ms']}ms | 最小: {result['min_ms']}ms | 最大: {result['max_ms']}ms")

        if result['errors']:
            print(f"  错误: {result['errors'][0]}")

    test_results['results']['api_response_time'] = api_results

    # ===== A2. 页面加载性能测试 =====
    print("\n" + "=" * 80)
    print("A2. 前端页面加载性能测试")
    print("=" * 80)

    page_results = []
    for page_name, url in FRONTEND_URLS.items():
        print(f"\n测试: {page_name} - {url}")
        result = test_page_load(url)
        result['page_name'] = page_name
        page_results.append(result)

        status = "成功" if result['success'] else "失败"
        print(f"  状态: {status} (HTTP {result['status_code']})")
        print(f"  加载时间: {result['load_time_ms']}ms")
        print(f"  页面大小: {result['content_size_bytes']} bytes")

        if result['error']:
            print(f"  错误: {result['error']}")

    test_results['results']['page_load_time'] = page_results

    # ===== A3. 并发能力测试 =====
    print("\n" + "=" * 80)
    print("A3. 并发能力测试 (5并发)")
    print("=" * 80)

    concurrency_test_url = f'{GATEWAY_URL}/api/user/list'
    print(f"\n测试端点: {concurrency_test_url}")
    print(f"并发用户数: {CONCURRENT_USERS}")

    concurrency_result = test_concurrent_requests(concurrency_test_url, CONCURRENT_USERS)
    test_results['results']['concurrency_test'] = concurrency_result

    print(f"\n总请求数: {concurrency_result['total_requests']}")
    print(f"成功请求: {concurrency_result['successful_requests']}")
    print(f"失败请求: {concurrency_result['failed_requests']}")
    print(f"成功率: {concurrency_result['success_rate']}%")
    print(f"平均响应时间: {concurrency_result['avg_response_time_ms']}ms")
    print(f"最小响应时间: {concurrency_result['min_response_time_ms']}ms")
    print(f"最大响应时间: {concurrency_result['max_response_time_ms']}ms")

    if concurrency_result['errors']:
        print(f"错误信息: {concurrency_result['errors'][0]}")

    # ===== 性能目标验证 =====
    print("\n" + "=" * 80)
    print("性能目标验证")
    print("=" * 80)

    performance_targets = []
    all_api_p50_pass = True
    all_api_p95_pass = True
    all_page_load_pass = True
    concurrency_pass = True

    # 检查API P50 < 200ms
    for api_result in api_results:
        p50_pass = api_result['p50_ms'] < 200 if api_result['p50_ms'] > 0 else False
        p95_pass = api_result['p95_ms'] < 500 if api_result['p95_ms'] > 0 else False

        performance_targets.append({
            'metric': f"API P50 < 200ms - {api_result['endpoint']}",
            'target': '< 200ms',
            'actual': f"{api_result['p50_ms']}ms",
            'passed': p50_pass,
            'severity': 'High'
        })

        performance_targets.append({
            'metric': f"API P95 < 500ms - {api_result['endpoint']}",
            'target': '< 500ms',
            'actual': f"{api_result['p95_ms']}ms",
            'passed': p95_pass,
            'severity': 'High'
        })

        if not p50_pass:
            all_api_p50_pass = False
        if not p95_pass:
            all_api_p95_pass = False

    # 检查页面加载 < 2s
    for page_result in page_results:
        load_pass = page_result['load_time_ms'] < 2000 if page_result['load_time_ms'] > 0 else False

        performance_targets.append({
            'metric': f"页面加载 < 2s - {page_result['page_name']}",
            'target': '< 2000ms',
            'actual': f"{page_result['load_time_ms']}ms",
            'passed': load_pass,
            'severity': 'Medium'
        })

        if not load_pass:
            all_page_load_pass = False

    # 检查并发无错误
    concurrency_pass = concurrency_result['success_rate'] == 100
    performance_targets.append({
        'metric': f"5并发无错误 - {concurrency_result['endpoint']}",
            'target': '100%',
            'actual': f"{concurrency_result['success_rate']}%",
            'passed': concurrency_pass,
            'severity': 'Critical'
        })

    test_results['results']['performance_targets'] = performance_targets
    test_results['summary'] = {
        'all_api_p50_pass': all_api_p50_pass,
        'all_api_p95_pass': all_api_p95_pass,
        'all_page_load_pass': all_page_load_pass,
        'concurrency_pass': concurrency_pass,
        'overall_status': 'PASS' if (all_api_p50_pass and all_api_p95_pass and all_page_load_pass and concurrency_pass) else 'FAIL'
    }

    # 打印目标验证表格
    print("\n{:<50} {:<15} {:<15} {:<10}".format(
        "指标", "目标值", "实际值", "状态"))
    print("-" * 90)
    for target in performance_targets:
        status_icon = "✓ PASS" if target['passed'] else "✗ FAIL"
        print("{:<50} {:<15} {:<15} {:<10}".format(
            target['metric'][:48],
            target['target'],
            target['actual'],
            status_icon
        ))

    print("\n" + "=" * 80)
    print(f"总体评估: {test_results['summary']['overall_status']}")
    print("=" * 80)

    return test_results

if __name__ == '__main__':
    # 执行测试
    results = run_performance_tests()

    # 保存结果到JSON文件
    output_file = r'd:\FinalCodeAndFile\lab-management-system\test_results\performance-benchmark-results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n测试结果已保存至: {output_file}")
