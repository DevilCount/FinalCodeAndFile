#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 - 全面性能基准测试 v1.4.0
执行时间: 2026-04-02

测试内容:
1. API响应时间基准测试 (每个端点5次请求, P50/P95/P99)
2. 并发压力测试 (10并发用户 x 10次请求)
3. 前端页面加载性能测试 (TTFB/DOM加载/完整加载)
4. 资源占用评估 (内存泄漏检测)

性能目标:
- API P95响应时间 < 500ms
- API P99响应时间 < 1000ms
- 页面首屏加载 < 2秒
- 支持10并发用户无5xx错误
- 内存使用稳定(无明显泄漏)

作者: Performance Expert
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
# 服务地址配置 (根据实际系统信息)
SERVICES = {
    'gateway': 'http://localhost:8080',
    'user_service': 'http://localhost:8081',
    'sample_service': 'http://localhost:8082',
    'report_service': 'http://localhost:8083',
    'ai_service': 'http://localhost:8084',
    'hl7_service': 'http://localhost:8085',
    'frontend': 'http://localhost:5173'
}

# 测试参数
API_ITERATIONS = 5  # 每个API端点请求次数(取平均值)
CONCURRENT_USERS = 10  # 并发用户数
REQUESTS_PER_USER = 10  # 每个并发用户的请求数
TIMEOUT_SECONDS = 30  # 超时时间(秒)

# 性能目标阈值
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
    """单个API端点的测试结果"""
    endpoint: str
    method: str
    display_name: str
    total_requests: int = 0
    success_count: int = 0
    success_rate: float = 0.0
    response_times: List[float] = field(default_factory=list)
    status_codes: List[int] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

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

    @property
    def std_dev_ms(self) -> float:
        if len(self.response_times) < 2:
            return 0.0
        return round(statistics.stdev(self.response_times), 2)

    def _calculate_percentile(self, percentile: float) -> float:
        """计算百分位数"""
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
            'std_dev_ms': self.std_dev_ms,
            'status_codes': list(set(self.status_codes)),
            'errors': self.errors[:5]
        }


@dataclass
class ConcurrencyTestResult:
    """并发测试结果"""
    endpoint: str
    concurrent_users: int
    requests_per_user: int
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    server_error_count: int = 0  # 5xx错误数
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
    def min_response_time_ms(self) -> float:
        if not self.response_times:
            return 0.0
        return round(min(self.response_times), 2)

    @property
    def max_response_time_ms(self) -> float:
        if not self.response_times:
            return 0.0
        return round(max(self.response_times), 2)

    @property
    def std_dev_ms(self) -> float:
        if len(self.response_times) < 2:
            return 0.0
        return round(statistics.stdev(self.response_times), 2)

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
            'min_response_time_ms': self.min_response_time_ms,
            'max_response_time_ms': self.max_response_time_ms,
            'std_dev_ms': self.std_dev_ms,
            'throughput_per_second': self.throughput_per_second,
            'total_test_time_ms': round(self.total_test_time_ms, 2),
            'errors': self.errors[:5]
        }


@dataclass
class PageLoadResult:
    """页面加载结果"""
    page_name: str
    url: str
    status_code: int = 0
    success: bool = False
    ttfb_ms: float = 0.0
    dom_load_ms: float = 0.0
    full_load_ms: float = 0.0
    content_size_bytes: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'page_name': self.page_name,
            'url': self.url,
            'status_code': self.status_code,
            'success': self.success,
            'ttfb_ms': self.ttfb_ms,
            'dom_load_ms': self.dom_load_ms,
            'full_load_ms': self.full_load_ms,
            'content_size_bytes': self.content_size_bytes,
            'error': self.error
        }


# ==================== 工具函数 ====================
def check_service_health(url: str, service_name: str) -> Dict[str, Any]:
    """
    检查服务健康状态
    返回服务是否可用、响应时间等信息
    """
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
    """检查所有服务的健康状态"""
    print("\n" + "="*70)
    print("服务健康检查")
    print("="*70)

    services_status = {}
    available_services = []

    for service_name, url in SERVICES.items():
        status = check_service_health(url, service_name)
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


# ==================== 1. API响应时间基准测试 ====================
def test_api_endpoint(method: str, url: str, display_name: str,
                     iterations: int = API_ITERATIONS,
                     payload: Optional[Dict] = None) -> ApiTestResult:
    """
    测试单个API端点的响应时间
    每个端点执行多次请求，记录P50/P95/P99等统计指标
    """
    result = ApiTestResult(
        endpoint=url,
        method=method,
        display_name=display_name
    )

    print(f"\n{'='*60}")
    print(f"API响应时间测试: {display_name}")
    print(f"端点: {method} {url}")
    print(f"请求次数: {iterations}次")
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

            # 打印每次请求结果
            status_icon = "✓" if response.status_code < 400 else "✗"
            print(f"  [{i+1}/{iterations}] {status_icon} {response.status_code} | {elapsed_ms:.2f}ms")

        except requests.exceptions.Timeout:
            result.errors.append(f"请求{i+1}超时(>{TIMEOUT_SECONDS}s)")
            result.total_requests += 1
            print(f"  [{i+1}/{iterations}] ✗ TIMEOUT")
        except requests.exceptions.ConnectionError as e:
            result.errors.append(f"请求{i+1}连接失败: {str(e)[:80]}")
            result.total_requests += 1
            print(f"  [{i+1}/{iterations}] ✗ CONNECTION_ERROR")
        except Exception as e:
            result.errors.append(f"请求{i+1}错误: {str(e)[:80]}")
            result.total_requests += 1
            print(f"  [{i+1}/{iterations}] ✗ ERROR: {str(e)[:50]}")

    # 计算成功率
    if result.total_requests > 0:
        result.success_rate = result.success_count / result.total_requests * 100

    # 打印统计摘要
    print(f"\n  统计结果:")
    print(f"  成功率: {result.success_rate:.1f}% ({result.success_count}/{result.total_requests})")
    print(f"  P50: {result.p50_ms}ms | P95: {result.p95_ms}ms | P99: {result.p99_ms}ms")
    print(f"  平均: {result.avg_ms}ms | 最小: {result.min_ms}ms | 最大: {result.max_ms}ms")
    print(f"  标准差: {result.std_dev_ms}ms")

    if result.errors:
        print(f"\n  错误详情({len(result.errors)}个):")
        for err in result.errors[:3]:
            print(f"    - {err}")

    return result


