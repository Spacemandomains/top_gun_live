import os
import httpx
import stripe
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Secure Keys from Vercel Environment Variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
PAYMENT_LINK = os.getenv("STRIPE_PAYMENT_LINK")
BASE_URL = "https://top-gun-live.vercel.app"

app = FastAPI(title="Top GUN GEO-Lens API")

# Security: Only allow your live domain to make cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[BASE_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def perform_geo_audit(query: str):
    """Scans the generative landscape using Brave Search."""
    headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
    params = {"q": f"{query} brand mentions and llm citations", "count": 5}
    
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params=params)
        if response.status_code != 200:
            return {"error": "Upstream Data Error", "status": 500}
        
        data = response.json()
        results = data.get("web", {}).get("results", [])
        score = min(len(results) * 15, 100) # Simple heuristic visibility score
        
        return {
            "query": query,
            "visibility_score": score,
            "llm_index_status": "Indexed" if score > 50 else "Partial",
            "top_citations": [r.get("url") for r in results[:3]],
            "timestamp": "2026-03-25"
        }

@app.get("/api/v1/audit")
async def geo_audit(query: str, request: Request):
    # Agents must provide the Stripe PaymentIntent ID in this header
    payment_intent_id = request.headers.get("X-Payment-Intent")

    if not payment_intent_id:
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={
                "error": "Payment Required",
                "amount": 1.50,
                "currency": "USD",
                "payment_url": PAYMENT_LINK,
                "instructions": "Submit PaymentIntent ID in 'X-Payment-Intent' header."
            }
        )

    try:
        # Verify payment status via Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status != "succeeded":
            raise HTTPException(status_code=403, detail="Payment not cleared.")
        
        # Execute the audit logic
        return await perform_geo_audit(query)

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Payment ID or Processing Error")

@app.get("/ai-agents.json")
async def discovery():
    return {
        "name": "Top GUN GEO-Lens",
        "api_url": f"{BASE_URL}/api/v1/audit",
        "protocol": "Stripe-MPP-x402",
        "pricing": "1.50 USD/req",
        "lookup_key": "top_gun_audit_v1"
    }
