import requests
import json
import time
import statistics

RESULTS_FILE = r"d:\FinalCodeAndFile\lab-management-system\test_results\api-live-test-v1.4.0.json"

services = {
    "User Service": "http://localhost:8086",
    "Sample Service": "http://localhost:8087",
    "Report Service": "http://localhost:8088",
    "AI Service": "http://localhost:8085",
    "HL7 Service": "http://localhost:8084",
}

test_cases = [
    # User Service - verify BCrypt fix
    {"service": "User Service", "method": "POST", "endpoint": "/user/login",
     "params": {"username": "admin", "password": "admin123"}, "expect": 200, "note": "BCrypt login (1st)"},
    {"service": "User Service", "method": "POST", "endpoint": "/user/login",
     "params": {"username": "admin", "password": "admin123"}, "expect": 200, "note": "BCrypt login (2nd)"},
    {"service": "User Service", "method": "POST", "endpoint": "/user/register",
     "json": {"username": "testuser_v4", "password": "test123456", "realName": "TestV4", "role": "DOCTOR"}, "expect": 200},
    {"service": "User Service", "method": "GET", "endpoint": "/user/list", "expect": 200},
    {"service": "User Service", "method": "GET", "endpoint": "/user/1", "expect": 200},

    # Report Service - verify 45-column fix
    {"service": "Report Service", "method": "GET", "endpoint": "/report/list", "expect": 200},
    {"service": "Report Service", "method": "GET", "endpoint": "/report/list",
     "params": {"page": 1, "pageSize": 10}, "expect": 200},
    {"service": "Report Service", "method": "GET", "endpoint": "/report/pending-list", "expect": 200},
    {"service": "Report Service", "method": "POST", "endpoint": "/report/create",
     "json": {"patientName": "TestPatient", "sampleId": 1, "status": "DRAFT"}, "expect": 200},

    # Sample Service - verify validation fix
    {"service": "Sample Service", "method": "GET", "endpoint": "/sample/list", "expect": 200},
    {"service": "Sample Service", "method": "POST", "endpoint": "/sample/create",
     "json": {"patientName": "PatientV4", "doctorName": "DoctorV4", "testItems": "Blood Test", "sampleType": "BLOOD"}, "expect": 200},
    {"service": "Sample Service", "method": "GET", "endpoint": "/sample/1", "expect": 200},

    # AI Service
    {"service": "AI Service", "method": "POST", "endpoint": "/ai/analyze",
     "json": {"indicators": [{"name": "WBC", "value": 11.5, "unit": "10^9/L"}]}, "expect": 200},
    {"service": "AI Service", "method": "GET", "endpoint": "/ai/models", "expect": 200},

    # HL7 Service
    {"service": "HL7 Service", "method": "POST", "endpoint": "/hl7/parse",
     "json": {"message": "MSH|^~\\&|LIS|LAB|20260402090000||ORM^O01|1234|P|2.5"}, "expect": 200},
    {"service": "HL7 Service", "method": "GET", "endpoint": "/hl7/templates", "expect": 200},
]

results = []
passed = 0
failed = 0

for i, tc in enumerate(test_cases, 1):
    svc = tc["service"]
    base_url = services[svc]
    method = tc["method"]
    endpoint = tc["endpoint"]
    expect = tc.get("expect", 200)
    note = tc.get("note", "")

    url = base_url + endpoint
    full_result = {
        "id": i, "service": svc, "method": method, "endpoint": endpoint,
        "url": url, "expected": expect, "note": note
    }

    try:
        start = time.time()
        if method == "GET":
            params = tc.get("params", {})
            resp = requests.get(url, params=params, timeout=15)
        elif method == "POST":
            json_data = tc.get("json")
            params = tc.get("params")
            if json_data:
                resp = requests.post(url, json=json_data, timeout=15)
            elif params:
                resp = requests.post(url, params=params, timeout=15)
            else:
                resp = requests.post(url, timeout=15)
        elapsed_ms = round((time.time() - start) * 1000, 2)

        status = resp.status_code
        body_text = resp.text[:300] if resp.text else ""

        is_pass = (status == expect or status == 201 or (expect == 200 and status < 400))
        if is_pass:
            passed += 1
            full_result["result"] = "PASS"
        else:
            failed += 1
            full_result["result"] = "FAIL"

        full_result.update({
            "status_code": status,
            "response_time_ms": elapsed_ms,
            "response_body": body_text,
            "headers": dict(resp.headers),
        })
    except Exception as e:
        failed += 1
        full_result.update({
            "result": "FAIL",
            "status_code": None,
            "response_time_ms": None,
            "error": str(e)[:500],
            "response_body": "",
        })

    results.append(full_result)
    status_icon = "✅" if full_result["result"] == "PASS" else "❌"
    sc = full_result.get("status_code", "N/A")
    rt = full_result.get("response_time_ms", "N/A")
    print(f"[{i:02d}] {status_icon} {method:4} {svc:16} {endpoint:30} → {sc} ({rt}ms) {note}")

total = len(results)
pass_rate = round(passed / total * 100, 1) if total > 0 else 0

print(f"\n{'='*70}")
print(f"v1.4.0 API Live Test Results: {passed}/{total} passed ({pass_rate}%)")
print(f"{'='*70}")

summary = {
    "version": "v1.4.0",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "total_tests": total,
    "passed": passed,
    "failed": failed,
    "pass_rate": pass_rate,
    "v1_3_1_pass_rate": 60.0,
    "change_from_v131": round(pass_rate - 60.0, 1),
    "results": results,
}

with open(RESULTS_FILE, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"\nResults saved to: {RESULTS_FILE}")
