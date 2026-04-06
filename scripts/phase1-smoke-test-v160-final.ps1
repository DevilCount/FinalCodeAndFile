# 第三轮最终验收测试脚本 v1.6.0 Final
# 目标: 验证NBP-001修复后系统是否达到100%验收标准
# 执行时间: 2026-04-05

param(
    [switch]$FullTest = $false,
    [switch]$SmokeOnly = $true  # 默认只执行冒烟测试
)

$ErrorActionPreference = "Stop"
$testResults = @()
$global:jwtToken = $null

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  第三轮最终验收测试 - Lab Management System v1.6.0 Final" -ForegroundColor Cyan
Write-Host "  测试目标: 确认100%验收标准达成" -ForegroundColor Cyan
Write-Host "  测试时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# ==================== 工具函数 ====================
function Test-API {
    param(
        [string]$TestId,
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [object]$Body,
        [string]$Token,
        [int]$ExpectedStatus,
        [scriptblock]$Validator
    )

    $result = @{
        TestId = $TestId
        Name = $Name
        Status = "FAIL"
        Message = ""
        ResponseTime = 0
        StatusCode = 0
        ActualData = $null
    }

    try {
        $headers = @{ "Content-Type" = "application/json" }
        if ($Token) {
            headers["Authorization"] = "Bearer $Token"
        }

        $sw = [System.Diagnostics.Stopwatch]::StartNew()

        if ($Method -eq "GET") {
            $response = Invoke-RestMethod -Uri $Url -Method Get -Headers $headers -ErrorAction Stop
        } else {
            $bodyJson = $Body | ConvertTo-Json -Depth 5
            $response = Invoke-RestMethod -Uri $Url -Method $Method -Body $bodyJson -Headers $headers -ErrorAction Stop
        }

        $sw.Stop()
        $result.ResponseTime = $sw.ElapsedMilliseconds

        # 调用验证器（如果提供）
        if ($Validator) {
            $validationResult = & $Validator $response
            if ($validationResult.Success) {
                $result.Status = "PASS"
                $result.Message = $validationResult.Message
                $result.ActualData = $response
            } else {
                $result.Status = "FAIL"
                $result.Message = $validationResult.Message
            }
        } else {
            # 默认验证: 检查success字段
            if ($response.success -eq $true) {
                $result.Status = "PASS"
                $result.Message = "操作成功"
                $result.ActualData = $response.data
            } else {
                $result.Status = "FAIL"
                $result.Message = "返回success=false: $($response.message)"
            }
        }

    } catch {
        $sw.Stop()
        $result.ResponseTime = $sw.ElapsedMilliseconds
        $result.StatusCode = $_.Exception.Response.StatusCode.value__
        $result.Status = "FAIL"
        $result.Message = "HTTP $($result.StatusCode): $($_.Exception.Message)"
    }

    return $result
}

function Write-TestResult {
    param($Result)

    if ($Result.Status -eq "PASS") {
        Write-Host "  ✅ [$($Result.TestId)] $($Result.Name)" -ForegroundColor Green
        Write-Host "     响应时间: $($Result.ResponseTime)ms | $($Result.Message)" -ForegroundColor Gray
    } else {
        Write-Host "  ❌ [$($Result.TestId)] $($Result.Name)" -ForegroundColor Red
        Write-Host "     错误: $($Result.Message)" -ForegroundColor Red
    }

    return $Result
}

