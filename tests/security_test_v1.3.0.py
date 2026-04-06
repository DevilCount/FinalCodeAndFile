#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 - 安全性测试 v1.3.0
任务2.5: 安全性测试
执行时间: 2026-04-02

测试内容:
- B1. 认证与授权测试 (未认证访问/无效Token/SQL注入/XSS)
- B2. 敏感信息泄露检查
- B3. 密码存储安全性 (代码审计)
"""

import requests
import re
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

# ==================== 配置 ====================
GATEWAY_URL = "http://localhost:8080"
USER_SERVICE_URL = "http://localhost:8086"  # 用户服务直连

# 测试端点配置
PROTECTED_ENDPOINTS = [
    ('GET', f'{GATEWAY_URL}/api/user/list', '用户列表'),
    ('GET', f'{GATEWAY_URL}/api/sample/list', '标本列表'),
    ('GET', f'{GATEWAY_URL}/api/report/list', '报告列表'),
    ('POST', f'{GATEWAY_URL}/api/sample/create', '创建标本'),
    ('DELETE', f'{GATEWAY_URL}/api/user/1', '删除用户'),
]

LOGIN_ENDPOINT = f'{USER_SERVICE_URL}/user/login'
REGISTER_ENDPOINT = f'{USER_SERVICE_URL}/user/register'

TIMEOUT_SECONDS = 10

# ==================== 安全测试结果类 ====================
class SecurityTestResult:
    def __init__(self, test_id: str, test_name: str, category: str):
        self.test_id = test_id
        self.test_name = test_name
        self.category = category
        self.status = "SKIP"  # PASS / FAIL / SKIP / ERROR
        self.severity = "Info"  # Critical / Major / Minor / Info
        self.description = ""
        self.details = ""
        self.evidence = ""
        self.remediation = ""
        self.cwe_id = ""  # Common Weakness Enumeration
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'test_id': self.test_id,
            'test_name': self.test_name,
            'category': self.category,
            'status': self.status,
            'severity': self.severity,
            'description': self.description,
            'details': self.details,
            'evidence': self.evidence,
            'remediation': self.remediation,
            'cwe_id': self.cwe_id,
            'timestamp': self.timestamp
        }

# ==================== B1. 认证与授权测试 ====================
def test_unauthorized_access() -> List[SecurityTestResult]:
    """
    B1.1 未认证访问测试
    尝试不带token访问受保护的API端点
    """
    results = []

    for method, url, name in PROTECTED_ENDPOINTS:
        result = SecurityTestResult(
            test_id="AUTH-001",
            test_name=f"未认证访问测试 - {name}",
            category="认证与授权"
        )

        try:
            if method == 'GET':
                response = requests.get(url, timeout=TIMEOUT_SECONDS)
            elif method == 'POST':
                response = requests.post(url, json={}, timeout=TIMEOUT_SECONDS)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=TIMEOUT_SECONDS)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            # 判断是否正确拦截了未认证请求
            if response.status_code in [401, 403]:
                result.status = "PASS"
                result.severity = "Info"
                result.description = "系统正确拦截了未认证的请求"
                result.details = f"返回状态码: {response.status_code} (预期: 401或403)"
                result.evidence = f"HTTP {response.status_code}: {response.text[:200]}"
                result.remediation = "无"
            elif response.status_code == 200:
                result.status = "FAIL"
                result.severity = "Critical"
                result.description = "系统未拦截未认证请求，存在严重安全漏洞"
                result.details = f"未认证请求成功访问了受保护资源"
                result.evidence = f"HTTP 200: 返回了{len(response.content)}字节数据"
                result.remediation = "在网关或各微服务中添加JWT Token校验过滤器，确保所有受保护API都需要有效认证"
                result.cwe_id = "CWE-306: Missing Authentication for Critical Function"
            else:
                result.status = "WARN"
                result.severity = "Minor"
                result.description = f"返回了意外的状态码: {response.status_code}"
                result.details = f"预期401/403或200，实际得到{response.status_code}"
                result.evidence = f"HTTP {response.status_code}: {response.text[:200]}"
                result.remediation = "检查API的认证中间件配置"

        except requests.exceptions.ConnectionError as e:
            result.status = "SKIP"
            result.severity = "Info"
            result.description = "无法连接到服务端，跳过此测试"
            result.details = str(e)[:100]
            result.remediation = "请确保服务已启动后重新执行测试"

        except Exception as e:
            result.status = "ERROR"
            result.severity = "Minor"
            result.description = f"测试执行出错: {str(e)[:100]}"
            result.remediation = "检查网络连接和服务状态"

        results.append(result)

    return results

def test_invalid_token() -> List[SecurityTestResult]:
    """
    B1.2 无效Token测试
    使用伪造或过期的JWT Token尝试访问API
    """
    results = []

    invalid_tokens = [
        ("无效Token格式", "Bearer invalid-token-12345"),
        ("空Token", "Bearer "),
        ("错误前缀", "Basic dXNlcjpwYXNz"),  # Base64编码的 user:pass
        ("过期Token", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"),
    ]

    test_url = f'{GATEWAY_URL}/api/user/list'

    for token_name, token_value in invalid_tokens:
        result = SecurityTestResult(
            test_id="AUTH-002",
            test_name=f"无效Token测试 - {token_name}",
            category="认证与授权"
        )

        try:
            headers = {'Authorization': token_value}
            response = requests.get(test_url, headers=headers, timeout=TIMEOUT_SECONDS)

            if response.status_code in [401, 403]:
                result.status = "PASS"
                result.severity = "Info"
                result.description = "系统正确拒绝了无效Token"
                result.details = f"Token类型: {token_name}, 返回状态码: {response.status_code}"
                result.evidence = f"HTTP {response.status_code}"
                result.remediation = "无"
            elif response.status_code == 200:
                result.status = "FAIL"
                result.severity = "Critical"
                result.description = f"系统接受了无效的{token_name}"
                result.details = "JWT验证机制可能未实现或存在绕过漏洞"
                result.evidence = f"HTTP 200: 使用{token_name}成功获取数据"
                result.remediation = "实现严格的JWT Token验证：检查签名、过期时间、签发者等字段"
                result.cwe_id = "CWE-287: Improper Authentication"
            else:
                result.status = "WARN"
                result.severity = "Minor"
                result.description = f"返回意外状态码: {response.status_code}"

        except requests.exceptions.ConnectionError:
            result.status = "SKIP"
            result.severity = "Info"
            result.description = "服务不可用，跳过测试"

        except Exception as e:
            result.status = "ERROR"
            result.severity = "Minor"
            result.description = f"测试异常: {str(e)[:100]}"

        results.append(result)

    return results

def test_sql_injection() -> List[SecurityTestResult]:
    """
    B1.3 SQL注入测试
    在登录接口的用户名字段中注入SQL语句
    """
    results = []

    sql_payloads = [
        ("经典OR注入", {"username": "' OR 1=1 --", "password": "test"}),
        ("注释注入", {"username": "admin'--", "password": "anything"}),
        ("UNION注入", {"username": "' UNION SELECT * FROM user --", "password": "test"}),
        ("单引号转义", {"username": "admin'; DROP TABLE user; --", "password": "test"}),
    ]

    for payload_name, payload in sql_payloads:
        result = SecurityTestResult(
            test_id="SEC-001",
            test_name=f"SQL注入测试 - {payload_name}",
            category="注入攻击"
        )

        try:
            response = requests.post(LOGIN_ENDPOINT, json=payload, timeout=TIMEOUT_SECONDS)

            # 检查是否返回了不应该返回的数据
            response_text = response.text.lower()

            # 危险信号：返回了大量用户数据或登录成功
            is_vulnerable = (
                response.status_code == 200 and
                ('token' in response_text or 'users' in response_text or 'data' in response_text) and
                len(response.content) > 500  # 返回数据量过大可能是泄露
            )

            if is_vulnerable:
                result.status = "FAIL"
                result.severity = "Critical"
                result.description = "检测到可能的SQL注入漏洞！"
                result.details = f"使用{payload_name}payload成功获取了异常数据"
                result.evidence = f"响应长度: {len(response.content)} bytes, 内容预览: {response_text[:300]}"
                result.remediation = "立即修复：1) 使用参数化查询(PreparedStatement) 2) 使用MyBatis的#{}占位符而非${} 3) 输入验证和过滤"
                result.cwe_id = "CWE-89: SQL Injection"
            elif response.status_code in [400, 401, 403]:
                result.status = "PASS"
                result.severity = "Info"
                result.description = "系统正确阻止了SQL注入尝试"
                result.details = f"{payload_name}被拒绝，返回{response.status_code}"
                result.evidence = f"HTTP {response.status_code}: {response_text[:200]}"
                result.remediation = "无"
            else:
                result.status = "PASS"
                result.severity = "Info"
                result.description = f"SQL注入尝试未成功 (HTTP {response.status_code})"
                result.details = f"响应状态码表明输入已被安全处理"

        except requests.exceptions.ConnectionError:
            result.status = "SKIP"
            result.severity = "Info"
            result.description = "服务不可用，跳过测试"

        except Exception as e:
            result.status = "ERROR"
            result.severity = "Minor"
            result.description = f"测试异常: {str(e)[:100]}"

        results.append(result)

    return results

def test_xss_attack() -> List[SecurityTestResult]:
    """
    B1.4 XSS跨站脚本攻击测试
    在注册/登录接口中注入JavaScript脚本
    """
    results = []

    xss_payloads = [
        ("基础Script标签", {"username": "<script>alert('xss')</script>", "password": "test123"}),
        ("事件处理器", {"username": "<img src=x onerror=alert('xss')>", "password": "test123"}),
        ("SVG注入", {"username": "<svg onload=alert('xss')>", "password": "test123"}),
        ("JavaScript协议", {"username": "javascript:alert('xss')", "password": "test123"}),
    ]

    for payload_name, payload in xss_payloads:
        result = SecurityTestResult(
            test_id="SEC-002",
            test_name=f"XSS攻击测试 - {payload_name}",
            category="跨站脚本攻击"
        )

        try:
            # 尝试注册接口（通常更容易受到XSS影响）
            response = requests.post(REGISTER_ENDPOINT, json=payload, timeout=TIMEOUT_SECONDS)

            response_text = response.text

            # 检查响应中是否存在未转义的脚本标签
            unescaped_script = '<script' in response_text.lower() and '</script>' not in response_text.lower().replace('</script>', '[ESCAPED]')
            contains_raw_html = any(tag in response_text.lower() for tag in ['<script', '<img ', '<svg ', 'onerror=', 'onclick=', 'javascript:'])

            if unescaped_script or contains_raw_html:
                result.status = "FAIL"
                result.severity = "Major"
                result.description = "检测到XSS漏洞！响应中包含未转义的HTML/JS代码"
                result.details = f"{payload_name}payload未被正确转义"
                result.evidence = f"响应包含原始HTML标签: {response_text[:400]}"
                result.remediation = "对所有用户输入进行HTML转义；使用成熟的模板引擎(Thymeleaf/Vue)；设置Content-Security-Policy头"
                result.cwe_id = "CWE-79: Cross-site Scripting"
            else:
                # 检查是否被正确转义
                escaped_indicators = ['&lt;script&gt;', '&amp;lt;', '\\u003c', '&#60;']
                is_escaped = any(indicator in response_text for indicator in escaped_indicators)

                if is_escaped or response.status_code in [400, 401, 403]:
                    result.status = "PASS"
                    result.severity = "Info"
                    result.description = "XSS payload已被正确处理/转义"
                    result.details = f"{payload_name}被安全处理"
                    result.evidence = f"HTTP {response.status_code}, 响应已转义或拒绝"
                    result.remediation = "无"
                else:
                    result.status = "PASS"
                    result.severity = "Info"
                    result.description = f"XSS测试通过 (HTTP {response.status_code})"
                    result.details = "未检测到明显的XSS漏洞"

        except requests.exceptions.ConnectionError:
            result.status = "SKIP"
            result.severity = "Info"
            result.description = "服务不可用，跳过测试"

        except Exception as e:
            result.status = "ERROR"
            result.severity = "Minor"
            result.description = f"测试异常: {str(e)[:100]}"

        results.append(result)

    return results

# ==================== B2. 敏感信息泄露检查 ====================
def test_sensitive_data_exposure() -> List[SecurityTestResult]:
    """
    B2. 敏感信息泄露检查
    检查API响应和错误消息是否泄露敏感信息
    """
    results = []

    # 测试1: 登录响应中的密码字段
    result1 = SecurityTestResult(
        test_id="DATA-001",
        test_name="登录响应密码泄露检查",
        category="敏感信息泄露"
    )

    try:
        login_payload = {'username': 'admin', 'password': 'admin123'}
        response = requests.post(LOGIN_ENDPOINT, json=login_payload, timeout=TIMEOUT_SECONDS)

        if response.status_code == 200:
            try:
                data = response.json()
                response_str = json.dumps(data).lower()

                password_fields = ['password', 'passwd', 'pwd', 'hash']
                found_passwords = [field for field in password_fields if field in response_str]

                if found_passwords:
                    result1.status = "FAIL"
                    result1.severity = "Major"
                    result1.description = "登录响应中包含敏感的密码相关字段！"
                    result1.details = f"发现字段: {found_passwords}"
                    result1.evidence = f"响应内容片段: {response_str[:500]}"
                    result1.remediation = "从API响应中移除所有密码字段；使用DTO对象排除敏感属性"
                    result1.cwe_id = "CWE-200: Exposure of Sensitive Information"
                else:
                    result1.status = "PASS"
                    result1.severity = "Info"
                    result1.description = "登录响应未包含明文密码字段"
                    result1.remediation = "无"
            except:
                result1.status = "WARN"
                result1.severity = "Minor"
                result1.description = "无法解析JSON响应"
        else:
            result1.status = "SKIP"
            result1.severity = "Info"
            result1.description = f"登录失败(HTTP {response.status_code})，跳过检查"

    except requests.exceptions.ConnectionError:
        result1.status = "SKIP"
        result1.severity = "Info"
        result1.description = "服务不可用，跳过测试"

    except Exception as e:
        result1.status = "ERROR"
        result1.severity = "Minor"
        result1.description = f"测试异常: {str(e)[:100]}"

    results.append(result1)

    # 测试2: 错误信息堆栈泄露
    result2 = SecurityTestResult(
        test_id="DATA-002",
        test_name="错误信息堆栈泄露检查",
        category="敏感信息泄露"
    )

    try:
        # 发送一个会触发错误的请求
        error_urls = [
            f'{USER_SERVICE_URL}/user/999999',  # 不存在的用户ID
            f'{GATEWAY_URL}/api/nonexistent-endpoint',  # 不存在的端点
        ]

        stack_trace_indicators = [
            'exception', 'stack trace', 'at com.',
            'java.sql.', 'caused by:', 'internal server error',
            'org.springframework', 'error: 500'
        ]

        has_stack_trace = False
        evidence = ""

        for url in error_urls:
            try:
                response = requests.get(url, timeout=TIMEOUT_SECONDS)
                response_lower = response.text.lower()

                found_indicators = [ind for ind in stack_trace_indicators if ind in response_lower]
                if found_indicators:
                    has_stack_trace = True
                    evidence = f"URL: {url}\n发现关键词: {found_indicators}\n响应片段: {response_lower[:500]}"
                    break

            except:
                continue

        if has_stack_trace:
            result2.status = "FAIL"
            result2.severity = "Major"
            result2.description = "错误响应中泄露了技术细节/堆栈信息！"
            result2.details = "生产环境不应暴露内部异常详情"
            result2.evidence = evidence
            result2.remediation = "配置全局异常处理器(GlobalExceptionHandler)，只返回通用错误消息；详细日志记录到服务器端"
            result2.cwe_id = "CWE-209: Generation of Error Message Containing Sensitive Information"
        else:
            result2.status = "PASS"
            result2.severity = "Info"
            result2.description = "错误响应未泄露明显的堆栈信息"
            result2.remediation = "无"

    except Exception as e:
        result2.status = "ERROR"
        result2.severity = "Minor"
        result2.description = f"测试异常: {str(e)[:100]}"

    results.append(result2)

    # 测试3: 安全头检查
    result3 = SecurityTestResult(
        test_id="SEC-003",
        test_name="HTTP安全响应头检查",
        category="安全配置"
    )

    try:
        response = requests.get(f'{GATEWAY_URL}/', timeout=TIMEOUT_SECONDS)

        required_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY or SAMEORIGIN',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=...',
            'Content-Security-Policy': "...",
        }

        missing_headers = []
        present_headers = {}

        for header, expected in required_headers.items():
            actual = response.headers.get(header, '')
            if actual:
                present_headers[header] = actual
            else:
                missing_headers.append(header)

        if len(missing_headers) <= 2:  # 允许缺少少量非关键头
            result3.status = "WARN"
            result3.severity = "Minor"
            result3.description = f"部分安全响应头缺失: {missing_headers}"
            result3.details = f"已配置: {list(present_headers.keys())}"
            result3.remediation = f"建议添加缺失的安全头: {missing_headers}"
        elif not missing_headers:
            result3.status = "PASS"
            result3.severity = "Info"
            result3.description = "所有关键安全响应头已配置"
            result3.details = f"已配置头: {list(present_headers.keys())}"
        else:
            result3.status = "FAIL"
            result3.severity = "Major"
            result3.description = "多个关键安全响应头缺失！"
            result3.details = f"缺失: {missing_headers}"
            result3.remediation = "在网关或Web服务器中配置完整的安全响应头集合"
            result3.cwe_id = "CWE-693: Protection Mechanism Failure"

        result3.evidence = f"实际响应头: {dict(response.headers)}"

    except requests.exceptions.ConnectionError:
        result3.status = "SKIP"
        result3.severity = "Info"
        result3.description = "服务不可用，跳过测试"

    except Exception as e:
        result3.status = "ERROR"
        result3.severity = "Minor"
        result3.description = f"测试异常: {str(e)[:100]}"

    results.append(result3)

    return results

# ==================== B3. 密码存储安全性代码审计 ====================
def audit_password_storage_security() -> List[SecurityTestResult]:
    """
    B3. 密码存储安全性审计
    通过读取源代码检查密码加密实现
    """
    results = []

    result = SecurityTestResult(
        test_id="CRYPTO-001",
        test_name="密码存储加密机制审查",
        category="密码安全"
    )

    try:
        # 读取UserServiceImpl.java文件
        impl_file = r'd:\FinalCodeAndFile\lab-management-system\lab-user-service\src\main\java\com\sunyaxin\user\service\impl\UserServiceImpl.java'

        with open(impl_file, 'r', encoding='utf-8') as f:
            code_content = f.read()

        # 检查密码相关的关键词
        security_indicators = {
            'BCryptPasswordEncoder': False,
            'PasswordEncoder': False,
            'MD5': False,
            'SHA': False,
            'plaintext': False,
            '明文': False,
            '.equals(password)': False,
            'password.encode()': False,
        }

        for indicator in security_indicators:
            if indicator in code_content:
                security_indicators[indicator] = True

        # 分析结果
        uses_bcrypt = security_indicators['BCryptPasswordEncoder'] or security_indicators['PasswordEncoder']
        uses_weak_hash = security_indicators['MD5'] or security_indicates.get('SHA', False)
        uses_plaintext = security_indicators['plaintext'] or security_indicators['明文'] or security_indicators['.equals(password)']

        if uses_plaintext:
            result.status = "FAIL"
            result.severity = "Critical"
            result.description = "严重安全问题：密码可能以明文形式存储或比较！"
            result.details = "代码中发现明文密码处理迹象"
            result.evidence = f"发现的关键词: {[k for k,v in security_indicators.items() if v]}"
            result.remediation = "立即修复：1) 引入Spring Security的BCryptPasswordEncoder 2) 在用户注册时对密码进行哈希 3) 登录时使用matches()方法比较"
            result.cwe_id = "CWE-256: Unprotected Storage of Passwords"
        elif uses_bcrypt:
            result.status = "PASS"
            result.severity = "Info"
            result.description = "使用了安全的密码哈希算法 (BCrypt)"
            result.details = "密码存储符合安全最佳实践"
            result.remediation = "无"
        elif uses_weak_hash:
            result.status = "FAIL"
            result.severity = "Critical"
            result.description = "使用了不安全的密码哈希算法(MD5/SHA)"
            result.details = "MD5和SHA系列不适合密码存储，易受彩虹表攻击"
            result.remediation = "迁移到BCrypt或Argon2算法；增加盐值(salt)"
            result.cwe_id = "CWE-328: Use of Weak Hash"
        else:
            result.status = "WARN"
            result.severity = "Major"
            result.description = "未能明确识别密码加密方式，需要人工审核"
            result.details = "请手动检查UserServiceImpl中的密码处理逻辑"
            result.remediation = "确保使用BCryptPasswordEncoder进行密码哈希"

        # 保存代码片段作为证据
        lines = code_content.split('\n')
        relevant_lines = [i+1 for i, line in enumerate(lines) if 'password' in line.lower()]
        code_snippets = "\n".join([f"Line {lines[i]}" for i in relevant_lines[:10]])
        result.evidence += f"\n\n相关代码行:\n{code_snippets}"

    except FileNotFoundError:
        result.status = "SKIP"
        result.severity = "Info"
        result.description = "源代码文件不存在，无法进行代码审计"

    except Exception as e:
        result.status = "ERROR"
        result.severity = "Minor"
        result.description = f"代码审计异常: {str(e)[:100]}"

    results.append(result)

    # 额外检查：查看application.yml中的安全配置
    result2 = SecurityTestResult(
        test_id="CONFIG-001",
        test_name="安全配置文件审查",
        category="安全配置"
    )

    try:
        config_files = [
            r'd:\FinalCodeAndFile\lab-management-system\lab-user-service\src\main\resources\application.yml',
            r'd:\FinalCodeAndFile\lab-management-system\lab-gateway\src\main\resources\application.yml',
        ]

        security_config_issues = []

        for config_file in config_files:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = f.read()

                # 检查常见的不安全配置
                if 'enable-cors: true' in config.lower() or 'allowed-origins: "*"' in config.lower():
                    security_config_issues.append("CORS配置过于宽松(允许所有来源)")

                if 'csrf:' in config.lower() and 'disable' in config.lower():
                    security_config_issues.append("CSRF保护被禁用")

                if 'ssl' not in config.lower() and 'https' not in config.lower():
                    security_config_issues.append("未强制HTTPS")

            except FileNotFoundError:
                continue

        if security_config_issues:
            result2.status = "WARN"
            result2.severity = "Major"
            result2.description = "发现潜在的不安全配置项"
            result2.details = "\n".join(security_config_issues)
            result2.remediation = "审查并收紧安全配置：限制CORS来源、启用CSRF保护、强制HTTPS"
        else:
            result2.status = "PASS"
            result2.severity = "Info"
            result2.description = "安全配置基本合理"
            result2.details = "未发现明显的不安全配置"

    except Exception as e:
        result2.status = "ERROR"
        result2.severity = "Minor"
        result2.description = f"配置文件审查异常: {str(e)[:100]}"

    results.append(result2)

    return results

# ==================== 主测试流程 ====================
def run_security_tests():
    """
    执行所有安全测试
    """
    print("=" * 80)
    print("实验室管理系统 - 安全性测试 v1.3.0")
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    all_results = []

    # ===== B1. 认证与授权测试 =====
    print("\n" + "=" * 80)
    print("B1. 认证与授权安全测试")
    print("=" * 80)

    print("\n[B1.1] 未认证访问测试...")
    auth_results = test_unauthorized_access()
    all_results.extend(auth_results)
    for r in auth_results:
        icon = "✓" if r.status == "PASS" else ("✗" if r.status == "FAIL" else "⚠")
        print(f"  {icon} [{r.status}] {r.test_name}")

    print("\n[B1.2] 无效Token测试...")
    token_results = test_invalid_token()
    all_results.extend(token_results)
    for r in token_results:
        icon = "✓" if r.status == "PASS" else ("✗" if r.status == "FAIL" else "⚠")
        print(f"  {icon} [{r.status}] {r.test_name}")

    print("\n[B1.3] SQL注入测试...")
    sqli_results = test_sql_injection()
    all_results.extend(sqli_results)
    for r in sqli_results:
        icon = "✓" if r.status == "PASS" else ("✗" if r.status == "FAIL" else "⚠")
        print(f"  {icon} [{r.status}] {r.test_name}")

    print("\n[B1.4] XSS攻击测试...")
    xss_results = test_xss_attack()
    all_results.extend(xss_results)
    for r in xss_results:
        icon = "✓" if r.status == "PASS" else ("✗" if r.status == "FAIL" else "⚠")
        print(f"  {icon} [{r.status}] {r.test_name}")

    # ===== B2. 敏感信息泄露检查 =====
    print("\n" + "=" * 80)
    print("B2. 敏感信息泄露检查")
    print("=" * 80)

    print("\n[B2.1] 敏感数据暴露检查...")
    data_results = test_sensitive_data_exposure()
    all_results.extend(data_results)
    for r in data_results:
        icon = "✓" if r.status == "PASS" else ("✗" if r.status == "FAIL" else "⚠")
        print(f"  {icon} [{r.status}] {r.test_name}")

    # ===== B3. 密码存储安全性审计 =====
    print("\n" + "=" * 80)
    print("B3. 密码存储安全性代码审计")
    print("=" * 80)

    print("\n[B3.1] 密码加密机制审查...")
    crypto_results = audit_password_storage_security()
    all_results.extend(crypto_results)
    for r in crypto_results:
        icon = "✓" if r.status == "PASS" else ("✗" if r.status == "FAIL" else "⚠")
        print(f"  {icon} [{r.status}] {r.test_name}")

    # ===== 统计汇总 =====
    print("\n" + "=" * 80)
    print("安全测试统计汇总")
    print("=" * 80)

    status_counts = {}
    severity_counts = {}

    for r in all_results:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1
        severity_counts[r.severity] = severity_counts.get(r.severity, 0) + 1

    print(f"\n总测试数: {len(all_results)}")
    print(f"\n按状态分布:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    print(f"\n按严重程度分布:")
    for severity, count in sorted(severity_counts.items(), key=lambda x: ['Critical','Major','Minor','Info'].index(x[0]) if x[0] in ['Critical','Major','Minor','Info'] else 99):
        print(f"  {severity}: {count}")

    # 识别关键问题
    critical_issues = [r for r in all_results if r.status == "FAIL" and r.severity == "Critical"]
    major_issues = [r for r in all_results if r.status == "FAIL" and r.severity == "Major"]

    if critical_issues:
        print(f"\n⚠️  发现 {len(critical_issues)} 个严重(Critical)安全问题:")
        for issue in critical_issues:
            print(f"  ✗ [{issue.test_id}] {issue.test_name}")
            print(f"      {issue.description[:100]}...")

    if major_issues:
        print(f"\n⚠️  发现 {len(major_issues)} 个重要(Major)安全问题:")
        for issue in major_issues:
            print(f"  ✗ [{issue.test_id}] {issue.test_name}")
            print(f"      {issue.description[:100]}...")

    # 构建最终报告
    report = {
        'test_version': 'v1.3.0',
        'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'environment': {
            'gateway_url': GATEWAY_URL,
            'user_service_url': USER_SERVICE_URL
        },
        'summary': {
            'total_tests': len(all_results),
            'passed': status_counts.get('PASS', 0),
            'failed': status_counts.get('FAIL', 0),
            'skipped': status_counts.get('SKIP', 0),
            'warnings': status_counts.get('WARN', 0),
            'errors': status_counts.get('ERROR', 0),
            'critical_issues': len(critical_issues),
            'major_issues': len(major_issues),
            'overall_status': 'FAIL' if (critical_issues or major_issues) else 'PASS'
        },
        'results': [r.to_dict() for r in all_results],
        'critical_findings': [r.to_dict() for r in critical_issues],
        'major_findings': [r.to_dict() for r in major_issues]
    }

    print("\n" + "=" * 80)
    print(f"总体评估: {report['summary']['overall_status']}")
    print("=" * 80)

    return report

if __name__ == '__main__':
    # 执行安全测试
    results = run_security_tests()

    # 保存结果到JSON文件
    output_file = r'd:\FinalCodeAndFile\lab-management-system\test_results\security-test-results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n安全测试结果已保存至: {output_file}")
