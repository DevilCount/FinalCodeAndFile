#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实验室管理系统 v1.4.2 回归测试脚本（第二轮修复验证）
=====================================================

验证目标:
- API-01: 空参数登录返回400(第二轮修复增强)
- API-03: 标本按状态查询返回200(第二轮修复增强)
- 功能回归确认(确保未破坏已有功能)

关键修复点:
1. 登录接口增加空格、null值等边界情况处理
2. 标本状态查询增加无效值校验
3. 确保正常功能不受影响

作者: API Test Pro (AI Testing Specialist)
日期: 2026-04-02
版本: v2.0 (R2专用)
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# ==================== 配置 ====================
BASE_URLS = {
    "user_service": "http://localhost:8086",
    "sample_service": "http://localhost:8087",
    "report_service": "http://localhost:8088",
    "ai_service": "http://localhost:8085",
    "hl7_service": "http://localhost:8084",
}

RESULTS_DIR = r"d:\FinalCodeAndFile\lab-management-system\test_results"
REPORT_FILE = f"{RESULTS_DIR}\\REGRESSION-REPORT-V1.4.2.md"
JSON_RESULTS_FILE = f"{RESULTS_DIR}\\regression-test-v142.json"

# 超时设置（秒）
TIMEOUT = 15

# ==================== 数据结构 ====================
class TestCase:
    """测试用例类"""
    def __init__(self, test_id: str, defect_id: str, name: str, service: str,
                 method: str, endpoint: str, expected_status: int,
                 expected_message_contains: str = None,
                 data: Dict = None, params: Dict = None,
                 headers: Dict = None, category: str = "P0-FIX"):
        self.test_id = test_id
        self.defect_id = defect_id
        self.name = name
        self.service = service
        self.method = method
        self.endpoint = endpoint
        self.expected_status = expected_status
        self.expected_message_contains = expected_message_contains
        self.data = data or {}
        self.params = params or {}
        self.headers = headers or {"Content-Type": "application/json"}
        self.category = category
        
        # 执行结果
        self.actual_status = None
        self.response_body = None
        self.response_time_ms = None
        self.error = None
        self.passed = False
        self.details = ""

    def to_dict(self) -> Dict:
        return {
            "test_id": self.test_id,
            "defect_id": self.defect_id,
            "name": self.name,
            "service": self.service,
            "method": self.method,
            "endpoint": self.endpoint,
            "expected_status": self.expected_status,
            "actual_status": self.actual_status,
            "expected_message": self.expected_message_contains,
            "response_time_ms": self.response_time_ms,
            "passed": self.passed,
            "category": self.category,
            "error": self.error,
            "details": self.details,
        }


