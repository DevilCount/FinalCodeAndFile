#!/bin/bash
# 通过代理下载更多Maven依赖的脚本

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
        if [ $? -eq 0 ]; then
            echo "  ✓ POM downloaded"
        fi
    fi
    
    # 下载JAR（如果需要）
    if [ "$packaging" = "jar" ] && [ ! -f "$target_dir/$artifact_id-$version.jar" ]; then
        curl -x $http_proxy -L -o "$target_dir/$artifact_id-$version.jar" "$base_url.jar"
        if [ $? -eq 0 ]; then
            echo "  ✓ JAR downloaded"
        fi
    fi
}

# 下载需要的传递依赖
echo "开始下载更多依赖..."

# Spring Cloud Gateway核心依赖
download_dep "org.springframework.cloud" "spring-cloud-gateway" "4.1.0" "pom"
download_dep "org.springframework.cloud" "spring-cloud-loadbalancer" "4.1.0" "pom"
download_dep "org.springframework.cloud" "spring-cloud-commons" "4.1.0" "pom"

# JWT根POM
download_dep "io.jsonwebtoken" "jjwt-root" "0.12.5" "pom"

# Spring Cloud Alibaba
download_dep "com.alibaba.cloud" "spring-cloud-alibaba-starters" "2023.0.1.2" "pom"
download_dep "com.alibaba.cloud" "spring-cloud-alibaba-dependencies" "2023.0.1.2" "pom"

# Spring Boot Actuator
download_dep "org.springframework.boot" "spring-boot-actuator-autoconfigure" "3.2.0" "jar"
download_dep "io.micrometer" "micrometer-jakarta9" "1.12.0" "jar"

# 其他可能需要的依赖
download_dep "com.stoyanr" "evictor" "1.0.0" "jar"

echo "更多依赖下载完成！"
