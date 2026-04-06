# 实验室管理系统 v1.6.0 - 全面回归测试套件 (PowerShell版本)
# Lab Management System v1.6.0 - Comprehensive Regression Test Suite

param(
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"

# ==================== 全局配置 ====================
$BASE_URLS = @{
    'gateway' = 'http://localhost:8080'
    'user_service' = 'http://localhost:8086'
    'sample_service' = 'http://localhost:8087'
    'report_service' = 'http://localhost:8088'
    'hl7_service' = 'http://localhost:8084'
    'ai_service' = 'http://localhost:8089'
}

$TIMEOUT_SECONDS = 10
$TestResults = @()
$PerformanceMetrics = @()
$GlobalJWTToken = $null

function Write-TestHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Yellow
    Write-Host ("=" * 80) -ForegroundColor Cyan
}

function New-TestResult {
    param(
        [string]$TestId,
        [string]$TestName,
        [string]$Category
    )
    
    return [PSCustomObject]@{
        test_id = $TestId
        test_name = $TestName
        category = $Category
        status = "PENDING"
        expected = ""
        actual = ""
        error_message = ""
        response_time_ms = 0
        http_status = 0
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        details = @{}
    }
}

function Invoke-ApiRequest {
    param(
        [string]$Url,
        [string]$Method = 'GET',
        $Data = $null,
        [hashtable]$Headers = $null
    )
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            ContentType = 'application/json; charset=utf-8'
            TimeoutSec = $TIMEOUT_SECONDS
            UseBasicParsing = $true
        }
        
        if ($Headers) {
            $params['Headers'] = $Headers
        }
        
        if ($Data -and $Method -ne 'GET') {
            $params['Body'] = ($Data | ConvertTo-Json -Depth 5)
        }
        
        $response = Invoke-RestMethod @params
        $stopwatch.Stop()
        
        # 获取HTTP状态码（需要重新请求）
        $response2 = Invoke-WebRequest @params
        $statusCode = $response2.StatusCode
        
        $elapsedMs = $stopwatch.Elapsed.TotalMilliseconds
        
        $PerformanceMetrics += [PSCustomObject]@{
            endpoint = $Url
            method = $Method
            response_time_ms = [math]::Round($elapsedMs, 2)
            status_code = $statusCode
            timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        }
        
        return @{
            success = $true
            data = $response
            status_code = $statusCode
            elapsed_ms = [math]::Round($elapsedMs, 2)
        }
    }
    catch {
        $stopwatch.Stop()
        $elapsedMs = $stopwatch.Elapsed.TotalMilliseconds
        
        $statusCode = 0
        $errorMessage = $_.Exception.Message
        
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            try {
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $errorBody = $reader.ReadToEnd()
                $errorMessage = $errorBody
            } catch {}
        }
        
        return @{
            success = $false
            data = $null
            status_code = $statusCode
            elapsed_ms = [math]::Round($elapsedMs, 2)
            error = $errorMessage
        }
    }
}

# ==================== 阶段1：健康检查测试 ====================

