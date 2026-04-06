#!/bin/bash
# 自动化下载Maven依赖脚本

export http_proxy=http://127.0.0.1:18080
export https_proxy=http://127.0.0.1:18080

MAVEN_REPO="/root/.m2/repository"
ALIYUN_MAVEN="https://maven.aliyun.com/repository/public"

download_single_dep() {
    local dep_spec=$1
    IFS=':' read -r group_id artifact_id version packaging <<< "$dep_spec"
    
    if [ -z "$packaging" ]; then
        packaging="jar"
    fi
    
    group_path=$(echo $group_id | tr '.' '/')
    target_dir="$MAVEN_REPO/$group_path/$artifact_id/$version"
    
    mkdir -p "$target_dir"
    
    base_url="$ALIYUN_MAVEN/$group_path/$artifact_id/$version/$artifact_id-$version"
    
    echo "Downloading $group_id:$artifact_id:$version"
    
    # 下载POM
    if [ ! -f "$target_dir/$artifact_id-$version.pom" ]; then
        curl -x $http_proxy -L -o "$target_dir/$artifact_id-$version.pom" "$base_url.pom" --connect-timeout 30 -m 60
        if [ $? -eq 0 ]; then
            echo "  ✓ POM downloaded"
        fi
    fi
    
    # 下载JAR（如果需要）
    if [ "$packaging" = "jar" ] && [ ! -f "$target_dir/$artifact_id-$version.jar" ]; then
        curl -x $http_proxy -L -o "$target_dir/$artifact_id-$version.jar" "$base_url.jar" --connect-timeout 30 -m 120
        if [ $? -eq 0 ]; then
            echo "  ✓ JAR downloaded"
        fi
    fi
}

echo "开始自动下载依赖..."

# 我们已知需要的依赖
deps=(
    "org.springframework.cloud:spring-cloud-gateway-server:4.1.0:pom"
    "org.springframework.boot:spring-boot-starter-webflux:3.2.0:pom"
    "com.alibaba.cloud:spring-cloud-alibaba:2023.0.1.2:pom"
    "io.projectreactor.addons:reactor-extra:3.5.1:pom"
    "org.springframework.boot:spring-boot-actuator:3.2.0:pom"
    "io.micrometer:micrometer-core:1.12.0:pom"
)

for dep in "${deps[@]}"; do
    download_single_dep "$dep"
done

echo "已知依赖下载完成！"
