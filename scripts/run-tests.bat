#!/bin/bash

# 实验室管理系统测试脚本
# 用于执行后端服务测试

echo "=== 实验室管理系统测试脚本 ==="
echo "启动时间: $(date)"
echo "================================="

# 切换到项目根目录
cd "D:\FinalCodeAndFile\lab-management-system"

echo "1. 检查Maven环境..."
mvn --version
if [ $? -ne 0 ]; then
    echo "错误: Maven未安装或未配置"
    exit 1
fi

echo "2. 清理项目..."
mvn clean -DskipTests

echo "3. 编译项目..."
mvn compile -DskipTests

echo "4. 执行单元测试..."
echo "4.1 执行标本服务测试..."
mvn test -pl lab-sample-service -am

echo "4.2 执行公共模块测试..."
mvn test -pl lab-common -am

echo "4.3 执行报告服务测试..."
mvn test -pl lab-report-service -am

echo "5. 生成测试报告..."
mvn surefire-report:report -pl lab-sample-service -am

echo "6. 查看测试结果..."
if [ -f "lab-sample-service/target/site/surefire-report.html" ]; then
    echo "测试报告生成成功: lab-sample-service/target/site/surefire-report.html"
    # 在Windows上可以用start命令打开
    # start lab-sample-service/target/site/surefire-report.html
else
    echo "警告: 测试报告未生成"
fi

echo "================================="
echo "测试执行完成: $(date)"
echo "请查看上述测试结果和报告文件"

# 运行集成测试（可选）
# echo "7. 启动服务并运行集成测试..."
# echo "7.1 启动Nacos（如果未运行）..."
# echo "7.2 启动Redis（如果未运行）..."
# echo "7.3 启动MySQL（如果未运行）..."
# echo "7.4 运行集成测试..."
# mvn verify -pl lab-sample-service -Pintegration-test

echo "================================="
echo "测试结果摘要:"
echo "- 单元测试: 已完成"
echo "- 集成测试: 需要手动配置"
echo "- 性能测试: 需要额外配置"
echo "- 安全测试: 需要额外配置"

echo "=== 测试脚本结束 ==="