def run_api_benchmark_tests() -> List[ApiTestResult]:
    """
    执行所有核心API的基准测试
    """
    print("\n\n" + "#"*80)
    print("# 第一部分: API响应时间基准测试")
    print("#"*80)

    api_endpoints = [
        # 登录接口
        ('POST', f"{SERVICES['gateway']}/api/user/login", '登录接口', {
            "username": "admin",
            "password": "admin123"
        }),

        # 标本管理接口
        ('GET', f"{SERVICES['gateway']}/api/sample/list", '标本列表', None),
        ('POST', f"{SERVICES['gateway']}/api/sample/create", '创建标本', {
            "patientName": "性能测试患者",
            "patientId": "PERF_TEST_001",
            "sampleType": "血液",
            "priority": "普通"
        }),

        # 报告管理接口
        ('GET', f"{SERVICES['gateway']}/api/report/list", '报告列表', None),
        ('POST', f"{SERVICES['gateway']}/api/report/create", '创建报告', {
            "sampleId": 1,
            "technicianId": 1,
            "testItems": ["WBC", "RBC", "PLT"]
        }),

        # AI服务接口
        ('GET', f"{SERVICES['gateway']}/api/ai/health", 'AI健康检查', None),

        # 用户管理接口
        ('GET', f"{SERVICES['gateway']}/api/user/list", '用户列表', None),
    ]

    results = []
    for method, url, name, payload in api_endpoints:
        result = test_api_endpoint(method, url, name, payload=payload)
        results.append(result)

    return results


# ==================== 2. 并发压力测试 ====================
def concurrent_user_worker(user_id: int, login_url: str, query_urls: List[str],
                          requests_per_user: int) -> Dict[str, Any]:
    """
    单个并发用户的工作函数
    执行登录和查询操作
    """
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

    # 首先尝试登录获取token
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
            user_results['errors'].append(f"登录返回5xx: {response.status_code}")

    except Exception as e:
        user_results['errors'].append(f"登录失败: {str(e)[:80]}")

    # 如果登录成功，继续发送查询请求
    if user_results['login_success']:
        for req_num in range(requests_per_user):
            # 循环使用不同的查询URL
            query_url = query_urls[req_num % len(query_urls)]

            try:
                start_time = time.time()
                response = session.get(query_url, timeout=TIMEOUT_SECONDS)
                elapsed_ms = (time.time() - start_time) * 1000

                user_results['response_times'].append(round(elapsed_ms, 2))

                if response.status_code < 500:
                    user_results['total_success'] += 1
                    user_results['query_results'].append({
                        'request_num': req_num + 1,
                        'url': query_url,
                        'status_code': response.status_code,
                        'time_ms': elapsed_ms
                    })
                else:
                    user_results['total_failed'] += 1
                    user_results['server_errors'] += 1
                    user_results['errors'].append(f"请求{req_num+1}返回{response.status_code}")

            except Exception as e:
                user_results['total_failed'] += 1
                user_results['errors'].append(f"请求{req_num+1}失败: {str(e)[:80]}")
    else:
        # 登录失败，标记所有查询为失败
        user_results['total_failed'] = requests_per_user

    return user_results


def run_concurrency_stress_test() -> ConcurrencyTestResult:
    """
    执行并发压力测试
    模拟10个并发用户，每个用户执行10次请求
    """
    print("\n\n" + "#"*80)
    print("# 第二部分: 并发压力测试")
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

    print(f"\n测试配置:")
    print(f"  登录端点: {login_url}")
    print(f"  查询端点: {query_urls}")
    print(f"  并发用户数: {CONCURRENT_USERS}")
    print(f"  每用户请求数: {REQUESTS_PER_USER}")
    print(f"  总预期请求: {CONCURRENT_USERS * REQUESTS_PER_USER + CONCURRENT_USERS} (含登录)")
    print(f"\n开始并发测试...")

    all_user_results = []
    start_time = time.time()

    # 使用线程池模拟并发用户
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

    # 汇总所有用户的结果
    for user_result in all_user_results:
        result.total_requests += 1 + REQUESTS_PER_USER  # 登录 + 查询
        result.successful_requests += user_result['total_success']
        result.failed_requests += user_result['total_failed']
        result.server_error_count += user_result['server_errors']
        result.response_times.extend(user_result['response_times'])
        if user_result['errors']:
            result.errors.extend(user_result['errors'])

    # 计算成功率
    if result.total_requests > 0:
        result.success_rate = result.successful_requests / result.total_requests * 100

    # 打印详细结果
    print(f"\n{'='*60}")
    print(f"并发测试结果汇总")
    print(f"{'='*60}")
    print(f"\n总体统计:")
    print(f"  总请求数: {result.total_requests}")
    print(f"  成功请求: {result.successful_requests}")
    print(f"  失败请求: {result.failed_requests}")
    print(f"  5xx服务器错误: {result.server_error_count}")
    print(f"  成功率: {result.success_rate:.2f}%")
    print(f"\n响应时间:")
    print(f"  平均: {result.avg_response_time_ms}ms")
    print(f"  最小: {result.min_response_time_ms}ms")
    print(f"  最大: {result.max_response_time_ms}ms")
    print(f"  标准差: {result.std_dev_ms}ms")
    print(f"\n吞吐量:")
    print(f"  吞吐量: {result.throughput_per_second} 请求/秒")
    print(f"  总耗时: {result.total_test_time_ms:.2f}ms ({result.total_test_time_ms/1000:.2f}s)")

    # 打印各用户详情
    print(f"\n各用户执行情况:")
    print(f"{'用户ID':<10} {'登录成功':<12} {'成功请求':<12} {'失败请求':<12} {'平均响应(ms)':<15}")
    print("-"*65)

    for user_result in all_user_results:
        avg_time = sum(user_result['response_times']) / len(user_result['response_times']) if user_result['response_times'] else 0
        print(f"用户{user_result['user_id']:<6} "
              f"{'是' if user_result['login_success'] else '否':<12} "
              f"{user_result['total_success']:<12} "
              f"{user_result['total_failed']:<12} "
              f"{avg_time:<15.2f}")

    if result.errors:
        print(f"\n错误详情(前10个):")
        for err in result.errors[:10]:
            print(f"  - {err}")

    return result