class RegressionTestRunnerV2:
    """回归测试运行器 V2 - 第二轮修复专用"""

    def __init__(self):
        self.test_cases: List[TestCase] = []
        self.results: List[Dict] = []
        self.start_time = None
        self.end_time = None
        self.auth_token = None

    def add_test_case(self, tc: TestCase):
        """添加测试用例"""
        self.test_cases.append(tc)

    def _make_request(self, tc: TestCase) -> Tuple[int, Any, float]:
        """发送HTTP请求并返回状态码、响应体和响应时间"""
        base_url = BASE_URLS.get(tc.service)
        if not base_url:
            raise ValueError(f"Unknown service: {tc.service}")

        url = base_url + tc.endpoint

        # 添加认证头（如果有token）
        headers = dict(tc.headers)
        if self.auth_token and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        start_time = time.time()
        try:
            if tc.method == "GET":
                resp = requests.get(url, params=tc.params, headers=headers, timeout=TIMEOUT)
            elif tc.method == "POST":
                if tc.headers.get("Content-Type") == "application/x-www-form-urlencoded":
                    resp = requests.post(url, data=tc.params, headers=headers, timeout=TIMEOUT)
                else:
                    resp = requests.post(url, json=tc.data, params=tc.params, headers=headers, timeout=TIMEOUT)
            elif tc.method == "PUT":
                resp = requests.put(url, json=tc.data, headers=headers, timeout=TIMEOUT)
            elif tc.method == "DELETE":
                resp = requests.delete(url, headers=headers, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported HTTP method: {tc.method}")

            elapsed_ms = round((time.time() - start_time) * 1000, 2)

            # 尝试解析JSON响应
            try:
                body = resp.json()
            except:
                body = resp.text[:500] if resp.text else ""

            return resp.status_code, body, elapsed_ms

        except requests.exceptions.Timeout:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return None, {"error": "请求超时"}, elapsed_ms
        except requests.exceptions.ConnectionError as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return None, {"error": f"连接失败: {str(e)[:200]}"}, elapsed_ms
        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return None, {"error": f"请求异常: {str(e)[:200]}"}, elapsed_ms

    def execute_test(self, tc: TestCase):
        """执行单个测试用例"""
        print(f"\n{'='*80}")
        print(f"[{tc.test_id}] 执行测试: {tc.name}")
        print(f"  缺陷ID: {tc.defect_id}")
        print(f"  服务: {tc.service} | 方法: {tc.method} | 端点: {tc.endpoint}")
        print(f"  期望状态码: {tc.expected_status}", end="")
        if tc.expected_message_contains:
            print(f" | 期望包含消息: '{tc.expected_message_contains}'")
        else:
            print()

        try:
            status_code, body, response_time = self._make_request(tc)

            tc.actual_status = status_code
            tc.response_body = body
            tc.response_time_ms = response_time

            # 判断是否通过
            if status_code is None:
                tc.passed = False
                tc.error = body.get("error", "未知错误") if isinstance(body, dict) else str(body)
                tc.details = f"请求失败: {tc.error}"

            elif status_code != tc.expected_status:
                tc.passed = False
                tc.details = f"状态码不匹配: 期望 {tc.expected_status}, 实际 {status_code}"

                # 检查是否是201（某些创建操作返回201）
                if tc.expected_status in [200, 201] and status_code in [200, 201]:
                    tc.passed = True
                    tc.details = "状态码在可接受范围内"

            else:
                # 状态码匹配，检查响应消息
                if tc.expected_message_contains and isinstance(body, dict):
                    message = body.get("message", "") or ""
                    if tc.expected_message_contains.lower() in message.lower():
                        tc.passed = True
                        tc.details = f"响应正确: {message}"
                    else:
                        tc.passed = False
                        tc.details = f"消息不匹配: 期望包含 '{tc.expected_message_contains}', 实际 '{message}'"
                else:
                    tc.passed = True
                    tc.details = "状态码匹配"

        except Exception as e:
            tc.passed = False
            tc.error = str(e)
            tc.details = f"执行异常: {str(e)}"

        # 打印结果
        status_icon = "PASS" if tc.passed else "FAIL"
        print(f"  结果: [{status_icon}] | 实际状态码: {tc.actual_status} | 响应时间: {tc.response_time_ms}ms")
        print(f"  详情: {tc.details}")

        if tc.response_body and isinstance(tc.response_body, dict):
            body_preview = json.dumps(tc.response_body, ensure_ascii=False)[:300]
            print(f"  响应预览: {body_preview}")

    def run_all_tests(self):
        """执行所有测试用例"""
        self.start_time = datetime.now()
        print("\n" + "="*80)
        print("实验室管理系统 v1.4.2 回归测试开始（第二轮修复验证）")
        print("="*80)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试用例总数: {len(self.test_cases)}")

        for i, tc in enumerate(self.test_cases, 1):
            print(f"\n[{i}/{len(self.test_cases)}]", end="")
            self.execute_test(tc)
            self.results.append(tc.to_dict())

            # 小延迟，避免请求过快
            time.sleep(0.3)

        self.end_time = datetime.now()

    def generate_statistics(self) -> Dict:
        """生成测试统计信息"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        pass_rate = round(passed / total * 100, 1) if total > 0 else 0

        # 按分类统计
        by_category = {}
        for r in self.results:
            cat = r["category"]
            if cat not in by_category:
                by_category[cat] = {"total": 0, "passed": 0}
            by_category[cat]["total"] += 1
            if r["passed"]:
                by_category[cat]["passed"] += 1

        # 按缺陷ID统计
        by_defect = {}
        for r in self.results:
            defect_id = r["defect_id"]
            if defect_id not in by_defect:
                by_defect[defect_id] = {"total": 0, "passed": 0, "name": r.get("name", "")}
            by_defect[defect_id]["total"] += 1
            if r["passed"]:
                by_defect[defect_id]["passed"] += 1

        # 响应时间统计
        response_times = [r["response_time_ms"] for r in self.results if r["response_time_ms"]]
        avg_response_time = round(sum(response_times) / len(response_times), 2) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0

        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0

        return {
            "version": "v1.4.2-R2",
            "timestamp": self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else "",
            "duration_seconds": round(duration, 2),
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "by_category": by_category,
            "by_defect": by_defect,
            "avg_response_time_ms": avg_response_time,
            "max_response_time_ms": max_response_time,
            "min_response_time_ms": min_response_time,
        }

    def print_summary(self):
        """打印测试摘要"""
        stats = self.generate_statistics()

        print("\n" + "="*80)
        print("回归测试执行完成")
        print("="*80)
        print(f"版本: {stats['version']}")
        print(f"结束时间: {stats['timestamp']}")
        print(f"总耗时: {stats['duration_seconds']}秒")
        print("-"*80)
        print(f"总测试数: {stats['total']}")
        print(f"通过数量: {stats['passed']}")
        print(f"失败数量: {stats['failed']}")
        print(f"通过率:   {stats['pass_rate']}%")
        print("-"*80)
        print(f"平均响应时间: {stats['avg_response_time_ms']}ms")
        print(f"最大响应时间: {stats['max_response_time_ms']}ms")
        print(f"最小响应时间: {stats['min_response_time_ms']}ms")
        print("="*80)

        # 按分类显示结果
        print("\n按分类统计:")
        for cat, data in stats["by_category"].items():
            rate = round(data["passed"] / data["total"] * 100, 1) if data["total"] > 0 else 0
            icon = "OK" if rate == 100 else "WARN" if rate >= 80 else "FAIL"
            print(f"  [{icon}] {cat}: {data['passed']}/{data['total']} ({rate}%)")

    def save_results_json(self):
        """保存测试结果为JSON格式"""
        stats = self.generate_statistics()
        output = {
            **stats,
            "test_results": self.results,
        }

        with open(JSON_RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n[OK] JSON结果已保存到: {JSON_RESULTS_FILE}")

    def generate_markdown_report(self):
        """生成Markdown格式的回归测试报告"""
        stats = self.generate_statistics()

        report = []
        report.append("# 回归测试报告 v1.4.2 (第二轮)\n")
        report.append("---\n")
        report.append(f"**生成时间**: {stats['timestamp']}  \n")
        report.append(f"**测试版本**: v1.4.2 (第二轮修复后)  \n")
        report.append(f"**测试工具**: API Test Pro - Regression Test Suite V2  \n")
        report.append(f"**总耗时**: {stats['duration_seconds']}秒  \n")
        report.append("---\n")

        # 1. 测试概要
        report.append("## 1. 测试概要\n")
        report.append("| 指标 | 数值 |")
        report.append("|------|------|")
        report.append(f"| 总测试用例数 | {stats['total']} |")
        report.append(f"| 通过用例数 | {stats['passed']} |")
        report.append(f"| 失败用例数 | {stats['failed']} |")
        report.append(f"| 通过率 | **{stats['pass_rate']}%** |")
        report.append(f"| 平均响应时间 | {stats['avg_response_time_ms']}ms |")
        report.append(f"| 最大响应时间 | {stats['max_response_time_ms']}ms |")
        report.append(f"| 最小响应时间 | {stats['min_response_time_ms']}ms |\n")

        # 2. 关键修复验证结果
        report.append("## 2. 关键修复验证结果\n")
        report.append("| 缺陷ID | 测试数 | 通过 | 失败 | 状态 |")
        report.append("|--------|--------|------|------|------|")

        defect_results = {}
        for r in self.results:
            defect_id = r["defect_id"]
            if defect_id not in defect_results:
                defect_results[defect_id] = {"total": 0, "passed": 0, "name": ""}
            defect_results[defect_id]["total"] += 1
            if r["passed"]:
                defect_results[defect_id]["passed"] += 1
            defect_results[defect_id]["name"] = r["name"]

        for defect_id in ["API-01", "API-03", "REGRESSION"]:
            if defect_id in defect_results:
                data = defect_results[defect_id]
                all_passed = data["passed"] == data["total"]
                status = "PASS" if all_passed else "FAIL"
                status_icon = "[PASS]" if all_passed else "[FAIL]"
                report.append(f"| {defect_id} | {data['total']} | {data['passed']} | {data['total'] - data['passed']} | {status_icon} {status} |")

        report.append("")

        # 3. 详细测试结果表
        report.append("## 3. 详细测试结果\n")

        # 按分组显示
        categories = {}
        for r in self.results:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)

        category_names = {
            "API-01-FIX": "### 3.1 API-01 空参数登录修复验证",
            "API-03-FIX": "### 3.2 API-03 标本按状态查询修复验证",
            "REGRESSION": "### 3.3 功能回归确认测试",
        }

        for cat in ["API-01-FIX", "API-03-FIX", "REGRESSION"]:
            if cat in categories:
                tests = categories[cat]
                report.append(category_names.get(cat, f"### {cat}\n"))
                report.append("| 测试ID | 测试名称 | 方法 | 端点 | 期望 | 实际 | 结果 | 响应时间(ms) | 详情 |")
                report.append("|--------|----------|------|------|------|------|------|-------------|------|")

                for t in tests:
                    icon = "PASS" if t["passed"] else "FAIL"
                    detail = t.get("details", "")[:50] if t.get("details") else ""
                    report.append(f"| {t['test_id']} | {t['name']} | {t['method']} | {t['endpoint']} | {t['expected_status']} | {t['actual_status']} | [{icon}] | {t['response_time_ms']} | {detail} |")

                report.append("")

        # 4. 版本对比
        report.append("## 4. 版本对比 (v1.4.0 vs v1.4.1 vs v1.4.2)\n")
        report.append("| 版本 | API-01状态 | API-03状态 | 总体评价 |")
        report.append("|------|-----------|-----------|----------|")
        report.append("| v1.4.0 | FAIL (500错误) | FAIL (500错误) | 存在P0缺陷 |")
        report.append("| v1.4.1 | PARTIAL (基础校验通过) | PARTIAL (基础功能恢复) | 部分修复 |")
        report.append("| v1.4.2 (R2) | 待验证 | 待验证 | 第二轮增强修复 |\n")

        # 根据实际结果填充v1.4.2的状态
        api01_pass = all(r["passed"] for r in self.results if r["category"] == "API-01-FIX")
        api03_pass = all(r["passed"] for r in self.results if r["category"] == "API-03-FIX")

        api01_status = "PASS (完全修复)" if api01_pass else "FAIL (仍有问题)"
        api03_status = "PASS (完全修复)" if api03_pass else "FAIL (仍有问题)"
        overall = "PASS (可以验收)" if (api01_pass and api03_pass) else "FAIL (需进一步修复)"

        # 更新表格中的v1.4.2行
        report_content = "\n".join(report)
        report_content = report_content.replace(
            "| v1.4.2 (R2) | 待验证 | 待验证 | 第二轮增强修复 |",
            f"| v1.4.2 (R2) | {api01_status} | {api03_status} | {overall} |"
        )
        report = [report_content]

        # 5. 结论
        report.append("")
        report.append("## 5. 结论与建议\n")

        all_api01_passed = all(r["passed"] for r in self.results if r["category"] == "API-01-FIX")
        all_api03_passed = all(r["passed"] for r in self.results if r["category"] == "API-03-FIX")
        all_regression_passed = all(r["passed"] for r in self.results if r["category"] == "REGRESSION")

        if all_api01_passed and all_api03_passed and all_regression_passed:
            report.append("### 结论: 可以进入验收阶段\n")
            report.append("**评估结果**: PASS - 全部通过  \n")
            report.append("**质量评级**: 5/5  \n")
            report.append("**部署风险**: 低风险  \n\n")
            report.append("**详细说明**:  \n")
            report.append(f"- 所有 {stats['total']} 个测试用例全部通过，通过率 100%  \n")
            report.append("- API-01 空参数登录修复已验证通过（包括空字符串、纯空格、null值）  \n")
            report.append("- API-03 标本按状态查询修复已验证通过（包括有效状态、空参数、无效值）  \n")
            report.append("- 正常功能未被破坏，回归测试全部通过  \n")
            report.append("- 系统性能表现良好，响应时间在合理范围内  \n\n")
            report.append("**建议**:  \n")
            report.append("1. 可以进入UAT用户验收测试阶段  \n")
            report.append("2. 可以准备生产环境部署  \n")
            report.append("3. 建议在生产环境部署后进行冒烟测试确认  \n")
        elif stats["pass_rate"] >= 90:
            report.append("### 结论: 基本可以进入验收，但有小问题需处理\n")
            report.append(f"**评估结果**: WARN - 大部分通过 ({stats['pass_rate']}%)  \n")
            report.append("**质量评级**: 4/5  \n")
            report.append("**部署风险**: 中等风险  \n\n")
            report.append("**说明**:  \n")
            report.append(f"- {stats['failed']} 个测试用例未通过，需要进一步检查  \n")
            if not all_api01_passed:
                report.append("- API-01 存在未通过的测试用例  \n")
            if not all_api03_passed:
                report.append("- API-03 存在未通过的测试用例  \n")
            if not all_regression_passed:
                report.append("- 存在功能回归问题  \n\n")
            report.append("**建议**:  \n")
            report.append("1. 优先修复失败的测试用例对应的问题  \n")
            report.append("2. 修复后重新执行回归测试  \n")
            report.append("3. 在问题解决前不建议进入生产环境  \n")
        else:
            report.append("### 结论: 不建议进入验收阶段\n")
            report.append(f"**评估结果**: FAIL - 通过率过低 ({stats['pass_rate']}%)  \n")
            report.append("**质量评级**: 2/5  \n")
            report.append("**部署风险**: 高风险  \n\n")
            report.append("**说明**:  \n")
            report.append(f"- {stats['failed']} 个测试用例未通过，存在严重问题  \n")
            if not all_api01_passed:
                report.append("- API-01 未完全修复  \n")
            if not all_api03_passed:
                report.append("- API-03 未完全修复  \n")
            if not all_regression_passed:
                report.append("- 存在功能 regression 问题  \n\n")
            report.append("**建议**:  \n")
            report.append("1. 暂停验收流程  \n")
            report.append("2. 立即修复所有失败用例  \n")
            report.append("3. 进行全面的根因分析  \n")
            report.append("4. 修复后必须重新进行完整回归测试  \n")

        report.append("\n---\n")
        report.append("*此报告由 API Test Pro 自动生成*  \n")
        report.append(f"*测试框架版本: V2.0 (R2专用) | 执行时间: {stats['timestamp']}*\n")

        # 写入文件
        final_report = "\n".join(report) if isinstance(report[-1], str) else report[0]
        if isinstance(report, list) and len(report) > 0:
            final_report = "\n".join(report)

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(final_report)

        print(f"[OK] Markdown报告已保存到: {REPORT_FILE}")
        return final_report


def setup_test_cases(runner: RegressionTestRunnerV2):
    """
    设置所有测试用例 - 第二轮修复专用
    重点验证:
    1. API-01: 空参数登录的各种边界情况
    2. API-03: 标本状态查询的完整场景
    3. 功能回归: 确保正常功能未被破坏
    """

    # ==================== API-01: 空参数登录修复验证 ====================
    # 共5个测试用例

    # TC-R2-01: 空用户名登录
    runner.add_test_case(TestCase(
        test_id="TC-R2-01",
        defect_id="API-01",
        name="空用户名登录测试",
        service="user_service",
        method="POST",
        endpoint="/user/login",
        expected_status=400,
        expected_message_contains="用户名不能为空",
        params={"username": "", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        category="API-01-FIX"
    ))

    # TC-R2-02: 空密码登录
    runner.add_test_case(TestCase(
        test_id="TC-R2-02",
        defect_id="API-01",
        name="空密码登录测试",
        service="user_service",
        method="POST",
        endpoint="/user/login",
        expected_status=400,
        expected_message_contains="密码不能为空",
        params={"username": "admin", "password": ""},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        category="API-01-FIX"
    ))

    # TC-R2-03: 纯空格用户名登录（第二轮新增）
    runner.add_test_case(TestCase(
        test_id="TC-R2-03",
        defect_id="API-01",
        name="纯空格用户名登录测试",
        service="user_service",
        method="POST",
        endpoint="/user/login",
        expected_status=400,
        expected_message_contains="用户名不能为空",
        params={"username": "   ", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        category="API-01-FIX"
    ))

    # TC-R2-04: null用户名登录（第二轮新增）
    runner.add_test_case(TestCase(
        test_id="TC-R2-04",
        defect_id="API-01",
        name="null用户名登录测试",
        service="user_service",
        method="POST",
        endpoint="/user/login",
        expected_status=400,
        expected_message_contains="用户名不能为空",
        params={"username": None, "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        category="API-01-FIX"
    ))

    # TC-R2-05: 正常登录（确保未破坏）
    runner.add_test_case(TestCase(
        test_id="TC-R2-05",
        defect_id="API-01",
        name="正常登录(admin/admin123)",
        service="user_service",
        method="POST",
        endpoint="/user/login",
        expected_status=200,
        params={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        category="API-01-FIX"
    ))

    # ==================== API-03: 标本按状态查询修复验证 ====================
    # 共6个测试用例

    # TC-R2-06: 查询PENDING状态标本
    runner.add_test_case(TestCase(
        test_id="TC-R2-06",
        defect_id="API-03",
        name="查询PENDING状态标本",
        service="sample_service",
        method="GET",
        endpoint="/sample/list-by-status",
        expected_status=200,
        params={"status": "PENDING"},
        category="API-03-FIX"
    ))

    # TC-R2-07: 查询RECEIVED状态标本
    runner.add_test_case(TestCase(
        test_id="TC-R2-07",
        defect_id="API-03",
        name="查询RECEIVED状态标本",
        service="sample_service",
        method="GET",
        endpoint="/sample/list-by-status",
        expected_status=200,
        params={"status": "RECEIVED"},
        category="API-03-FIX"
    ))

    # TC-R2-08: 查询TESTING状态标本
    runner.add_test_case(TestCase(
        test_id="TC-R2-08",
        defect_id="API-03",
        name="查询TESTING状态标本",
        service="sample_service",
        method="GET",
        endpoint="/sample/list-by-status",
        expected_status=200,
        params={"status": "TESTING"},
        category="API-03-FIX"
    ))

    # TC-R2-09: 查询COMPLETED状态标本
    runner.add_test_case(TestCase(
        test_id="TC-R2-09",
        defect_id="API-03",
        name="查询COMPLETED状态标本",
        service="sample_service",
        method="GET",
        endpoint="/sample/list-by-status",
        expected_status=200,
        params={"status": "COMPLETED"},
        category="API-03-FIX"
    ))

    # TC-R2-10: 空状态参数查询（应返回400）
    runner.add_test_case(TestCase(
        test_id="TC-R2-10",
        defect_id="API-03",
        name="空状态参数查询测试",
        service="sample_service",
        method="GET",
        endpoint="/sample/list-by-status",
        expected_status=400,
        expected_message_contains="不能为空",
        params={"status": ""},
        category="API-03-FIX"
    ))

    # TC-R2-11: 无效状态值查询（应返回400）
    runner.add_test_case(TestCase(
        test_id="TC-R2-11",
        defect_id="API-03",
        name="无效状态值查询测试",
        service="sample_service",
        method="GET",
        endpoint="/sample/list-by-status",
        expected_status=400,
        expected_message_contains="无效",
        params={"status": "INVALID"},
        category="API-03-FIX"
    ))

    # ==================== 功能回归确认测试 ====================
    # 共8个测试用例

    # TC-R2-12: 正常登录（重复验证）
    runner.add_test_case(TestCase(
        test_id="TC-R2-12",
        defect_id="REGRESSION",
        name="正常登录确认(admin/admin123)",
        service="user_service",
        method="POST",
        endpoint="/user/login",
        expected_status=200,
        params={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        category="REGRESSION"
    ))

    # TC-R2-13: 创建标本（最小数据）
    runner.add_test_case(TestCase(
        test_id="TC-R2-13",
        defect_id="REGRESSION",
        name="创建标本(最小数据)",
        service="sample_service",
        method="POST",
        endpoint="/sample/create",
        expected_status=200,
        data={
            "sampleNo": f"R2-MIN-{int(time.time())}",
            "patientName": "回归最小数据患者",
            "testItems": "血常规"
        },
        category="REGRESSION"
    ))

    # TC-R2-14: 创建标本（完整数据）- 第一轮已修复
    runner.add_test_case(TestCase(
        test_id="TC-R2-14",
        defect_id="REGRESSION",
        name="创建标本(完整数据)",
        service="sample_service",
        method="POST",
        endpoint="/sample/create",
        expected_status=200,
        data={
            "sampleNo": f"R2-FULL-{int(time.time())}",
            "patientId": 1,
            "patientName": "回归完整数据患者",
            "patientGender": "男",
            "patientAge": 35,
            "doctorId": 1,
            "doctorName": "张医生",
            "testItems": "血常规,尿常规,生化全项",
            "sampleType": "BLOOD",
            "collectTime": "2026-04-02T10:00:00",
            "collectLocation": "门诊采血室",
            "status": "COLLECTED",
            "remark": "第二轮回归测试标本"
        },
        category="REGRESSION"
    ))

    # TC-R2-15: 获取标本列表
    runner.add_test_case(TestCase(
        test_id="TC-R2-15",
        defect_id="REGRESSION",
        name="获取标本列表",
        service="sample_service",
        method="GET",
        endpoint="/sample/list",
        expected_status=200,
        category="REGRESSION"
    ))

    # TC-R2-16: 创建报告（最小数据）
    runner.add_test_case(TestCase(
        test_id="TC-R2-16",
        defect_id="REGRESSION",
        name="创建报告(最小数据)",
        service="report_service",
        method="POST",
        endpoint="/report/create",
        expected_status=200,
        data={
            "sampleId": 1,
            "patientName": "回归最小数据患者",
            "testItems": "血常规"
        },
        category="REGRESSION"
    ))

    # TC-R2-17: 创建报告（完整数据）- 第一轮已修复
    runner.add_test_case(TestCase(
        test_id="TC-R2-17",
        defect_id="REGRESSION",
        name="创建报告(完整数据)",
        service="report_service",
        method="POST",
        endpoint="/report/create",
        expected_status=200,
        data={
            "reportNo": f"R2-RPT-{int(time.time())}",
            "sampleId": 1,
            "sampleNo": "SAMPLE-001",
            "patientId": 1,
            "patientName": "回归完整数据患者",
            "testItems": "血常规,尿常规",
            "technicianId": 1,
            "technicianName": "李技师",
            "status": "PENDING",
            "remark": "第二轮回归测试报告"
        },
        category="REGRESSION"
    ))

    # TC-R2-18: 获取报告列表
    runner.add_test_case(TestCase(
        test_id="TC-R2-18",
        defect_id="REGRESSION",
        name="获取报告列表",
        service="report_service",
        method="GET",
        endpoint="/report/list",
        expected_status=200,
        category="REGRESSION"
    ))

    # TC-R2-19: AI健康检查
    runner.add_test_case(TestCase(
        test_id="TC-R2-19",
        defect_id="REGRESSION",
        name="AI健康检查",
        service="ai_service",
        method="GET",
        endpoint="/ai/health",
        expected_status=200,
        category="REGRESSION"
    ))


def main():
    """主函数"""
    print("\n" + "="*80)
    print("实验室管理系统 v1.4.2 回归测试套件（第二轮修复验证）")
    print("API Test Pro - 专业API测试工具 V2")
    print("="*80)

    # 确保输出目录存在
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # 创建测试运行器
    runner = RegressionTestRunnerV2()

    # 设置测试用例
    setup_test_cases(runner)

    # 执行所有测试
    runner.run_all_tests()

    # 打印摘要
    runner.print_summary()

    # 保存结果
    runner.save_results_json()

    # 生成Markdown报告
    report = runner.generate_markdown_report()

    # 返回退出码
    stats = runner.generate_statistics()
    if stats["pass_rate"] == 100:
        print("\n" + "="*80)
        print("[SUCCESS] 回归测试全部通过! 系统可以进入验收阶段.")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print(f"[WARNING] 回归测试完成，通过率: {stats['pass_rate']}%")
        print(f"   请查看详细报告: {REPORT_FILE}")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