function Test-HealthChecks {
    Write-TestHeader "阶段1：微服务健康检查测试 (Health Check Tests)"
    
    $services = @(
        @{id='HC001'; name='Gateway健康检查'; url=($BASE_URLS['gateway'] + '/actuator/health')},
        @{id='HC002'; name='HL7 Service健康检查'; url=($BASE_URLS['hl7_service'] + '/actuator/health')},
        @{id='HC003'; name='User Service健康检查'; url=($BASE_URLS['user_service'] + '/actuator/health')},
        @{id='HC004'; name='Sample Service健康检查'; url=($BASE_URLS['sample_service'] + '/actuator/health')},
        @{id='HC005'; name='Report Service健康检查'; url=($BASE_URLS['report_service'] + '/actuator/health')},
        @{id='HC006'; name='AI Service健康检查'; url=($BASE_URLS['ai_service'] + '/actuator/health')}
    )
    
    foreach ($svc in $services) {
        $result = New-TestResult -TestId $svc.id -TestName $svc.name -Category "Health Check"
        $result.expected = "HTTP 200 - UP status"
        
        $apiResult = Invoke-ApiRequest -Url $svc.url -Method 'GET'
        
        $result.http_status = $apiResult.status_code
        $result.response_time_ms = $apiResult.elapsed_ms
        
        if ($apiResult.success) {
            if ($apiResult.status_code -eq 200) {
                $statusValue = if ($apiResult.data.status) { $apiResult.data.status } else { "Unknown" }
                if ($statusValue -eq "UP") {
                    $result.status = "PASS"
                    $result.actual = "HTTP $($apiResult.status_code) - $statusValue"
                    Write-Host "  [PASS] $($svc.name): $($result.actual) ($($apiResult.elapsed_ms)ms)" -ForegroundColor Green
                } elseif ($apiResult.status_code -eq 200) {
                    $result.status = "WARN"
                    $result.actual = "HTTP 200 (non-standard health response)"
                    Write-Host "  [WARN] $($svc.name): HTTP 200 but status=$statusValue" -ForegroundColor Yellow
                }
            } else {
                $result.status = "FAIL"
                $result.actual = "HTTP $($apiResult.status_code)"
                $result.error_message = "Expected 200, got $($apiResult.status_code)"
                Write-Host "  [FAIL] $($svc.name): HTTP $($apiResult.status_code)" -ForegroundColor Red
            }
        } else {
            $result.status = "FAIL"
            $result.actual = "Connection Failed / Timeout"
            $result.error_message = "Service not reachable"
            Write-Host "  [FAIL] $($svc.name): Not running or unreachable" -ForegroundColor Red
        }
        
        $TestResults += $result
    }
}

# ==================== 阶段2：用户认证测试 ====================

function Test-UserAuthentication {
    Write-TestHeader "阶段2：用户认证API测试 (User Authentication API Tests)"
    
    $authTests = @(
        @{
            id = 'AUTH001'
            name = '管理员登录（直连User Service）'
            url = ($BASE_URLS['user_service'] + '/user/login')
            method = 'POST'
            data = @{username='admin'; password='admin123'}
            expected_status = 200
        },
        @{
            id = 'AUTH002'
            name = '管理员登录（通过Gateway）'
            url = ($BASE_URLS['gateway'] + '/api/user/login')
            method = 'POST'
            data = @{username='admin'; password='admin123'}
            expected_status = 200
        },
        @{
            id = 'AUTH003'
            name = '错误密码登录测试'
            url = ($BASE_URLS['user_service'] + '/user/login')
            method = 'POST'
            data = @{username='admin'; password='wrongpassword'}
            expected_status = 400
        },
        @{
            id = 'AUTH004'
            name = '空用户名登录测试'
            url = ($BASE_URLS['user_service'] + '/user/login')
            method = 'POST'
            data = @{username=''; password='admin123'}
            expected_status = 400
        }
    )
    
    foreach ($test in $authTests) {
        $result = New-TestResult -TestId $test.id -TestName $test.name -Category "Authentication"
        $result.expected = "HTTP $($test.expected_status)"
        
        $apiResult = Invoke-ApiRequest -Url $test.url -Method $test.method -Data $test.data
        
        $result.http_status = $apiResult.status_code
        $result.response_time_ms = $apiResult.elapsed_ms
        
        if (-not $apiResult.success -and $apiResult.status_code -ne 0) {
            # 请求失败但有响应（如400错误）
            try {
                $errorData = $apiResult.error | ConvertFrom-Json
                $result.details = $errorData
                
                if ($apiResult.status_code -eq $test.expected_status) {
                    $result.status = "PASS"
                    $result.actual = "HTTP $($apiResult.status_code) - Correctly rejected"
                    Write-Host "  [PASS] $($test.name): Correctly rejected" -ForegroundColor Green
                } else {
                    $result.status = "FAIL"
                    $result.actual = "HTTP $($apiResult.status_code) (expected $($test.expected_status))"
                    $result.error_message = $errorData
                    Write-Host "  [FAIL] $($test.name): $($result.actual)" -ForegroundColor Red
                }
            } catch {
                $result.status = "ERROR"
                $result.actual = "Parse error: $($apiResult.error)"
                Write-Host "  [ERROR] $($test.name): $($apiResult.error)" -ForegroundColor Magenta
            }
        } elseif ($apiResult.success) {
            $result.details = $apiResult.data
            
            if ($apiResult.status_code -eq $test.expected_status) {
                if ($apiResult.data.success -eq $true) {
                    $result.status = "PASS"
                    $result.actual = "HTTP $($apiResult.status_code) - Login Success"
                    
                    # 提取token
                    if ($apiResult.data.data -and $apiResult.data.data.token) {
                        $script:GlobalJWTToken = $apiResult.data.data.token
                        Write-Host "  [PASS] $($test.name): Login successful, JWT obtained" -ForegroundColor Green
                    } else {
                        Write-Host "  [PASS] $($test.name): $($apiResult.data.message)" -ForegroundColor Green
                    }
                } else {
                    $result.status = "FAIL"
                    $result.actual = "HTTP $($apiResult.status_code) - $($apiResult.data.message)"
                    Write-Host "  [FAIL] $($test.name): $($result.actual)" -ForegroundColor Red
                }
            } else {
                $result.status = "FAIL"
                $result.actual = "HTTP $($apiResult.status_code) (expected $($test.expected_status))"
                Write-Host "  [FAIL] $($test.name): $($result.actual)" -ForegroundColor Red
            }
        } else {
            $result.status = "FAIL"
            $result.actual = "Request failed"
            $result.error_message = $apiResult.error
            Write-Host "  [FAIL] $($test.name): No response from server" -ForegroundColor Red
        }
        
        $TestResults += $result
    }
    
    return $script:GlobalJWTToken
}

