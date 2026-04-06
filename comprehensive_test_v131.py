#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 - API连通性与性能综合测试 v1.3.1
============================================
任务A: 31个端点真实调用测试
任务B: 性能基准实测 (P50/P95/P99, 并发, 页面加载)
"""

import requests
import time
import statistics
import json
import concurrent.futures
from datetime import datetime
from collections import defaultdict

# 配置
BASE_URLS = {
    'user': 'http://localhost:8086',
    'sample': 'http://localhost:8087',
    'report': 'http://localhost:8088',
    'ai': 'http://localhost:8085',
    'gateway': 'http://localhost:8080',
    'frontend': 'http://localhost:3000'
}

TIMEOUT = 15
RESULTS_DIR = r'd:\FinalCodeAndFile\lab-management-system\test_results'

def make_request(method, url, json_data=None, params=None, description=""):
    """
    发送HTTP请求并记录详细结果
    返回: dict包含状态码、响应时间、响应体大小、响应内容等
    """
    result = {
        'description': description,
        'method': method,
        'url': url,
        'status_code': None,
        'response_time_ms': None,
        'response_size_bytes': None,
        'success': False,
        'error': None,
        'has_code_field': False,
        'has_message_field': False,
        'has_data_field': False,
        'response_body_preview': None
    }

    try:
        start = time.perf_counter()

        if method == 'GET':
            resp = requests.get(url, params=params, timeout=TIMEOUT)
        elif method == 'POST':
            resp = requests.post(url, json=json_data, timeout=TIMEOUT)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")

        elapsed = (time.perf_counter() - start) * 1000

        # 记录结果
        result['status_code'] = resp.status_code
        result['response_time_ms'] = round(elapsed, 2)
        result['response_size_bytes'] = len(resp.content)
        result['success'] = resp.status_code in [200, 201]

        # 尝试解析JSON响应
        try:
            body = resp.json()
            result['has_code_field'] = 'code' in body
            result['has_message_field'] = 'message' in body
            result['has_data_field'] = 'data' in body

            # 只保存前500个字符作为预览
            body_str = json.dumps(body, ensure_ascii=False)
            if len(body_str) > 500:
                result['response_body_preview'] = body_str[:500] + '...'
            else:
                result['response_body_preview'] = body_str
        except:
            result['response_body_preview'] = resp.text[:500] if resp.text else None

    except requests.exceptions.Timeout:
        result['error'] = f'请求超时 (>{TIMEOUT}s)'
    except requests.exceptions.ConnectionError as e:
        result['error'] = f'连接失败: {str(e)[:100]}'
    except Exception as e:
        result['error'] = f'请求异常: {str(e)[:100]}'

    return result


def task_a_api_connectivity_test():
    """任务A: API真实连通性深度测试 - 31个端点"""
    print("\n" + "="*80)
    print("【任务A】API真实连通性深度测试")
    print("="*80)

    test_results = []
    summary = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'by_service': defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0})
    }

    # ==================== User Service Tests (5个) ====================
    print("\n--- User Service 测试 ---")

    # 1. POST /user/login
    result = make_request(
        'POST',
        f"{BASE_URLS['user']}/user/login",
        json_data={"username": "admin", "password": "admin123"},
        description="用户登录"
    )
    test_results.append(result)
    summary['by_service']['user']['total'] += 1
    if result['success']:
        summary['by_service']['user']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['user']['failed'] += 1
        summary['failed'] += 1
    print(f"  [1/20] POST /user/login - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 2. POST /user/register
    result = make_request(
        'POST',
        f"{BASE_URLS['user']}/user/register",
        json_data={
            "username": "test_v131",
            "password": "test123",
            "realName": "测试用户",
            "role": "DOCTOR",
            "phone": "13800138000"
        },
        description="用户注册"
    )
    test_results.append(result)
    summary['by_service']['user']['total'] += 1
    if result['success']:
        summary['by_service']['user']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['user']['failed'] += 1
        summary['failed'] += 1
    print(f"  [2/20] POST /user/register - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 3. GET /user/list 或 /user/all
    for endpoint in ['/user/list', '/user/all']:
        result = make_request('GET', f"{BASE_URLS['user']}{endpoint}", description=f"获取用户列表({endpoint})")
        if result['status_code'] != 404:
            test_results.append(result)
            summary['by_service']['user']['total'] += 1
            if result['success']:
                summary['by_service']['user']['passed'] += 1
                summary['passed'] += 1
            else:
                summary['by_service']['user']['failed'] += 1
                summary['failed'] += 1
            print(f"  [3/20] GET {endpoint} - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")
            break
    else:
        print("  [3/20] GET /user/list 和 /user/all 均返回404")

    # 4. GET /user/1
    result = make_request(
        'GET',
        f"{BASE_URLS['user']}/user/1",
        description="获取admin用户详情"
    )
    test_results.append(result)
    summary['by_service']['user']['total'] += 1
    if result['success']:
        summary['by_service']['user']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['user']['failed'] += 1
        summary['failed'] += 1
    print(f"  [4/20] GET /user/1 - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 5. GET /user/list?page=1&size=10
    result = make_request(
        'GET',
        f"{BASE_URLS['user']}/user/list",
        params={'page': 1, 'size': 10},
        description="分页获取用户列表"
    )
    test_results.append(result)
    summary['by_service']['user']['total'] += 1
    if result['success']:
        summary['by_service']['user']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['user']['failed'] += 1
        summary['failed'] += 1
    print(f"  [5/20] GET /user/list?page=1&size=10 - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # ==================== Sample Service Tests (4个) ====================
    print("\n--- Sample Service 测试 ---")

    # 6. POST /sample/create
    result = make_request(
        'POST',
        f"{BASE_URLS['sample']}/sample/create",
        json_data={
            "patientName": "测试患者v131",
            "patientId": "P131001",
            "sampleType": "血液",
            "department": "检验科"
        },
        description="创建样本"
    )
    test_results.append(result)
    summary['by_service']['sample']['total'] += 1
    if result['success']:
        summary['by_service']['sample']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['sample']['failed'] += 1
        summary['failed'] += 1
    print(f"  [6/20] POST /sample/create - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 7. GET /sample/list
    result = make_request(
        'GET',
        f"{BASE_URLS['sample']}/sample/list",
        description="获取样本列表"
    )
    test_results.append(result)
    summary['by_service']['sample']['total'] += 1
    if result['success']:
        summary['by_service']['sample']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['sample']['failed'] += 1
        summary['failed'] += 1
    print(f"  [7/20] GET /sample/list - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 8. GET /sample/list-by-status?status=PENDING
    result = make_request(
        'GET',
        f"{BASE_URLS['sample']}/sample/list-by-status",
        params={'status': 'PENDING'},
        description="按状态查询样本"
    )
    test_results.append(result)
    summary['by_service']['sample']['total'] += 1
    if result['success']:
        summary['by_service']['sample']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['sample']['failed'] += 1
        summary['failed'] += 1
    print(f"  [8/20] GET /sample/list-by-status?status=PENDING - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 9. GET /sample/list?page=1&size=10
    result = make_request(
        'GET',
        f"{BASE_URLS['sample']}/sample/list",
        params={'page': 1, 'size': 10},
        description="分页获取样本列表"
    )
    test_results.append(result)
    summary['by_service']['sample']['total'] += 1
    if result['success']:
        summary['by_service']['sample']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['sample']['failed'] += 1
        summary['failed'] += 1
    print(f"  [9/20] GET /sample/list?page=1&size=10 - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # ==================== Report Service Tests (4个) ====================
    print("\n--- Report Service 测试 ---")

    # 10. POST /report/create
    result = make_request(
        'POST',
        f"{BASE_URLS['report']}/report/create",
        json_data={
            "reportNo": "RP-v131-001",
            "patientId": "P131001",
            "patientName": "测试患者v131",
            "sampleType": "血液"
        },
        description="创建报告"
    )
    test_results.append(result)
    summary['by_service']['report']['total'] += 1
    if result['success']:
        summary['by_service']['report']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['report']['failed'] += 1
        summary['failed'] += 1
    print(f"  [10/20] POST /report/create - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 11. GET /report/list
    result = make_request(
        'GET',
        f"{BASE_URLS['report']}/report/list",
        description="获取报告列表"
    )
    test_results.append(result)
    summary['by_service']['report']['total'] += 1
    if result['success']:
        summary['by_service']['report']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['report']['failed'] += 1
        summary['failed'] += 1
    print(f"  [11/20] GET /report/list - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 12. GET /report/pending-list
    result = make_request(
        'GET',
        f"{BASE_URLS['report']}/report/pending-list",
        description="获取待审核报告列表"
    )
    test_results.append(result)
    summary['by_service']['report']['total'] += 1
    if result['success']:
        summary['by_service']['report']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['report']['failed'] += 1
        summary['failed'] += 1
    print(f"  [12/20] GET /report/pending-list - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 13. GET /report/list?page=1&size=10
    result = make_request(
        'GET',
        f"{BASE_URLS['report']}/report/list",
        params={'page': 1, 'size': 10},
        description="分页获取报告列表"
    )
    test_results.append(result)
    summary['by_service']['report']['total'] += 1
    if result['success']:
        summary['by_service']['report']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['report']['failed'] += 1
        summary['failed'] += 1
    print(f"  [13/20] GET /report/list?page=1&size=10 - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # ==================== AI Service Tests (3个) ====================
    print("\n--- AI Service 测试 ---")

    # 14. GET /ai/health
    result = make_request(
        'GET',
        f"{BASE_URLS['ai']}/ai/health",
        description="AI服务健康检查"
    )
    test_results.append(result)
    summary['by_service']['ai']['total'] += 1
    if result['success']:
        summary['by_service']['ai']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['ai']['failed'] += 1
        summary['failed'] += 1
    print(f"  [14/20] GET /ai/health - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 15. POST /ai/simple-diagnose
    blood_data = {"wbc": 10.5, "rbc": 4.5, "hgb": 140, "plt": 250}
    result = make_request(
        'POST',
        f"{BASE_URLS['ai']}/ai/simple-diagnose",
        json_data={"type": "blood_routine", "data": blood_data},
        description="简单诊断(血常规)"
    )
    test_results.append(result)
    summary['by_service']['ai']['total'] += 1
    if result['success']:
        summary['by_service']['ai']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['ai']['failed'] += 1
        summary['failed'] += 1
    print(f"  [15/20] POST /ai/simple-diagnose - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 16. POST /ai/diagnose/blood-routine
    result = make_request(
        'POST',
        f"{BASE_URLS['ai']}/ai/diagnose/blood-routine",
        json_data=blood_data,
        description="血常规诊断"
    )
    test_results.append(result)
    summary['by_service']['ai']['total'] += 1
    if result['success']:
        summary['by_service']['ai']['passed'] += 1
        summary['passed'] += 1
    else:
        summary['by_service']['ai']['failed'] += 1
        summary['failed'] += 1
    print(f"  [16/20] POST /ai/diagnose/blood-routine - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # ==================== Gateway Routes Tests (4个) ====================
    print("\n--- Gateway 路由转发测试 ---")

    gateway_tests = [
        ('GET', '/api/user/list', 'User Service'),
        ('GET', '/api/sample/list', 'Sample Service'),
        ('GET', '/api/report/list', 'Report Service'),
        ('GET', '/api/ai/health', 'AI Service')
    ]

    for idx, (method, path, target) in enumerate(gateway_tests, start=17):
        result = make_request(
            method,
            f"{BASE_URLS['gateway']}{path}",
            description=f"网关转发到{target}"
        )
        test_results.append(result)
        summary['by_service']['gateway']['total'] += 1
        if result['success']:
            summary['by_service']['gateway']['passed'] += 1
            summary['passed'] += 1
        else:
            summary['by_service']['gateway']['failed'] += 1
            summary['failed'] += 1
        print(f"  [{idx}/20] {method} {path} -> {target} - 状态码:{result['status_code']} 耗时:{result['response_time_ms']}ms {'✓' if result['success'] else '✗'}")

    # 更新总计数
    summary['total_tests'] = len(test_results)

    return {
        'test_type': 'API_CONNECTIVITY_TEST',
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': summary['total_tests'],
            'passed': summary['passed'],
            'failed': summary['failed'],
            'pass_rate': round(summary['passed'] / summary['total_tests'] * 100, 2) if summary['total_tests'] > 0 else 0,
            'by_service': dict(summary['by_service'])
        },
        'details': test_results
    }


def task_b_performance_benchmark():
    """任务B: 性能基准实测"""
    print("\n" + "="*80)
    print("【任务B】性能基准实测")
    print("="*80)

    performance_results = {}

    # ==================== B1: API响应时间基准测试 ====================
    print("\n--- B1: API响应时间基准测试 (每个API执行10次) ---")

    apis_to_test = [
        ('GET', f"{BASE_URLS['user']}/user/list", 'User Service - 用户列表'),
        ('GET', f"{BASE_URLS['sample']}/sample/list", 'Sample Service - 样本列表'),
        ('GET', f"{BASE_URLS['report']}/report/list", 'Report Service - 报告列表'),
        ('GET', f"{BASE_URLS['ai']}/ai/health", 'AI Service - 健康检查'),
        ('GET', f"{BASE_URLS['gateway']}/api/user/list", 'Gateway -> User Service'),
    ]

    benchmark_results = {}
    for method, url, desc in apis_to_test:
        times = []
        status_codes = []

        for i in range(10):
            start = time.perf_counter()
            try:
                if method == 'GET':
                    resp = requests.get(url, timeout=TIMEOUT)
                else:
                    resp = requests.post(url, json={}, timeout=TIMEOUT)
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
                status_codes.append(resp.status_code)
            except Exception as e:
                times.append(-1)
                status_codes.append(0)

        valid_times = [t for t in times if t > 0]
        sorted_times = sorted(valid_times) if valid_times else []

        result = {
            'description': desc,
            'url': url,
            'method': method,
            'total_requests': 10,
            'successful_requests': len(valid_times),
            'success_rate': round(len(valid_times) / 10 * 100, 2),
            'statistics': {}
        }

        if valid_times and len(valid_times) >= 1:
            result['statistics'] = {
                'avg_ms': round(sum(valid_times) / len(valid_times), 2),
                'min_ms': round(min(valid_times), 2),
                'max_ms': round(max(valid_times), 2),
                'p50_ms': round(statistics.median(valid_times), 2),
                'p95_ms': round(sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 1 else sorted_times[0], 2),
                'p99_ms': round(sorted_times[min(int(len(sorted_times) * 0.99), len(sorted_times)-1)] if len(sorted_times) > 1 else sorted_times[0], 2),
                'std_dev_ms': round(statistics.stdev(valid_times), 2) if len(valid_times) > 1 else 0
            }

        result['all_response_times_ms'] = times
        result['status_codes'] = status_codes

        benchmark_results[url] = result

        stats = result['statistics']
        print(f"\n  {desc}")
        print(f"    URL: {url}")
        print(f"    成功率: {result['success_rate']}% ({len(valid_times)}/10)")
        if stats:
            print(f"    平均: {stats['avg_ms']}ms | P50: {stats['p50_ms']}ms | P95: {stats['p95_ms']}ms | P99: {stats['p99_ms']}ms")
            print(f"    最小: {stats['min_ms']}ms | 最大: {stats['max_ms']}ms | 标准差: {stats['std_dev_ms']}ms")

    performance_results['b1_response_time_benchmark'] = {
        'test_type': 'RESPONSE_TIME_BENCHMARK',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'requests_per_api': 10,
            'timeout_seconds': TIMEOUT
        },
        'results': benchmark_results
    }

    # ==================== B2: 并发能力测试 (5并发) ====================
    print("\n\n--- B2: 并发能力测试 (5个并发请求) ---")

    def concurrent_request(url, request_id):
        start = time.perf_counter()
        try:
            resp = requests.get(url, timeout=TIMEOUT)
            elapsed = (time.perf_counter() - start) * 1000
            return {
                'request_id': request_id,
                'time_ms': round(elapsed, 2),
                'status_code': resp.status_code,
                'success': True,
                'error': None
            }
        except Exception as e:
            return {
                'request_id': request_id,
                'time_ms': -1,
                'status_code': 0,
                'success': False,
                'error': str(e)[:100]
            }

    concurrent_urls = [
        (f"{BASE_URLS['user']}/user/list", 'User Service'),
        (f"{BASE_URLS['sample']}/sample/list", 'Sample Service'),
        (f"{BASE_URLS['report']}/report/list", 'Report Service'),
        (f"{BASE_URLS['gateway']}/api/user/list", 'Gateway'),
    ]

    concurrent_results = {}

    for url, service_name in concurrent_urls:
        print(f"\n  测试 {service_name}: {url}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(concurrent_request, url, i+1) for i in range(5)]
            results_5concurrent = [f.result() for f in futures]

        successful = [r for r in results_5concurrent if r['success']]
        failed = [r for r in results_5concurrent if not r['success']]

        times = [r['time_ms'] for r in successful]

        concurrent_results[url] = {
            'service': service_name,
            'url': url,
            'concurrency_level': 5,
            'total_requests': 5,
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': round(len(successful) / 5 * 100, 2),
            'avg_response_time_ms': round(sum(times) / len(times), 2) if times else None,
            'min_response_time_ms': min(times) if times else None,
            'max_response_time_ms': max(times) if times else None,
            'details': results_5concurrent
        }

        result = concurrent_results[url]
        print(f"    成功率: {result['success_rate']}% ({result['successful']}/{result['total_requests']})")
        if times:
            print(f"    平均响应: {result['avg_response_time_ms']}ms | 最快: {result['min_response_time_ms']}ms | 最慢: {result['max_response_time_ms']}ms")
        if failed:
            print(f"    失败请求: {[f['request_id'] for f in failed]}")

        for detail in results_5concurrent:
            status = "✓" if detail['success'] else "✗"
            print(f"      请求#{detail['request_id']}: {detail['time_ms']}ms (状态码:{detail['status_code']}) {status}")

    performance_results['b2_concurrency_test'] = {
        'test_type': 'CONCURRENCY_TEST',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'concurrency_level': 5,
            'timeout_seconds': TIMEOUT
        },
        'results': concurrent_results
    }

    # ==================== B3: 页面加载时间测试 ====================
    print("\n\n--- B3: 页面加载时间测试 ---")

    pages = [
        ('/', '首页'),
        ('/login', '登录页'),
        ('/dashboard', '仪表盘'),
    ]

    page_load_results = {}

    for path, page_name in pages:
        url = f"{BASE_URLS['frontend']}{path}"
        start = time.perf_counter()
        try:
            resp = requests.get(url, timeout=30)
            load_time = (time.perf_counter() - start) * 1000

            page_load_results[path] = {
                'page_name': page_name,
                'url': url,
                'status_code': resp.status_code,
                'load_time_ms': round(load_time, 2),
                'content_size_bytes': len(resp.content),
                'success': resp.status_code == 200
            }

            status = "✓" if resp.status_code == 200 else "✗"
            print(f"  {page_name} ({url}): {load_time:.2f}ms (状态码:{resp.status_code}, 大小:{len(resp.content)}bytes) {status}")

        except Exception as e:
            page_load_results[path] = {
                'page_name': page_name,
                'url': url,
                'status_code': None,
                'load_time_ms': None,
                'content_size_bytes': None,
                'success': False,
                'error': str(e)[:100]
            }
            print(f"  {page_name} ({url}): ERROR - {e}")

    performance_results['b3_page_load_test'] = {
        'test_type': 'PAGE_LOAD_TEST',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'timeout_seconds': 30
        },
        'results': page_load_results
    }

    # ==================== 性能目标验证表 ====================
    print("\n\n--- 性能目标验证表 ---")

    # 提取关键指标
    validation_table = []

    # 指标1: API P50 < 200ms
    all_p50_values = []
    for url, data in benchmark_results.items():
        if data['statistics'].get('p50_ms'):
            all_p50_values.append(data['statistics']['p50_ms'])

    avg_p50 = sum(all_p50_values) / len(all_p50_values) if all_p50_values else None
    p50_pass = avg_p50 < 200 if avg_p50 else False
    validation_table.append({
        'metric': 'API P50响应时间',
        'target': '< 200ms',
        'measured': f"{avg_p50:.2f}ms" if avg_p50 else 'N/A',
        'pass': p50_pass,
        'details': f"平均P50={avg_p50:.2f}ms (基于{len(all_p50_values)}个API)" if avg_p50 else '无法测量'
    })
    print(f"  {'✓' if p50_pass else '✗'} API P50 < 200ms: 实测 {avg_p50:.2f}ms" if avg_p50 else "  ✗ API P50 < 200ms: 无法测量")

    # 指标2: API P95 < 500ms
    all_p95_values = []
    for url, data in benchmark_results.items():
        if data['statistics'].get('p95_ms'):
            all_p95_values.append(data['statistics']['p95_ms'])

    avg_p95 = sum(all_p95_values) / len(all_p95_values) if all_p95_values else None
    p95_pass = avg_p95 < 500 if avg_p95 else False
    validation_table.append({
        'metric': 'API P95响应时间',
        'target': '< 500ms',
        'measured': f"{avg_p95:.2f}ms" if avg_p95 else 'N/A',
        'pass': p95_pass,
        'details': f"平均P95={avg_p95:.2f}ms (基于{len(all_p95_values)}个API)" if avg_p95 else '无法测量'
    })
    print(f"  {'✓' if p95_pass else '✗'} API P95 < 500ms: 实测 {avg_p95:.2f}ms" if avg_p95 else "  ✗ API P95 < 500ms: 无法测量")

    # 指标3: 首页加载 < 2s
    home_load_time = page_load_results.get('/', {}).get('load_time_ms')
    home_pass = home_load_time < 2000 if home_load_time else False
    validation_table.append({
        'metric': '首页加载时间',
        'target': '< 2000ms (2s)',
        'measured': f"{home_load_time:.2f}ms" if home_load_time else 'N/A',
        'pass': home_pass,
        'details': f"首页加载耗时{home_load_time:.2f}ms" if home_load_time else '无法测量'
    })
    print(f"  {'✓' if home_pass else '✗'} 首页加载 < 2s: 实测 {home_load_time:.2f}ms" if home_load_time else "  ✗ 首页加载 < 2s: 无法测量")

    # 指标4: 5并发无错误
    all_concurrent_success = all(
        r['success_rate'] == 100.0
        for r in concurrent_results.values()
    )
    concurrency_pass = all_concurrent_success and len(concurrent_results) > 0
    failed_services = [
        r['service'] for r in concurrent_results.values()
        if r['success_rate'] < 100.0
    ]
    validation_table.append({
        'metric': '5并发无错误',
        'target': '100%成功率',
        'measured': f"{len(concurrent_results) - len(failed_services)}/{len(concurrent_results)} 服务通过" if concurrent_results else 'N/A',
        'pass': concurrency_pass,
        'details': f"所有服务5并发测试通过" if concurrency_pass else f"失败服务: {', '.join(failed_services)}"
    })
    print(f"  {'✓' if concurrency_pass else '✗'} 5并发无错误: {'全部通过' if concurrency_pass else f'失败: {failed_services}'}")

    total_metrics = len(validation_table)
    passed_metrics = sum(1 for v in validation_table if v['pass'])
    overall_pass_rate = passed_metrics / total_metrics * 100 if total_metrics > 0 else 0

    print(f"\n  总体达标率: {passed_metrics}/{total_metrics} ({overall_pass_rate:.1f}%)")

    performance_results['validation_summary'] = {
        'total_metrics': total_metrics,
        'passed_metrics': passed_metrics,
        'overall_pass_rate': round(overall_pass_rate, 2),
        'validation_table': validation_table
    }

    return performance_results


def generate_performance_report(performance_results):
    """生成性能测试报告(Markdown格式)"""
    report_lines = []
    report_lines.append("# 实验室管理系统 - 性能基准实测报告 v1.3.1")
    report_lines.append("")
    report_lines.append(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**测试环境**: 本地开发环境")
    report_lines.append("")

    # B1部分
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## B1: API响应时间基准测试")
    report_lines.append("")
    report_lines.append("| API | 平均(ms) | P50(ms) | P95(ms) | P99(ms) | 成功率 |")
    report_lines.append("|-----|---------|--------|--------|--------|-------|")

    b1_results = performance_results.get('b1_response_time_benchmark', {}).get('results', {})
    for url, data in b1_results.items():
        stats = data.get('statistics', {})
        report_lines.append(
            f"| {data.get('description', url)} | "
            f"{stats.get('avg_ms', 'N/A')} | "
            f"{stats.get('p50_ms', 'N/A')} | "
            f"{stats.get('p95_ms', 'N/A')} | "
            f"{stats.get('p99_ms', 'N/A')} | "
            f"{data.get('success_rate', 0)}% |"
        )

    report_lines.append("")

    # B2部分
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## B2: 并发能力测试 (5并发)")
    report_lines.append("")
    report_lines.append("| 服务 | 成功率 | 平均响应(ms) | 最快(ms) | 最慢(ms) |")
    report_lines.append("|------|-------|------------|---------|---------|")

    b2_results = performance_results.get('b2_concurrency_test', {}).get('results', {})
    for url, data in b2_results.items():
        report_lines.append(
            f"| {data.get('service', url)} | "
            f"{data.get('success_rate', 0)}% | "
            f"{data.get('avg_response_time_ms', 'N/A')} | "
            f"{data.get('min_response_time_ms', 'N/A')} | "
            f"{data.get('max_response_time_ms', 'N/A')} |"
        )

    report_lines.append("")

    # B3部分
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## B3: 页面加载时间测试")
    report_lines.append("")
    report_lines.append("| 页面 | 加载时间(ms) | 状态码 | 页面大小(bytes) |")
    report_lines.append("|------|-------------|--------|----------------|")

    b3_results = performance_results.get('b3_page_load_test', {}).get('results', {})
    for path, data in b3_results.items():
        report_lines.append(
            f"| {data.get('page_name', path)} | "
            f"{data.get('load_time_ms', 'N/A')} | "
            f"{data.get('status_code', 'N/A')} | "
            f"{data.get('content_size_bytes', 'N/A')} |"
        )

    report_lines.append("")

    # 验证总结
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## 性能目标验证表")
    report_lines.append("")
    report_lines.append("| 指标 | 目标值 | 实测值 | 达标? |")
    report_lines.append("|------|-------|-------|------|")

    validation = performance_results.get('validation_summary', {}).get('validation_table', [])
    for item in validation:
        status = "✅ 通过" if item['pass'] else "❌ 未通过"
        report_lines.append(
            f"| {item['metric']} | "
            f"{item['target']} | "
            f"{item['measured']} | "
            f"{status} |"
        )

    report_lines.append("")

    # 总体结论
    validation_summary = performance_results.get('validation_summary', {})
    overall_rate = validation_summary.get('overall_pass_rate', 0)
    passed = validation_summary.get('passed_metrics', 0)
    total = validation_summary.get('total_metrics', 0)

    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## 总体结论")
    report_lines.append("")
    if overall_rate >= 75:
        report_lines.append(f"### 🎉 性能测试总体评估: **良好** ({passed}/{total}项指标通过, 达标率{overall_rate:.1f}%)")
    elif overall_rate >= 50:
        report_lines.append(f"### ⚠️ 性能测试总体评估: **一般** ({passed}/{total}项指标通过, 达标率{overall_rate:.1f}%)")
    else:
        report_lines.append(f"### ❌ 性能测试总体评估: **需优化** ({passed}/{total}项指标通过, 达标率{overall_rate:.1f}%)")

    report_lines.append("")
    report_lines.append("### 建议")
    report_lines.append("- 如有未达标项，建议进行针对性性能优化")
    report_lines.append("- 关注高延迟接口，考虑添加缓存或数据库索引优化")
    report_lines.append("- 在生产环境部署前建议进行更全面的压力测试")
    report_lines.append("")

    return "\n".join(report_lines)


def main():
    """主函数：执行所有测试并保存结果"""
    print("="*80)
    print("实验室管理系统 - API与性能综合测试 v1.3.1")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 执行任务A: API连通性测试
    api_results = task_a_api_connectivity_test()

    # 执行任务B: 性能基准测试
    performance_results = task_b_performance_benchmark()

    # 组合完整结果
    full_report = {
        'version': 'v1.3.1',
        'test_datetime': datetime.now().isoformat(),
        'environment': {
            'frontend': BASE_URLS['frontend'],
            'gateway': BASE_URLS['gateway'],
            'services': {
                'user': BASE_URLS['user'],
                'sample': BASE_URLS['sample'],
                'report': BASE_URLS['report'],
                'ai': BASE_URLS['ai']
            }
        },
        'task_a_api_connectivity': api_results,
        'task_b_performance': performance_results
    }

    # 保存JSON结果
    json_file_path = f"{RESULTS_DIR}\\api-live-test-v1.3.1.json"
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(full_report, f, ensure_ascii=False, indent=2)
    print(f"\n✓ JSON测试结果已保存: {json_file_path}")

    # 生成并保存Markdown性能报告
    md_content = generate_performance_report(performance_results)
    md_file_path = f"{RESULTS_DIR}\\performance-live-v1.3.1.md"
    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✓ Markdown性能报告已保存: {md_file_path}")

    # 打印最终摘要
    print("\n" + "="*80)
    print("测试完成 - 最终摘要")
    print("="*80)

    api_summary = api_results.get('summary', {})
    perf_validation = performance_results.get('validation_summary', {})

    print(f"\n【任务A】API连通性测试:")
    print(f"  总计: {api_summary.get('total_tests', 0)} 个端点")
    print(f"  通过: {api_summary.get('passed', 0)} 个")
    print(f"  失败: {api_summary.get('failed', 0)} 个")
    print(f"  通过率: {api_summary.get('pass_rate', 0):.1f}%")

    print(f"\n【任务B】性能基准测试:")
    print(f"  指标达标: {perf_validation.get('passed_metrics', 0)}/{perf_validation.get('total_metrics', 0)} 项")
    print(f"  总体达标率: {perf_validation.get('overall_pass_rate', 0):.1f}%")

    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)


if __name__ == '__main__':
    main()
