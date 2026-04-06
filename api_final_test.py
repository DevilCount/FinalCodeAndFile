import requests
import json
import time

RESULTS_FILE = r"d:\FinalCodeAndFile\lab-management-system\test_results\api-live-test-v1.4.0-final.json"

services = {
    "User Service": "http://localhost:8086",
    "Sample Service": "http://localhost:8087",
    "Report Service": "http://localhost:8088",
    "AI Service": "http://localhost:8085",
    "HL7 Service": "http://localhost:8084",
}

test_cases = [
    # User Service - BCrypt fix verification
    {"service": "User Service", "method": "POST", "endpoint": "/user/login",
     "params": {"username": "admin", "password": "admin123"}, "expect": 200, "note": "BCrypt login"},
    {"service": "User Service", "method": "POST", "endpoint": "/user/register",
     "json": {"username": "testuser_v4_final", "password": "test123456", "realName": "TestV4Final", "role": "DOCTOR"}, "expect": 200, "note": "Register with GlobalEH"},
    {"service": "User Service", "method": "GET", "endpoint": "/user/list", "expect": 200},
    {"service": "User Service", "method": "GET", "endpoint": "/user/1", "expect": 200},

    # Report Service - 47-column fix verification
    {"service": "Report Service", "method": "GET", "endpoint": "/report/list", "expect": 200, "note": "47-col list"},
    {"service": "Report Service", "method": "GET", "endpoint": "/report/list",
     "params": {"page": 1, "pageSize": 10}, "expect": 200, "note": "Paged list"},
    {"service": "Report Service", "method": "GET", "endpoint": "/report/pending-list", "expect": 200},
    {"service": "Report Service", "method": "POST", "endpoint": "/report/create",
     "json": {"patientName": "FinalTestPatient", "sampleId": 1, "status": "DRAFT"}, "expect": 200, "note": "Create report"},

    # Sample Service - validation fix verification
    {"service": "Sample Service", "method": "GET", "endpoint": "/sample/list", "expect": 200},
    {"service": "Sample Service", "method": "POST", "endpoint": "/sample/create",
     "json": {"patientName": "FinalPatient", "doctorName": "FinalDoctor", "testItems": "Blood,Urine", "sampleType": "BLOOD"}, "expect": 200, "note": "Create sample"},
    {"service": "Sample Service", "method": "GET", "endpoint": "/sample/1", "expect": 200},

    # AI Service - correct endpoints
    {"service": "AI Service", "method": "POST", "endpoint": "/ai/diagnose",
     "json": {"patientName": "TestPatient", "testResults": {"WBC": 11.5, "RBC": 4.2}}, "expect": 200, "note": "AI diagnose"},
    {"service": "AI Service", "method": "GET", "endpoint": "/ai/health", "expect": 200, "note": "AI health check"},

    # HL7 Service - correct endpoints
    {"service": "HL7 Service", "method": "POST", "endpoint": "/hl7/parse",
     'json': {"message": "MSH|^~\\&|LIS|HIS|202604021200||ORM^O01|123|P|2.3.1"}, "expect": 200, "note": "Parse HL7"},
    {"service": "HL7 Service", "method": "POST", "endpoint": "/hl7/generate-order",
     "json": {"patientId": "P001", "patientName": "TestPatient", "orderType": "BloodRoutine"}, "expect": 200, "note": "Generate order"},
]

results = []
passed = 0
failed = 0

print("=" * 80)
print("v1.4.0 FINAL API Live Test")
print("=" * 80)

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
        })
    except Exception as e:
        failed += 1
        full_result.update({
            "result": "FAIL",
            "status_code": None,
            "response_time_ms": None,
            "error": str(e)[:300],
            "response_body": "",
        })

    results.append(full_result)
    icon = "✅" if full_result["result"] == "PASS" else "❌"
    sc = full_result.get("status_code")
    sc_str = str(sc) if sc is not None else "N/A"
    rt = full_result.get("response_time_ms")
    rt_str = f"{rt:.2f}" if rt is not None else "N/A"
    print(f"[{i:02d}] {icon} {method:4} {svc:16} {endpoint:30} → {sc_str:>4} ({rt_str:>10}ms) {note}")

total = len(results)
pass_rate = round(passed / total * 100, 1) if total > 0 else 0

print(f"\n{'='*80}")
print(f"FINAL RESULTS: {passed}/{total} passed ({pass_rate}%)")
print(f"v1.3.1 baseline: 60.0% | Change: {pass_rate - 60.0:+.1f}%")
print(f"{'='*80}")

summary = {
    "version": "v1.4.0-FINAL",
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
