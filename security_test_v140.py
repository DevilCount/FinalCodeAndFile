#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统安全测试脚本 v1.4.0
===============================
作为安全测试专家+API测试专家，对系统进行全面的安全性测试

测试范围：
1. 认证与授权测试
2. SQL注入测试
3. XSS跨站脚本测试
4. 敏感信息泄露检测
5. CSRF防护测试
6. 暴力破解防护测试
7. 密码安全检查
8. 安全响应头检测
9. CORS配置检测
10. 速率限制测试

作者: API Test Pro (安全测试专家)
日期: 2026-04-02
版本: v1.4.0
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import urllib.parse


class RiskLevel(Enum):
    """风险等级枚举"""
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"
    INFO = "Info"


class TestResult(Enum):
    """测试结果枚举"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    ERROR = "ERROR"


@dataclass
class SecurityTestItem:
    """安全测试项"""
    id: str
    name: str
    category: str
    result: TestResult = TestResult.ERROR
    details: str = ""
    risk_level: RiskLevel = RiskLevel.INFO
    request_url: str = ""
    request_method: str = ""
    request_data: Any = None
    response_status: int = 0
    response_data: Any = None
    vulnerability_type: str = ""
    remediation: str = ""
    cvss_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Vulnerability:
    """安全漏洞"""
    id: str
    title: str
    severity: RiskLevel
    cvss_score: float
    description: str
    reproduction_steps: List[str]
    impact: str
    remediation: str
    references: List[str] = field(default_factory=list)
    affected_endpoints: List[str] = field(default_factory=list)


class SecurityTestSuite:
    """安全测试套件"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
        self.test_results: List[SecurityTestItem] = []
        self.vulnerabilities: List[Vulnerability] = []
        self.auth_token: Optional[str] = None
        self.test_user_credentials = {
            "username": "admin",
            "password": "admin123"
        }

        # API端点配置
        self.endpoints = {
            "user_login": "/api/user/login",
            "user_register": "/api/user/register",
            "user_list": "/api/user/list",
            "user_by_id": "/api/user/{id}",
            "user_all": "/api/user/all",
            "sample_create": "/api/sample/create",
            "sample_list": "/api/sample/list",
            "sample_by_id": "/api/sample/{id}",
            "report_list": "/api/report/list",
            "ai_diagnose": "/api/ai/diagnose",
            "hl7_message": "/api/hl7/message"
        }

        # 统计信息
        self.stats = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "errors": 0,
            "critical_count": 0,
            "major_count": 0,
            "minor_count": 0
        }

    def add_test_result(self, test_item: SecurityTestItem):
        """添加测试结果"""
        self.test_results.append(test_item)
        self.stats["total_tests"] += 1

        if test_item.result == TestResult.PASS:
            self.stats["passed"] += 1
        elif test_item.result == TestResult.FAIL:
            self.stats["failed"] += 1
            if test_item.risk_level == RiskLevel.CRITICAL:
                self.stats["critical_count"] += 1
            elif test_item.risk_level == RiskLevel.MAJOR:
                self.stats["major_count"] += 1
            elif test_item.risk_level == RiskLevel.MINOR:
                self.stats["minor_count"] += 1
        elif test_item.result == TestResult.WARN:
            self.stats["warnings"] += 1
        else:
            self.stats["errors"] += 1

    def add_vulnerability(self, vuln: Vulnerability):
        """添加漏洞"""
        self.vulnerabilities.append(vuln)

    def make_request(self, method: str, endpoint: str, **kwargs) -> Tuple[requests.Response, float]:
        """
        发送HTTP请求并记录响应时间
        返回: (response, response_time_ms)
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            if method.upper() == "GET":
                response = self.session.get(url, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, **kwargs)
            elif method.upper() == "PUT":
                response = self.session.put(url, **kwargs)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, **kwargs)
            elif method.upper() == "OPTIONS":
                response = self.session.options(url, **kwargs)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            response_time = (time.time() - start_time) * 1000
            return response, response_time

        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")

    def login(self, username: str = None, password: str = None) -> bool:
        """登录获取Token"""
        username = username or self.test_user_credentials["username"]
        password = password or self.test_user_credentials["password"]

        try:
            data = {"username": username, "password": password}
            response, _ = self.make_request("POST", self.endpoints["user_login"], data=data)

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200 and result.get("data"):
                    # 尝试从响应中提取token
                    user_data = result.get("data", {})
                    # 假设token在某个字段中，或者使用session cookie
                    if "token" in user_data:
                        self.auth_token = user_data["token"]
                    return True
            return False

        except Exception as e:
            print(f"[登录失败] {str(e)}")
            return False

    # ==================== 认证与授权测试 ====================

    def test_auth_no_token_access(self):
        """测试1.1: 无Token访问受保护接口"""
        print("\n[测试1.1] 无Token访问受保护接口")

        protected_endpoints = [
            ("GET", self.endpoints["user_list"]),
            ("GET", self.endpoints["user_all"]),
            ("GET", self.endpoints["sample_list"]),
            ("POST", self.endpoints["sample_create"]),
        ]

        for method, endpoint in protected_endpoints:
            test_id = f"AUTH-NO-TOKEN-{method}-{endpoint.replace('/', '-')}"
            try:
                response, _ = self.make_request(method, endpoint)

                # 检查是否返回401或403（应该拒绝未认证访问）
                if response.status_code in [401, 403]:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"无Token访问 {method} {endpoint}",
                        category="认证与授权",
                        result=TestResult.PASS,
                        details=f"正确返回{response.status_code}状态码，拒绝未认证访问",
                        risk_level=RiskLevel.INFO,
                        request_url=endpoint,
                        request_method=method,
                        response_status=response.status_code,
                        vulnerability_type="无",
                        remediation="无需修复"
                    )
                elif response.status_code == 200:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"无Token访问 {method} {endpoint}",
                        category="认证与授权",
                        result=TestResult.FAIL,
                        details=f"严重安全漏洞！未认证即可访问受保护资源，返回200状态码",
                        risk_level=RiskLevel.CRITICAL,
                        request_url=endpoint,
                        request_method=method,
                        response_status=response.status_code,
                        vulnerability_type="认证绕过",
                        cvss_score=9.8,
                        remediation="添加JWT Token验证拦截器或Spring Security配置"
                    )
                    self.add_vulnerability(Vulnerability(
                        id=test_id,
                        title="认证绕过 - 未授权访问受保护API",
                        severity=RiskLevel.CRITICAL,
                        cvss_score=9.8,
                        description=f"端点 {method} {endpoint} 无需认证即可访问",
                        reproduction_steps=[
                            f"1. 不携带任何认证Token",
                            f"2. 发送 {method} 请求到 {self.base_url}{endpoint}",
                            f"3. 观察到服务器返回200成功响应"
                        ],
                        impact="攻击者可以未经授权访问敏感数据和执行操作",
                        remediation="在Gateway或各微服务中添加JWT Token验证过滤器",
                        affected_endpoints=[f"{method} {endpoint}"]
                    ))
                else:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"无Token访问 {method} {endpoint}",
                        category="认证与授权",
                        result=TestResult.WARN,
                        details=f"返回意外状态码: {response.status_code}",
                        risk_level=RiskLevel.MINOR,
                        request_url=endpoint,
                        request_method=method,
                        response_status=response.status_code
                    )

                self.add_test_result(result)

            except Exception as e:
                self.add_test_result(SecurityTestItem(
                    id=test_id,
                    name=f"无Token访问 {method} {endpoint}",
                    category="认证与授权",
                    result=TestResult.ERROR,
                    details=f"测试异常: {str(e)}",
                    request_url=endpoint,
                    request_method=method
                ))

    def test_auth_expired_token(self):
        """测试1.2: 使用过期/伪造的Token访问"""
        print("\n[测试1.2] 使用过期/伪造的Token访问")

        fake_tokens = [
            "invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
            "",
            "null",
            "Bearer fake_token_12345"
        ]

        for token in fake_tokens:
            test_id = f"AUTH-FAKE-TOKEN-{hash(token) % 10000}"
            headers = {"Authorization": f"Bearer {token}"}

            try:
                response, _ = self.make_request("GET", self.endpoints["user_list"], headers=headers)

                if response.status_code in [401, 403]:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"伪造Token访问 (token={token[:20]}...)",
                        category="认证与授权",
                        result=TestResult.PASS,
                        details=f"正确拒绝伪造Token，返回{response.status_code}",
                        risk_level=RiskLevel.INFO,
                        response_status=response.status_code
                    )
                elif response.status_code == 200:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"伪造Token访问 (token={token[:20]}...)",
                        category="认证与授权",
                        result=TestResult.FAIL,
                        details="严重漏洞！接受无效Token并允许访问",
                        risk_level=RiskLevel.CRITICAL,
                        response_status=response.status_code,
                        vulnerability_type="Token伪造",
                        cvss_score=9.8,
                        remediation="实现严格的JWT Token验证机制"
                    )
                else:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"伪造Token访问 (token={token[:20]}...)",
                        category="认证与授权",
                        result=TestResult.WARN,
                        details=f"返回状态码: {response.status_code}",
                        risk_level=RiskLevel.MINOR,
                        response_status=response.status_code
                    )

                self.add_test_result(result)

            except Exception as e:
                self.add_test_result(SecurityTestItem(
                    id=test_id,
                    name=f"伪造Token访问",
                    category="认证与授权",
                    result=TestResult.ERROR,
                    details=f"测试异常: {str(e)}"
                ))

    def test_auth_role_based_access(self):
        """测试1.3: 角色权限边界测试（如果有角色区分）"""
        print("\n[测试1.3] 角色权限边界测试")

        # 测试不同角色的访问权限
        role_based_tests = [
            ("ADMIN", self.endpoints["user_list"], "管理员应能访问用户列表"),
            ("DOCTOR", self.endpoints["user_list"], "医生不应能访问完整用户列表"),
            ("LAB_TECHNICIAN", self.endpoints["user_list"], "检验师不应能访问完整用户列表"),
        ]

        for role, endpoint, description in role_based_tests:
            test_id = f"AUTH-ROLE-{role}"
            # 注意：此测试需要在有有效Token的情况下进行
            # 这里仅记录测试用例，实际测试依赖具体业务逻辑
            result = SecurityTestItem(
                id=test_id,
                name=f"角色权限测试 - {role}",
                category="认证与授权",
                result=TestResult.WARN,
                details=f"待测试: {description}。需要有效的{role}角色Token才能完成测试",
                risk_level=RiskLevel.INFO,
                remediation="确保实现了基于角色的访问控制(RBAC)"
            )
            self.add_test_result(result)

    # ==================== SQL注入测试 ====================

    def test_sql_injection_login(self):
        """测试2.1: 登录接口SQL注入"""
        print("\n[测试2.1] 登录接口SQL注入测试")

        sql_injection_payloads = [
            ("admin' OR '1'='1", "经典SQL注入"),
            ("admin'--", "MySQL注释注入"),
            ("admin'#", "MySQL注释注入#"),
            ("' OR 1=1--", "OR注入"),
            ("' OR '1'='1' --", "字符串比较注入"),
            ("admin' UNION SELECT * FROM sys_user--", "UNION注入"),
            ("'; DROP TABLE users; --", "DROP TABLE注入"),
            ("1' OR '1'='1", "数字ID注入"),
            ("-1' OR 1=1 LIMIT 1--", "LIMIT注入"),
            ("admin\\'", "反斜杠转义"),
        ]

        for payload, desc in sql_injection_payloads:
            test_id = f"SQLI-LOGIN-{hash(payload) % 10000}"
            try:
                data = {"username": payload, "password": "anything"}
                response, response_time = self.make_request("POST", self.endpoints["user_login"], data=data)

                response_text = response.text.lower()
                is_vulnerable = False

                # 检查是否出现SQL注入成功的迹象
                success_indicators = [
                    response.status_code == 200 and "登录成功" in response.text,
                    "sql syntax" in response_text,
                    "mysql" in response_text,
                    "ORA-" in response_text,
                    "postgresql" in response_text,
                    "unclosed quotation mark" in response_text,
                ]

                if any(success_indicators):
                    is_vulnerable = True

                if is_vulnerable:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"SQL注入测试 - {desc}",
                        category="SQL注入",
                        result=TestResult.FAIL,
                        details=f"发现SQL注入漏洞！Payload: {payload}, 响应: {response.text[:200]}",
                        risk_level=RiskLevel.CRITICAL,
                        request_url=self.endpoints["user_login"],
                        request_method="POST",
                        request_data=data,
                        response_status=response.status_code,
                        response_data=response.text[:500],
                        vulnerability_type="SQL注入",
                        cvss_score=10.0,
                        remediation="使用参数化查询(PreparedStatement)或ORM框架(MyBatis Plus)"
                    )
                    self.add_vulnerability(Vulnerability(
                        id=test_id,
                        title=f"SQL注入漏洞 - {desc}",
                        severity=RiskLevel.CRITICAL,
                        cvss_score=10.0,
                        description=f"登录接口存在SQL注入漏洞，攻击者可使用payload: {payload}",
                        reproduction_steps=[
                            f"1. 在登录用户名输入框输入: {payload}",
                            "2. 密码输入任意值",
                            "3. 点击登录",
                            "4. 观察是否能够绕过认证或获取数据库错误信息"
                        ],
                        impact="可能导致数据泄露、数据篡改、甚至整个数据库被删除",
                        remediation="使用MyBatis Plus的参数化查询或Spring Data JPA，避免拼接SQL",
                        affected_endpoints=[f"POST {self.endpoints['user_login']}"]
                    ))
                else:
                    # 检查是否正确拒绝了恶意输入
                    if response.status_code in [400, 401, 403]:
                        result = SecurityTestItem(
                            id=test_id,
                            name=f"SQL注入测试 - {desc}",
                            category="SQL注入",
                            result=TestResult.PASS,
                            details=f"已正确拦截SQL注入尝试，返回{response.status_code}",
                            risk_level=RiskLevel.INFO,
                            request_url=self.endpoints["user_login"],
                            request_method="POST",
                            request_data=data,
                            response_status=response.status_code,
                            vulnerability_type="无"
                        )
                    else:
                        result = SecurityTestItem(
                            id=test_id,
                            name=f"SQL注入测试 - {desc}",
                            category="SQL注入",
                            result=TestResult.WARN,
                            details=f"响应状态码: {response.status_code}, 需人工确认是否安全",
                            risk_level=RiskLevel.MINOR,
                            request_url=self.endpoints["user_login"],
                            request_method="POST",
                            request_data=data,
                            response_status=response.status_code
                        )

                self.add_test_result(result)

            except Exception as e:
                self.add_test_result(SecurityTestItem(
                    id=test_id,
                    name=f"SQL注入测试 - {desc}",
                    category="SQL注入",
                    result=TestResult.ERROR,
                    details=f"测试异常: {str(e)}"
                ))

    def test_sql_injection_search_and_id(self):
        """测试2.2: 搜索和ID参数的SQL注入"""
        print("\n[测试2.2] 搜索和ID参数SQL注入测试")

        injection_payloads = [
            ("1 OR 1=1", "OR注入"),
            ("1; DROP TABLE samples--", "DROP注入"),
            ("1' AND 1=1--", "AND注入"),
            ("1 UNION SELECT * FROM sys_user--", "UNION注入"),
            ("-1 OR 1=1", "负数OR注入"),
            ("1; WAITFOR DELAY '0:0:5'--", "时间盲注"),
        ]

        # 测试用户ID参数
        for payload, desc in injection_payloads:
            test_id = f"SQLI-ID-{hash(payload) % 10000}"
            endpoint = self.endpoints["user_by_id"].format(id=payload)

            try:
                response, _ = self.make_request("GET", endpoint)

                # 检查是否有SQL错误或异常行为
                response_text = response.text.lower()
                error_indicators = ["sql", "syntax", "error", "exception", "mysql", "ora-"]

                has_error = any(indicator in response_text for indicator in error_indicators)
                returns_data = response.status_code == 200 and len(response.text) > 100

                if has_error:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"ID参数SQL注入 - {desc}",
                        category="SQL注入",
                        result=TestResult.FAIL,
                        details=f"发现潜在SQL注入！响应包含错误信息: {response_text[:200]}",
                        risk_level=RiskLevel.CRITICAL,
                        request_url=endpoint,
                        request_method="GET",
                        response_status=response.status_code,
                        vulnerability_type="SQL注入",
                        cvss_score=9.8,
                        remediation="使用@PathVariable参数绑定和类型转换"
                    )
                    self.add_vulnerability(Vulnerability(
                        id=test_id,
                        title=f"ID参数SQL注入 - {desc}",
                        severity=RiskLevel.CRITICAL,
                        cvss_score=9.8,
                        description=f"ID参数存在SQL注入风险，payload: {payload}"
                    ))
                elif not returns_data or response.status_code in [400, 404]:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"ID参数SQL注入 - {desc}",
                        category="SQL注入",
                        result=TestResult.PASS,
                        details=f"已正确处理恶意ID参数，返回{response.status_code}",
                        risk_level=RiskLevel.INFO,
                        request_url=endpoint,
                        request_method="GET",
                        response_status=response.status_code
                    )
                else:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"ID参数SQL注入 - {desc}",
                        category="SQL注入",
                        result=TestResult.WARN,
                        details=f"需进一步验证安全性，状态码: {response.status_code}",
                        risk_level=RiskLevel.MINOR,
                        request_url=endpoint,
                        request_method="GET",
                        response_status=response.status_code
                    )

                self.add_test_result(result)

            except Exception as e:
                self.add_test_result(SecurityTestItem(
                    id=test_id,
                    name=f"ID参数SQL注入 - {desc}",
                    category="SQL注入",
                    result=TestResult.ERROR,
                    details=f"测试异常: {str(e)}"
                ))

    # ==================== XSS跨站脚本测试 ====================

    def test_xss_injection(self):
        """测试3: XSS跨站脚本注入"""
        print("\n[测试3] XSS跨站脚本注入测试")

        xss_payloads = [
            ("<script>alert('xss')</script>", "基础Script标签"),
            ("<img onerror=alert('xss') src=x>", "Img onerror事件"),
            ("<svg onload=alert('xss')>", "SVG onload事件"),
            ("javascript:alert('xss')", "JavaScript协议"),
            ("'><script>alert('xss')</script>", "属性逃逸"),
            ("<iframe src='javascript:alert(`xss`)'>", "Iframe注入"),
            ("{{constructor.constructor('return this')()}}", "模板注入"),
            ("<body onload=alert('xss')>", "Body onload事件"),
            ("</textarea><script>alert('xss')</script>", "Textarea闭合"),
            ("-alert(1)-", "表达式注入"),
        ]

        # 测试注册接口XSS
        for payload, desc in xss_payloads:
            test_id = f"XSS-REGISTER-{hash(payload) % 10000}"

            # 构造包含XSS的用户数据
            xss_user_data = {
                "username": f"xss_test_{hash(payload) % 10000}",
                "password": "test123456",
                "realName": payload,  # 在姓名字段注入
                "role": "DOCTOR",
                "department": "测试科室"
            }

            try:
                response, _ = self.make_request("POST", self.endpoints["user_register"],
                                               json=xss_user_data)

                # 检查是否存储了未转义的XSS
                response_text = response.text
                is_stored_unescaped = payload.lower() in response_text.lower()

                # 如果注册成功，尝试检索该用户看XSS是否被存储
                if response.status_code == 200 or (response.json().get("code") == 200):
                    # 尝试通过用户名查询
                    list_response, _ = self.make_request("GET", self.endpoints["user_all"])
                    if payload.lower() in list_response.text.lower():
                        is_stored_unescaped = True

                if is_stored_unescaped:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"XSS存储型注入 - {desc}",
                        category="XSS跨站脚本",
                        result=TestResult.FAIL,
                        details=f"发现存储型XSS漏洞！Payload未被过滤/转义: {payload}",
                        risk_level=RiskLevel.CRITICAL,
                        request_url=self.endpoints["user_register"],
                        request_method="POST",
                        request_data=xss_user_data,
                        response_status=response.status_code,
                        vulnerability_type="存储型XSS",
                        cvss_score=8.5,
                        remediation="对所有输出进行HTML实体编码，使用ESAPI或OWASP Java Encoder"
                    )
                    self.add_vulnerability(Vulnerability(
                        id=test_id,
                        title=f"存储型XSS漏洞 - {desc}",
                        severity=RiskLevel.CRITICAL,
                        cvss_score=8.5,
                        description=f"姓名字段存在存储型XSS漏洞，可注入payload: {payload}",
                        reproduction_steps=[
                            f"1. 在注册页面的姓名字段输入: {payload}",
                            "2. 完成注册流程",
                            "3. 访问用户列表页面",
                            "4. JavaScript代码将在浏览器中执行"
                        ],
                        impact="可以窃取用户Session、Cookie、键盘记录、重定向到钓鱼网站等",
                        remediation="后端：使用HTML编码库对输出进行编码；前端：使用Vue的v-text代替v-html",
                        affected_endpoints=[f"POST {self.endpoints['user_register']}"]
                    ))
                else:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"XSS注入测试 - {desc}",
                        category="XSS跨站脚本",
                        result=TestResult.PASS,
                        details=f"XSS payload已被正确过滤或转义",
                        risk_level=RiskLevel.INFO,
                        request_url=self.endpoints["user_register"],
                        request_method="POST",
                        request_data=xss_user_data,
                        response_status=response.status_code,
                        vulnerability_type="无"
                    )

                self.add_test_result(result)

            except Exception as e:
                self.add_test_result(SecurityTestItem(
                    id=test_id,
                    name=f"XSS注入测试 - {desc}",
                    category="XSS跨站脚本",
                    result=TestResult.ERROR,
                    details=f"测试异常: {str(e)}"
                ))

    # ==================== 敏感信息泄露检测 ====================

    def test_sensitive_info_leakage(self):
        """测试4: 敏感信息泄露检测"""
        print("\n[测试4] 敏感信息泄露检测")

        # 4.1 测试API响应中是否暴露密码字段
        test_id = "SENSITIVE-PASSWORD-EXPOSURE"
        try:
            # 先尝试登录获取一个用户
            login_data = {"username": "admin", "password": "admin123"}
            response, _ = self.make_request("POST", self.endpoints["user_login"], data=login_data)

            if response.status_code == 200:
                result_data = response.json().get("data", {})

                # 检查响应中是否包含密码相关字段
                sensitive_fields = ["password", "pwd", "passwd", "passwordHash", "token", "secret"]
                exposed_fields = []

                for field in sensitive_fields:
                    if field in str(result_data).lower():
                        exposed_fields.append(field)

                if exposed_fields:
                    result = SecurityTestItem(
                        id=test_id,
                        name="密码字段泄露检测",
                        category="敏感信息泄露",
                        result=TestResult.FAIL,
                        details=f"API响应中暴露了敏感字段: {exposed_fields}",
                        risk_level=RiskLevel.CRITICAL,
                        response_status=response.status_code,
                        response_data=str(result_data)[:500],
                        vulnerability_type="敏感信息泄露",
                        cvss_score=7.5,
                        remediation="在返回用户对象前移除password字段，使用DTO模式"
                    )
                    self.add_vulnerability(Vulnerability(
                        id=test_id,
                        title="API响应泄露敏感信息 - 密码字段",
                        severity=RiskLevel.CRITICAL,
                        cvss_score=7.5,
                        description=f"登录/用户API响应中包含敏感字段: {exposed_fields}"
                    ))
                else:
                    result = SecurityTestItem(
                        id=test_id,
                        name="密码字段泄露检测",
                        category="敏感信息泄露",
                        result=TestResult.PASS,
                        details="API响应中未发现密码等敏感字段",
                        risk_level=RiskLevel.INFO,
                        response_status=response.status_code
                    )
            else:
                result = SecurityTestItem(
                    id=test_id,
                    name="密码字段泄露检测",
                    category="敏感信息泄露",
                    result=TestResult.WARN,
                    details=f"无法完成测试，登录返回: {response.status_code}",
                    risk_level=RiskLevel.MINOR,
                    response_status=response.status_code
                )

            self.add_test_result(result)

        except Exception as e:
            self.add_test_result(SecurityTestItem(
                id=test_id,
                name="密码字段泄露检测",
                category="敏感信息泄露",
                result=TestResult.ERROR,
                details=f"测试异常: {str(e)}"
            ))

        # 4.2 测试错误信息是否暴露内部细节
        test_id = "SENSITIVE-ERROR-MESSAGE"
        try:
            # 发送畸形请求触发错误
            invalid_data = {
                "username": "",  # 空用户名
                "password": ""   # 空密码
            }
            response, _ = self.make_request("POST", self.endpoints["user_login"], data=invalid_data)

            response_text = response.text.lower()
            internal_info_patterns = [
                r"exception",
                r"stack\s*trace",
                r"java\.",
                r"com\.sunyaxin",
                r"sql\s*syntax",
                r"at\s+\w+\.\w+\(",
                r"caused\s*by",
                r"internal\s*server\s*error.*\d{3,}",
                r"/home/|/var/|/usr/",
                r"localhost:\d+",
                r"127\.0\.0\.1:\d+"
            ]

            leaked_info = []
            for pattern in internal_info_patterns:
                matches = re.findall(pattern, response_text, re.IGNORECASE)
                if matches:
                    leaked_info.append(f"{pattern}: {matches[0]}")

            if leaked_info:
                result = SecurityTestItem(
                    id=test_id,
                    name="错误信息泄露检测",
                    category="敏感信息泄露",
                    result=TestResult.FAIL,
                    details=f"错误响应暴露了内部信息: {leaked_info[:5]}",
                    risk_level=RiskLevel.MAJOR,
                    response_status=response.status_code,
                    response_data=response_text[:500],
                    vulnerability_type="信息泄露",
                    cvss_score=5.0,
                    remediation="配置全局异常处理器，只返回通用错误消息给客户端"
                )
                self.add_vulnerability(Vulnerability(
                    id=test_id,
                    title="错误信息泄露内部实现细节",
                    severity=RiskLevel.MAJOR,
                    cvss_score=5.0,
                    description="API错误响应暴露了堆栈跟踪、类路径等内部信息"
                ))
            else:
                result = SecurityTestItem(
                    id=test_id,
                    name="错误信息泄露检测",
                    category="敏感信息泄露",
                    result=TestResult.PASS,
                    details="错误响应未暴露敏感内部信息",
                    risk_level=RiskLevel.INFO,
                    response_status=response.status_code
                )

            self.add_test_result(result)

        except Exception as e:
            self.add_test_result(SecurityTestItem(
                id=test_id,
                name="错误信息泄露检测",
                category="敏感信息泄露",
                result=TestResult.ERROR,
                details=f"测试异常: {str(e)}"
            ))

    # ==================== CORS配置检测 ====================

    def test_cors_configuration(self):
        """测试5: CORS跨域资源共享配置检测"""
        print("\n[测试5] CORS跨域资源配置检测")

        test_id = "CORS-CHECK"
        try:
            # 发送OPTIONS请求检查CORS头
            headers = {
                "Origin": "https://malicious-site.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization"
            }

            response, _ = self.make_request("OPTIONS", self.endpoints["user_login"], headers=headers)

            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
            }

            allowed_origin = cors_headers["Access-Control-Allow-Origin"]

            # 检查CORS配置安全性
            issues = []

            if allowed_origin == "*" or allowed_origin is None:
                issues.append("允许任意来源访问 (通配符*或无限制)")
            elif "malicious-site.com" in str(allowed_origin):
                issues.append("允许恶意域名访问")

            allow_credentials = cors_headers["Access-Control-Allow-Credentials"]
            if allow_credentials == "true" and allowed_origin == "*":
                issues.append("同时允许Credentials和通配符Origin（不安全的组合）")

            if issues:
                result = SecurityTestItem(
                    id=test_id,
                    name="CORS配置安全检测",
                    category="CORS安全",
                    result=TestResult.FAIL,
                    details=f"CORS配置存在安全问题: {'; '.join(issues)}",
                    risk_level=RiskLevel.MAJOR,
                    response_status=response.status_code,
                    response_data=cors_headers,
                    vulnerability_type="CORS配置不当",
                    cvss_score=6.5,
                    remediation="限制Allowed-Origin为特定域名，避免使用通配符*配合Credentials"
                )
                self.add_vulnerability(Vulnerability(
                    id=test_id,
                    title="CORS配置过于宽松",
                    severity=RiskLevel.MAJOR,
                    cvss_score=6.5,
                    description="CORS策略允许任意来源发起跨域请求",
                    impact="可能被利用进行跨站请求伪造(CSRF)攻击",
                    remediation="将allowedOriginPatterns改为具体的白名单域名"
                ))
            else:
                result = SecurityTestItem(
                    id=test_id,
                    name="CORS配置安全检测",
                    category="CORS安全",
                    result=TestResult.PASS,
                    details="CORS配置合理，限制了跨域访问来源",
                    risk_level=RiskLevel.INFO,
                    response_status=response.status_code,
                    response_data=cors_headers
                )

            self.add_test_result(result)

        except Exception as e:
            self.add_test_result(SecurityTestItem(
                id=test_id,
                name="CORS配置安全检测",
                category="CORS安全",
                result=TestResult.ERROR,
                details=f"测试异常: {str(e)}"
            ))

    # ==================== 安全响应头检测 ====================

    def test_security_headers(self):
        """测试6: 安全响应头检测"""
        print("\n[测试6] 安全响应头检测")

        required_security_headers = {
            "X-Frame-Options": {
                "expected_values": ["DENY", "SAMEORIGIN"],
                "description": "防止点击劫持攻击",
                "risk": RiskLevel.MAJOR,
                "cvss": 5.5
            },
            "X-Content-Type-Options": {
                "expected_values": ["nosniff"],
                "description": "防止MIME类型嗅探",
                "risk": RiskLevel.MINOR,
                "cvss": 3.5
            },
            "X-XSS-Protection": {
                "expected_values": ["1; mode=block", "1"],
                "description": "启用浏览器XSS过滤器",
                "risk": RiskLevel.MINOR,
                "cvss": 4.0
            },
            "Strict-Transport-Security": {
                "expected_values": ["max-age="],
                "description": "强制HTTPS连接(HSTS)",
                "risk": RiskLevel.MAJOR,
                "cvss": 5.0
            },
            "Content-Security-Policy": {
                "expected_values": [""],  # 只要有值就行
                "description": "内容安全策略，防止XSS和数据注入",
                "risk": RiskLevel.MAJOR,
                "cvss": 6.0
            },
            "Cache-Control": {
                "expected_values": ["no-store", "no-cache", "private"],
                "description": "防止缓存敏感响应",
                "risk": RiskLevel.MINOR,
                "cvss": 3.0
            },
            "Pragma": {
                "expected_values": ["no-cache"],
                "description": "HTTP/1.0防缓存指令",
                "risk": RiskLevel.INFO,
                "cvss": 2.0
            }
        }

        try:
            response, _ = self.make_request("GET", self.endpoints["user_login"])

            for header_name, config in required_security_headers.items():
                test_id = f"SEC-HEADER-{header_name.replace('-', '_')}"

                header_value = response.headers.get(header_name, "")

                if header_value:
                    # 检查是否符合预期
                    is_valid = any(
                        expected in header_value.lower()
                        for expected in config["expected_values"]
                        if expected  # 空字符串表示只要有值就通过
                    ) or (config["expected_values"] == [""] and header_value)

                    if is_valid or config["expected_values"] == [""]:
                        result = SecurityTestItem(
                            id=test_id,
                            name=f"安全响应头 - {header_name}",
                            category="安全响应头",
                            result=TestResult.PASS,
                            details=f"已设置 {header_name}: {header_value[:50]}",
                            risk_level=RiskLevel.INFO
                        )
                    else:
                        result = SecurityTestItem(
                            id=test_id,
                            name=f"安全响应头 - {header_name}",
                            category="安全响应头",
                            result=TestResult.WARN,
                            details=f"已设置但值可能不符合最佳实践: {header_value}",
                            risk_level=config["risk"]
                        )
                else:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"安全响应头 - {header_name}",
                        category="安全响应头",
                        result=TestResult.FAIL,
                        details=f"缺少关键安全响应头: {header_name} ({config['description']})",
                        risk_level=config["risk"],
                        vulnerability_type="缺少安全头",
                        cvss_score=config["cvss"],
                        remediation=f"在Gateway或Web服务器中添加{header_name}响应头"
                    )

                    if config["risk"] in [RiskLevel.MAJOR, RiskLevel.CRITICAL]:
                        self.add_vulnerability(Vulnerability(
                            id=test_id,
                            title=f"缺少安全响应头: {header_name}",
                            severity=config["risk"],
                            cvss_score=config["cvss"],
                            description=f"HTTP响应缺少{header_name}头，{config['description']}"
                        ))

                self.add_test_result(result)

        except Exception as e:
            self.add_test_result(SecurityTestItem(
                id="SEC-HEADER-ALL",
                name="安全响应头检测",
                category="安全响应头",
                result=TestResult.ERROR,
                details=f"测试异常: {str(e)}"
            ))

    # ==================== CSRF防护测试 ====================

    def test_csrf_protection(self):
        """测试7: CSRF跨站请求伪造防护"""
        print("\n[测试7] CSRF防护测试")

        test_id = "CSRF-PROTECTION"

        try:
            # 构造一个没有CSRF Token的POST请求
            csrf_test_data = {
                "username": "csrf_test_user",
                "password": "test123456",
                "realName": "CSRF测试",
                "role": "DOCTOR"
            }

            # 设置模拟来自其他域的Referer
            headers = {
                "Referer": "https://evil.com/attack.html",
                "Origin": "https://evil.com"
            }

            response, _ = self.make_request("POST", self.endpoints["user_register"],
                                           json=csrf_test_data, headers=headers)

            # 如果没有CSRF保护且请求成功了，说明存在CSRF漏洞
            if response.status_code == 200 and response.json().get("code") == 200:
                result = SecurityTestItem(
                    id=test_id,
                    name="CSRF防护检测",
                    category="CSRF防护",
                    result=TestResult.FAIL,
                    details="警告：可能缺少CSRF Token验证，跨域POST请求成功执行",
                    risk_level=RiskLevel.MAJOR,
                    response_status=response.status_code,
                    vulnerability_type="CSRF",
                    cvss_score=6.5,
                    remediation="实施CSRF Token、SameSite Cookie属性或双重提交Cookie"
                )
                self.add_vulnerability(Vulnerability(
                    id=test_id,
                    title="缺少CSRF防护",
                    severity=RiskLevel.MAJOR,
                    cvss_score=6.5,
                    description="State-changing操作(如注册)可能受到CSRF攻击",
                    reproduction_steps=[
                        "1. 用户已在目标网站登录",
                        "2. 用户访问恶意网站evil.com",
                        "3. 恶意网站自动向目标API发送POST请求",
                        "4. 请求以用户身份成功执行"
                    ],
                    impact="攻击者可以用户身份执行未授权操作",
                    remediation="对于REST API使用SameSite Cookie；对于传统表单使用CSRF Token"
                ))
            else:
                # 可能已有其他保护机制
                result = SecurityTestItem(
                    id=test_id,
                    name="CSRF防护检测",
                    category="CSRF防护",
                    result=TestResult.PASS,
                    details=f"跨域请求被阻止或需要额外认证，状态码: {response.status_code}",
                    risk_level=RiskLevel.INFO,
                    response_status=response.status_code
                )

            self.add_test_result(result)

        except Exception as e:
            self.add_test_result(SecurityTestItem(
                id=test_id,
                name="CSRF防护检测",
                category="CSRF防护",
                result=TestResult.ERROR,
                details=f"测试异常: {str(e)}"
            ))

    # ==================== 暴力破解防护测试 ====================

    def test_brute_force_protection(self):
        """测试8: 暴力破解防护"""
        print("\n[测试8] 暴力破解防护测试")

        test_id = "BRUTE-FORCE-PROTECTION"

        try:
            # 连续发送多次错误的登录请求
            failed_attempts = []
            start_time = time.time()

            for i in range(10):  # 尝试10次错误登录
                wrong_password = f"wrong_password_{i}"
                data = {"username": "admin", "password": wrong_password}

                attempt_start = time.time()
                response, response_time = self.make_request("POST", self.endpoints["user_login"], data=data)
                attempt_duration = time.time() - attempt_start

                failed_attempts.append({
                    "attempt": i + 1,
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                    "duration_s": round(attempt_duration, 3),
                    "timestamp": datetime.now().isoformat()
                })

                # 检测是否出现延迟或锁定迹象
                if i > 2:  # 第3次之后开始观察
                    pass

            total_time = time.time() - start_time
            avg_response_time = sum(a["response_time_ms"] for a in failed_attempts) / len(failed_attempts)

            # 分析是否存在速率限制或账户锁定
            last_5_times = [a["response_time_ms"] for a in failed_attempts[-5:]]
            first_5_times = [a["response_time_ms"] for a in failed_attempts[:5]]

            has_rate_limiting = avg(last_5_times) > avg(first_5_times) * 2  # 后半部分明显变慢
            has_account_lock = any(a["status_code"] == 429 for a in failed_attempts[-3:])  # Too Many Requests

            if has_account_lock or has_rate_limiting:
                result = SecurityTestItem(
                    id=test_id,
                    name="暴力破解防护检测",
                    category="暴力破解防护",
                    result=TestResult.PASS,
                    details=f"检测到防护机制! 总时间:{total_time:.2f}s, 平均响应:{avg_response_time:.2f}ms, 最后5次平均:{avg(last_5_times):.2f}ms",
                    risk_level=RiskLevel.INFO,
                    remediation="无需修复"
                )
            else:
                result = SecurityTestItem(
                    id=test_id,
                    name="暴力破解防护检测",
                    category="暴力破解防护",
                    result=TestResult.FAIL,
                    details=f"未检测到明显的速率限制或账户锁定! 10次尝试总时间:{total_time:.2f}s, 平均响应:{avg_response_time:.2f}ms",
                    risk_level=RiskLevel.MAJOR,
                    response_data=failed_attempts,
                    vulnerability_type="缺乏暴力破解防护",
                    cvss_score=7.0,
                    remediation="实施登录失败次数限制、账户临时锁IP黑名单机制"
                )
                self.add_vulnerability(Vulnerability(
                    id=test_id,
                    title="缺乏暴力破解防护机制",
                    severity=RiskLevel.MAJOR,
                    cvss_score=7.0,
                    description="登录接口未实施账户锁定或速率限制，可被暴力破解",
                    reproduction_steps=[
                        "1. 编写脚本自动发送登录请求",
                        "2. 使用常见密码字典进行猜测",
                        "3. 观察到无任何限制，可持续尝试"
                    ],
                    impact="攻击者可通过暴力破解获取管理员账户",
                    remediation="实现: ①5次失败后锁定15分钟 ②IP频率限制 ③验证码机制 ④登录日志告警"
                ))

            self.add_test_result(result)

        except Exception as e:
            self.add_test_result(SecurityTestItem(
                id=test_id,
                name="暴力破解防护检测",
                category="暴力破解防护",
                result=TestResult.ERROR,
                details=f"测试异常: {str(e)}"
            ))

    # ==================== 密码安全检查 ====================

    def test_password_security(self):
        """测试9: 密码安全策略检查"""
        print("\n[测试9] 密码安全策略检查")

        # 9.1 弱密码测试
        weak_passwords = [
            ("admin", "admin", "弱密码: admin/admin"),
            ("admin", "123456", "弱密码: 123456"),
            ("admin", "password", "弱密码: password"),
            ("admin", "admin123", "弱密码: admin123"),
            ("admin", "111111", "弱密码: 全相同字符"),
            ("admin", "abc123", "弱密码: 常见组合"),
        ]

        for username, password, desc in weak_passwords:
            test_id = f"PWD-WEAK-{hash(password) % 10000}"
            try:
                data = {"username": username, "password": password}
                response, _ = self.make_request("POST", self.endpoints["user_login"], data=data)

                if response.status_code == 200 and response.json().get("code") == 200:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"弱密码测试 - {desc}",
                        category="密码安全",
                        result=TestResult.WARN,
                        details=f"弱密码 '{password}' 可以成功登录!",
                        risk_level=RiskLevel.MAJOR,
                        remediation="强制实施强密码策略: 至少8位，包含大小写字母、数字、特殊字符"
                    )
                else:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"弱密码测试 - {desc}",
                        category="密码安全",
                        result=TestResult.PASS,
                        details=f"弱密码被正确拒绝，状态码: {response.status_code}",
                        risk_level=RiskLevel.INFO
                    )

                self.add_test_result(result)

            except Exception as e:
                self.add_test_result(SecurityTestItem(
                    id=test_id,
                    name=f"弱密码测试 - {desc}",
                    category="密码安全",
                    result=TestResult.ERROR,
                    details=f"测试异常: {str(e)}"
                ))

        # 9.2 密码传输加密检测
        test_id = "PWD-TRANSPORT-ENCRYPTION"
        try:
            response, _ = self.make_request("GET", self.endpoints["user_login"])

            # 检查是否使用HTTPS
            is_https = self.base_url.startswith("https://")

            if is_https:
                result = SecurityTestItem(
                    id=test_id,
                    name="密码传输加密检测",
                    category="密码安全",
                    result=TestResult.PASS,
                    details="使用HTTPS传输，密码在传输过程中被加密",
                    risk_level=RiskLevel.INFO
                )
            else:
                result = SecurityTestItem(
                    id=test_id,
                    name="密码传输加密检测",
                    category="密码安全",
                    result=TestResult.FAIL,
                    details="严重问题! 使用HTTP明文传输，密码可能被中间人窃取",
                    risk_level=RiskLevel.CRITICAL,
                    vulnerability_type="明文传输",
                    cvss_score=7.5,
                    remediation="立即部署SSL/TLS证书，强制使用HTTPS"
                )
                self.add_vulnerability(Vulnerability(
                    id=test_id,
                    title="密码明文传输 - 缺少HTTPS",
                    severity=RiskLevel.CRITICAL,
                    cvss_score=7.5,
                    description="登录凭证通过HTTP明文传输，易受中间人攻击"
                ))

            self.add_test_result(result)

        except Exception as e:
            self.add_test_result(SecurityTestItem(
                id=test_id,
                name="密码传输加密检测",
                category="密码安全",
                result=TestResult.ERROR,
                details=f"测试异常: {str(e)}"
            ))

    # ==================== 速率限制测试 ====================

    def test_rate_limiting(self):
        """测试10: API速率限制"""
        print("\n[测试10] API速率限制测试")

        test_id = "RATE-LIMITING"

        try:
            # 快速连续发送请求
            responses = []
            for i in range(20):  # 20次快速请求
                response, response_time = self.make_request("GET", self.endpoints["user_list"])
                responses.append({
                    "attempt": i + 1,
                    "status": response.status_code,
                    "time_ms": round(response_time, 2)
                })
                time.sleep(0.05)  # 50ms间隔

            # 检查是否有429 Too Many Requests响应
            rate_limited = any(r["status"] == 429 for r in responses)

            if rate_limited:
                result = SecurityTestItem(
                    id=test_id,
                    name="API速率限制检测",
                    category="速率限制",
                    result=TestResult.PASS,
                    details=f"检测到速率限制! 20次快速请求中有429响应",
                    risk_level=RiskLevel.INFO
                )
            else:
                # 检查响应时间是否显著增加
                times = [r["time_ms"] for r in responses]
                if len(times) > 10 and avg(times[-5:]) > avg(times[:5]) * 3:
                    result = SecurityTestItem(
                        id=test_id,
                        name="API速率限制检测",
                        category="速率限制",
                        result=TestResult.WARN,
                        details="未明确限制，但响应时间显著增加，可能有软限制",
                        risk_level=RiskLevel.MINOR
                    )
                else:
                    result = SecurityTestItem(
                        id=test_id,
                        name="API速率限制检测",
                        category="速率限制",
                        result=TestResult.FAIL,
                        details="未检测到API速率限制! 20次快速请求均成功",
                        risk_level=RiskLevel.MAJOR,
                        response_data=responses,
                        vulnerability_type="无速率限制",
                        cvss_score=5.5,
                        remediation="实施API速率限制: 同一IP每分钟最多60次请求"
                    )
                    self.add_vulnerability(Vulnerability(
                        id=test_id,
                        title="API缺少速率限制",
                        severity=RiskLevel.MAJOR,
                        cvss_score=5.5,
                        description="API端点未实施速率限制，可能遭受DDoS或滥用"
                    ))

            self.add_test_result(result)

        except Exception as e:
            self.add_test_result(SecurityTestItem(
                id=test_id,
                name="API速率限制检测",
                category="速率限制",
                result=TestResult.ERROR,
                details=f"测试异常: {str(e)}"
            ))

    # ==================== HTTP方法测试 ====================

    def test_http_methods_security(self):
        """测试11: HTTP方法安全"""
        print("\n[测试11] HTTP方法安全测试")

        test_endpoint = self.endpoints["user_list"]
        dangerous_methods = ["TRACE", "PUT", "DELETE", "PATCH", "OPTIONS"]

        for method in dangerous_methods:
            test_id = f"HTTP-METHOD-{method}"
            try:
                if method == "TRACE":
                    # TRACE方法特殊处理
                    continue

                response, _ = self.make_request(method, test_endpoint)

                if response.status_code == 405:  # Method Not Allowed
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"HTTP方法安全 - {method}",
                        category="HTTP安全",
                        result=TestResult.PASS,
                        details=f"{method} 方法被正确禁止，返回405",
                        risk_level=RiskLevel.INFO,
                        response_status=response.status_code
                    )
                elif response.status_code in [200, 201, 204]:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"HTTP方法安全 - {method}",
                        category="HTTP安全",
                        result=TestResult.FAIL,
                        details=f"危险! {method} 方法可用且返回成功",
                        risk_level=RiskLevel.MAJOR,
                        response_status=response.status_code,
                        vulnerability_type="HTTP方法滥用",
                        cvss_score=5.0,
                        remediation="禁用不必要的HTTP方法，只允许GET/POST"
                    )
                else:
                    result = SecurityTestItem(
                        id=test_id,
                        name=f"HTTP方法安全 - {method}",
                        category="HTTP安全",
                        result=TestResult.WARN,
                        details=f"{method} 返回: {response.status_code}",
                        risk_level=RiskLevel.MINOR,
                        response_status=response.status_code
                    )

                self.add_test_result(result)

            except Exception as e:
                self.add_test_result(SecurityTestItem(
                    id=test_id,
                    name=f"HTTP方法安全 - {method}",
                    category="HTTP安全",
                    result=TestResult.ERROR,
                    details=f"测试异常: {str(e)}"
                ))

    # ==================== 辅助函数 ====================

    def calculate_security_score(self) -> Tuple[str, float]:
        """计算总体安全评分"""
        if self.stats["total_tests"] == 0:
            return "F", 0.0

        # 权重计算
        critical_weight = 10
        major_weight = 5
        minor_weight = 2
        pass_weight = 1

        weighted_failures = (
            self.stats["critical_count"] * critical_weight +
            self.stats["major_count"] * major_weight +
            self.stats["minor_count"] * minor_weight
        )

        weighted_total = self.stats["passed"] * pass_weight + weighted_failures

        if weighted_total == 0:
            score = 100.0
        else:
            score = max(0, min(100, (self.stats["passed"] * pass_weight / weighted_total) * 100))

        # 评级
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        return grade, round(score, 1)

    def generate_report(self) -> dict:
        """生成测试报告"""
        grade, score = self.calculate_security_score()

        # 按CVSS分数排序漏洞
        sorted_vulnerabilities = sorted(self.vulnerabilities, key=lambda x: x.cvss_score, reverse=True)

        report = {
            "metadata": {
                "version": "v1.4.0",
                "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "target_system": "实验室管理系统 (Lab Management System)",
                "base_url": self.base_url,
                "tester": "API Test Pro (安全测试专家)",
                "framework": "Python requests + 自定义安全测试框架"
            },
            "summary": {
                "total_tests": self.stats["total_tests"],
                "passed": self.stats["passed"],
                "failed": self.stats["failed"],
                "warnings": self.stats["warnings"],
                "errors": self.stats["errors"],
                "pass_rate": round((self.stats["passed"] / max(1, self.stats["total_tests"])) * 100, 1),
                "security_grade": grade,
                "security_score": score,
                "critical_vulnerabilities": self.stats["critical_count"],
                "major_vulnerabilities": self.stats["major_count"],
                "minor_vulnerabilities": self.stats["minor_count"]
            },
            "test_results": [
                {
                    "id": t.id,
                    "name": t.name,
                    "category": t.category,
                    "result": t.result.value,
                    "details": t.details,
                    "risk_level": t.risk_level.value,
                    "request_url": t.request_url,
                    "request_method": t.request_method,
                    "response_status": t.response_status,
                    "vulnerability_type": t.vulnerability_type,
                    "cvss_score": t.cvss_score,
                    "remediation": t.remediation
                }
                for t in self.test_results
            ],
            "vulnerabilities": [
                {
                    "id": v.id,
                    "title": v.title,
                    "severity": v.severity.value,
                    "cvss_score": v.cvss_score,
                    "description": v.description,
                    "reproduction_steps": v.reproduction_steps,
                    "impact": v.impact,
                    "remediation": v.remediation,
                    "affected_endpoints": v.affected_endpoints
                }
                for v in sorted_vulnerabilities
            ]
        }

        return report

    def run_all_tests(self):
        """运行所有安全测试"""
        print("=" * 80)
        print("实验室管理系统安全测试套件 v1.4.0")
        print("=" * 80)
        print(f"目标系统: {self.base_url}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        try:
            # 执行所有测试
            print("\n>>> 开始执行安全测试...\n")

            # 1. 认证与授权测试
            self.test_auth_no_token_access()
            self.test_auth_expired_token()
            self.test_auth_role_based_access()

            # 2. SQL注入测试
            self.test_sql_injection_login()
            self.test_sql_injection_search_and_id()

            # 3. XSS测试
            self.test_xss_injection()

            # 4. 敏感信息泄露
            self.test_sensitive_info_leakage()

            # 5. CORS配置
            self.test_cors_configuration()

            # 6. 安全响应头
            self.test_security_headers()

            # 7. CSRF防护
            self.test_csrf_protection()

            # 8. 暴力破解防护
            self.test_brute_force_protection()

            # 9. 密码安全
            self.test_password_security()

            # 10. 速率限制
            self.test_rate_limiting()

            # 11. HTTP方法安全
            self.test_http_methods_security()

            print("\n" + "=" * 80)
            print("测试完成!")
            print("=" * 80)

        except KeyboardInterrupt:
            print("\n\n[中断] 测试被用户终止")
        except Exception as e:
            print(f"\n\n[错误] 测试执行异常: {str(e)}")
            import traceback
            traceback.print_exc()


def avg(lst):
    """计算平均值"""
    if not lst:
        return 0
    return sum(lst) / len(lst)


def main():
    """主函数"""
    import sys
    import os

    # 配置
    BASE_URL = "http://localhost:8080"
    OUTPUT_DIR = r"d:\FinalCodeAndFile\lab-management-system\test_results"

    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n" + "="*80)
    print("  实验室管理系统 - 全面安全测试 v1.4.0")
    print("  Security Testing Suite by API Test Pro")
    print("="*80 + "\n")

    # 初始化测试套件
    suite = SecurityTestSuite(base_url=BASE_URL)

    # 运行所有测试
    suite.run_all_tests()

    # 生成报告
    report = suite.generate_report()

    # 保存JSON格式结果
    json_output_path = os.path.join(OUTPUT_DIR, "security-test-results-v1.4.0.json")
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n[保存] JSON测试结果: {json_output_path}")

    # 打印摘要
    print("\n" + "="*80)
    print("  安全测试摘要")
    print("="*80)
    summary = report['summary']
    print(f"\n  总体安全评分: {summary['security_grade']} ({summary['security_score']}/100)")
    print(f"  测试总数: {summary['total_tests']}")
    print(f"  通过: {summary['passed']} ({summary['pass_rate']}%)")
    print(f"  失败: {summary['failed']}")
    print(f"  警告: {summary['warnings']}")
    print(f"  错误: {summary['errors']}")
    print(f"\n  漏洞统计:")
    print(f"    - 严重(Critical): {summary['critical_vulnerabilities']}")
    print(f"    - 高危(Major):     {summary['major_vulnerabilities']}")
    print(f"    - 低危(Minor):     {summary['minor_vulnerabilities']}")

    if report['vulnerabilities']:
        print(f"\n  发现的安全漏洞:")
        for i, vuln in enumerate(report['vulnerabilities'], 1):
            print(f"    {i}. [{vuln['severity']}] {vuln['title']} (CVSS: {vuln['cvss_score']})")

    print("\n" + "="*80 + "\n")

    return report


if __name__ == "__main__":
    report = main()
