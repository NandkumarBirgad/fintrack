import requests
import json

BASE = "http://localhost:5000"
lines = []

def test(label, resp, expect_fail=False):
    status = resp.status_code
    try:
        body = resp.json()
    except:
        body = {"raw": resp.text[:200]}
    passed = (status >= 400) if expect_fail else (status < 400)
    icon = "OK" if passed else "XX"
    msg = body.get("msg", body.get("message", "")) if isinstance(body, dict) else ""
    lines.append(f"{icon} [{status}] {label} -- {msg}")
    return body

r = requests.get(f"{BASE}/health")
test("GET /health", r)

r = requests.post(f"{BASE}/auth/register", json={"name":"API Test","email":"apitest99@x.com","password":"Test@12345","role":"viewer"})
test("POST /auth/register", r)

r = requests.post(f"{BASE}/auth/login", json={"email":"admin@fintrack.com","password":"Admin@123"})
d = test("POST /auth/login (admin)", r)
at = d.get("data",{}).get("access_token","")
rt = d.get("data",{}).get("refresh_token","")
ah = {"Authorization": f"Bearer {at}"}

r = requests.post(f"{BASE}/auth/login", json={"email":"viewer@fintrack.com","password":"Viewer@123"})
d2 = test("POST /auth/login (viewer)", r)
vt = d2.get("data",{}).get("access_token","")
vh = {"Authorization": f"Bearer {vt}"}

r = requests.post(f"{BASE}/auth/login", json={"email":"analyst@fintrack.com","password":"Analyst@123"})
d3 = test("POST /auth/login (analyst)", r)
ant = d3.get("data",{}).get("access_token","")
anh = {"Authorization": f"Bearer {ant}"}

r = requests.get(f"{BASE}/auth/me", headers=ah)
test("GET /auth/me", r)

r = requests.post(f"{BASE}/auth/refresh", headers={"Authorization": f"Bearer {rt}"})
test("POST /auth/refresh", r)

r = requests.get(f"{BASE}/transactions", headers=ah)
test("GET /transactions (admin)", r)

r = requests.get(f"{BASE}/transactions?type=income", headers=anh)
test("GET /transactions?type=income (analyst)", r)

r = requests.post(f"{BASE}/transactions", headers=ah, json={"amount":999,"type":"expense","category":"Test","date":"2025-01-01","notes":"test"})
cd = test("POST /transactions (admin create)", r)
tid = cd.get("data",{}).get("id") if cd.get("data") else None

if tid:
    r = requests.get(f"{BASE}/transactions/{tid}", headers=ah)
    test(f"GET /transactions/{tid}", r)
    r = requests.put(f"{BASE}/transactions/{tid}", headers=ah, json={"amount":1500})
    test(f"PUT /transactions/{tid}", r)

r = requests.post(f"{BASE}/transactions", headers=vh, json={"amount":50,"type":"expense","category":"X","date":"2025-01-01"})
test("POST /transactions (viewer-DENY)", r, expect_fail=True)

r = requests.get(f"{BASE}/analytics/summary", headers=ah)
test("GET /analytics/summary", r)

r = requests.get(f"{BASE}/analytics/monthly?year=2024", headers=ah)
test("GET /analytics/monthly (admin)", r)

r = requests.get(f"{BASE}/analytics/categories?type=expense", headers=ah)
test("GET /analytics/categories (admin)", r)

r = requests.get(f"{BASE}/analytics/recent?limit=5", headers=ah)
test("GET /analytics/recent", r)

r = requests.get(f"{BASE}/analytics/monthly?year=2024", headers=vh)
test("GET /analytics/monthly (viewer-DENY)", r, expect_fail=True)

r = requests.get(f"{BASE}/users", headers=ah)
test("GET /users (admin)", r)

r = requests.get(f"{BASE}/users", headers=vh)
test("GET /users (viewer-DENY)", r, expect_fail=True)

if tid:
    r = requests.delete(f"{BASE}/transactions/{tid}", headers=ah)
    test(f"DELETE /transactions/{tid}", r)

r = requests.get(f"{BASE}/transactions")
test("GET /transactions (no-auth-DENY)", r, expect_fail=True)

ok = sum(1 for l in lines if l.startswith("OK"))
xx = sum(1 for l in lines if l.startswith("XX"))
with open("results.log", "w", encoding="ascii", errors="replace") as f:
    for l in lines:
        f.write(l + "\n")
    f.write(f"\nTOTAL={len(lines)} OK={ok} FAIL={xx}\n")
print(f"Done. OK={ok} FAIL={xx}")
