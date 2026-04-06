#!/bin/bash
# 通过代理下载Maven依赖的脚本

export http_proxy=http://127.0.0.1:18080
export https_proxy=http://127.0.0.1:18080

MAVEN_REPO="/root/.m2/repository"
ALIYUN_MAVEN="https://maven.aliyun.com/repository/public"

download_dep() {
    group_id=$1
    artifact_id=$2
    version=$3
    packaging=${4:-jar}
    
    group_path=$(echo $group_id | tr '.' '/')
    target_dir="$MAVEN_REPO/$group_path/$artifact_id/$version"
    
    mkdir -p "$target_dir"
    
    base_url="$ALIYUN_MAVEN/$group_path/$artifact_id/$version/$artifact_id-$version"
    
    echo "Downloading $group_id:$artifact_id:$version"
    
    # 下载POM
    if [ ! -f "$target_dir/$artifact_id-$version.pom" ]; then
        curl -x $http_proxy -L -o "$target_dir/$artifact_id-$version.pom" "$base_url.pom"
    fi
    
    # 下载JAR（如果需要）
    if [ "$packaging" = "jar" ] && [ ! -f "$target_dir/$artifact_id-$version.jar" ]; then
        curl -x $http_proxy -L -o "$target_dir/$artifact_id-$version.jar" "$base_url.jar"
    fi
}

# 下载需要的依赖
echo "开始下载依赖..."

# Spring Cloud Gateway
download_dep "org.springframework.cloud" "spring-cloud-starter-gateway" "4.1.0" "pom"

# JWT
download_dep "io.jsonwebtoken" "jjwt-api" "0.12.5" "jar"
download_dep "io.jsonwebtoken" "jjwt-impl" "0.12.5" "jar"
download_dep "io.jsonwebtoken" "jjwt-jackson" "0.12.5" "jar"

# Spring Cloud Alibaba
download_dep "com.alibaba.cloud" "spring-cloud-starter-alibaba-nacos-discovery" "2023.0.1.2" "pom"
download_dep "com.alibaba.cloud" "spring-cloud-starter-alibaba-nacos-config" "2023.0.1.2" "pom"

# Spring Cloud LoadBalancer
download_dep "org.springframework.cloud" "spring-cloud-starter-loadbalancer" "4.1.0" "pom"

# Spring Boot Actuator
download_dep "org.springframework.boot" "spring-boot-starter-actuator" "3.2.0" "pom"

echo "依赖下载完成！"