# ==================== 阶段3：标本管理测试 ====================

function Test-SampleManagement {
    param([string]$Token = $null)
    
    Write-TestHeader "阶段3：标本管理API测试 (Sample Management API Tests)"
    
    $headers = @{}
    if ($Token) {
        $headers['Authorization'] = "Bearer $Token"
    }
    
    $sampleTests = @(
        @{
            id = 'SM001'
            name = '获取标本列表'
            url = ($BASE_URLS['sample_service'] + '/sample/list')
            method = 'GET'
            expected_status = 200
        },
        @{
            id = 'SM002'
            name = '获取标本列表（分页参数）'
            url = ($BASE_URLS['sample_service'] + '/sample/list?page=1&size=5')
            method = 'GET'
            expected_status = 200
        },
        @{
            id = 'SM003'
            name = '创建新标本'
            url = ($BASE_URLS['sample_service'] + '/sample/create')
            method = 'POST'
            data = @{
                patientName = 'RegressionTest Patient'
                patientGender = '男'
                patientAge = 45
                doctorName = 'Test Doctor'
                testItems = '血常规'
                sampleType = 'BLOOD'
                collectLocation = '检验科'
            }
            expected_status = 200
        },
        @{
            id = 'SM004'
            name = '通过Gateway获取标本列表'
            url = ($BASE_URLS['gateway'] + '/api/sample/list')
            method = 'GET'
            expected_status = 200
        }
    )
    
    foreach ($test in $sampleTests) {
        $result = New-TestResult -TestId $test.id -TestName $test.name -Category "Sample Management"
        $result.expected = "HTTP $($test.expected_status)"
        
        $apiResult = Invoke-ApiRequest -Url $test.url -Method $test.method -Data $test.data -Headers $headers
        
        $result.http_status = $apiResult.status_code
        $result.response_time_ms = $apiResult.elapsed_ms
        
        if ($apiResult.success) {
            $result.details = $apiResult.data
            
            if ($apiResult.status_code -eq $test.expected_status) {
                if ($apiResult.data.success -eq $true) {
                    $result.status = "PASS"
                    
                    if ($test.method -eq 'GET' -and $apiResult.data.data) {
                        $count = if ($apiResult.data.data -is [array]) { $apiResult.data.data.Count } else { 1 }
                        $result.actual = "HTTP $($apiResult.status_code) - Returned $count records"
                        Write-Host "  [PASS] $($test.name): $count records ($($apiResult.elapsed_ms)ms)" -ForegroundColor Green
                    } else {
                        $result.actual = "HTTP $($apiResult.status_code) - Operation successful"
                        Write-Host "  [PASS] $($test.name): Operation successful" -ForegroundColor Green
                    }
                } else {
                    $result.status = "FAIL"
                    $result.actual = "HTTP $($apiResult.status_code) - $($apiResult.data.message)"
                    Write-Host "  [FAIL] $($test.name): $($result.actual)" -ForegroundColor Red
                }
            } else {
                $result.status = "FAIL"
                $result.actual = "HTTP $($apiResult.status_code) (expected $($test.expected_status))"
                Write-Host "  [FAIL] $($test.name): $($result.actual)" -ForegroundColor Red
            }
        } else {
            $result.status = "FAIL"
            $result.actual = "Request failed"
            $result.error_message = $apiResult.error
            Write-Host "  [FAIL] $($test.name): No response" -ForegroundColor Red
        }
        
        $TestResults += $result
    }
}

