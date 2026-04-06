# Redis缓存测试脚本
Write-Host "=== 实验室管理系统 Redis缓存测试 ===" -ForegroundColor Cyan
Write-Host ""

# 1. 检查Redis状态
Write-Host "[1/5] 检查Redis服务..." -ForegroundColor Yellow
$redisPing = redis-cli ping
if ($redisPing -eq "PONG") {
    Write-Host "  ✓ Redis服务正常" -ForegroundColor Green
} else {
    Write-Host "  ✗ Redis服务异常" -ForegroundColor Red
    exit
}

# 2. 清空Redis缓存
Write-Host "`n[2/5] 清空Redis缓存..." -ForegroundColor Yellow
redis-cli flushall
Write-Host "  ✓ 缓存已清空" -ForegroundColor Green

# 3. 测试登录API（第一次请求 - 无缓存）
Write-Host "`n[3/5] 第一次登录请求（无缓存）..." -ForegroundColor Yellow
$start1 = Get-Date
try {
    $result1 = Invoke-RestMethod -Uri "http://localhost:8086/user/login?username=admin&password=admin123" -Method POST -TimeoutSec 10
    $end1 = Get-Date
    $time1 = ($end1 - $start1).TotalMilliseconds
    
    if ($result1.code -eq 200) {
        Write-Host "  ✓ 登录成功 (${time1}ms)" -ForegroundColor Green
        Write-Host "  用户: $($result1.data.username) | 角色: $($result1.data.role)" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ 登录失败: $($result1.message)" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ 请求失败: $_" -ForegroundColor Red
}

# 4. 检查Redis中的缓存键
Write-Host "`n[4/5] 检查Redis缓存键..." -ForegroundColor Yellow
Start-Sleep -Milliseconds 500
$keys = redis-cli keys "*"
if ($keys) {
    Write-Host "  ✓ 发现 $($keys.Count) 个缓存键:" -ForegroundColor Green
    $keys | ForEach-Object { Write-Host "    - $_" -ForegroundColor Gray }
    
    # 检查特定缓存键
    $loginKey = redis-cli keys "*login*"
    if ($loginKey) {
        Write-Host "`n  登录缓存详情:" -ForegroundColor Cyan
        $ttl = redis-cli ttl $loginKey[0]
        Write-Host "    Key: $loginKey" -ForegroundColor Gray
        Write-Host "    TTL: $ttl 秒" -ForegroundColor Gray
    }
} else {
    Write-Host "  ✗ 未发现缓存键（缓存可能未生效）" -ForegroundColor Red
}

# 5. 测试第二次登录（应有缓存）
Write-Host "`n[5/5] 第二次登录请求（应有缓存）..." -ForegroundColor Yellow
$start2 = Get-Date
try {
    $result2 = Invoke-RestMethod -Uri "http://localhost:8086/user/login?username=admin&password=admin123" -Method POST -TimeoutSec 10
    $end2 = Get-Date
    $time2 = ($end2 - $start2).TotalMilliseconds
    
    if ($result2.code -eq 200) {
        Write-Host "  ✓ 登录成功 (${time2}ms)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 登录失败" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ 请求失败: $_" -ForegroundColor Red
}

# 性能对比
Write-Host "`n=== 性能对比 ===" -ForegroundColor Cyan
if ($time1 -and $time2) {
    $speedup = [math]::Round($time1 / $time2, 1)
    Write-Host "  第一次请求: ${time1}ms" -ForegroundColor White
    Write-Host "  第二次请求: ${time2}ms" -ForegroundColor White
    Write-Host "  加速比: ${speedup}x" -ForegroundColor $(if ($speedup -gt 10) { "Green" } else { "Yellow" })
    
    if ($speedup -gt 10) {
        Write-Host "`n  ✓ 缓存效果显著！" -ForegroundColor Green
    } elseif ($speedup -gt 2) {
        Write-Host "`n  ⚠ 缓存有一定效果" -ForegroundColor Yellow
    } else {
        Write-Host "`n  ✗ 缓存可能未生效" -ForegroundColor Red
    }
}

Write-Host "`n=== 测试完成 ===" -ForegroundColor Cyan