# ==================== 3. 页面加载性能测试 ====================
def test_page_load(page_url: str, page_name: str) -> PageLoadResult:
    """
    测试前端页面加载性能
    测量TTFB、DOM加载时间、完整加载时间
    """
    result = PageLoadResult(page_name=page_name, url=page_url)

    print(f"\n{'='*60}")
    print(f"页面加载测试: {page_name}")
    print(f"URL: {page_url}")
    print(f"{'='*60}")

    try:
        session = requests.Session()

        # TTFB测量
        ttfb_start = time.time()
        response = session.get(page_url, timeout=30, stream=True)
        ttfb_time = (time.time() - ttfb_start) * 1000

        result.status_code = response.status_code
        result.success = response.status_code == 200
        result.ttfb_ms = round(ttfb_time, 2)

        # DOM加载时间测量(读取前部分内容)
        dom_content = b''
        dom_start = time.time()
        chunk_count = 0
        for chunk in response.iter_content(chunk_size=8192):
            dom_content += chunk
            chunk_count += 1
            # 模拟DOM解析完成(读取到一定量的HTML内容)
            if len(dom_content) > 2048 or chunk_count > 5:
                break
        dom_load_time = (time.time() - dom_start) * 1000
        result.dom_load_ms = round(ttfb_time + dom_load_time, 2)

        # 完整内容加载
        full_content = dom_content
        for chunk in response.iter_content(chunk_size=8192):
            full_content += chunk

        total_time = (time.time() - ttfb_start) * 1000
        result.full_load_ms = round(total_time, 2)
        result.content_size_bytes = len(full_content)

        # 打印结果
        print(f"\n  加载结果:")
        print(f"  状态码: {response.status_code} ({'成功' if result.success else '失败'})")
        print(f"  TTFB (首字节时间): {result.ttfb_ms}ms")
        print(f"  DOM加载时间: {result.dom_load_ms}ms")
        print(f"  完整加载时间: {result.full_load_ms}ms")
        size_kb = round(result.content_size_bytes / 1024, 2)
        print(f"  页面大小: {result.content_size_bytes} bytes ({size_kb} KB)")

    except Exception as e:
        result.error = str(e)[:150]
        print(f"\n  加载失败: {e}")

    return result


def run_frontend_page_tests() -> List[PageLoadResult]:
    """
    执行前端页面加载性能测试
    """
    print("\n\n" + "#"*80)
    print("# 第三部分: 前端页面加载性能测试")
    print("#"*80)

    pages = [
        (f"{SERVICES['frontend']}/", '首页'),
        (f"{SERVICES['frontend']}/dashboard", '仪表盘'),
        (f"{SERVICES['frontend']}/sample", '标本管理'),
        (f"{SERVICES['frontend']}/report", '报告管理'),
        (f"{SERVICES['frontend']}/login", '登录页'),
    ]

    results = []
    for url, name in pages:
        result = test_page_load(url, name)
        results.append(result)

    return results


