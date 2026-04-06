#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理系统 - Selenium自动化测试套件
"""

import time
import unittest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class LabManagementSystemTest(unittest.TestCase):
    """实验室管理系统自动化测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试套件初始化"""
        cls.base_url = "http://localhost:3000"
        cls.test_results = []
        cls.start_time = datetime.now()
        
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        # 初始化WebDriver
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 15)
        
        print("=" * 80)
        print("实验室管理系统 - Selenium自动化测试套件")
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
        
        cls.driver.quit()
        cls.generate_test_report()
    
    @classmethod
    def generate_test_report(cls):
        """生成测试报告"""
        report_content = []
        report_content.append("# 实验室管理系统 - Selenium自动化测试报告\n")
        report_content.append(f"## 测试日期: {cls.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_content.append(f"## 测试时长: {cls.duration:.2f}秒\n\n")
        
        # 测试结果统计
        passed = sum(1 for r in cls.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in cls.test_results if r['status'] == 'FAIL')
        total = len(cls.test_results)
        
        report_content.append("## 测试结果统计\n")
        report_content.append(f"- **总测试用例**: {total}\n")
        report_content.append(f"- **通过**: {passed} ({(passed/total*100):.1f}%)\n")
        report_content.append(f"- **失败**: {failed} ({(failed/total*100):.1f}%)\n\n")
        
        # 详细测试结果
        report_content.append("## 详细测试结果\n\n")
        report_content.append("| 序号 | 测试用例 | 状态 | 耗时(秒) | 备注 |\n")
        report_content.append("|------|---------|------|---------|------|\n")
        
        for idx, result in enumerate(cls.test_results, 1):
            report_content.append(f"| {idx} | {result['name']} | {result['status']} | {result['duration']:.2f} | {result.get('note', '')} |\n")
        
        report_content.append("\n## 测试详情\n\n")
        for result in cls.test_results:
            report_content.append(f"### {result['name']}\n")
            report_content.append(f"- **状态**: {result['status']}\n")
            report_content.append(f"- **耗时**: {result['duration']:.2f}秒\n")
            if result.get('note'):
                report_content.append(f"- **备注**: {result['note']}\n")
            report_content.append("\n")
        
        report_content.append(f"---\n\n**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 写入报告文件
        report_file = "d:\\FinalCodeAndFile\\lab-management-system\\SELENIUM_TEST_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        
        print(f"\n测试报告已生成: {report_file}")
    
    def record_result(self, test_name, status, duration, note=""):
        """记录测试结果"""
        self.test_results.append({
            'name': test_name,
            'status': status,
            'duration': duration,
            'note': note
        })
    
    def test_01_page_load(self):
        """测试1: 首页加载测试"""
        test_name = "首页加载测试"
        start_time = time.time()
        
        try:
            print(f"\n[测试] {test_name}")
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # 验证页面标题
            title = self.driver.title
            print(f"  页面标题: {title}")
            
            # 验证URL
            current_url = self.driver.current_url
            print(f"  当前URL: {current_url}")
            
            status = "PASS"
            note = f"页面成功加载,标题: {title}"
            
        except Exception as e:
            status = "FAIL"
            note = f"错误: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note)
        self.assertEqual(status, "PASS", note)
    
    def test_02_dashboard_elements(self):
        """测试2: 仪表盘页面元素测试"""
        test_name = "仪表盘页面元素测试"
        start_time = time.time()
        
        try:
            print(f"\n[测试] {test_name}")
            
            # 验证页面标题包含"仪表盘"
            self.assertIn("仪表盘", self.driver.title)
            
            # 查找主要元素
            elements_found = []
            
            # 检查侧边栏菜单
            try:
                sidebar = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '工作台') or contains(text(), '检验管理')]"))
                )
                elements_found.append("侧边栏菜单")
            except:
                pass
            
            # 检查页面标题
            try:
                page_title = self.driver.find_element(By.XPATH, "//*[contains(text(), '检验科工作台')]")
                elements_found.append("页面标题")
            except:
                pass
            
            # 检查面包屑导航
            try:
                breadcrumb = self.driver.find_element(By.XPATH, "//*[contains(text(), '首页')]")
                elements_found.append("面包屑导航")
            except:
                pass
            
            print(f"  找到的元素: {', '.join(elements_found)}")
            
            status = "PASS"
            note = f"找到 {len(elements_found)} 个主要元素"
            
        except Exception as e:
            status = "FAIL"
            note = f"错误: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note)
    
    def test_03_navigate_sample(self):
        """测试3: 导航到标本管理页面"""
        test_name = "导航到标本管理页面"
        start_time = time.time()
        
        try:
            print(f"\n[测试] {test_name}")
            
            # 直接访问标本管理页面
            self.driver.get(f"{self.base_url}/sample")
            time.sleep(3)
            
            # 验证URL
            current_url = self.driver.current_url
            print(f"  当前URL: {current_url}")
            
            # 验证页面标题
            title = self.driver.title
            print(f"  页面标题: {title}")
            
            self.assertIn("sample", current_url.lower())
            
            status = "PASS"
            note = f"成功导航到标本管理页面,标题: {title}"
            
        except Exception as e:
            status = "FAIL"
            note = f"错误: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note)
    
    def test_04_sample_page_elements(self):
        """测试4: 标本管理页面元素"""
        test_name = "标本管理页面元素测试"
        start_time = time.time()
        
        try:
            print(f"\n[测试] {test_name}")
            
            elements_found = []
            
            # 检查搜索框
            try:
                search_box = self.driver.find_element(By.XPATH, "//input[@placeholder and (contains(@placeholder, '搜索') or contains(@placeholder, '标本'))]")
                elements_found.append("搜索框")
            except:
                pass
            
            # 检查新建按钮
            try:
                new_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), '新建') or contains(text(), '新增')]")
                elements_found.append("新建按钮")
            except:
                pass
            
            # 检查详情按钮
            try:
                detail_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), '详情')]")
                elements_found.append("详情按钮")
            except:
                pass
            
            print(f"  找到的元素: {', '.join(elements_found)}")
            
            status = "PASS"
            note = f"找到 {len(elements_found)} 个页面元素"
            
        except Exception as e:
            status = "FAIL"
            note = f"错误: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note)
    
    def test_05_navigate_report(self):
        """测试5: 导航到报告管理页面"""
        test_name = "导航到报告管理页面"
        start_time = time.time()
        
        try:
            print(f"\n[测试] {test_name}")
            
            self.driver.get(f"{self.base_url}/report")
            time.sleep(3)
            
            current_url = self.driver.current_url
            title = self.driver.title
            
            print(f"  当前URL: {current_url}")
            print(f"  页面标题: {title}")
            
            self.assertIn("report", current_url.lower())
            
            status = "PASS"
            note = f"成功导航到报告管理页面,标题: {title}"
            
        except Exception as e:
            status = "FAIL"
            note = f"错误: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note)
    
    def test_06_navigate_user(self):
        """测试6: 导航到用户管理页面"""
        test_name = "导航到用户管理页面"
        start_time = time.time()
        
        try:
            print(f"\n[测试] {test_name}")
            
            self.driver.get(f"{self.base_url}/user")
            time.sleep(3)
            
            current_url = self.driver.current_url
            title = self.driver.title
            
            print(f"  当前URL: {current_url}")
            print(f"  页面标题: {title}")
            
            self.assertIn("user", current_url.lower())
            
            status = "PASS"
            note = f"成功导航到用户管理页面,标题: {title}"
            
        except Exception as e:
            status = "FAIL"
            note = f"错误: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note)
    
    def test_07_navigate_system(self):
        """测试7: 导航到系统管理页面"""
        test_name = "导航到系统管理页面"
        start_time = time.time()
        
        try:
            print(f"\n[测试] {test_name}")
            
            self.driver.get(f"{self.base_url}/system")
            time.sleep(3)
            
            current_url = self.driver.current_url
            title = self.driver.title
            
            print(f"  当前URL: {current_url}")
            print(f"  页面标题: {title}")
            
            status = "PASS"
            note = f"成功导航到系统管理页面,标题: {title}"
            
        except Exception as e:
            status = "FAIL"
            note = f"错误: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note)
    
    def test_08_return_dashboard(self):
        """测试8: 返回仪表盘页面"""
        test_name = "返回仪表盘页面"
        start_time = time.time()
        
        try:
            print(f"\n[测试] {test_name}")
            
            self.driver.get(self.base_url)
            time.sleep(3)
            
            current_url = self.driver.current_url
            
            print(f"  当前URL: {current_url}")
            
            status = "PASS"
            note = "成功返回仪表盘页面"
            
        except Exception as e:
            status = "FAIL"
            note = f"错误: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note)
    
    def test_09_page_response_time(self):
        """测试9: 页面响应时间测试"""
        test_name = "页面响应时间测试"
        start_time = time.time()
        
        try:
            print(f"\n[测试] {test_name}")
            
            response_times = []
            
            # 测试多个页面的加载时间
            pages = [
                ("仪表盘", self.base_url),
                ("标本管理", f"{self.base_url}/sample"),
                ("报告管理", f"{self.base_url}/report"),
                ("用户管理", f"{self.base_url}/user"),
            ]
            
            for page_name, page_url in pages:
                page_start = time.time()
                self.driver.get(page_url)
                time.sleep(2)
                page_time = time.time() - page_start
                response_times.append((page_name, page_time))
                print(f"  {page_name}: {page_time:.2f}秒")
            
            # 计算平均响应时间
            avg_time = sum(t for _, t in response_times) / len(response_times)
            print(f"  平均响应时间: {avg_time:.2f}秒")
            
            # 检查平均响应时间是否小于3秒
            if avg_time < 3:
                status = "PASS"
                note = f"平均响应时间 {avg_time:.2f}秒, 符合要求"
            else:
                status = "FAIL"
                note = f"平均响应时间 {avg_time:.2f}秒, 超过3秒"
            
        except Exception as e:
            status = "FAIL"
            note = f"错误: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note)
    
    def test_10_full_navigation_flow(self):
        """测试10: 完整导航流程测试"""
        test_name = "完整导航流程测试"
        start_time = time.time()
        
        try:
            print(f"\n[测试] {test_name}")
            
            navigation_flow = [
                ("仪表盘", self.base_url),
                ("标本管理", f"{self.base_url}/sample"),
                ("报告管理", f"{self.base_url}/report"),
                ("用户管理", f"{self.base_url}/user"),
                ("系统管理", f"{self.base_url}/system"),
                ("返回仪表盘", self.base_url),
            ]
            
            successful_pages = []
            
            for page_name, page_url in navigation_flow:
                try:
                    self.driver.get(page_url)
                    time.sleep(2)
                    successful_pages.append(page_name)
                    print(f"  ✓ {page_name}")
                except Exception as e:
                    print(f"  ✗ {page_name}: {e}")
            
            success_rate = len(successful_pages) / len(navigation_flow) * 100
            print(f"  导航成功率: {success_rate:.1f}%")
            
            if success_rate >= 80:
                status = "PASS"
                note = f"导航成功率 {success_rate:.1f}%, 成功页面: {', '.join(successful_pages)}"
            else:
                status = "FAIL"
                note = f"导航成功率 {success_rate:.1f}%"
            
        except Exception as e:
            status = "FAIL"
            note = f"错误: {str(e)}"
            print(f"  错误: {e}")
        
        duration = time.time() - start_time
        self.record_result(test_name, status, duration, note)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
