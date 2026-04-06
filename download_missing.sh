#!/bin/bash
# 手动下载缺失的依赖

export http_proxy=http://127.0.0.1:18080
export https_proxy=http://127.0.0.1:18080

MAVEN_REPO="/root/.m2/repository"
ALIYUN_MAVEN="https://maven.aliyun.com/repository/public"

download() {
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
    pom_file="$target_dir/$artifact_id-$version.pom"
    if [ ! -f "$pom_file" ]; then
        echo "  Downloading POM..."
        curl -x $http_proxy -L -o "$pom_file" "$base_url.pom" --connect-timeout 30 -m 60 -v
        if [ $? -eq 0 ]; then
            echo "  ✓ POM downloaded successfully"
        else
            echo "  ✗ POM download failed"
            rm -f "$pom_file" 2>/dev/null
        fi
    else
        echo "  ✓ POM already exists"
    fi
    
    # 下载JAR（如果需要）
    if [ "$packaging" = "jar" ]; then
        jar_file="$target_dir/$artifact_id-$version.jar"
        if [ ! -f "$jar_file" ]; then
            echo "  Downloading JAR..."
            curl -x $http_proxy -L -o "$jar_file" "$base_url.jar" --connect-timeout 30 -m 120 -v
            if [ $? -eq 0 ]; then
                echo "  ✓ JAR downloaded successfully"
            else
                echo "  ✗ JAR download failed"
                rm -f "$jar_file" 2>/dev/null
            fi
        else
            echo "  ✓ JAR already exists"
        fi
    fi
    echo ""
}

echo "开始下载缺失的依赖..."
echo ""

# 从错误日志中获取的具体依赖
download "org.springframework.boot" "spring-boot-starter-reactor-netty" "3.2.0" "pom"
download "org.springframework" "spring-webflux" "6.1.1" "pom"
download "com.alibaba.cloud" "spring-cloud-alibaba-commons" "2023.0.1.2" "pom"
download "com.alibaba.nacos" "nacos-client" "2.3.2" "pom"
download "com.alibaba.spring" "spring-context-support" "1.0.11" "pom"
download "org.hdrhistogram" "HdrHistogram" "2.1.12" "pom"
download "org.latencyutils" "LatencyUtils" "2.0.3" "pom"
download "org.springframework.cloud" "spring-cloud-starter-gateway" "4.1.0" "pom"
download "org.springframework.cloud" "spring-cloud-gateway-server" "4.1.0" "pom"
download "io.projectreactor.addons" "reactor-extra" "3.5.1" "pom"
download "org.springframework.boot" "spring-boot-starter-webflux" "3.2.0" "pom"
download "org.springframework.cloud" "spring-cloud-starter-loadbalancer" "4.1.0" "pom"
download "org.springframework.cloud" "spring-cloud-loadbalancer" "4.1.0" "pom"
download "org.springframework.boot" "spring-boot-starter-actuator" "3.2.0" "pom"
download "org.springframework.boot" "spring-boot-actuator" "3.2.0" "pom"
download "io.micrometer" "micrometer-core" "1.12.0" "pom"

echo "完成！"