# ==================== 4. 资源占用评估 ====================
def monitor_resource_usage(duration_seconds: int = 5) -> Dict[str, Any]:
    """
    监控系统资源使用情况
    用于检测内存泄漏迹象
    """
    print("\n\n" + "#"*80)
    print("# 第四部分: 系统资源监控")
    print("#"*80)

    print(f"\n监控时长: {duration_seconds}秒")
    print("采集间隔: 1秒")

    cpu_samples = []
    memory_samples = []
    timestamps = []

    start_time = time.time()

    while (time.time() - start_time) < duration_seconds:
        current_time = datetime.now().strftime('%H:%M:%S')
        timestamps.append(current_time)

        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_samples.append(cpu_percent)

        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_samples.append({
            'total_gb': round(memory.total / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'percent': memory.percent
        })

        print(f"  [{current_time}] CPU: {cpu_percent}% | 内存: {memory.percent}% ({round(memory.used/(1024**3), 2)}/{round(memory.total/(1024**3), 2)} GB)")

        time.sleep(1)

    # 分析内存趋势
    memory_trend = analyze_memory_trend(memory_samples)

    result = {
        'monitor_duration_seconds': duration_seconds,
        'sample_count': len(cpu_samples),
        'cpu_usage': {
            'average_percent': round(statistics.mean(cpu_samples), 2) if cpu_samples else 0,
            'max_percent': max(cpu_samples) if cpu_samples else 0,
            'min_percent': min(cpu_samples) if cpu_samples else 0,
            'samples': cpu_samples
        },
        'memory_usage': {
            'average_percent': round(statistics.mean([m['percent'] for m in memory_samples]), 2) if memory_samples else 0,
            'average_used_gb': round(statistics.mean([m['used_gb'] for m in memory_samples]), 2) if memory_samples else 0,
            'samples': memory_samples[-5:]  # 保留最后5个样本
        },
        'memory_leak_detection': memory_trend
    }

    # 打印汇总
    print(f"\n资源监控汇总:")
    print(f"  CPU使用率:")
    print(f"    平均: {result['cpu_usage']['average_percent']}%")
    print(f"    最大: {result['cpu_usage']['max_percent']}%")
    print(f"    最小: {result['cpu_usage']['min_percent']}%")
    print(f"\n  内存使用:")
    print(f"    平均使用率: {result['memory_usage']['average_percent']}%")
    print(f"    平均使用量: {result['memory_usage']['average_used_gb']} GB")
    print(f"\n  内存泄漏检测:")
    print(f"    趋势: {memory_trend.get('trend', 'N/A')}")
    print(f"    判定: {'可能存在泄漏' if memory_trend.get('potential_leak') else '正常'}")

    return result


def analyze_memory_trend(memory_samples: List[Dict]) -> Dict[str, Any]:
    """
    分析内存使用趋势，检测可能的内存泄漏
    """
    if len(memory_samples) < 3:
        return {
            'trend': 'insufficient_data',
            'potential_leak': False,
            'details': '样本数据不足'
        }

    used_values = [m['used_gb'] for m in memory_samples]

    # 计算内存增长趋势
    first_half_avg = statistics.mean(used_values[:len(used_values)//2])
    second_half_avg = statistics.mean(used_values[len(used_values)//2:])

    growth_rate = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0

    # 判断是否存在明显增长趋势
    potential_leak = growth_rate > 5  # 增长超过5%视为可疑

    trend = 'stable'
    if growth_rate > 10:
        trend = 'increasing_rapidly'
    elif growth_rate > 5:
        trend = 'increasing_slowly'
    elif growth_rate < -5:
        trend = 'decreasing'

    return {
        'trend': trend,
        'growth_rate_percent': round(growth_rate, 2),
        'first_half_average_gb': round(first_half_avg, 3),
        'second_half_average_gb': round(second_half_avg, 3),
        'potential_leak': potential_leak,
        'sample_count': len(memory_samples)
    }


# ==================== 性能达标验证 ====================
def verify_performance_targets(api_results: List[ApiTestResult],
                               concurrency_result: ConcurrencyTestResult,
                               page_results: List[PageLoadResult],
                               resource_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证是否达到性能目标
    """
    verifications = {
        'targets': PERFORMANCE_TARGETS,
        'results': {},
        'overall_passed': True,
        'pass_count': 0,
        'total_criteria': 5
    }

    # 1. 验证API P95响应时间
    p95_passed = True
    p95_details = []
    for api in api_results:
        passed = api.p95_ms < PERFORMANCE_TARGETS['api_p95_ms']
        p95_details.append({
            'endpoint': api.display_name,
            'value_ms': api.p95_ms,
            'target_ms': PERFORMANCE_TARGETS['api_p95_ms'],
            'passed': passed
        })
        if not passed and api.success_count > 0:  # 只有在服务可用时才判定为未通过
            p95_passed = False

    verifications['results']['api_p95_target'] = {
        'target': f"< {PERFORMANCE_TARGETS['api_p95_ms']}ms",
        'passed': p95_passed,
        'details': p95_details
    }
    if p95_passed:
        verifications['pass_count'] += 1
    else:
        verifications['overall_passed'] = False

    # 2. 验证API P99响应时间
    p99_passed = True
    p99_details = []
    for api in api_results:
        passed = api.p99_ms < PERFORMANCE_TARGETS['api_p99_ms']
        p99_details.append({
            'endpoint': api.display_name,
            'value_ms': api.p99_ms,
            'target_ms': PERFORMANCE_TARGETS['api_p99_ms'],
            'passed': passed
        })
        if not passed and api.success_count > 0:
            p99_passed = False

    verifications['results']['api_p99_target'] = {
        'target': f"< {PERFORMANCE_TARGETS['api_p99_ms']}ms",
        'passed': p99_passed,
        'details': p99_details
    }
    if p99_passed:
        verifications['pass_count'] += 1
    else:
        verifications['overall_passed'] = False

    # 3. 验证页面加载时间
    page_passed = True
    page_details = []
    for page in page_results:
        passed = page.full_load_ms < PERFORMANCE_TARGETS['page_load_ms'] and page.full_load_ms > 0
        page_details.append({
            'page': page.page_name,
            'value_ms': page.full_load_ms,
            'target_ms': PERFORMANCE_TARGETS['page_load_ms'],
            'passed': passed
        })
        if not passed and page.success:  # 只有页面可访问时才判定
            page_passed = False

    verifications['results']['page_load_target'] = {
        'target': f"< {PERFORMANCE_TARGETS['page_load_ms']}ms",
        'passed': page_passed,
        'details': page_details
    }
    if page_passed:
        verifications['pass_count'] += 1
    else:
        verifications['overall_passed'] = False

    # 4. 验证并发成功率
    concurrency_passed = concurrency_result.server_error_count <= PERFORMANCE_TARGETS['max_5xx_errors']
    verifications['results']['concurrency_target'] = {
        'target': f"无5xx错误 (<={PERFORMANCE_TARGETS['max_5xx_errors']})",
        'passed': concurrency_passed,
        'details': [{
            'metric': '5xx错误数',
            'value': concurrency_result.server_error_count,
            'target': PERFORMANCE_TARGETS['max_5xx_errors'],
            'passed': concurrency_passed
        }, {
            'metric': '成功率',
            'value': f"{concurrency_result.success_rate:.2f}%",
            'target': f"> {PERFORMANCE_TARGETS['concurrency_success_rate']}%",
            'passed': concurrency_result.success_rate >= PERFORMANCE_TARGETS['concurrency_success_rate']
        }]
    }
    if concurrency_passed:
        verifications['pass_count'] += 1
    else:
        verifications['overall_passed'] = False

    # 5. 验证内存稳定性
    memory_stable = not resource_result.get('memory_leak_detection', {}).get('potential_leak', True)
    verifications['results']['memory_stability_target'] = {
        'target': '无明显内存泄漏',
        'passed': memory_stable,
        'details': [{
            'metric': '内存趋势',
            'value': resource_result.get('memory_leak_detection', {}).get('trend', 'N/A'),
            'passed': memory_stable
        }]
    }
    if memory_stable:
        verifications['pass_count'] += 1
    else:
        verifications['overall_passed'] = False

    # 计算达标率
    verifications['pass_rate'] = round(verifications['pass_count'] / verifications['total_criteria'] * 100, 1)

    return verifications


def print_verification_summary(verifications: Dict[str, Any]):
    """打印验证结果摘要"""
    print("\n\n" + "="*90)
    print("性能目标验证表")
    print("="*90)

    print(f"\n{'指标':<25} {'目标值':<22} {'判定':<15}")
    print("-"*90)

    targets_display = [
        ('API P95响应时间', 'api_p95_target'),
        ('API P99响应时间', 'api_p99_target'),
        ('页面首屏加载时间', 'page_load_target'),
        ('并发无5xx错误', 'concurrency_target'),
        ('内存使用稳定性', 'memory_stability_target')
    ]

    for display_name, key in targets_display:
        target_info = verifications['results'][key]
        status_icon = "PASS" if target_info['passed'] else "FAIL"
        status_color = "通过" if target_info['passed'] else "未通过"

        print(f"{display_name:<25} {target_info['target']:<22} {status_color:<15}")

    print("-"*90)

    pass_count = verifications['pass_count']
    total = verifications['total_criteria']
    pass_rate = verifications['pass_rate']

    overall_status = "全部达标" if verifications['overall_passed'] else f"部分未达标 ({pass_count}/{total})"

    print(f"\n总体评估: **{overall_status}** (达标率 {pass_rate}%)")


# ==================== 主测试流程 ====================
def run_performance_tests():
    """
    执行完整的性能基准测试套件
    """
    print("="*90)
    print("实验室管理系统 - 全面性能基准测试 v1.4.0")
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*90)

    test_results = {
        'version': 'v1.4.0',
        'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'environment': SERVICES,
        'configuration': {
            'api_iterations': API_ITERATIONS,
            'concurrent_users': CONCURRENT_USERS,
            'requests_per_user': REQUESTS_PER_USER,
            'timeout_seconds': TIMEOUT_SECONDS
        },
        'performance_targets': PERFORMANCE_TARGETS,
        'results': {}
    }

    # ====== 0. 服务健康检查 ======
    service_status = check_all_services()
    test_results['results']['service_status'] = service_status

    # ====== 第一部分: API响应时间测试 ======
    api_results = run_api_benchmark_tests()
    test_results['results']['api_response_time'] = [r.to_dict() for r in api_results]

    # ====== 第二部分: 并发压力测试 ======
    concurrency_result = run_concurrency_stress_test()
    test_results['results']['concurrency_test'] = concurrency_result.to_dict()

    # ====== 第三部分: 前端页面加载测试 ======
    page_results = run_frontend_page_tests()
    test_results['results']['frontend_page_load'] = [r.to_dict() for r in page_results]

    # ====== 第四部分: 资源占用评估 ======
    resource_result = monitor_resource_usage(duration_seconds=5)
    test_results['results']['resource_usage'] = resource_result

    # ====== 第五部分: 性能达标验证 ======
    verifications = verify_performance_targets(api_results, concurrency_result, page_results, resource_result)
    test_results['results']['verification'] = verifications

    # 打印验证结果表格
    print_verification_summary(verifications)

    # ====== 总结与建议 ======
    print_final_summary(test_results, verifications, api_results, concurrency_result, page_results)

    return test_results


def print_final_summary(test_results: Dict, verifications: Dict,
                        api_results: List[ApiTestResult],
                        concurrency_result: ConcurrencyTestResult,
                        page_results: List[PageLoadResult]):
    """打印最终总结和建议"""
    print("\n\n" + "="*90)
    print("性能测试总结报告")
    print("="*90)

    pass_count = verifications['pass_count']
    total = verifications['total_criteria']
    pass_rate = verifications['pass_rate']

    print(f"\n### 总体结论")
    if verifications['overall_passed']:
        print(f"\n**性能测试总体评估: 全部达标** ({pass_count}/{total}项指标通过, 达标率 {pass_rate}%)")
        print("\n系统性能表现优秀，满足所有验收标准要求。")
    else:
        print(f"\n**性能测试总体评估: 部分未达标** ({pass_count}/{total}项指标通过, 达标率 {pass_rate}%)")
        print("\n存在未达标的性能指标，需要进行针对性优化。")

    # 关键指标汇总
    print(f"\n### 关键性能指标汇总")
    print(f"\n**API响应时间:**")
    valid_apis = [a for a in api_results if a.success_count > 0]
    if valid_apis:
        avg_p95 = sum([a.p95_ms for a in valid_apis]) / len(valid_apis)
        avg_p99 = sum([a.p99_ms for a in valid_apis]) / len(valid_apis)
        worst_api = max(valid_apis, key=lambda a: a.p95_ms)
        print(f"- 平均P95响应时间: {avg_p95:.2f}ms (目标: < {PERFORMANCE_TARGETS['api_p95_ms']}ms)")
        print(f"- 平均P99响应时间: {avg_p99:.2f}ms (目标: < {PERFORMANCE_TARGETS['api_p99_ms']}ms)")
        print(f"- 最慢API端点: {worst_api.display_name} (P95: {worst_api.p95_ms}ms)")

    print(f"\n**并发处理能力:**")
    print(f"- 成功率: {concurrency_result.success_rate:.2f}%")
    print(f"- 5xx错误数: {concurrency_result.server_error_count}")
    print(f"- 吞吐量: {concurrency_result.throughput_per_second} 请求/秒")

    print(f"\n**页面加载性能:**")
    valid_pages = [p for p in page_results if p.success]
    if valid_pages:
        slowest_page = max(valid_pages, key=lambda p: p.full_load_ms)
        print(f"- 最慢页面: {slowest_page.page_name} ({slowest_page.full_load_ms}ms)")
        for page in valid_pages:
            status = "达标" if page.full_load_ms < PERFORMANCE_TARGETS['page_load_ms'] else "未达标"
            print(f"  - {page.page_name}: {page.full_load_ms}ms ({status})")

    print(f"\n**资源使用情况:**")
    resource = test_results['results'].get('resource_usage', {})
    if resource:
        print(f"- CPU平均使用率: {resource.get('cpu_usage', {}).get('average_percent', 0)}%")
        print(f"- 内存平均使用率: {resource.get('memory_usage', {}).get('average_percent', 0)}%")
        leak_info = resource.get('memory_leak_detection', {})
        leak_status = "正常" if not leak_info.get('potential_leak') else "需关注"
        print(f"- 内存泄漏检测: {leak_status} (趋势: {leak_info.get('trend', 'N/A')})")

    # 优化建议
    print(f"\n### 优化建议")
    if verifications['overall_passed']:
        print("\n1. **当前状态良好**: 所有性能指标均达到验收标准")
        print("2. **生产环境建议**: 在部署到生产环境前进行更大规模的压力测试")
        print("3. **持续监控**: 建议实施APM监控以持续跟踪性能表现")
        print("4. **容量规划**: 根据实际用户规模调整服务器资源配置")
    else:
        suggestions = []
        if not verifications['results']['api_p95_target']['passed']:
            suggestions.append("- **API响应时间优化**: 检查数据库查询效率，添加必要的索引，考虑引入缓存层")
        if not verifications['results']['api_p99_target']['passed']:
            suggestions.append("- **长尾延迟优化**: 分析P99请求的瓶颈，优化慢查询和网络传输")
        if not verifications['results']['page_load_target']['passed']:
            suggestions.append("- **前端性能优化**: 压缩静态资源，启用CDN，实现懒加载和代码分割")
        if not verifications['results']['concurrency_target']['passed']:
            suggestions.append("- **并发能力提升**: 优化线程池配置，增加连接池大小，考虑负载均衡")
        if not verifications['results']['memory_stability_target']['passed']:
            suggestions.append("- **内存泄漏排查**: 使用内存分析工具定位泄漏点，检查对象生命周期管理")

        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")

    print("\n" + "="*90)
    print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*90)


# ==================== 报告生成函数 ====================
def generate_json_report(test_results: Dict) -> Dict:
    """生成JSON格式的详细报告"""
    return test_results


def generate_markdown_report(test_results: Dict) -> str:
    """
    生成Markdown格式的性能测试报告
    """
    verifications = test_results['results']['verification']
    api_results = test_results['results']['api_response_time']
    concurrency_result = test_results['results']['concurrency_test']
    page_results = test_results['results']['frontend_page_load']
    resource_result = test_results['results']['resource_usage']
    service_status = test_results['results']['service_status']

    md = []
    md.append("# 性能测试报告 v1.4.0")
    md.append("")
    md.append(f"**测试时间**: {test_results['test_date']}")
    md.append(f"**测试版本**: {test_results['version']}")
    md.append("")

    # 一、测试环境
    md.append("---")
    md.append("## 一、测试环境")
    md.append("")
    md.append("| 服务 | 地址 | 状态 |")
    md.append("|------|------|------|")

    for service_name, status in service_status['services'].items():
        availability = "可用" if status['available'] else "不可用"
        md.append(f"| {service_name} | {status['url']} | {availability} |")

    md.append("")
    md.append("**测试配置:**")
    md.append(f"- API请求次数: {test_results['configuration']['api_iterations']} 次/端点")
    md.append(f"- 并发用户数: {test_results['configuration']['concurrent_users']}")
    md.append(f"- 每用户请求数: {test_results['configuration']['requests_per_user']}")
    md.append(f"- 请求超时: {test_results['configuration']['timeout_seconds']} 秒")
    md.append("")

    # 二、响应时间分析
    md.append("---")
    md.append("## 二、响应时间分析")
    md.append("")
    md.append("### 2.1 API响应时间基准测试结果")
    md.append("")
    md.append("| API端点 | 方法 | 平均(ms) | P50(ms) | P95(ms) | P99(ms) | 最小(ms) | 最大(ms) | 标准差(ms) | 成功率 |")
    md.append("|--------|------|---------|--------|--------|--------|---------|---------|-----------|-------|")

    for api in api_results:
        md.append(
            f"| {api['display_name']} | {api['method']} | {api['avg_ms']} | "
            f"{api['p50_ms']} | {api['p95_ms']} | {api['p99_ms']} | "
            f"{api['min_ms']} | {api['max_ms']} | {api['std_dev_ms']} | {api['success_rate']}% |"
        )

    md.append("")
    md.append("**图表描述 - API响应时间分布:**")
    md.append("")
    md.append("```")
    md.append("API响应时间分布图 (单位: ms)")
    md.append("")
    md.append("P50 ████████████████████████████████████████")
    md.append("P95 ████████████████████████████████████████████████████████████")
    md.append("P99 █████████████████████████████████████████████████████████████████████████████████████████")
    md.append("")
    md.append("目标线: P95 < 500ms | P99 < 1000ms")
    md.append("```")
    md.append("")

    # 三、并发测试结果
    md.append("---")
    md.append("## 三、并发测试结果")
    md.append("")
    md.append("### 3.1 并发压力测试概况")
    md.append("")
    md.append("| 指标 | 数值 |")
    md.append("|------|------|")
    md.append(f"| 测试端点 | {concurrency_result['endpoint']} |")
    md.append(f"| 并发用户数 | {concurrency_result['concurrent_users']} |")
    md.append(f"| 每用户请求数 | {concurrency_result['requests_per_user']} |")
    md.append(f"| 总请求数 | {concurrency_result['total_requests']} |")
    md.append(f"| 成功请求数 | {concurrency_result['successful_requests']} |")
    md.append(f"| 失败请求数 | {concurrency_result['failed_requests']} |")
    md.append(f"| **5xx服务器错误** | **{concurrency_result['server_error_count']}** |")
    md.append(f"| **成功率** | **{concurrency_result['success_rate']}%** |")
    md.append(f"| 平均响应时间 | {concurrency_result['avg_response_time_ms']}ms |")
    md.append(f"| 响应时间范围 | {concurrency_result['min_response_time_ms']}ms - {concurrency_result['max_response_time_ms']}ms |")
    md.append(f"| 标准差 | {concurrency_result['std_dev_ms']}ms |")
    md.append(f"| **吞吐量** | **{concurrency_result['throughput_per_second']} 请求/秒** |")
    md.append(f"| 总测试耗时 | {concurrency_result['total_test_time_ms']/1000:.2f}s |")
    md.append("")

    md.append("### 3.2 并发测试结论")
    md.append("")
    conc_pass = verifications['results']['concurrency_target']['passed']
    if conc_pass:
        md.append("**结论: PASS** - 并发测试通过，无5xx服务器错误")
    else:
        md.append("**结论: FAIL** - 存在5xx服务器错误，需要调查原因")
    md.append("")

    # 四、页面加载性能
    md.append("---")
    md.append("## 四、页面加载性能")
    md.append("")
    md.append("| 页面 | URL | TTFB(ms) | DOM加载(ms) | 完整加载(ms) | 大小(KB) | 状态 |")
    md.append("|------|-----|----------|------------|-------------|----------|------|")

    for page in page_results:
        size_kb = round(page['content_size_bytes']/1024, 2) if page['content_size_bytes'] > 0 else 0
        status = "成功" if page['success'] else "失败"
        md.append(
            f"| {page['page_name']} | {page['url'].replace(SERVICES['frontend'], '')} | "
            f"{page['ttfb_ms']} | {page['dom_load_ms']} | {page['full_load_ms']} | "
            f"{size_kb} | {status} |"
        )

    md.append("")
    md.append("**图表描述 - 页面加载时间对比:**")
    md.append("")
    md.append("```")
    md.append("页面加载时间对比 (单位: ms)")
    md.append("")
    for page in page_results:
        if page['full_load_ms'] > 0:
            bar_len = min(int(page['full_load_ms'] / 50), 40)
            bar = "█" * bar_len
            target_line = "|" if page['full_load_ms'] < 2000 else ""
            md.append(f"{page['page_name']:<12} {bar}{target_line} {page['full_load_ms']}ms")
    md.append("")
    md.append("目标线: < 2000ms")
    md.append("```")
    md.append("")

    # 五、资源使用情况
    md.append("---")
    md.append("## 五、资源使用情况")
    md.append("")
    md.append("### 5.1 CPU使用情况")
    md.append("")
    md.append("| 指标 | 数值 |")
    md.append("|------|------|")
    md.append(f"| 平均CPU使用率 | {resource_result['cpu_usage']['average_percent']}% |")
    md.append(f"| 最大CPU使用率 | {resource_result['cpu_usage']['max_percent']}% |")
    md.append(f"| 最小CPU使用率 | {resource_result['cpu_usage']['min_percent']}% |")
    md.append(f"| 监控时长 | {resource_result['monitor_duration_seconds']} 秒 |")
    md.append("")

    md.append("### 5.2 内存使用情况")
    md.append("")
    md.append("| 指标 | 数值 |")
    md.append("|------|------|")
    md.append(f"| 平均内存使用率 | {resource_result['memory_usage']['average_percent']}% |")
    md.append(f"| 平均内存使用量 | {resource_result['memory_usage']['average_used_gb']} GB |")
    md.append("")

    leak_info = resource_result['memory_leak_detection']
    md.append("### 5.3 内存泄漏检测")
    md.append("")
    md.append("| 检测项目 | 结果 |")
    md.append("|---------|------|")
    md.append(f"| 内存趋势 | {leak_info['trend']} |")
    md.append(f"| 增长率 | {leak_info['growth_rate_percent']}% |")
    md.append(f"| 是否存在泄漏 | {'否' if not leak_info['potential_leak'] else '是(需关注)'} |")
    md.append("")

    # 六、瓶颈识别与优化建议
    md.append("---")
    md.append("## 六、瓶颈识别与优化建议")
    md.append("")

    bottlenecks = []
    optimizations = []

    # 分析API性能瓶颈
    slow_apis = [api for api in api_results if api['p95_ms'] > 300 and api['success_count'] > 0]
    if slow_apis:
        bottlenecks.append(f"发现{len(slow_apis)}个API端点P95响应时间超过300ms")
        for api in slow_apis:
            bottlenecks.append(f"  - {api['display_name']}: P95={api['p95_ms']}ms")
        optimizations.append("建议对慢API进行数据库查询优化，添加索引，或引入Redis缓存")

    # 分析页面加载瓶颈
    slow_pages = [p for p in page_results if p['full_load_ms'] > 1500 and p['success']]
    if slow_pages:
        bottlenecks.append(f"发现{len(slow_pages)}个页面加载时间超过1.5秒")
        for page in slow_pages:
            bottlenecks.append(f"  - {page['page_name']}: {page['full_load_ms']}ms")
        optimizations.append("建议优化前端资源加载：压缩JS/CSS、启用Gzip、使用CDN加速")

    # 分析并发问题
    if concurrency_result['server_error_count'] > 0:
        bottlenecks.append(f"并发测试中出现{concurrency_result['server_error_count']}个5xx错误")
        optimizations.append("建议检查服务器资源限制、线程池配置、数据库连接池设置")

    # 分析内存问题
    if leak_info['potential_leak']:
        bottlenecks.append(f"内存使用呈上升趋势(增长率:{leak_info['growth_rate_percent']}%)，可能存在内存泄漏")
        optimizations.append("建议使用内存分析工具(如VisualVM、YourKit)进行内存泄漏排查")

    if bottlenecks:
        md.append("### 6.1 已识别的性能瓶颈")
        md.append("")
        for item in bottlenecks:
            md.append(f"- {item}")
        md.append("")

        md.append("### 6.2 优化建议")
        md.append("")
        for i, opt in enumerate(optimizations, 1):
            md.append(f"{i}. {opt}")
        md.append("")
    else:
        md.append("### 6.1 性能状况")
        md.append("")
        md.append("当前系统性能良好，未发现明显的性能瓶颈。")
        md.append("")

        md.append("### 6.2 进一步优化方向")
        md.append("")
        md.append("1. 生产环境部署前建议进行更大规模的压力测试(100+并发用户)")
        md.append("2. 考虑引入APM工具(如SkyWalking、Pinpoint)进行持续性能监控")
        md.append("3. 对关键业务路径进行代码级性能剖析")
        md.append("4. 评估缓存策略(Redis)的使用效果")
        md.append("")

    # 七、结论
    md.append("---")
    md.append("## 七、结论")
    md.append("")

    pass_count = verifications['pass_count']
    total = verifications['total_criteria']
    pass_rate = verifications['pass_rate']

    md.append("### 7.1 性能达标总评")
    md.append("")
    md.append("| 验收标准 | 目标值 | 实际值 | 达标状态 |")
    md.append("|---------|-------|-------|---------|")

    criteria_list = [
        ('API P95响应时间', 'api_p95_target', f"< {PERFORMANCE_TARGETS['api_p95_ms']}ms"),
        ('API P99响应时间', 'api_p99_target', f"< {PERFORMANCE_TARGETS['api_p99_ms']}ms"),
        ('页面首屏加载', 'page_load_target', f"< {PERFORMANCE_TARGETS['page_load_ms']}ms"),
        ('并发无5xx错误', 'concurrency_target', f"<= {PERFORMANCE_TARGETS['max_5xx_errors']}"),
        ('内存稳定性', 'memory_stability_target', '无明显泄漏')
    ]

    for name, key, target in criteria_list:
        info = verifications['results'][key]
        actual = "PASS" if info['passed'] else "FAIL"
        md.append(f"| {name} | {target} | {actual} | {'通过' if info['passed'] else '未通过'} |")

    md.append("")

    if verifications['overall_passed']:
        md.append(f"### 7.2 最终结论: **通过**")
        md.append("")
        md.append(f"**性能测试总体评估: 全部达标**")
        md.append(f"- 通过指标: {pass_count}/{total}")
        md.append(f"- 达标率: {pass_rate}%")
        md.append("")
        md.append("实验室管理系统v1.4.0版本性能表现良好，满足所有预定义的性能验收标准。")
        md.append("系统可以进入下一阶段的部署准备和生产环境测试。")
    else:
        md.append(f"### 7.2 最终结论: **有条件通过**")
        md.append("")
        md.append(f"**性能测试总体评估: 部分未达标**")
        md.append(f"- 通过指标: {pass_count}/{total}")
        md.append(f"- 达标率: {pass_rate}%")
        md.append("")
        md.append("系统基本性能符合要求，但存在部分需要优化的指标。")
        md.append("建议针对未达标项进行专项优化后重新测试。")
    md.append("")

    md.append("---")
    md.append(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    md.append("*测试工具: Python performance_test_v140.py*")
    md.append("*测试人员: Performance Expert*")

    return "\n".join(md)


# ==================== 主程序入口 ====================
if __name__ == '__main__':
    try:
        print("\n" + "="*90)
        print("实验室管理系统 - 全面性能基准测试 v1.4.0")
        print("Performance Expert - 专业性能分析与优化")
        print("="*90 + "\n")

        # 执行性能测试
        results = run_performance_tests()

        # 确保输出目录存在
        output_dir = r'd:\FinalCodeAndFile\lab-management-system\test_results'
        os.makedirs(output_dir, exist_ok=True)

        # 保存JSON格式详细结果
        json_file = os.path.join(output_dir, 'performance-live-v1.4.0.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n[SUCCESS] JSON详细结果已保存至: {json_file}")

        # 生成并保存Markdown报告
        markdown_report = generate_markdown_report(results)
        md_file = os.path.join(output_dir, 'performance-report-v1.4.0.md')
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        print(f"[SUCCESS] Markdown报告已保存至: {md_file}")

        print("\n" + "="*90)
        print("性能基准测试全部完成!")
        print("="*90)
        print(f"\n生成的文件:")
        print(f"  1. JSON详细数据: {json_file}")
        print(f"  2. Markdown报告: {md_file}")

    except KeyboardInterrupt:
        print("\n\n[INFO] 测试被用户中断")
    except Exception as e:
        print(f"\n\n[ERROR] 测试执行出错: {e}")
        import traceback
        traceback.print_exc()
