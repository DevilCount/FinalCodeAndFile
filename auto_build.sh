#!/bin/bash
# 完全自动化的构建脚本

export http_proxy=http://127.0.0.1:18080
export https_proxy=http://127.0.0.1:18080

MAVEN_REPO="/root/.m2/repository"
ALIYUN_MAVEN="https://maven.aliyun.com/repository/public"
MAX_ATTEMPTS=50
attempt=0

download_dep() {
    local dep_line=$1
    
    # 解析依赖信息
    if [[ $dep_line == *"Could not resolve"* ]]; then
        # 提取 group:artifact:version
        if [[ $dep_line =~ ([^:]+):([^:]+):([^:]+) ]]; then
            group_id="${BASH_REMATCH[1]}"
            artifact_id="${BASH_REMATCH[2]}"
            version="${BASH_REMATCH[3]}"
            
            # 去除可能的前缀
            group_id=$(echo "$group_id" | sed 's/.*dependency: //')
            group_id=$(echo "$group_id" | sed 's/.*artifact //')
            
            download_single "$group_id" "$artifact_id" "$version"
        fi
    elif [[ $dep_line == *"The POM for"* ]]; then
        # 提取 group:artifact:version
        if [[ $dep_line =~ ([^:]+):([^:]+):([^:]+) ]]; then
            group_id="${BASH_REMATCH[1]}"
            artifact_id="${BASH_REMATCH[2]}"
            version="${BASH_REMATCH[3]}"
            
            # 去除可能的前缀
            group_id=$(echo "$group_id" | sed 's/.*The POM for //')
            
            download_single "$group_id" "$artifact_id" "$version" "pom"
        fi
    fi
}

download_single() {
    local group_id=$1
    local artifact_id=$2
    local version=$3
    local packaging=${4:-jar}
    
    group_path=$(echo $group_id | tr '.' '/')
    target_dir="$MAVEN_REPO/$group_path/$artifact_id/$version"
    
    mkdir -p "$target_dir"
    
    base_url="$ALIYUN_MAVEN/$group_path/$artifact_id/$version/$artifact_id-$version"
    
    echo "[$(date '+%H:%M:%S')] 下载: $group_id:$artifact_id:$version"
    
    # 下载POM
    pom_file="$target_dir/$artifact_id-$version.pom"
    if [ ! -f "$pom_file" ]; then
        curl -x $http_proxy -L -o "$pom_file" "$base_url.pom" --connect-timeout 30 -m 60 -s -f
        if [ $? -eq 0 ]; then
            echo "  ✓ POM下载成功"
        else
            echo "  ✗ POM下载失败"
            rm -f "$pom_file" 2>/dev/null
        fi
    fi
    
    # 下载JAR（如果需要）
    if [ "$packaging" = "jar" ]; then
        jar_file="$target_dir/$artifact_id-$version.jar"
        if [ ! -f "$jar_file" ]; then
            curl -x $http_proxy -L -o "$jar_file" "$base_url.jar" --connect-timeout 30 -m 120 -s -f
            if [ $? -eq 0 ]; then
                echo "  ✓ JAR下载成功"
            else
                echo "  ✗ JAR下载失败"
                rm -f "$jar_file" 2>/dev/null
            fi
        fi
    fi
}

echo "========================================"
echo "开始自动化构建过程"
echo "========================================"

while [ $attempt -lt $MAX_ATTEMPTS ]; do
    attempt=$((attempt + 1))
    echo ""
    echo "========================================"
    echo "尝试 #$attempt"
    echo "========================================"
    
    # 运行Maven编译并捕获输出
    mvn_output=$(mvn compile -Dmaven.test.skip=true -Dmaven.javadoc.skip=true -o 2>&1)
    mvn_exit_code=$?
    
    echo "$mvn_output"
    
    if [ $mvn_exit_code -eq 0 ]; then
        echo ""
        echo "========================================"
        echo "✓ 构建成功！"
        echo "========================================"
        exit 0
    fi
    
    # 提取需要的依赖
    echo ""
    echo "分析缺少的依赖..."
    
    # 检查输出中的错误行
    missing_deps=()
    while IFS= read -r line; do
        if [[ $line == *"Could not resolve"* ]] || [[ $line == *"The POM for"* ]]; then
            missing_deps+=("$line")
        fi
    done <<< "$mvn_output"
    
    if [ ${#missing_deps[@]} -eq 0 ]; then
        echo "无法解析错误，退出"
        echo "$mvn_output"
        exit 1
    fi
    
    # 下载缺失的依赖
    echo ""
    echo "下载缺失的依赖..."
    for dep in "${missing_deps[@]}"; do
        download_dep "$dep"
    done
    
    # 短暂暂停
    sleep 2
done

echo ""
echo "========================================"
echo "已达到最大尝试次数 ($MAX_ATTEMPTS)，构建失败"
echo "========================================"
exit 1