# ==================== 阶段4：报告管理测试 ====================

function Test-ReportManagement {
    param([string]$Token = $null)
    
    Write-TestHeader "阶段4：报告管理API测试 (Report Management API Tests)"
    
    $headers = @{}
    if ($Token) {
        $headers['Authorization'] = "Bearer $Token"
    }
    
    $reportTests = @(
        @{
            id = 'RP001'
            name = '获取报告列表'
            url = ($BASE_URLS['report_service'] + '/report/list')
            method = 'GET'
            expected_status = 200
        },
        @{
            id = 'RP002'
            name = '通过Gateway获取报告列表'
            url = ($BASE_URLS['gateway'] + '/api/report/list')
            method = 'GET'
            expected_status = 200
        },
        @{
            id = 'RP003'
            name = '创建新报告'
            url = ($BASE_URLS['report_service'] + '/report/create')
            method = 'POST'
            data = @{
                sampleId = 1
                patientName = 'Report Test Patient'
                testItems = '血常规,尿常规'
                remark = '回归测试报告'
            }
            expected_status = 200
        }
    )
    
    foreach ($test in $reportTests) {
        $result = New-TestResult -TestId $test.id -TestName $test.name -Category "Report Management"
        $result.expected = "HTTP $($test.expected_status)"
        
        $apiResult = Invoke-ApiRequest -Url $test.url -Method $test.method -Data $test.data -Headers $headers
        
        $result.http_status = $apiResult.status_code
        $result.response_time_ms = $apiResult.elapsed_ms
        
        if ($apiResult.success) {
            $result.details = $apiResult.data
            
            if ($apiResult.status_code -eq $test.expected_status) {
                if ($apiResult.data.success -eq $true) {
                    $result.status = "PASS"
                    
                    if ($test.method -eq 'GET' -and $apiResult.data.data) {
                        $count = if ($apiResult.data.data -is [array]) { $apiResult.data.data.Count } else { 1 }
                        $result.actual = "HTTP $($apiResult.status_code) - Returned $count reports"
                        Write-Host "  [PASS] $($test.name): $count reports ($($apiResult.elapsed_ms)ms)" -ForegroundColor Green
                    } else {
                        $result.actual = "HTTP $($apiResult.status_code) - Operation successful"
                        Write-Host "  [PASS] $($test.name): Operation successful" -ForegroundColor Green
                    }
                } else {
                    $result.status = "FAIL"
                    $result.actual = "HTTP $($apiResult.status_code) - $($apiResult.data.message)"
                    Write-Host "  [FAIL] $($test.name): $($result.actual)" -ForegroundColor Red
                }
            } else {
                $result.status = "FAIL"
                $result.actual = "HTTP $($apiResult.status_code) (expected $($test.expected_status))"
                Write-Host "  [FAIL] $($test.name): $($result.actual)" -ForegroundColor Red
            }
        } else {
            $result.status = "FAIL"
            $result.actual = "Request failed"
            $result.error_message = $apiResult.error
            Write-Host "  [FAIL] $($test.name): No response" -ForegroundColor Red
        }
        
        $TestResults += $result
    }
}

