#!/bin/bash
# 使用代理构建Maven项目

export http_proxy=http://127.0.0.1:18080
export https_proxy=http://127.0.0.1:18080
export MAVEN_OPTS="-Dhttp.proxyHost=127.0.0.1 -Dhttp.proxyPort=18080 -Dhttps.proxyHost=127.0.0.1 -Dhttps.proxyPort=18080"

echo "使用代理构建Maven项目..."
echo "HTTP代理: $http_proxy"
echo "HTTPS代理: $https_proxy"
echo "MAVEN_OPTS: $MAVEN_OPTS"

mvn compile -Dmaven.test.skip=true -Dmaven.javadoc.skip=true
