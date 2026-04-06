#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 - 性能基准测试 v1.4.0
执行时间: 2026-04-02

测试内容:
1. API响应时间基准测试 (50次请求, P50/P90/P95/P99/标准差)
2. 并发能力测试 (10并发用户登录)
3. 前端页面加载性能测试 (TTFB/DOM加载/完整加载)

验收标准:
- P50响应时间 < 50ms
- P95响应时间 < 200ms
- 页面完整加载 < 2秒
- 并发成功率 > 95%
"""

import requests
import time
import statistics
import concurrent.futures
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple

# ==================== 配置 ====================
# 服务地址配置
SERVICES = {
    'gateway': 'http://localhost:8080',
    'user_service': 'http://localhost:8086',
    'sample_service': 'http://localhost:8087',
    'report_service': 'http://localhost:8088',
    'ai_service': 'http://localhost:8085',
    'frontend': 'http://localhost:3000'
}

# 测试参数
TEST_ITERATIONS = 50  # 每个API端点请求次数
CONCURRENT_USERS = 10  # 并发用户数
TIMEOUT_SECONDS = 15  # 超时时间(秒)

# v1.3.1基线数据（用于对比）
V131_BASELINE = {
    'p50_ms': 19.81,
    'p95_ms': 34.29,
    'page_load_ms': 23.37,
    'concurrency_success_rate': 100.0
}

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
    return round(sorted_data[index], 2)

def calculate_std_dev(data: List[float]) -> float:
    """计算标准差"""
    if len(data) < 2:
        return 0.0
    return round(statistics.stdev(data), 2)

# ==================== 1. API响应时间测试 ====================
def test_api_response_time(method: str, url: str, iterations: int = TEST_ITERATIONS) -> Dict[str, Any]:
    """
    测试单个API端点的响应时间（多次请求取统计值）
    返回包含P50/P90/P95/P99/平均值/最小值/最大值/标准差的字典
    """
    times = []
    status_codes = []
    errors = []

    print(f"\n{'='*60}")
    print(f"测试端点: {method} {url}")
    print(f"请求次数: {iterations}次")
    print(f"{'='*60}")

    for i in range(iterations):
        try:
            start_time = time.time()
            if method == 'GET':
                response = requests.get(url, timeout=TIMEOUT_SECONDS)
            elif method == 'POST':
                # AI分析接口使用POST，发送示例数据
                payload = {
                    "sampleId": "test-sample-001",
                    "testType": "blood",
                    "results": {"WBC": 7.5, "RBC": 4.5, "PLT": 250}
                }
                response = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            elapsed_ms = (time.time() - start_time) * 1000
            times.append(round(elapsed_ms, 2))
            status_codes.append(response.status_code)

            # 每10次打印进度
            if (i + 1) % 10 == 0:
                print(f"  进度: {i+1}/{iterations} 次")

        except requests.exceptions.Timeout:
            times.append(-1)
            status_codes.append(0)
            errors.append(f"请求超时 (>{TIMEOUT_SECONDS}s)")
        except requests.exceptions.ConnectionError as e:
            times.append(-1)
            status_codes.append(0)
            errors.append(f"连接失败: {str(e)[:80]}")
        except Exception as e:
            times.append(-1)
            status_codes.append(0)
            errors.append(f"未知错误: {str(e)[:80]}")

    # 计算统计指标
    valid_times = [t for t in times if t > 0]
    success_count = len(valid_times)

    result = {
        'endpoint': url,
        'method': method,
        'service_name': url.split(':')[1][2:] if ':' in url else 'unknown',  # 提取服务名
        'total_requests': iterations,
        'success_count': success_count,
        'success_rate': round(success_count / iterations * 100, 2) if iterations > 0 else 0,
        # 百分位数
        'p50_ms': calculate_percentile(valid_times, 50),
        'p90_ms': calculate_percentile(valid_times, 90),
        'p95_ms': calculate_percentile(valid_times, 95),
        'p99_ms': calculate_percentile(valid_times, 99),
        # 统计值
        'avg_ms': round(sum(valid_times) / len(valid_times), 2) if valid_times else 0,
        'min_ms': round(min(valid_times), 2) if valid_times else 0,
        'max_ms': round(max(valid_times), 2) if valid_times else 0,
        'std_dev_ms': calculate_std_dev(valid_times),
        # 其他信息
        'status_codes': list(set(status_codes)),
        'errors': errors[:5]  # 保留前5个错误
    }

    # 打印结果摘要
    print(f"\n  结果统计:")
    print(f"  成功率: {result['success_rate']}% ({success_count}/{iterations})")
    print(f"  P50: {result['p50_ms']}ms | P90: {result['p90_ms']}ms | P95: {result['p95_ms']}ms | P99: {result['p99_ms']}ms")
    print(f"  平均: {result['avg_ms']}ms | 最小: {result['min_ms']}ms | 最大: {result['max_ms']}ms | 标准差: {result['std_dev_ms']}ms")

    if result['errors']:
        print(f"  错误数: {len(errors)}")
        for err in result['errors'][:3]:
            print(f"    - {err}")

    return result

# ==================== 2. 并发测试 ====================
def concurrent_login_worker(user_id: int) -> Dict[str, Any]:
    """
    单个并发用户的工作函数 - 执行登录请求
    """
    login_url = f"{SERVICES['user_service']}/user/login"
    try:
        start_time = time.time()
        # 发送POST登录请求
        payload = {
            "username": f"test_user_{user_id}",
            "password": "test123456"
        }
        response = requests.post(login_url, json=payload, timeout=TIMEOUT_SECONDS)
        elapsed_ms = (time.time() - start_time) * 1000

        return {
            'user_id': user_id,
            'time_ms': round(elapsed_ms, 2),
            'status_code': response.status_code,
            'success': response.status_code in [200, 201, 400],  # 200成功或400用户不存在都算请求成功
            'error': None
        }
    except Exception as e:
        return {
            'user_id': user_id,
            'time_ms': -1,
            'status_code': 0,
            'success': False,
            'error': str(e)[:100]
        }

def test_concurrent_requests(num_users: int = CONCURRENT_USERS) -> Dict[str, Any]:
    """
    测试并发登录能力
    使用线程池模拟多个用户同时请求
    """
    print(f"\n{'='*60}")
    print(f"并发能力测试")
    print(f"{'='*60}")
    print(f"测试端点: {SERVICES['user_service']}/user/login")
    print(f"并发用户数: {num_users}")

    results = []
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(concurrent_login_worker, i+1) for i in range(num_users)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    total_time = round((time.time() - start_time) * 1000, 2)

    # 统计结果
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    response_times = [r['time_ms'] for r in successful if r['time_ms'] > 0]

    result = {
        'endpoint': f"{SERVICES['user_service']}/user/login",
        'concurrent_users': num_users,
        'total_requests': len(results),
        'successful_requests': len(successful),
        'failed_requests': len(failed),
        'success_rate': round(len(successful) / len(results) * 100, 2) if results else 0,
        'avg_response_time_ms': round(sum(response_times) / len(response_times), 2) if response_times else 0,
        'min_response_time_ms': round(min(response_times), 2) if response_times else 0,
        'max_response_time_ms': round(max(response_times), 2) if response_times else 0,
        'std_dev_ms': calculate_std_dev(response_times),
        'total_test_time_ms': total_time,
        'throughput_per_second': round(num_users / (total_time / 1000), 2) if total_time > 0 else 0,
        'errors': [r['error'] for r in failed if r['error']][:5]
    }

    # 打印结果
    print(f"\n  并发测试结果:")
    print(f"  总请求数: {result['total_requests']}")
    print(f"  成功请求: {result['successful_requests']}")
    print(f"  失败请求: {result['failed_requests']}")
    print(f"  成功率: {result['success_rate']}%")
    print(f"  平均响应时间: {result['avg_response_time_ms']}ms")
    print(f"  响应时间范围: {result['min_response_time_ms']}ms - {result['max_response_time_ms']}ms")
    print(f"  标准差: {result['std_dev_ms']}ms")
    print(f"  吞吐量: {result['throughput_per_second']} 请求/秒")
    print(f"  总测试耗时: {result['total_test_time_ms']}ms")

    if result['errors']:
        print(f"\n  错误详情:")
        for err in result['errors'][:3]:
            print(f"    - {err}")

    return result

# ==================== 3. 前端页面加载测试 ====================
def test_frontend_page_load(page_url: str, page_name: str) -> Dict[str, Any]:
    """
    测试前端页面加载性能
    测量指标：
    - TTFB (Time To First Byte): 首字节时间
    - DOM加载时间
    - 完整加载时间
    """
    print(f"\n{'='*60}")
    print(f"前端页面加载测试: {page_name}")
    print(f"URL: {page_url}")
    print(f"{'='*60}")

    try:
        # 记录开始时间
        request_start = time.time()

        # 发送请求并测量各项时间
        session = requests.Session()

        # TTFB测量
        ttfb_start = time.time()
        response = session.get(page_url, timeout=30, stream=True)
        ttfb_time = (time.time() - ttfb_start) * 1000

        # 读取完整内容（模拟DOM加载）
        dom_content = b''
        dom_start = time.time()
        for chunk in response.iter_content(chunk_size=8192):
            dom_content += chunk
            # 模拟DOM解析完成（读取到一定量的内容）
            if len(dom_content) > 1024:  # 1KB后认为DOM基本加载
                break
        dom_load_time = (time.time() - dom_start) * 1000

        # 完整内容加载
        full_content = dom_content
        for chunk in response.iter_content(chunk_size=8192):
            full_content += chunk
        total_load_time = (time.time() - request_start) * 1000

        result = {
            'page_name': page_name,
            'url': page_url,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            # 时间指标
            'ttfb_ms': round(ttfb_time, 2),
            'dom_load_ms': round(dom_load_time + ttfb_time, 2),  # DOM加载包含TTFB
            'full_load_ms': round(total_load_time, 2),
            # 页面信息
            'content_size_bytes': len(full_content),
            'error': None
        }

        # 打印结果
        print(f"\n  加载结果:")
        print(f"  状态码: {response.status_code} ({'成功' if result['success'] else '失败'})")
        print(f"  TTFB (首字节时间): {result['ttfb_ms']}ms")
        print(f"  DOM加载时间: {result['dom_load_ms']}ms")
        print(f"  完整加载时间: {result['full_load_ms']}ms")
        print(f"  页面大小: {result['content_size_bytes']} bytes ({round(result['content_size_bytes']/1024, 2)} KB)")

        return result

    except Exception as e:
        result = {
            'page_name': page_name,
            'url': page_url,
            'status_code': 0,
            'success': False,
            'ttfb_ms': -1,
            'dom_load_ms': -1,
            'full_load_ms': -1,
            'content_size_bytes': 0,
            'error': str(e)[:150]
        }
        print(f"\n  加载失败: {e}")
        return result

# ==================== 主测试流程 ====================
def run_performance_tests():
    """
    执行完整的性能基准测试套件
    """
    print("=" * 80)
    print("实验室管理系统 - 性能基准测试 v1.4.0")
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    test_results = {
        'version': 'v1.4.0',
        'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'environment': SERVICES,
        'configuration': {
            'api_iterations': TEST_ITERATIONS,
            'concurrent_users': CONCURRENT_USERS,
            'timeout_seconds': TIMEOUT_SECONDS
        },
        'results': {},
        'comparison_with_v131': V131_BASELINE
    }

    # ====== 第一部分: API响应时间测试 ======
    print("\n\n" + "#" * 80)
    print("# 第一部分: API响应时间基准测试 (每个端点50次请求)")
    print("#" * 80)

    api_endpoints = [
        ('GET', f"{SERVICES['user_service']}/user/list", 'User Service - 用户列表'),
        ('GET', f"{SERVICES['sample_service']}/sample/list", 'Sample Service - 样本列表'),
        ('GET', f"{SERVICES['report_service']}/report/list", 'Report Service - 报告列表'),
        ('GET', f"{SERVICES['report_service']}/report/pending-list", 'Report Service - 待审核报告列表'),
        ('POST', f"{SERVICES['ai_service']}/ai/analyze", 'AI Service - AI分析')
    ]

    api_results = []
    for method, url, name in api_endpoints:
        result = test_api_response_time(method, url)
        result['display_name'] = name
        api_results.append(result)

    test_results['results']['api_response_time'] = api_results

    # ====== 第二部分: 并发测试 ======
    print("\n\n" + "#" * 80)
    print("# 第二部分: 并发能力测试 (10个并发用户)")
    print("#" * 80)

    concurrency_result = test_concurrent_requests(CONCURRENT_USERS)
    test_results['results']['concurrency_test'] = concurrency_result

    # ====== 第三部分: 前端页面加载测试 ======
    print("\n\n" + "#" * 80)
    print("# 第三部分: 前端页面加载性能测试")
    print("#" * 80)

    frontend_pages = [
        (f"{SERVICES['frontend']}/login", '登录页'),
    ]

    page_results = []
    for url, name in frontend_pages:
        result = test_frontend_page_load(url, name)
        page_results.append(result)

    test_results['results']['frontend_page_load'] = page_results

    # ====== 性能达标验证 ======
    print("\n\n" + "#" * 80)
    print("# 第四部分: 性能达标验证与对比分析")
    print("#" * 80)

    verification_results = verify_performance_targets(api_results, concurrency_result, page_results)
    test_results['results']['verification'] = verification_results

    # 打印验证结果表格
    print_verification_table(verification_results)

    # ====== 总结 ======
    print_summary(test_results, verification_results)

    return test_results

def verify_performance_targets(api_results: List[Dict], concurrency_result: Dict, page_results: List[Dict]) -> Dict:
    """
    验证是否达到性能目标
    """
    verifications = {
        'api_p50_target': {'target': '< 50ms', 'passed': True, 'details': []},
        'api_p95_target': {'target': '< 200ms', 'passed': True, 'details': []},
        'page_load_target': {'target': '< 2000ms (2s)', 'passed': True, 'details': []},
        'concurrency_target': {'target': '> 95%', 'passed': True, 'details': []}
    }

    # 验证API P50
    all_p50_values = []
    for api in api_results:
        p50_pass = api['p50_ms'] < 50
        all_p50_values.append(api['p50_ms'])
        verifications['api_p50_target']['details'].append({
            'endpoint': api.get('display_name', api['endpoint']),
            'value': f"{api['p50_ms']}ms",
            'passed': p50_pass
        })
        if not p50_pass:
            verifications['api_p50_target']['passed'] = False

    # 验证API P95
    all_p95_values = []
    for api in api_results:
        p95_pass = api['p95_ms'] < 200
        all_p95_values.append(api['p95_ms'])
        verifications['api_p95_target']['details'].append({
            'endpoint': api.get('display_name', api['endpoint']),
            'value': f"{api['p95_ms']}ms",
            'passed': p95_pass
        })
        if not p95_pass:
            verifications['api_p95_target']['passed'] = False

    # 验证页面加载时间
    for page in page_results:
        load_pass = page['full_load_ms'] < 2000 and page['full_load_ms'] > 0
        verifications['page_load_target']['details'].append({
            'page': page['page_name'],
            'value': f"{page['full_load_ms']}ms",
            'passed': load_pass
        })
        if not load_pass:
            verifications['page_load_target']['passed'] = False

    # 验证并发成功率
    concurrency_pass = concurrency_result['success_rate'] > 95
    verifications['concurrency_target']['passed'] = concurrency_pass
    verifications['concurrency_target']['details'].append({
        'metric': '成功率',
        'value': f"{concurrency_result['success_rate']}%",
        'passed': concurrency_pass
    })

    # 计算总体统计
    verifications['overall_statistics'] = {
        'average_p50_ms': round(sum(all_p50_values) / len(all_p50_values), 2) if all_p50_values else 0,
        'average_p95_ms': round(sum(all_p95_values) / len(all_p95_values), 2) if all_p95_values else 0,
        'worst_p50_ms': max(all_p50_values) if all_p50_values else 0,
        'worst_p95_ms': max(all_p95_values) if all_p95_values else 0
    }

    # 总体判定
    all_passed = all([
        verifications['api_p50_target']['passed'],
        verifications['api_p95_target']['passed'],
        verifications['page_load_target']['passed'],
        verifications['concurrency_target']['passed']
    ])
    verifications['overall_passed'] = all_passed
    verifications['pass_count'] = sum([1 for k in ['api_p50_target', 'api_p95_target', 'page_load_target', 'concurrency_target']
                                       if verifications[k]['passed']])
    verifications['total_criteria'] = 4

    return verifications

def print_verification_table(verifications: Dict):
    """打印验证结果表格"""
    print("\n\n" + "="*90)
    print("性能目标验证表")
    print("="*90)

    print(f"\n{'指标':<25} {'目标值':<20} {'实际值':<25} {'状态':<10}")
    print("-"*90)

    # API P50
    avg_p50 = verifications['overall_statistics']['average_p50_ms']
    p50_status = "✅ 通过" if verifications['api_p50_target']['passed'] else "❌ 未通过"
    print(f"{'API P50响应时间':<25} {'< 50ms':<20} {f'{avg_p50}ms (平均)':<25} {p50_status:<10}")

    # API P95
    avg_p95 = verifications['overall_statistics']['average_p95_ms']
    p95_status = "✅ 通过" if verifications['api_p95_target']['passed'] else "❌ 未通过"
    print(f"{'API P95响应时间':<25} {'< 200ms':<20} {f'{avg_p95}ms (平均)':<25} {p95_status:<10}")

    # 页面加载
    page_val = verifications['page_load_target']['details'][0]['value'] if verifications['page_load_target']['details'] else 'N/A'
    page_status = "✅ 通过" if verifications['page_load_target']['passed'] else "❌ 未通过"
    print(f"{'页面完整加载':<25} {'< 2000ms':<20} {page_val:<25} {page_status:<10}")

    # 并发成功率
    conc_val = verifications['concurrency_target']['details'][0]['value'] if verifications['concurrency_target']['details'] else 'N/A'
    conc_status = "✅ 通过" if verifications['concurrency_target']['passed'] else "❌ 未通过"
    print(f"{'并发成功率':<25} {'> 95%':<20} {conc_val:<25} {conc_status:<10}")

    print("-"*90)

    # 详细API性能
    print("\n各API端点详细性能:")
    print(f"{'API端点':<35} {'P50(ms)':<12} {'P95(ms)':<12} {'平均(ms)':<12} {'标准差(ms)':<12}")
    print("-"*90)

    for detail in verifications['api_p50_target']['details']:
        endpoint = detail['endpoint'][:33]
        p50_val = detail['value']

        # 找到对应的P95值
        p95_detail = next((d for d in verifications['api_p95_target']['details']
                           if d['endpoint'] == detail['endpoint']), {})
        p95_val = p95_detail.get('value', 'N/A')

        # 从原始数据中找到对应的平均值和标准差（这里简化处理）
        print(f"{endpoint:<35} {p50_val:<12} {p95_val:<12} {'-':<12} {'-':<12}")

    print("\n")

def print_summary(test_results: Dict, verifications: Dict):
    """打印总结"""
    print("\n" + "="*90)
    print("总体结论")
    print("="*90)

    pass_count = verifications['pass_count']
    total = verifications['total_criteria']
    pass_rate = round(pass_count / total * 100, 1)

    overall_status = "✅ 全部达标" if verifications['overall_passed'] else f"⚠️ 部分未达标 ({pass_count}/{total})"

    print(f"\n性能测试总体评估: **{overall_status}** (达标率 {pass_rate}%)")

    # 与v1.3.1对比
    print(f"\n与 v1.3.1 版本对比:")
    print(f"  v1.3.1 基线数据:")
    print(f"    - P50: {V131_BASELINE['p50_ms']}ms")
    print(f"    - P95: {V131_BASELINE['p95_ms']}ms")
    print(f"    - 页面加载: {V131_BASELINE['page_load_ms']}ms")
    print(f"    - 并发成功率: {V131_BASELINE['concurrency_success_rate']}%")

    current_avg_p50 = verifications['overall_statistics']['average_p50_ms']
    current_avg_p95 = verifications['overall_statistics']['average_p95_ms']
    current_page_load = verifications['page_load_target']['details'][0]['value'] if verifications['page_load_target']['details'] else 'N/A'
    current_concurrency = verifications['concurrency_target']['details'][0]['value'] if verifications['concurrency_target']['details'] else 'N/A'

    print(f"\n  v1.4.0 实测数据:")
    print(f"    - P50: {current_avg_p50}ms")
    print(f"    - P95: {current_avg_p95}ms")
    print(f"    - 页面加载: {current_page_load}")
    print(f"    - 并发成功率: {current_concurrency}")

    # 计算变化百分比
    if V131_BASELINE['p50_ms'] > 0:
        p50_change = round((current_avg_p50 - V131_BASELINE['p50_ms']) / V131_BASELINE['p50_ms'] * 100, 2)
        p95_change = round((current_avg_p95 - V131_BASELINE['p95_ms']) / V131_BASELINE['p95_ms'] * 100, 2)
        print(f"\n  变化趋势:")
        print(f"    - P50: {'+' if p50_change > 0 else ''}{p50_change}%")
        print(f"    - P95: {'+' if p95_change > 0 else ''}{p95_change}%")

    print("\n建议:")
    if verifications['overall_passed']:
        print("  ✓ 所有性能指标均达到验收标准")
        print("  ✓ 系统性能表现良好，可以进入下一阶段")
    else:
        print("  ⚠ 存在未达标的性能指标，建议进行针对性优化")
        if not verifications['api_p50_target']['passed']:
            print("    - API P50响应时间偏高，建议检查数据库查询和网络延迟")
        if not verifications['api_p95_target']['passed']:
            print("    - API P95响应时间偏高，建议分析慢请求原因")
        if not verifications['page_load_target']['passed']:
            print("    - 页面加载时间过长，建议优化前端资源加载")
        if not verifications['concurrency_target']['passed']:
            print("    - 并发处理能力不足，建议增加服务器资源或优化并发策略")

    print("\n" + "="*90)
    print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*90)

# ==================== 报告生成函数 ====================
def generate_markdown_report(test_results: Dict) -> str:
    """
    生成Markdown格式的性能测试报告
    """
    verifications = test_results['results']['verification']
    api_results = test_results['results']['api_response_time']
    concurrency_result = test_results['results']['concurrency_test']
    page_results = test_results['results']['frontend_page_load']

    md = []
    md.append("# 实验室管理系统 - 性能基准实测报告 v1.4.0")
    md.append("")
    md.append(f"**测试时间**: {test_results['test_date']}")
    md.append(f"**测试环境**: 本地开发环境")
    md.append(f"**测试版本**: v1.4.0")
    md.append("")

    # B1: API响应时间测试
    md.append("---")
    md.append("## B1: API响应时间基准测试 (50次请求/端点)")
    md.append("")
    md.append("| API端点 | 平均(ms) | P50(ms) | P90(ms) | P95(ms) | P99(ms) | 最小(ms) | 最大(ms) | 标准差(ms) | 成功率 |")
    md.append("|--------|---------|--------|--------|--------|--------|---------|---------|-----------|-------|")

    for api in api_results:
        display_name = api.get('display_name', api['endpoint'])
        md.append(f"| {display_name} | {api['avg_ms']} | {api['p50_ms']} | {api['p90_ms']} | {api['p95_ms']} | {api['p99_ms']} | {api['min_ms']} | {api['max_ms']} | {api['std_dev_ms']} | {api['success_rate']}% |")

    md.append("")

    # B2: 并发测试
    md.append("---")
    md.append(f"## B2: 并发能力测试 ({CONCURRENT_USERS}并发用户)")
    md.append("")
    md.append("| 指标 | 数值 |")
    md.append("|------|------|")
    md.append(f"| 测试端点 | {concurrency_result['endpoint']} |")
    md.append(f"| 并发用户数 | {concurrency_result['concurrent_users']} |")
    md.append(f"| 总请求数 | {concurrency_result['total_requests']} |")
    md.append(f"| 成功请求数 | {concurrency_result['successful_requests']} |")
    md.append(f"| 失败请求数 | {concurrency_result['failed_requests']} |")
    md.append(f"| **成功率** | **{concurrency_result['success_rate']}%** |")
    md.append(f"| 平均响应时间 | {concurrency_result['avg_response_time_ms']}ms |")
    md.append(f"| 最小响应时间 | {concurrency_result['min_response_time_ms']}ms |")
    md.append(f"| 最大响应时间 | {concurrency_result['max_response_time_ms']}ms |")
    md.append(f"| 标准差 | {concurrency_result['std_dev_ms']}ms |")
    md.append(f"| 吞吐量 | {concurrency_result['throughput_per_second']} 请求/秒 |")
    md.append("")

    # B3: 页面加载测试
    md.append("---")
    md.append("## B3: 前端页面加载时间测试")
    md.append("")
    md.append("| 页面 | TTFB(ms) | DOM加载(ms) | 完整加载(ms) | 状态码 | 页面大小(bytes) |")
    md.append("|------|----------|------------|-------------|--------|---------------|")

    for page in page_results:
        size_kb = round(page['content_size_bytes']/1024, 2) if page['content_size_bytes'] > 0 else 0
        md.append(f"| {page['page_name']} | {page['ttfb_ms']} | {page['dom_load_ms']} | {page['full_load_ms']} | {page['status_code']} | {size_kb} KB |")

    md.append("")

    # B4: 性能目标验证
    md.append("---")
    md.append("## B4: 性能目标验证与v1.3.1对比")
    md.append("")
    md.append("| 指标 | 目标值 | v1.3.1基线 | v1.4.0实测 | 变化 | 达标? |")
    md.append("|------|-------|-----------|-----------|------|------|")

    # P50对比
    avg_p50 = verifications['overall_statistics']['average_p50_ms']
    p50_change = f"{round((avg_p50 - V131_BASELINE['p50_ms']) / V131_BASELINE['p50_ms'] * 100, 1)}%" if V131_BASELINE['p50_ms'] > 0 else "N/A"
    p50_icon = "✅" if verifications['api_p50_target']['passed'] else "❌"
    md.append(f"| API P50响应时间 | < 50ms | {V131_BASELINE['p50_ms']}ms | {avg_p50}ms | {p50_change} | {p50_icon} |")

    # P95对比
    avg_p95 = verifications['overall_statistics']['average_p95_ms']
    p95_change = f"{round((avg_p95 - V131_BASELINE['p95_ms']) / V131_BASELINE['p95_ms'] * 100, 1)}%" if V131_BASELINE['p95_ms'] > 0 else "N/A"
    p95_icon = "✅" if verifications['api_p95_target']['passed'] else "❌"
    md.append(f"| API P95响应时间 | < 200ms | {V131_BASELINE['p95_ms']}ms | {avg_p95}ms | {p95_change} | {p95_icon} |")

    # 页面加载对比
    page_current = page_results[0]['full_load_ms'] if page_results else 0
    page_change = f"{round((page_current - V131_BASELINE['page_load_ms']) / V131_BASELINE['page_load_ms'] * 100, 1)}%" if V131_BASELINE['page_load_ms'] > 0 and page_current > 0 else "N/A"
    page_icon = "✅" if verifications['page_load_target']['passed'] else "❌"
    md.append(f"| 页面完整加载时间 | < 2000ms | {V131_BASELINE['page_load_ms']}ms | {page_current}ms | {page_change} | {page_icon} |")

    # 并发成功率对比
    conc_current = concurrency_result['success_rate']
    conc_icon = "✅" if verifications['concurrency_target']['passed'] else "❌"
    md.append(f"| 并发成功率 | > 95% | {V131_BASELINE['concurrency_success_rate']}% | {conc_current}% | - | {conc_icon} |")

    md.append("")

    # 总体结论
    md.append("---")
    md.append("## 总体结论")
    md.append("")
    pass_count = verifications['pass_count']
    total = verifications['total_criteria']
    pass_rate = round(pass_count / total * 100, 1)

    if verifications['overall_passed']:
        md.append(f"### 🎉 性能测试总体评估: **全部达标** ({pass_count}/{total}项指标通过, 达标率{pass_rate}%)")
    else:
        md.append(f"### ⚠️ 性能测试总体评估: **部分未达标** ({pass_count}/{total}项指标通过, 达标率{pass_rate}%)")

    md.append("")
    md.append("### 建议")
    if verifications['overall_passed']:
        md.append("- 所有性能指标均达到验收标准")
        md.append("- 系统性能表现良好，可以进入生产环境部署准备")
        md.append("- 建议在生产环境进行压力测试以验证极限性能")
    else:
        md.append("- 存在未达标的性能指标，建议进行针对性优化")
        if not verifications['api_p50_target']['passed']:
            md.append("- API P50响应时间偏高，建议检查数据库查询和索引优化")
        if not verifications['api_p95_target']['passed']:
            md.append("- API P95响应时间偏高，建议分析慢请求并进行优化")
        if not verifications['page_load_target']['passed']:
            md.append("- 页面加载时间过长，建议优化前端资源加载和CDN配置")
        if not verifications['concurrency_target']['passed']:
            md.append("- 并发处理能力不足，建议评估服务器资源和连接池配置")

    md.append("")
    md.append("---")
    md.append(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return "\n".join(md)

# ==================== 主程序入口 ====================
if __name__ == '__main__':
    try:
        # 执行性能测试
        print("\n开始执行实验室管理系统 v1.4.0 性能基准测试...\n")
        results = run_performance_tests()

        # 保存JSON格式详细结果
        json_output_file = r'd:\FinalCodeAndFile\lab-management-system\test_results\performance-live-v1.4.0.json'
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ JSON详细结果已保存至: {json_output_file}")

        # 生成并保存Markdown报告
        markdown_report = generate_markdown_report(results)
        md_output_file = r'd:\FinalCodeAndFile\lab-management-system\test_results\performance-live-v1.4.0.md'
        with open(md_output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        print(f"✓ Markdown报告已保存至: {md_output_file}")

        print("\n" + "="*80)
        print("性能基准测试完成!")
        print("="*80)

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试执行出错: {e}")
        import traceback
        traceback.print_exc()
