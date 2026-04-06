#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实验室管理系统 v1.4.1 回归测试脚本
=====================================

验证目标:
- API-01: 空参数登录返回400(不再是500)
- API-02: 完整数据创建标本成功(不再是500)
- API-03: 标本按状态查询成功(不再是500)
- API-04: 完整数据创建报告成功(不再是500)
- 参数校验改进验证
- 正常功能回归

作者: API Test Pro (AI Testing Specialist)
日期: 2026-04-02
版本: v1.0
"""

import requests
import json
import time
import sys
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
REPORT_FILE = f"{RESULTS_DIR}\\REGRESSION-REPORT-V1.4.1.md"
JSON_RESULTS_FILE = f"{RESULTS_DIR}\\regression-test-v141.json"

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


class RegressionTestRunner:
    """回归测试运行器"""
    
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
        status_icon = "✅ PASS" if tc.passed else "❌ FAIL"
        print(f"  结果: {status_icon} | 实际状态码: {tc.actual_status} | 响应时间: {tc.response_time_ms}ms")
        print(f"  详情: {tc.details}")
        
        if tc.response_body and isinstance(tc.response_body, dict):
            body_preview = json.dumps(tc.response_body, ensure_ascii=False)[:300]
            print(f"  响应预览: {body_preview}")
    
    def run_all_tests(self):
        """执行所有测试用例"""
        self.start_time = datetime.now()
        print("\n" + "="*80)
        print("实验室管理系统 v1.4.1 回归测试开始")
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
            "version": "v1.4.1",
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
        print(f"通过数量: {stats['passed']} ✅")
        print(f"失败数量: {stats['failed']} ❌")
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
            icon = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"
            print(f"  {icon} {cat}: {data['passed']}/{data['total']} ({rate}%)")
    
    def save_results_json(self):
        """保存测试结果为JSON格式"""
        stats = self.generate_statistics()
        output = {
            **stats,
            "test_results": self.results,
        }
        
        with open(JSON_RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ JSON结果已保存到: {JSON_RESULTS_FILE}")
    
    def generate_markdown_report(self):
        """生成Markdown格式的回归测试报告"""
        stats = self.generate_statistics()
        
        report = []
        report.append("# 回归测试报告 v1.4.1\n")
        report.append("---\n")
        report.append(f"**生成时间**: {stats['timestamp']}  \n")
        report.append(f"**测试版本**: v1.4.1  \n")
        report.append(f"**测试工具**: API Test Pro - Regression Test Suite  \n")
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
        
        # 2. 修复验证结果
        report.append("## 2. 修复验证结果（逐项）\n")
        report.append("| 缺陷ID | 测试场景 | v1.4.0结果 | v1.4.1结果 | 状态码 | 状态 |")
        report.append("|--------|----------|------------|------------|--------|------|")
        
        defect_results = {}
        for r in self.results:
            defect_id = r["defect_id"]
            if defect_id not in defect_results:
                defect_results[defect_id] = []
            defect_results[defect_id].append(r)
        
        # 定义v1.4.0的预期失败结果
        v140_expected = {
            "API-01": ("HTTP 500 Internal Server Error", "应返回400"),
            "API-02": ("HTTP 500 Internal Server Error", "应返回200/201"),
            "API-03": ("HTTP 500 Internal Server Error", "应返回200"),
            "API-04": ("HTTP 500 Internal Server Error", "应返回200/201"),
            "VAL-01": ("可能缺少校验或500", "应返回400+字段错误"),
            "VAL-02": ("可能缺少校验或500", "应返回400+字段错误"),
            "REG-01": ("正常", "应保持正常"),
            "REG-02": ("正常", "应保持正常"),
            "REG-03": ("正常", "应保持正常"),
            "REG-04": ("正常", "应保持正常"),
        }
        
        for defect_id, tests in defect_results.items():
            all_passed = all(t["passed"] for t in tests)
            first_test = tests[0]
            v140_result, expectation = v140_expected.get(defect_id, ("未知", "未知"))
            
            actual_status = first_test.get("actual_status", "N/A")
            current_result = f"HTTP {actual_status}" if actual_status else "请求失败"
            
            if all_passed:
                status_icon = "✅ 已修复/通过"
                status = "PASS"
            else:
                status_icon = "❌ 未修复/失败"
                status = "FAIL"
            
            report.append(f"| {defect_id} | {first_test['name']} | {v140_result} | {current_result} | {actual_status} | {status_icon} |")
        
        report.append("")
        
        # 3. 详细测试结果
        report.append("## 3. 详细测试结果\n")
        
        # 按分组显示
        categories = {}
        for r in self.results:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)
        
        for cat, tests in categories.items():
            category_names = {
                "P0-FIX": "### P0级缺陷修复验证（关键）",
                "VALIDATION": "### 参数校验改进验证",
                "REGRESSION": "### 正常功能回归测试",
            }
            report.append(category_names.get(cat, f"### {cat}\n"))
            report.append("| 测试ID | 缺陷ID | 测试名称 | 方法 | 端点 | 期望 | 实际 | 结果 | 响应时间 |")
            report.append("|--------|--------|----------|------|------|------|------|------|----------|")
            
            for t in tests:
                icon = "✅" if t["passed"] else "❌"
                report.append(f"| {t['test_id']} | {t['defect_id']} | {t['name']} | {t['method']} | {t['endpoint']} | {t['expected_status']} | {t['actual_status']} | {icon} | {t['response_time_ms']}ms |")
            
            report.append("")
        
        # 4. 回归通过率分析
        report.append("## 4. 回归通过率分析\n")
        report.append("| 分类 | 总数 | 通过 | 失败 | 通过率 |")
        report.append("|------|------|------|------|--------|")
        
        for cat, data in stats["by_category"].items():
            rate = round(data["passed"] / data["total"] * 100, 1)
            icon = "🟢" if rate == 100 else "🟡" if rate >= 80 else "🔴"
            report.append(f"| {cat} | {data['total']} | {data['passed']} | {data['total'] - data['passed']} | {rate}% {icon} |")
        
        total_rate = stats["pass_rate"]
        overall_icon = "🟢" if total_rate == 100 else "🟡" if total_rate >= 80 else "🔴"
        report.append(f"| **总计** | **{stats['total']}** | **{stats['passed']}** | **{stats['failed']}** | **{total_rate}%** {overall_icon} |\n")
        
        # 5. 新发现问题
        failed_tests = [r for r in self.results if not r["passed"]]
        report.append("## 5. 新发现问题\n")
        
        if failed_tests:
            report.append("以下测试用例未通过，需要关注:\n")
            report.append("| 测试ID | 缺陷ID | 测试名称 | 实际状态码 | 错误详情 |")
            report.append("|--------|--------|----------|------------|----------|")
            
            for t in failed_tests:
                error_detail = t.get("details", t.get("error", "未知错误"))[:100]
                report.append(f"| {t['test_id']} | {t['defect_id']} | {t['name']} | {t['actual_status']} | {error_detail} |")
            
            report.append("")
        else:
            report.append("**✅ 所有测试均通过，未发现新问题！**\n")
        
        # 6. 性能指标
        report.append("## 6. 性能指标\n")
        report.append("| 指标 | 数值 | 评价 |")
        report.append("|------|------|------|")
        
        avg_rt = stats["avg_response_time_ms"]
        avg_eval = "优秀" if avg_rt < 200 else "良好" if avg_rt < 500 else "需优化"
        report.append(f"| 平均响应时间 | {avg_rt}ms | {avg_eval} |")
        
        max_rt = stats["max_response_time_ms"]
        max_eval = "正常" if max_rt < 1000 else "较慢" if max_rt < 3000 else "超时风险"
        report.append(f"| 最大响应时间 | {max_rt}ms | {max_eval} |")
        
        min_rt = stats["min_response_time_ms"]
        report.append(f"| 最小响应时间 | {min_rt}ms | 正常 |")
        report.append("")
        
        # 7. 结论与建议
        report.append("## 7. 结论与建议\n")
        
        if stats["pass_rate"] == 100:
            report.append("### 🎉 结论: 可以进入验收阶段\n")
            report.append("**评估结果**: ✅ 全部通过  \n")
            report.append("**质量评级**: ⭐⭐⭐⭐⭐ (5/5)  \n")
            report.append("**部署风险**: 🟢 低风险  \n\n")
            report.append("**详细说明**:  \n")
            report.append(f"- 所有 {stats['total']} 个测试用例全部通过，通过率 100%  \n")
            report.append("- P0级缺陷（API-01至API-04）已全部修复验证通过  \n")
            report.append("- 参数校验改进已生效，返回友好的错误信息  \n")
            report.append("- 正常功能未被破坏，回归测试全部通过  \n")
            report.append("- 系统性能表现良好，响应时间在合理范围内  \n\n")
            report.append("**建议**:  \n")
            report.append("1. ✅ 可以进入UAT用户验收测试阶段  \n")
            report.append("2. ✅ 可以准备生产环境部署  \n")
            report.append("3. ⚠️ 建议在生产环境部署后进行冒烟测试确认  \n")
            report.append("4. 📋 建议补充自动化单元测试覆盖新增的校验逻辑  \n")
        elif stats["pass_rate"] >= 90:
            report.append("### ⚠️ 结论: 基本可以进入验收，但有小问题需处理\n")
            report.append(f"**评估结果**: ⚠️ 大部分通过 ({stats['pass_rate']}%)  \n")
            report.append("**质量评级**: ⭐⭐⭐⭐ (4/5)  \n")
            report.append("**部署风险**: 🟡 中等风险  \n\n")
            report.append("**说明**:  \n")
            report.append(f"- {stats['failed']} 个测试用例未通过，需要进一步检查  \n")
            report.append("- 主要P0缺陷已修复，但存在边缘情况问题  \n\n")
            report.append("**建议**:  \n")
            report.append("1. 🔧 优先修复失败的测试用例对应的问题  \n")
            report.append("2. 🧪 修复后重新执行回归测试  \n")
            report.append("3. ⚠️ 在问题解决前不建议进入生产环境  \n")
        else:
            report.append("### ❌ 结论: 不建议进入验收阶段\n")
            report.append(f"**评估结果**: ❌ 通过率过低 ({stats['pass_rate']}%)  \n")
            report.append("**质量评级**: ⭐⭐ (2/5)  \n")
            report.append("**部署风险**: 🔴 高风险  \n\n")
            report.append("**说明**:  \n")
            report.append(f"- {stats['failed']} 个测试用例未通过，存在严重问题  \n")
            report.append("- P0级缺陷可能未完全修复  \n")
            report.append("- 存在功能 regression 问题  \n\n")
            report.append("**建议**:  \n")
            report.append("1. 🚫 暂停验收流程  \n")
            report.append("2. 🔧 立即修复所有失败用例  \n")
            report.append("3. 🔍 进行全面的根因分析  \n")
            report.append("4. 📋 修复后必须重新进行完整回归测试  \n")
        
        report.append("\n---\n")
        report.append("*此报告由 API Test Pro 自动生成*  \n")
        report.append(f"*测试框架版本: v1.0 | 执行时间: {stats['timestamp']}*\n")
        
        # 写入文件
        report_content = "\n".join(report)
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"✅ Markdown报告已保存到: {REPORT_FILE}")
        return report_content


def setup_test_cases(runner: RegressionTestRunner):
    """设置所有测试用例"""
    
    # ==================== P0级缺陷修复验证 ====================
    
    # API-01: 空参数登录 → 应返回400(不再是500)
    runner.add_test_case(TestCase(
        test_id="TC-001",
        defect_id="API-01",
        name="空用户名登录测试",
        service="user_service",
        method="POST",
        endpoint="/user/login",
        expected_status=400,
        expected_message_contains="用户名不能为空",
        params={"username": "", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        category="P0-FIX"
    ))
    
    runner.add_test_case(TestCase(
        test_id="TC-002",
        defect_id="API-01",
        name="空密码登录测试",
        service="user_service",
        method="POST",
        endpoint="/user/login",
        expected_status=400,
        expected_message_contains="密码不能为空",
        params={"username": "admin", "password": ""},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        category="P0-FIX"
    ))
    
    runner.add_test_case(TestCase(
        test_id="TC-003",
        defect_id="API-01",
        name="用户名和密码都为空测试",
        service="user_service",
        method="POST",
        endpoint="/user/login",
        expected_status=400,
        expected_message_contains="不能为空",
        params={"username": "", "password": ""},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        category="P0-FIX"
    ))
    
    # API-02: 完整数据创建标本 → 应成功(不再是500)
    complete_sample_data = {
        "sampleNo": f"REG-{int(time.time())}",
        "patientId": 1,
        "patientName": "回归测试患者",
        "patientGender": "男",
        "patientAge": 35,
        "doctorId": 1,
        "doctorName": "张医生",
        "testItems": "血常规,尿常规,生化全项",
        "sampleType": "BLOOD",
        "collectTime": "2026-04-02T10:00:00",
        "collectLocation": "门诊采血室",
        "status": "COLLECTED",
        "remark": "回归测试标本"
    }
    
    runner.add_test_case(TestCase(
        test_id="TC-004",
        defect_id="API-02",
        name="完整数据创建标本测试",
        service="sample_service",
        method="POST",
        endpoint="/sample/create",
        expected_status=200,  # 接受200或201
        data=complete_sample_data,
        category="P0-FIX"
    ))
    
    runner.add_test_case(TestCase(
        test_id="TC-005",
        defect_id="API-02",
        name="最小必填字段创建标本测试",
        service="sample_service",
        method="POST",
        endpoint="/sample/create",
        expected_status=200,
        data={
            "sampleNo": f"MIN-{int(time.time())}",
            "patientName": "最小字段患者",
            "testItems": "血常规"
        },
        category="P0-FIX"
    ))
    
    # API-03: 标本按状态查询 → 应成功(不再是500)
    for status in ["PENDING", "RECEIVED", "TESTING", "COMPLETED", "COLLECTED"]:
        runner.add_test_case(TestCase(
            test_id=f"TC-006-{status[:3].upper()}",
            defect_id="API-03",
            name=f"按状态查询标本({status})",
            service="sample_service",
            method="GET",
            endpoint="/sample/list-by-status",
            expected_status=200,
            params={"status": status},
            category="P0-FIX"
        ))
    
    runner.add_test_case(TestCase(
        test_id="TC-007",
        defect_id="API-03",
        name="空状态参数查询测试",
        service="sample_service",
        method="GET",
        endpoint="/sample/list-by-status",
        expected_status=400,
        expected_message_contains="不能为空",
        params={"status": ""},
        category="P0-FIX"
    ))
    
    # API-04: 完整数据创建报告 → 应成功(不再是500)
    complete_report_data = {
        "reportNo": f"RPT-{int(time.time())}",
        "sampleId": 1,
        "sampleNo": "SAMPLE-001",
        "patientId": 1,
        "patientName": "回归测试患者",
        "testItems": "血常规,尿常规",
        "technicianId": 1,
        "technicianName": "李技师",
        "status": "PENDING",
        "remark": "回归测试报告"
    }
    
    runner.add_test_case(TestCase(
        test_id="TC-008",
        defect_id="API-04",
        name="完整数据创建报告测试",
        service="report_service",
        method="POST",
        endpoint="/report/create",
        expected_status=200,  # 接受200或201
        data=complete_report_data,
        category="P0-FIX"
    ))
    
    runner.add_test_case(TestCase(
        test_id="TC-009",
        defect_id="API-04",
        name="最小必填字段创建报告测试",
        service="report_service",
        method="POST",
        endpoint="/report/create",
        expected_status=200,
        data={
            "sampleId": 1,
            "patientName": "最小字段患者",
            "testItems": "血常规"
        },
        category="P0-FIX"
    ))
    
    # ==================== 参数校验改进验证 ====================
    
    runner.add_test_case(TestCase(
        test_id="TC-010",
        defect_id="VAL-01",
        name="创建标本-patientName为空",
        service="sample_service",
        method="POST",
        endpoint="/sample/create",
        expected_status=400,
        expected_message_contains="患者姓名不能为空",
        data={
            "sampleNo": f"VAL-{int(time.time())}",
            "patientName": "",
            "testItems": "血常规"
        },
        category="VALIDATION"
    ))
    
    runner.add_test_case(TestCase(
        test_id="TC-011",
        defect_id="VAL-01",
        name="创建标本-sampleNo为空",
        service="sample_service",
        method="POST",
        endpoint="/sample/create",
        expected_status=400,
        expected_message_contains="标本编号不能为空",
        data={
            "sampleNo": "",
            "patientName": "有效患者",
            "testItems": "血常规"
        },
        category="VALIDATION"
    ))
    
    runner.add_test_case(TestCase(
        test_id="TC-012",
        defect_id="VAL-01",
        name="创建标本-testItems为空",
        service="sample_service",
        method="POST",
        endpoint="/sample/create",
        expected_status=400,
        expected_message_contains="检验项目不能为空",
        data={
            "sampleNo": f"VAL2-{int(time.time())}",
            "patientName": "有效患者",
            "testItems": ""
        },
        category="VALIDATION"
    ))
    
    runner.add_test_case(TestCase(
        test_id="TC-013",
        defect_id="VAL-02",
        name="创建报告-reportNo为空",
        service="report_service",
        method="POST",
        endpoint="/report/create",
        expected_status=400,
        expected_message_contains="报告编号不能为空",
        data={
            "reportNo": "",
            "sampleId": 1,
            "patientName": "有效患者",
            "testItems": "血常规"
        },
        category="VALIDATION"
    ))
    
    runner.add_test_case(TestCase(
        test_id="TC-014",
        defect_id="VAL-02",
        name="创建报告-patientName为空",
        service="report_service",
        method="POST",
        endpoint="/report/create",
        expected_status=400,
        expected_message_contains="患者姓名不能为空",
        data={
            "reportNo": f"RPTV-{int(time.time())}",
            "sampleId": 1,
            "patientName": "",
            "testItems": "血常规"
        },
        category="VALIDATION"
    ))
    
    runner.add_test_case(TestCase(
        test_id="TC-015",
        defect_id="VAL-02",
        name="创建报告-sampleId为空",
        service="report_service",
        method="POST",
        endpoint="/report/create",
        expected_status=400,
        expected_message_contains="标本ID不能为空",
        data={
            "reportNo": f"RPTV2-{int(time.time())}",
            "patientName": "有效患者",
            "testItems": "血常规"
        },
        category="VALIDATION"
    ))
    
    # ==================== 正常功能回归测试 ====================
    
    # REG-01: 正常登录
    runner.add_test_case(TestCase(
        test_id="TC-016",
        defect_id="REG-01",
        name="正常登录(admin/admin123)",
        service="user_service",
        method="POST",
        endpoint="/user/login",
        expected_status=200,
        params={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        category="REGRESSION"
    ))
    
    # REG-02: 获取标本列表
    runner.add_test_case(TestCase(
        test_id="TC-017",
        defect_id="REG-02",
        name="获取标本列表",
        service="sample_service",
        method="GET",
        endpoint="/sample/list",
        expected_status=200,
        category="REGRESSION"
    ))
    
    # REG-03: 获取报告列表
    runner.add_test_case(TestCase(
        test_id="TC-018",
        defect_id="REG-03",
        name="获取报告列表",
        service="report_service",
        method="GET",
        endpoint="/report/list",
        expected_status=200,
        category="REGRESSION"
    ))
    
    # REG-04: AI健康检查
    runner.add_test_case(TestCase(
        test_id="TC-019",
        defect_id="REG-04",
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
    print("实验室管理系统 v1.4.1 回归测试套件")
    print("API Test Pro - 专业API测试工具")
    print("="*80)
    
    # 创建测试运行器
    runner = RegressionTestRunner()
    
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
        print("🎉 回归测试全部通过! 系统可以进入验收阶段.")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print(f"⚠️ 回归测试完成，通过率: {stats['pass_rate']}%")
        print(f"   请查看详细报告: {REPORT_FILE}")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
