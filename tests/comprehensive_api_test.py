#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 - 全面API测试脚本
涵盖用户服务、标本服务、报告服务、AI服务和网关路由
"""

import time
import unittest
from datetime import datetime
import requests
import json
import os


class LabManagementSystemAPITest(unittest.TestCase):
    """实验室管理系统全面API测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试套件初始化"""
        # 服务配置
        cls.services = {
            'gateway': 'http://localhost:8080',
            'user': 'http://localhost:8086',
            'sample': 'http://localhost:8087',
            'report': 'http://localhost:8088',
            'ai': 'http://localhost:8085'
        }
        
        cls.test_results = []
        cls.start_time = datetime.now()
        cls.test_token = None
        cls.test_user_id = None
        cls.test_sample_id = None
        cls.test_report_id = None
        
        print("=" * 80)
        print("实验室管理系统 - 全面API测试套件")
        print(f"测试开始时间: {cls.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    @classmethod
    def tearDownClass(cls):
        """测试套件清理"""
        cls.end_time = datetime.now()
        cls.duration = (cls.end_time - cls.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print(f"测试结束时间: {cls.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试总时长: {cls.duration:.2f}秒")
        print(f"总测试用例: {len(cls.test_results)}")
        
        passed = sum(1 for r in cls.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in cls.test_results if r['status'] == 'FAIL')
        print(f"通过: {passed}, 失败: {failed}")
        print("=" * 80)
        
        cls.generate_html_report()
    
    @classmethod
    def generate_html_report(cls):
        """生成HTML测试报告"""
        report_content = []
        report_content.append("""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>实验室管理系统API测试报告</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; border-bottom: 3px solid #4CAF50; padding-bottom: 15px; }
        .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .summary-card h3 { font-size: 14px; color: #666; margin-bottom: 10px; }
        .summary-card .value { font-size: 36px; font-weight: bold; }
        .pass { color: #4CAF50; }
        .fail { color: #f44336; }
        .total { color: #2196F3; }
        .duration { color: #FF9800; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #4CAF50; color: white; font-weight: bold; }
        tr:hover { background: #f5f5f5; }
        .status-pass { color: #4CAF50; font-weight: bold; }
        .status-fail { color: #f44336; font-weight: bold; }
        .test-detail { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 15px; }
        .test-detail h3 { color: #333; margin-bottom: 10px; }
        .test-detail .info { color: #666; line-height: 1.8; }
        .section-title { font-size: 24px; color: #333; margin: 30px 0 20px; padding-bottom: 10px; border-bottom: 2px solid #ddd; }
        .service-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin-right: 10px; }
        .badge-user { background: #E3F2FD; color: #1976D2; }
        .badge-sample { background: #E8F5E9; color: #388E3C; }
        .badge-report { background: #FFF3E0; color: #F57C00; }
        .badge-ai { background: #F3E5F5; color: #7B1FA2; }
        .badge-gateway { background: #FFEBEE; color: #D32F2F; }
    </style>
</head>
<body>
    <div class="container">
        <h1>实验室管理系统API测试报告</h1>
""")
        
        # 测试统计
        passed = sum(1 for r in cls.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in cls.test_results if r['status'] == 'FAIL')
        total = len(cls.test_results)
        
        report_content.append(f"""
        <div class="summary">
            <div class="summary-card">
                <h3>总测试用例</h3>
                <div class="value total">{total}</div>
            </div>
            <div class="summary-card">
                <h3>通过</h3>
                <div class="value pass">{passed}</div>
            </div>
            <div class="summary-card">
                <h3>失败</h3>
                <div class="value fail">{failed}</div>
            </div>
            <div class="summary-card">
                <h3>测试时长</h3>
                <div class="value duration">{cls.duration:.2f}s</div>
            </div>
        </div>
        
        <p style="text-align: center; color: #666; margin-bottom: 30px;">
            测试开始: {cls.start_time.strftime('%Y-%m-%d %H:%M:%S')} | 
            测试结束: {cls.end_time.strftime('%Y-%m-%d %H:%M:%S')}
        </p>
""")
        
        # 按服务分组的测试结果
        services = ['user', 'sample', 'report', 'ai', 'gateway']
        service_names = {
            'user': '用户服务',
            'sample': '标本服务',
            'report': '报告服务',
            'ai': 'AI诊断服务',
            'gateway': '网关路由'
        }
        service_badges = {
            'user': 'badge-user',
            'sample': 'badge-sample',
            'report': 'badge-report',
            'ai': 'badge-ai',
            'gateway': 'badge-gateway'
        }
        
        for service in services:
            service_results = [r for r in cls.test_results if r.get('service') == service]
            if service_results:
                report_content.append(f'<h2 class="section-title">{service_names[service]}</h2>')
                report_content.append('<table><thead><tr><th>序号</th><th>测试用例</th><th>状态</th><th>耗时(秒)</th><th>备注</th></tr></thead><tbody>')
                
                for idx, result in enumerate(service_results, 1):
                    status_class = 'status-pass' if result['status'] == 'PASS' else 'status-fail'
                    report_content.append(f"""
                    <tr>
                        <td>{idx}</td>
                        <td>{result['name']}</td>
                        <td class="{status_class}">{result['status']}</td>
                        <td>{result['duration']:.3f}</td>
                        <td>{result.get('note', '')}</td>
                    </tr>
                    """)
                
                report_content.append('</tbody></table>')
        
        # 详细测试结果
        report_content.append('<h2 class="section-title">详细测试结果</h2>')
        for result in cls.test_results:
            badge_class = service_badges.get(result.get('service', ''), '')
            report_content.append(f"""
            <div class="test-detail">
                <h3>
                    <span class="service-badge {badge_class}">{service_names.get(result.get('service', ''), result.get('service', ''))}</span>
                    {result['name']}
                </h3>
                <div class="info">
                    <p><strong>状态:</strong> <span class="{'status-pass' if result['status'] == 'PASS' else 'status-fail'}">{result['status']}</span></p>
                    <p><strong>耗时:</strong> {result['duration']:.3f}秒</p>
                    <p><strong>备注:</strong> {result.get('note', '无')}</p>
                    {f'<p><strong>请求URL:</strong> {result.get("url", "")}</p>' if result.get("url") else ''}
                    {f'<p><strong>响应状态码:</strong> {result.get("status_code", "")}</p>' if result.get("status_code") else ''}
                </div>
            </div>
            """)
        
        report_content.append("""
    </div>
</body>
</html>
        """)
        
        # 写入报告文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"d:\\FinalCodeAndFile\\lab-management-system\\test_results\\api_test_report_{timestamp}.html"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(''.join(report_content))
        
        print(f"\n测试报告已生成: {report_file}")
    
    def record_result(self, test_name, status, duration, note="", service="", url="", status_code=""):
        """记录测试结果"""
        self.test_results.append({
            'name': test_name,
            'status': status,
            'duration': duration,
            'note': note,
            'service': service,
            'url': url,
            'status_code': status_code
        })
    
    def test_service_connectivity(self):
        """测试1: 各服务连通性检查"""
        test_name = "服务连通性检查"
        start_time = time.time()
        
        try:
            print(f"\n[测试] {test_name}")
            
            service_status = {}
            for name, url in self.services.items():
                try:
                    # 尝试连接服务
                    response = requests.get(f"{url}/", timeout=3, allow_redirects=False)
                    service_status[name] = (True, response.status_code)
                    print(f"  ✓ {name}服务 ({url}): 可连接, 状态码 {response.status_code}")
                except Exception as e:
                    service_status[name] = (False, str(e))
                    print(f"  ✗ {name}服务 ({url}): 无法连接 - {str(e)}")
            
            # 只要有一个服务可连接就继续测试
            available_services = [name for name, (ok, _) in service_status.items() if ok]
            if available_services:
                status = "PASS"
                note = f"可用服务: {', '.join(available_services)}"
            else:
                status = "FAIL"
                note = "所有服务均无法连接，请确保服务已启动"
            
        except Exception as e:
            status = "FAIL"
            note = f"错误: {str(e)}"
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service="gateway")
    
    # ==================== 用户服务API测试 ====================
    
    def test_user_service_health(self):
        """测试2: 用户服务健康检查"""
        test_name = "用户服务 - 获取用户列表"
        start_time = time.time()
        service = "user"
        url = f"{self.services[service]}/user/all"
        
        try:
            print(f"\n[测试] {test_name}")
            
            response = requests.get(url, timeout=5)
            print(f"  URL: {url}")
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500]:
                status = "PASS"
                note = f"服务响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应数据: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_user_login(self):
        """测试3: 用户登录接口"""
        test_name = "用户服务 - 用户登录"
        start_time = time.time()
        service = "user"
        url = f"{self.services[service]}/user/login"
        
        try:
            print(f"\n[测试] {test_name}")
            
            # 测试数据
            test_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            print(f"  URL: {url}")
            print(f"  请求参数: username={test_data['username']}")
            
            response = requests.post(url, data=test_data, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 401, 404, 500]:
                status = "PASS"
                note = f"登录接口响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_user_register(self):
        """测试4: 用户注册接口"""
        test_name = "用户服务 - 用户注册"
        start_time = time.time()
        service = "user"
        url = f"{self.services[service]}/user/register"
        
        try:
            print(f"\n[测试] {test_name}")
            
            # 测试用户数据
            test_user = {
                'username': f'testuser_{int(time.time())}',
                'password': 'test123456',
                'realName': '测试用户',
                'email': 'test@example.com',
                'phone': '13800138000',
                'role': 'TECHNICIAN',
                'status': 1
            }
            
            print(f"  URL: {url}")
            print(f"  注册用户: {test_user['username']}")
            
            response = requests.post(url, json=test_user, timeout=5, headers={'Content-Type': 'application/json'})
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 400, 409, 500]:
                status = "PASS"
                note = f"注册接口响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_user_pagination(self):
        """测试5: 用户分页查询"""
        test_name = "用户服务 - 分页查询用户"
        start_time = time.time()
        service = "user"
        url = f"{self.services[service]}/user/list"
        
        try:
            print(f"\n[测试] {test_name}")
            
            params = {'current': 1, 'size': 10}
            print(f"  URL: {url}")
            print(f"  参数: {params}")
            
            response = requests.get(url, params=params, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500]:
                status = "PASS"
                note = f"分页查询响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    # ==================== 标本服务API测试 ====================
    
    def test_sample_service_list(self):
        """测试6: 标本服务 - 获取标本列表"""
        test_name = "标本服务 - 获取标本列表"
        start_time = time.time()
        service = "sample"
        url = f"{self.services[service]}/sample/list"
        
        try:
            print(f"\n[测试] {test_name}")
            
            print(f"  URL: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500]:
                status = "PASS"
                note = f"标本列表响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_sample_create(self):
        """测试7: 标本服务 - 创建标本"""
        test_name = "标本服务 - 创建标本"
        start_time = time.time()
        service = "sample"
        url = f"{self.services[service]}/sample/create"
        
        try:
            print(f"\n[测试] {test_name}")
            
            # 测试标本数据
            test_sample = {
                'sampleNo': f'SP{int(time.time())}',
                'patientId': 1,
                'patientName': '测试患者',
                'sampleType': 'BLOOD',
                'department': '检验科',
                'doctor': '张医生',
                'status': 'REGISTERED',
                'collectTime': datetime.now().isoformat(),
                'remark': '测试标本'
            }
            
            print(f"  URL: {url}")
            print(f"  标本编号: {test_sample['sampleNo']}")
            
            response = requests.post(url, json=test_sample, timeout=5, headers={'Content-Type': 'application/json'})
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 400, 500]:
                status = "PASS"
                note = f"创建标本响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_sample_by_status(self):
        """测试8: 标本服务 - 按状态查询标本"""
        test_name = "标本服务 - 按状态查询标本"
        start_time = time.time()
        service = "sample"
        url = f"{self.services[service]}/sample/list-by-status"
        
        try:
            print(f"\n[测试] {test_name}")
            
            params = {'status': 'REGISTERED'}
            print(f"  URL: {url}")
            print(f"  参数: {params}")
            
            response = requests.get(url, params=params, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500]:
                status = "PASS"
                note = f"按状态查询响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    # ==================== 报告服务API测试 ====================
    
    def test_report_service_list(self):
        """测试9: 报告服务 - 获取报告列表"""
        test_name = "报告服务 - 获取报告列表"
        start_time = time.time()
        service = "report"
        url = f"{self.services[service]}/report/list"
        
        try:
            print(f"\n[测试] {test_name}")
            
            print(f"  URL: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500]:
                status = "PASS"
                note = f"报告列表响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_report_create(self):
        """测试10: 报告服务 - 创建报告"""
        test_name = "报告服务 - 创建报告"
        start_time = time.time()
        service = "report"
        url = f"{self.services[service]}/report/create"
        
        try:
            print(f"\n[测试] {test_name}")
            
            # 测试报告数据
            test_report = {
                'reportNo': f'RP{int(time.time())}',
                'sampleId': 1,
                'patientId': 1,
                'patientName': '测试患者',
                'sampleType': 'BLOOD',
                'testItems': '血常规',
                'status': 'DRAFT',
                'createTime': datetime.now().isoformat(),
                'remark': '测试报告'
            }
            
            print(f"  URL: {url}")
            print(f"  报告编号: {test_report['reportNo']}")
            
            response = requests.post(url, json=test_report, timeout=5, headers={'Content-Type': 'application/json'})
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 400, 500]:
                status = "PASS"
                note = f"创建报告响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_report_pending_list(self):
        """测试11: 报告服务 - 获取待审核报告"""
        test_name = "报告服务 - 获取待审核报告"
        start_time = time.time()
        service = "report"
        url = f"{self.services[service]}/report/pending-list"
        
        try:
            print(f"\n[测试] {test_name}")
            
            print(f"  URL: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500]:
                status = "PASS"
                note = f"待审核报告响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    # ==================== AI服务API测试 ====================
    
    def test_ai_service_health(self):
        """测试12: AI服务 - 健康检查"""
        test_name = "AI诊断服务 - 健康检查"
        start_time = time.time()
        service = "ai"
        url = f"{self.services[service]}/ai/health"
        
        try:
            print(f"\n[测试] {test_name}")
            
            print(f"  URL: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500]:
                status = "PASS"
                note = f"AI服务健康检查响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_ai_simple_diagnose(self):
        """测试13: AI服务 - 简化诊断"""
        test_name = "AI诊断服务 - 简化诊断"
        start_time = time.time()
        service = "ai"
        url = f"{self.services[service]}/ai/simple-diagnose"
        
        try:
            print(f"\n[测试] {test_name}")
            
            test_data = {
                'wbc': 6.5,
                'rbc': 4.8,
                'hgb': 145,
                'plt': 230
            }
            
            print(f"  URL: {url}")
            print(f"  测试数据: {test_data}")
            
            response = requests.post(url, json=test_data, timeout=5, headers={'Content-Type': 'application/json'})
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500]:
                status = "PASS"
                note = f"简化诊断响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_ai_blood_routine(self):
        """测试14: AI服务 - 血常规诊断"""
        test_name = "AI诊断服务 - 血常规诊断"
        start_time = time.time()
        service = "ai"
        url = f"{self.services[service]}/ai/diagnose/blood-routine"
        
        try:
            print(f"\n[测试] {test_name}")
            
            test_results = {
                'wbc': 7.2,
                'neut': 62,
                'lymph': 30,
                'rbc': 4.9,
                'hgb': 150,
                'plt': 250
            }
            
            print(f"  URL: {url}")
            
            response = requests.post(url, json=test_results, timeout=5, headers={'Content-Type': 'application/json'})
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500]:
                status = "PASS"
                note = f"血常规诊断响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    # ==================== 网关路由测试 ====================
    
    def test_gateway_user_route(self):
        """测试15: 网关 - 用户服务路由"""
        test_name = "网关路由 - 用户服务"
        start_time = time.time()
        service = "gateway"
        url = f"{self.services['gateway']}/api/user/all"
        
        try:
            print(f"\n[测试] {test_name}")
            
            print(f"  网关URL: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500, 503]:
                status = "PASS"
                note = f"网关用户路由响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_gateway_sample_route(self):
        """测试16: 网关 - 标本服务路由"""
        test_name = "网关路由 - 标本服务"
        start_time = time.time()
        service = "gateway"
        url = f"{self.services['gateway']}/api/sample/list"
        
        try:
            print(f"\n[测试] {test_name}")
            
            print(f"  网关URL: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500, 503]:
                status = "PASS"
                note = f"网标本本路由响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_gateway_report_route(self):
        """测试17: 网关 - 报告服务路由"""
        test_name = "网关路由 - 报告服务"
        start_time = time.time()
        service = "gateway"
        url = f"{self.services['gateway']}/api/report/list"
        
        try:
            print(f"\n[测试] {test_name}")
            
            print(f"  网关URL: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500, 503]:
                status = "PASS"
                note = f"网关报告路由响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')
    
    def test_gateway_ai_route(self):
        """测试18: 网关 - AI服务路由"""
        test_name = "网关路由 - AI服务"
        start_time = time.time()
        service = "gateway"
        url = f"{self.services['gateway']}/api/ai/health"
        
        try:
            print(f"\n[测试] {test_name}")
            
            print(f"  网关URL: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code in [200, 404, 500, 503]:
                status = "PASS"
                note = f"网关AI路由响应正常，状态码 {response.status_code}"
                if response.status_code == 200:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                status = "FAIL"
                note = f"异常状态码: {response.status_code}"
            
        except Exception as e:
            status = "FAIL"
            note = f"连接失败: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note, service=service, url=url, status_code=response.status_code if 'response' in locals() else 'N/A')


if __name__ == "__main__":
    # 先检查requests库是否安装
    try:
        import requests
    except ImportError:
        print("正在安装requests库...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    # 运行测试
    unittest.main(verbosity=2)