# ==================== 阶段5：AI诊断和HL7服务测试 ====================

function Test-AIAndHL7Services {
    Write-TestHeader "阶段5：AI诊断 & HL7服务测试 (AI Diagnosis & HL7 Service Tests)"
    
    # AI诊断测试
    $aiTests = @(
        @{
            id = 'AI001'
            name = '血常规AI诊断'
            url = ($BASE_URLS['ai_service'] + '/ai/diagnose/blood-routine')
            method = 'POST'
            data = @{
                indicators = @{
                    WBC = 11.5
                    RBC = 4.8
                    HGB = 145
                    PLT = 280
                }
            }
        },
        @{
            id = 'AI002'
            name = '尿常规AI诊断'
            url = ($BASE_URLS['ai_service'] + '/ai/diagnose/urine-routine')
            method = 'POST'
            data = @{
                indicators = @{
                    LEU = '2+'
                    ERY = '1+'
                    PRO = '+-'
                    GLU = '-'
                }
            }
        }
    )
    
    foreach ($test in $aiTests) {
        $result = New-TestResult -TestId $test.id -TestName $test.name -Category "AI Diagnosis"
        $result.expected = "HTTP 200 - Diagnosis completed"
        
        $apiResult = Invoke-ApiRequest -Url $test.url -Method $test.method -Data $test.data
        
        $result.http_status = $apiResult.status_code
        $result.response_time_ms = $apiResult.elapsed_ms
        
        if ($apiResult.success) {
            $result.details = $apiResult.data
            $result.status = "PASS"
            $result.actual = "HTTP $($apiResult.status_code) - Diagnosis completed"
            Write-Host "  [PASS] $($test.name): Completed ($($apiResult.elapsed_ms)ms)" -ForegroundColor Green
        } elseif ($apiResult.status_code -eq 404) {
            $result.status = "WARN"
            $result.actual = "HTTP 404 - AI Service not available"
            $result.error_message = "AI Service may not be started"
            Write-Host "  [WARN] $($test.name): AI Service not running (HTTP 404)" -ForegroundColor Yellow
        } else {
            $result.status = "FAIL"
            $result.actual = "HTTP $($apiResult.status_code)"
            Write-Host "  [FAIL] $($test.name): HTTP $($apiResult.status_code)" -ForegroundColor Red
        }
        
        $TestResults += $result
    }
    
    # HL7消息解析测试
    $hl7Test = @{
        id = 'HL7001'
        name = 'HL7消息解析'
        url = ($BASE_URLS['hl7_service'] + '/hl7/parse')
        method = 'POST'
        data = @{
            message = 'MSH|^~\&|LAB|HOSP|LAB|HOSP|202604051200||ORM^O01|MSG00001|P|2.3.1`rPID|1||PT001||DOE^JOHN^|19700101|M`rOBR|1|ORD001||BLD^Blood Routine|||202604051200'
        }
    }
    
    $result = New-TestResult -TestId $hl7Test.id -TestName $hl7Test.name -Category "HL7 Service"
    $result.expected = "HTTP 200 - Message parsed"
    
    $apiResult = Invoke-ApiRequest -Url $hl7Test.url -Method $hl7Test.method -Data $hl7Test.data
    
    $result.http_status = $apiResult.status_code
    $result.response_time_ms = $apiResult.elapsed_ms
    
    if ($apiResult.success) {
        $result.details = $apiResult.data
        $result.status = "PASS"
        $result.actual = "HTTP $($apiResult.status_code) - Parsed successfully"
        Write-Host "  [PASS] $($hl7Test.name): Parsed ($($apiResult.elapsed_ms)ms)" -ForegroundColor Green
    } else {
        $result.status = "WARN"
        $result.actual = "HL7 Service error or not available"
        Write-Host "  [WARN] $($hl7Test.name): Service error" -ForegroundColor Yellow
    }
    
    $TestResults += $result
}

