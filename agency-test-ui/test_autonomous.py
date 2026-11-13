import asyncio
import sys
from pathlib import Path
import httpx

# Add agency-test-ui to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from main import app, daemon

async def run_tests():
    print("=== STARTING 24/7 AUTONOMOUS ENGINE & API VERIFICATION ===")
    transport = httpx.ASGITransport(app=app)
    
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test daemon status endpoint
        resp = await client.get("/api/daemon/status")
        assert resp.status_code == 200, f"Daemon status failed: {resp.text}"
        status_data = resp.json()
        print(f"[*] /api/daemon/status OK: is_active={status_data['is_active']}, uptime={status_data['uptime_seconds']}s")
        assert "audit_logs" in status_data
        
        # 2. Test manual trigger of morning radar
        resp = await client.post("/api/daemon/trigger-job", json={"job_id": "morning-radar"})
        assert resp.status_code == 200, f"Trigger job failed: {resp.text}"
        print(f"[*] /api/daemon/trigger-job (morning-radar) OK")
        
        # 3. Test manual trigger of nightly audit
        resp = await client.post("/api/daemon/trigger-job", json={"job_id": "nightly-audit"})
        assert resp.status_code == 200, f"Trigger job failed: {resp.text}"
        print(f"[*] /api/daemon/trigger-job (nightly-audit) OK")
        
        # 4. Test submitting a new client brief (e.g. for Shopee e-commerce)
        brief_payload = {
            "name": "Hoàng Thu Thảo",
            "contact": "0988776655",
            "service": "ecommerce-shopee",
            "details": "Cần tối ưu gian hàng mỹ phẩm và kịch bản livestream TikTok Shop Mega Sale."
        }
        resp = await client.post("/api/submit-brief", json=brief_payload)
        assert resp.status_code == 200, f"Submit brief failed: {resp.text}"
        brief_res = resp.json()
        print(f"[*] /api/submit-brief OK: lead_index={brief_res.get('lead_index')}")
        
        # Wait a moment for background task to execute
        await asyncio.sleep(1.0)
        
        # 5. Check leads ledger to verify auto-fulfillment
        resp = await client.get("/api/leads")
        assert resp.status_code == 200
        leads = resp.json().get("leads", [])
        assert len(leads) > 0
        latest_lead = leads[-1]
        print(f"[*] Latest Lead: {latest_lead.get('name')} | Status: {latest_lead.get('status')}")
        assert latest_lead.get("status") == "ready-for-review", f"Status expected ready-for-review, got {latest_lead.get('status')}"
        assert latest_lead.get("assigned_agent", {}).get("slug") == "specialized-vietnamese-ecommerce-strategist"
        assert "draft_deliverable" in latest_lead and len(latest_lead["draft_deliverable"]) > 100
        print(f"[*] Auto-fulfillment verified! Specialist assigned: {latest_lead['assigned_agent']['title']}")
        
        # 6. Test Admin HTML page rendering
        resp = await client.get("/admin")
        assert resp.status_code == 200
        assert "Trung Tâm Tự Hành 24/7" in resp.text
        print("[*] /admin HTML render OK")
        
        # 7. Test Studio HTML page rendering
        resp = await client.get("/studio")
        assert resp.status_code == 200
        print("[*] /studio HTML render OK")
        
        # 8. Test Landing HTML page rendering
        resp = await client.get("/")
        assert resp.status_code == 200
        print("[*] / Landing HTML render OK")
        
        # 9. Test toggle daemon
        resp = await client.post("/api/daemon/toggle", json={"active": False})
        assert resp.status_code == 200 and resp.json()["is_active"] is False
        resp = await client.post("/api/daemon/toggle", json={"active": True})
        assert resp.status_code == 200 and resp.json()["is_active"] is True
        print("[*] /api/daemon/toggle OK")
        
    print("=== ALL 24/7 AUTONOMOUS TESTS PASSED WITH 100% SUCCESS ===")

if __name__ == "__main__":
    asyncio.run(run_tests())

