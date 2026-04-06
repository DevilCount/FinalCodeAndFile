# 实验室管理系统 - 完整API测试报告

**测试时间**: 2026-04-03 08:13:51


## 测试摘要


- **总测试用例**: 20

- **通过**: 6 (30.0%)

- **失败**: 14


## 重点测试结果


### 1. 登录接口空参数验证

- **测试名称**: 登录接口 - 空参数验证

- **期望状态码**: 400

- **实际状态码**: 200

- **测试结果**: FAIL

- **响应时间**: 26.57ms


### 2. 标本按状态查询接口

- **标本服务 - 按状态查询 (PENDING)**: FAIL (状态码: 500)

- **标本服务 - 按状态查询 (RECEIVED)**: FAIL (状态码: 500)

- **标本服务 - 按状态查询 (TESTING)**: FAIL (状态码: 500)

- **标本服务 - 按状态查询 (COMPLETED)**: FAIL (状态码: 500)

- **标本服务 - 按状态查询 (REPORTED)**: FAIL (状态码: 500)


## 详细测试结果


| 序号 | 测试名称 | 服务 | 方法 | 端点 | 期望 | 实际 | 结果 | 响应时间(ms) |

|------|---------|------|------|------|------|------|------|-------------|

| 1 | Gateway 健康检查 | Gateway | GET | /actuator/health | 200 | 404 | FAIL | 910.51 |

| 2 | User Service 健康检查 | User Service | GET | /actuator/health | 200 | 500 | FAIL | 91.27 |

| 3 | Sample Service 健康检查 | Sample Service | GET | /actuator/health | 200 | 500 | FAIL | 711.97 |

| 4 | Report Service 健康检查 | Report Service | GET | /actuator/health | 200 | 500 | FAIL | 1715.47 |

| 5 | HL7 Service 健康检查 | HL7 Service | GET | /actuator/health | 200 | 404 | FAIL | 1604.55 |

| 6 | AI Service 健康检查 | AI Service | GET | /actuator/health | 200 | 404 | FAIL | 1712.8 |

| 7 | 登录接口 - 空参数验证 | User Service | POST | /user/login | 400 | 200 | FAIL | 26.57 |

| 8 | 登录接口 - 缺少用户名 | User Service | POST | /user/login | 400 | 200 | FAIL | 30.5 |

| 9 | 登录接口 - 缺少密码 | User Service | POST | /user/login | 400 | 200 | FAIL | 26.64 |

| 10 | 登录接口 - 正常登录 | User Service | POST | /user/login | 200 | 200 | PASS | 27.63 |

| 11 | 用户服务 - 获取用户列表 | User Service | GET | /user/list | 200 | 200 | PASS | 1299.32 |

| 12 | 标本服务 - 获取标本列表 | Sample Service | GET | /sample/list | 200 | 200 | PASS | 431.34 |

| 13 | 标本服务 - 按状态查询 (PENDING) | Sample Service | GET | /sample/list-by-status | 200 | 500 | FAIL | 51.03 |

| 14 | 标本服务 - 按状态查询 (RECEIVED) | Sample Service | GET | /sample/list-by-status | 200 | 500 | FAIL | 15.51 |

| 15 | 标本服务 - 按状态查询 (TESTING) | Sample Service | GET | /sample/list-by-status | 200 | 500 | FAIL | 26.33 |

| 16 | 标本服务 - 按状态查询 (COMPLETED) | Sample Service | GET | /sample/list-by-status | 200 | 500 | FAIL | 41.0 |

| 17 | 标本服务 - 按状态查询 (REPORTED) | Sample Service | GET | /sample/list-by-status | 200 | 500 | FAIL | 20.34 |

| 18 | 报告服务 - 获取报告列表 | Report Service | GET | /report/list | 200 | 200 | PASS | 284.46 |

| 19 | AI服务 - 健康检查 | AI Service | GET | /ai/health | 200 | 200 | PASS | 128.98 |

| 20 | HL7服务 - 解析HL7消息 | HL7 Service | POST | /hl7/parse | 200 | 200 | PASS | 93.36 |


## 服务配置


| 服务 | 地址 |

|------|------|

| Gateway | http://localhost:8080 |

| User Service | http://localhost:8086 |

| Sample Service | http://localhost:8087 |

| Report Service | http://localhost:8088 |

| HL7 Service | http://localhost:8084 |

| AI Service | http://localhost:8085 |