# ==================== 阶段6：安全性测试 ====================

function Test-Security {
    param([string]$Token = $null)
    
    Write-TestHeader "阶段6：安全性测试 (Security Tests)"
    
    # 测试未授权访问
    $result = New-TestResult -TestId 'SEC001' -TestName '未授权访问保护' -Category "Security"
    $result.expected = "HTTP 401/403 - Unauthorized access blocked"
    
    $apiResult = Invoke-ApiRequest -Url ($BASE_URLS['user_service'] + '/user/list') -Method 'GET'
    
    $result.http_status = $apiResult.status_code
    $result.response_time_ms = $apiResult.elapsed_ms
    
    if ($apiResult.status_code -in @(401, 403)) {
        $result.status = "PASS"
        $result.actual = "HTTP $($apiResult.status_code) - Properly blocked"
        Write-Host "  [PASS] 未授权访问保护: Access denied (HTTP $($apiResult.status_code))" -ForegroundColor Green
    } elseif ($apiResult.status_code -eq 200) {
        $result.status = "FAIL"
        $result.actual = "HTTP 200 - Unauthorized access allowed!"
        $result.error_message = "Security vulnerability: endpoint not protected"
        Write-Host "  [FAIL] 未授权访问保护: NOT PROTECTED (HTTP 200)" -ForegroundColor Red
    } else {
        $result.status = "WARN"
        $result.actual = "HTTP $($apiResult.status_code)"
        Write-Host "  [WARN] 未授权访问保护: HTTP $($apiResult.status_code)" -ForegroundColor Yellow
    }
    
    $TestResults += $result
}

# ==================== 阶段7：性能基准测试 ====================

function Test-PerformanceBenchmark {
    Write-TestHeader "阶段7：性能基准测试 (Performance Benchmark Tests)"
    
    $endpoints = @(
        @{id='PERF001'; name='标本列表查询性能'; url=($BASE_URLS['sample_service'] + '/sample/list'); method='GET'},
        @{id='PERF002'; name='报告列表查询性能'; url=($BASE_URLS['report_service'] + '/report/list'); method='GET'},
        @{id='PERF003'; name='Gateway路由性能'; url=($BASE_URLS['gateway'] + '/api/sample/list'); method='GET'}
    )
    
    foreach ($ep in $endpoints) {
        $result = New-TestResult -TestId $ep.id -TestName $ep.name -Category "Performance"
        $result.expected = "P50 < 200ms, P95 < 500ms"
        
        $times = @()
        $successCount = 0
        
        for ($i = 0; $i -lt 10; $i++) {
            $apiResult = Invoke-ApiRequest -Url $ep.url -Method $ep.method
            $times += $apiResult.elapsed_ms
            if ($apiResult.success -and $apiResult.status_code -eq 200) {
                $successCount++
            }
            Start-Sleep -Milliseconds 100
        }
        
        if ($times.Count -gt 0) {
            $sortedTimes = $times | Sort-Object
            $p50Idx = [math]::Floor($sortedTimes.Count * 0.50)
            $p95Idx = [math]::Min([math]::Floor($sortedTimes.Count * 0.95), $sortedTimes.Count - 1)
            $p99Idx = [math]::Min([math]::Floor($sortedTimes.Count * 0.99), $sortedTimes.Count - 1)
            
            $p50 = $sortedTimes[$p50Idx]
            $p95 = $sortedTimes[$p95Idx]
            $p99 = $sortedTimes[$p99Idx]
            $avg = ($sortedTimes | Measure-Object -Average).Average
            
            $result.details = @{
                avg_ms = [math]::Round($avg, 2)
                p50_ms = [math]::Round($p50, 2)
                p95_ms = [math]::Round($p95, 2)
                p99_ms = [math]::Round($p99, 2)
                min_ms = [math]::Round(($sortedTimes | Measure-Object -Minimum).Minimum, 2)
                max_ms = [math]::Round(($sortedTimes | Measure-Object -Maximum).Maximum, 2)
                success_rate = "$successCount/$($times.Count)"
            }
            
            $result.response_time_ms = [math]::Round($avg, 2)
            
            if ($p95 -lt 500 -and $p50 -lt 200) {
                $result.status = "PASS"
                $result.actual = "Avg:${avg:0}ms P50:${p50:0}ms P95:${p95:0}ms P99:${p99:0}ms"
                Write-Host "  [PASS] $($ep.name): Avg=${avg:0}ms, P50=${p50:0}ms, P95=${p95:0}ms, P99=${p99:0}ms" -ForegroundColor Green
            } elseif ($p95 -lt 1000) {
                $result.status = "WARN"
                $result.actual = "P95=${p95:0}ms (above target <500ms)"
                Write-Host "  [WARN] $($ep.name): P95=${p95:0}ms (target <500ms)" -ForegroundColor Yellow
            } else {
                $result.status = "FAIL"
                $result.actual = "P95=${p95:0}ms exceeds limit"
                Write-Host "  [FAIL] $($ep.name): P95=${p95:0}ms > 1000ms limit" -ForegroundColor Red
            }
        }
        
        $TestResults += $result
    }
}

