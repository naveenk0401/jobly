import httpx
import asyncio
import os

BASE_URL = "http://localhost:8001"
USER_ID  = "69bcdaa40d8db9c658e885d5" # Verified ID from previous steps

async def test_flow():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n1. --- UPLOADING RESUME ---")
        # Use any small file as a placeholder PDF
        with open("requirements.txt", "rb") as f:
            files = {"file": ("resume.pdf", f, "application/pdf")}
            data  = {"user_id": USER_ID}
            resp  = await client.post(f"{BASE_URL}/resume/", data=data, files=files)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.json()}")

        print(f"\n2. --- TRIGGERING MATCH ---")
        params = {"user_id": USER_ID, "limit": 10}
        # Try with/without slash if first fails
        resp = await client.post(f"{BASE_URL}/applications/match", params=params)
        print(f"POST /applications/match Status: {resp.status_code}")
        if resp.status_code == 404:
            resp = await client.post(f"{BASE_URL}/applications/match/", params=params)
            print(f"POST /applications/match/ Status: {resp.status_code}")

        print(f"\n3. --- CHECKING DASHBOARD ---")
        resp = await client.get(f"{BASE_URL}/applications/dashboard", params=params)
        print(f"GET /applications/dashboard Status: {resp.status_code}")
        if resp.status_code == 404:
            resp = await client.get(f"{BASE_URL}/applications/dashboard/", params=params)
            print(f"GET /applications/dashboard/ Status: {resp.status_code}")

        print(f"\n4. --- WAITING FOR RESULTS ---")
        await asyncio.sleep(5)
        resp = await client.get(f"{BASE_URL}/applications/dashboard", params=params)
        print(f"Final Dashboard Status: {resp.status_code}")
        print(f"Body: {resp.json()}")

if __name__ == "__main__":
    asyncio.run(test_flow())
