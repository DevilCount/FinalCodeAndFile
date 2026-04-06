# 实验室管理系统 - 修正后的API测试报告

**测试时间**: 2026-04-03 08:15:26


## 测试摘要


- **总测试用例**: 13

- **通过**: 5 (38.5%)

- **失败**: 8


## 重点测试结果


### 1. 登录接口空参数验证 (使用表单参数)

- **测试名称**: 登录接口 - 空参数验证 (表单格式)

- **期望状态码**: 400

- **实际状态码**: 200

- **测试结果**: FAIL

- **响应时间**: 33.04ms

- **响应内容**: {"code":400,"message":"用户名不能为空","timestamp":1775175325896,"error":true,"success":false}


### 2. 标本按状态查询接口

- **标本服务 - 按状态查询 (PENDING)**: FAIL (状态码: 500)

- **标本服务 - 按状态查询 (RECEIVED)**: FAIL (状态码: 500)

- **标本服务 - 按状态查询 (TESTING)**: FAIL (状态码: 500)

- **标本服务 - 按状态查询 (COMPLETED)**: FAIL (状态码: 500)

- **标本服务 - 按状态查询 (REPORTED)**: FAIL (状态码: 500)


## 详细测试结果


| 序号 | 测试名称 | 服务 | 方法 | 端点 | 期望 | 实际 | 结果 | 响应时间(ms) |

|------|---------|------|------|------|------|------|------|-------------|

| 1 | 登录接口 - 空参数验证 (表单格式) | User Service | POST | /user/login | 400 | 200 | FAIL | 33.04 |

| 2 | 登录接口 - 缺少用户名 (表单格式) | User Service | POST | /user/login | 400 | 200 | FAIL | 22.68 |

| 3 | 登录接口 - 缺少密码 (表单格式) | User Service | POST | /user/login | 400 | 200 | FAIL | 27.23 |

| 4 | 登录接口 - 正常登录 (表单格式) | User Service | POST | /user/login | 200 | 200 | PASS | 30.19 |

| 5 | 标本服务 - 获取标本列表 | Sample Service | GET | /sample/list | 200 | 200 | PASS | 19.94 |

| 6 | 标本服务 - 按状态查询 (PENDING) | Sample Service | GET | /sample/list-by-status | 200 | 500 | FAIL | 8.35 |

| 7 | 标本服务 - 按状态查询 (RECEIVED) | Sample Service | GET | /sample/list-by-status | 200 | 500 | FAIL | 41.49 |

| 8 | 标本服务 - 按状态查询 (TESTING) | Sample Service | GET | /sample/list-by-status | 200 | 500 | FAIL | 19.25 |

| 9 | 标本服务 - 按状态查询 (COMPLETED) | Sample Service | GET | /sample/list-by-status | 200 | 500 | FAIL | 8.13 |

| 10 | 标本服务 - 按状态查询 (REPORTED) | Sample Service | GET | /sample/list-by-status | 200 | 500 | FAIL | 22.29 |

| 11 | 用户服务 - 获取用户列表 | User Service | GET | /user/list | 200 | 200 | PASS | 50.84 |

| 12 | 报告服务 - 获取报告列表 | Report Service | GET | /report/list | 200 | 200 | PASS | 40.57 |

| 13 | AI服务 - 健康检查 | AI Service | GET | /ai/health | 200 | 200 | PASS | 7.08 |