# ==================== 主测试流程 ====================

function Main {
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "实验室管理系统 v1.6.0 - 全面回归测试套件" -ForegroundColor Yellow
    Write-Host "Lab Management System v1.6.0 - Comprehensive Regression Test Suite" -ForegroundColor White
    Write-Host "测试开始时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
    Write-Host ("=" * 80) -ForegroundColor Cyan
    
    try {
        # 执行所有测试阶段
        Test-HealthChecks
        $token = Test-UserAuthentication
        Test-SampleManagement -Token $token
        Test-ReportManagement -Token $token
        Test-AIAndHL7Services
        Test-Security -Token $token
        Test-PerformanceBenchmark
    }
    catch {
        Write-Host "`n[CRITICAL ERROR] Test suite failed: $_" -ForegroundColor Red
        $_ | Out-String | Write-Host -ForegroundColor Red
    }
    
    # 生成测试报告
    Generate-TestReport
}

function Generate-TestReport {
    Write-TestHeader "测试报告汇总 (Test Summary Report)"
    
    # 统计结果
    $total = $TestResults.Count
    $passed = ($TestResults | Where-Object { $_.status -eq 'PASS' }).Count
    $failed = ($TestResults | Where-Object { $_.status -eq 'FAIL' }).Count
    $warned = ($TestResults | Where-Object { $_.status -eq 'WARN' }).Count
    $errors = ($TestResults | Where-Object { $_.status -eq 'ERROR' }).Count
    
    $passRate = if ($total -gt 0) { [math]::Round(($passed / $total) * 100, 1) } else { 0 }
    
    Write-Host "`n总测试用例数: $total"
    Write-Host "通过 (PASS):   $passed ($passRate%)" -ForegroundColor Green
    Write-Host "失败 (FAIL):   $failed" -ForegroundColor Red
    Write-Host "警告 (WARN):   $warned" -ForegroundColor Yellow
    Write-Host "错误 (ERROR):  $errors" -ForegroundColor Magenta
    
    # 按类别统计
    Write-Host "`n按测试类别统计:" -ForegroundColor Cyan
    $categories = $TestResults | Group-Object -Property category
    foreach ($cat in $categories | Sort-Object Name) {
        $catPassed = ($cat.Group | Where-Object { $_.status -eq 'PASS' }).Count
        $catTotal = $cat.Group.Count
        $catRate = if ($catTotal -gt 0) { [math]::Round(($catPassed / $catTotal) * 100, 1) } else { 0 }
        Write-Host ("  {0,-25}: {1,3}/{2,3} 通过 ({3,5}%)" -f $cat.Name, $catPassed, $catTotal, $catRate)
    }
    
    # 性能指标汇总
    if ($PerformanceMetrics.Count -gt 0) {
        Write-Host "`n性能指标汇总:" -ForegroundColor Cyan
        $perfTimes = $PerformanceMetrics | Where-Object { $_.response_time_ms -gt 0 } | Select-Object -ExpandProperty response_time_ms
        if ($perfTimes.Count -gt 0) {
            $sortedPerf = $perfTimes | Sort-Object
            $n = $sortedPerf.Count
            Write-Host ("  总请求数:       {0}" -f $n)
            Write-Host ("  平均响应时间:   {0:F2}ms" -f (($sortedPerf | Measure-Object -Average).Average))
            Write-Host ("  最小响应时间:   {0:F2}ms" -f ($sortedPerf | Measure-Object -Minimum).Minimum)
            Write-Host ("  最大响应时间:   {0:F2}ms" -f ($sortedPerf | Measure-Object -Maximum).Maximum)
            Write-Host ("  P50 响应时间:   {0:F2}ms" -f $sortedPerf[[math]::Floor($n * 0.50)])
            Write-Host ("  P95 响应时间:   {0:F2}ms" -f $sortedPerf[[math]::Min([math]::Floor($n * 0.95), $n - 1)])
            Write-Host ("  P99 响应时间:   {0:F2}ms" -f $sortedPerf[[math]::Min([math]::Floor($n * 0.99), $n - 1)])
        }
    }
    
    # 失败的测试用例详情
    $failedTests = $TestResults | Where-Object { $_.status -in @('FAIL', 'ERROR') }
    if ($failedTests.Count -gt 0) {
        Write-Host "`n失败的测试用例:" -ForegroundColor Red
        foreach ($ft in $failedTests) {
            Write-Host ("  [{0}] {1}: {2}" -f $ft.status, $ft.test_id, $ft.test_name) -ForegroundColor Red
            if ($ft.error_message) {
                Write-Host ("         Error: {0}" -f ($ft.error_message.ToString().Substring(0, [Math]::Min(100, $ft.error_message.ToString().Length)))) -ForegroundColor Gray
            }
        }
    }
    
    # 保存详细结果到JSON文件
    $reportData = @{
        version = 'v1.6.0'
        test_timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        summary = @{
            total_tests = $total
            passed = $passed
            failed = $failed
            warned = $warned
            errors = $errors
            pass_rate = $passRate
        }
        performance_summary = @{
            total_requests = $PerformanceMetrics.Count
            avg_response_ms = if ($PerformanceMetrics.Count -gt 0) { [math]::Round(($PerformanceMetrics | Measure-Object -Property response_time_ms -Average).Average, 2) } else { 0 }
        }
        test_results = $TestResults
        performance_metrics = $PerformanceMetrics
    }
    
    $outputFile = 'd:\FinalCodeAndFile\lab-management-system\test_results\api-test-results-v1.6.0.json'
    $reportData | ConvertTo-Json -Depth 5 | Out-File -FilePath $outputFile -Encoding UTF8
    Write-Host "`n详细测试结果已保存至: $outputFile" -ForegroundColor Cyan
    
    # 最终结论
    Write-TestHeader "最终结论 (Final Conclusion)"
    
    if ($passRate -ge 90) {
        Write-Host "`n测试通过率: $passRate%" -ForegroundColor Green
        Write-Host "状态: 通过验收标准 (PASSED)" -ForegroundColor Green
        Write-Host "系统版本 v1.6.0 已达到生产就绪状态，可以部署上线。" -ForegroundColor White
    } elseif ($passRate -ge 70) {
        Write-Host "`n测试通过率: $passRate%" -ForegroundColor Yellow
        Write-Host "状态: 有条件通过 (CONDITIONAL PASS)" -ForegroundColor Yellow
        Write-Host "系统基本功能正常，但存在部分缺陷需要修复后才能部署。" -ForegroundColor White
    } else {
        Write-Host "`n测试通过率: $passRate%" -ForegroundColor Red
        Write-Host "状态: 未通过验收 (FAILED)" -ForegroundColor Red
        Write-Host "系统存在严重问题，不建议部署，需要修复后重新测试。" -ForegroundColor White
    }
    
    Write-Host "`n测试完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
    
    return $passRate -ge 90
}

# 执行主函数
Main