# ==================== Phase 1: 冒烟测试 ====================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PHASE 1: 冒烟测试 (关键API验证)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# SMOKE-001: 登录接口
Write-Host "[SMOKE-001] POST /user/login - 登录接口 (本轮重点)" -ForegroundColor Green
try {
    $loginBody = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json

    # 尝试直连User Service
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8086/user/login" `
        -Method Post -Body $loginBody -ContentType "application/json" -ErrorAction Stop

    if ($loginResponse.success -eq $true) {
        $global:jwtToken = $loginResponse.data.token
        Write-Host "  ✅ PASS - HTTP 200 + JWT Token获取成功!" -ForegroundColor Green
        Write-Host "     Token长度: $($global:jwtToken.Length) 字符" -ForegroundColor Gray
        Write-Host "     用户: $($loginResponse.data.user.username) ($($loginResponse.data.user.role))" -ForegroundColor Gray
        $smoke001 = @{ TestId="SMOKE-001"; Name="登录接口"; Status="PASS"; Details="Token=$($global:jwtToken.Length)字符" }
    } else {
        Write-Host "  ❌ FAIL - 返回success=false" -ForegroundColor Red
        $smoke001 = @{ TestId="SMOKE-001"; Name="登录接口"; Status="FAIL"; Details=$loginResponse.message }
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "  ❌ FAIL - HTTP $statusCode" -ForegroundColor Red
    Write-Host "     错误: $($_.Exception.Message)" -ForegroundColor Gray
    $smoke001 = @{ TestId="SMOKE-001"; Name="登录接口"; Status="FAIL"; Details="HTTP $statusCode" }
}

# 如果登录失败，终止冒烟测试
if ($smoke001.Status -ne "PASS") {
    Write-Host "`n⛔ 冒烟测试失败! 登录接口不可用，无法继续测试。" -ForegroundColor Red
    Write-Host "   判定: NOT ACCEPTED - 阻断性问题" -ForegroundColor Red
    exit 1
}

Write-Host ""

# SMOKE-002: 创建标本接口 (NBP-001修复验证)
Write-Host "[SMOKE-002] POST /sample/create - 创建标本 (本轮重点修复!)" -ForegroundColor Green
try {
    $sampleCreateBody = @{
        patientName = "验收测试患者"
        patientId = "ACC20260405001"
        sampleType = "BLOOD"
        priority = "NORMAL"
        department = "检验科"
        doctor = "验收测试医师"
        notes = "第三轮验收测试数据"
    } | ConvertTo-Json

    $sampleResponse = Invoke-RestMethod -Uri "http://localhost:8087/sample/create" `
        -Method Post -Body $sampleCreateBody -ContentType "application/json" `
        -Headers @{ Authorization="Bearer $global:jwtToken" } -ErrorAction Stop

    if ($sampleResponse.success -eq $true) {
        $newSampleId = $sampleResponse.data.id
        Write-Host "  ✅ PASS - 标本创建成功!" -ForegroundColor Green
        Write-Host "     新标本ID: $newSampleId" -ForegroundColor Cyan
        Write-Host "     标本编号: $($sampleResponse.data.sampleNo)" -ForegroundColor Gray
        $global:newSampleId = $newSampleId
        $smoke002 = @{ TestId="SMOKE-002"; Name="创建标本"; Status="PASS"; Details="ID=$newSampleId, SampleNo=$($sampleResponse.data.sampleNo)" }
    } else {
        Write-Host "  ❌ FAIL - 返回success=false" -ForegroundColor Red
        Write-Host "     消息: $($sampleResponse.message)" -ForegroundColor Gray
        $smoke002 = @{ TestId="SMOKE-002"; Name="创建标本"; Status="FAIL"; Details=$sampleResponse.message }
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $errorBody = try { $_.Exception.Response.GetResponseStream() } catch { $null }

    Write-Host "  ❌ FAIL - HTTP $statusCode" -ForegroundColor Red
    Write-Host "     错误: $($_.Exception.Message)" -ForegroundColor Gray

    # 尝试读取错误详情
    try {
        $reader = New-Object System.IO.StreamReader($errorBody)
        $errorText = $reader.ReadToEnd()
        Write-Host "     响应体: $errorText" -ForegroundColor Yellow
        $smoke002 = @{ TestId="SMOKE-002"; Name="创建标本"; Status="FAIL"; Details="HTTP $statusCode: $errorText" }
    } catch {
        $smoke002 = @{ TestId="SMOKE-002"; Name="创建标本"; Status="FAIL"; Details="HTTP $statusCode" }
    }
}

Write-Host ""

# SMOKE-003: 创建报告接口 (NBP-001修复验证)
Write-Host "[SMOKE-003] POST /report/create - 创建报告 (本轮重点修复!)" -ForegroundColor Green
try {
    $reportCreateBody = @{
        sampleId = $(if ($global:newSampleId) { $global:newSampleId } else { 1 })
        reportType = "BLOOD_ROUTINE"
        technician = "验收测试技师"
        findings = "第三轮验收测试 - 各项指标正常"
        conclusion = "未见明显异常"
        status = "DRAFT"
    } | ConvertTo-Json

    $reportResponse = Invoke-RestMethod -Uri "http://localhost:8088/report/create" `
        -Method Post -Body $reportCreateBody -ContentType "application/json" `
        -Headers @{ Authorization="Bearer $global:jwtToken" } -ErrorAction Stop

    if ($reportResponse.success -eq $true) {
        $newReportId = $reportResponse.data.id
        Write-Host "  ✅ PASS - 报告创建成功!" -ForegroundColor Green
        Write-Host "     新报告ID: $newReportId" -ForegroundColor Cyan
        Write-Host "     报告编号: $($reportResponse.data.reportNo)" -ForegroundColor Gray
        $global:newReportId = $newReportId
        $smoke003 = @{ TestId="SMOKE-003"; Name="创建报告"; Status="PASS"; Details="ID=$newReportId, ReportNo=$($reportResponse.data.reportNo)" }
    } else {
        Write-Host "  ❌ FAIL - 返回success=false" -ForegroundColor Red
        Write-Host "     消息: $($reportResponse.message)" -ForegroundColor Gray
        $smoke003 = @{ TestId="SMOKE-003"; Name="创建报告"; Status="FAIL"; Details=$reportResponse.message }
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $errorBody = try { $_.Exception.Response.GetResponseStream() } catch { $null }

    Write-Host "  ❌ FAIL - HTTP $statusCode" -ForegroundColor Red
    Write-Host "     错误: $($_.Exception.Message)" -ForegroundColor Gray

    try {
        $reader = New-Object System.IO.StreamReader($errorBody)
        $errorText = $reader.ReadToEnd()
        Write-Host "     响应体: $errorText" -ForegroundColor Yellow
        $smoke003 = @{ TestId="SMOKE-003"; Name="创建报告"; Status="FAIL"; Details="HTTP $statusCode: $errorText" }
    } catch {
        $smoke003 = @{ TestId="SMOKE-003"; Name="创建报告"; Status="FAIL"; Details="HTTP $statusCode" }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  冒烟测试结果汇总" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$smokeTests = @($smoke001, $smoke002, $smoke003)
$passCount = ($smokeTests | Where-Object { $_.Status -eq "PASS" }).Count
$totalCount = $smokeTests.Count
$passRate = [math]::Round($passCount / $totalCount * 100)

foreach ($test in $smokeTests) {
    $icon = if ($test.Status -eq "PASS") { "✅" } else { "❌" }
    $color = if ($test.Status -eq "PASS") { "Green" } else { "Red" }
    Write-Host "  $icon [$($test.TestId)] $($test.Name): $($test.Status) - $($test.Details)" -ForegroundColor $color
}

Write-Host "`n  通过率: $passCount/$totalCount ($passRate%)" -ForegroundColor $(if ($passRate -eq 100) { "Green" } else { "Red" })

# 判定
if ($passCount -lt 3) {
    Write-Host "`n⛔ 冒烟测试未通过! 存在阻断性问题。" -ForegroundColor Red
    Write-Host "   判定: NOT ACCEPTED" -ForegroundColor Red
    Write-Host "   原因: 关键API不可用，无法继续全量测试" -ForegroundColor Red
    exit 1
} else {
    Write-Host "`n🎉 冒烟测试全部通过! 继续全量测试..." -ForegroundColor Green
}

Write-Host ""