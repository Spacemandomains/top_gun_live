import os
import httpx
import stripe
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Secure Keys from Vercel Environment Variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
PAYMENT_LINK = os.getenv("STRIPE_PAYMENT_LINK") # https://buy.stripe.com/...

app = FastAPI(title="Top GUN GEO-Lens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

async def perform_geo_audit(query: str):
    """Actual logic to scan generative visibility using Brave Search."""
    headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
    params = {"q": f"{query} reviews and citations", "count": 5}
    
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params=params)
        if response.status_code != 200:
            return {"error": "Upstream Data Error"}
        
        data = response.json()
        # Simple GEO visibility heuristic based on web results
        results = data.get("web", {}).get("results", [])
        score = min(len(results) * 18, 100) # Mock scoring logic
        
        return {
            "query": query,
            "visibility_score": score,
            "citations_found": len(results),
            "sources": [r.get("url") for r in results[:3]],
            "geo_optimization_status": "High" if score > 70 else "Needs Improvement"
        }

@app.get("/api/v1/audit")
async def geo_audit(query: str, request: Request):
    payment_intent_id = request.headers.get("X-Payment-Intent")

    if not payment_intent_id:
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={
                "error": "Payment Required",
                "amount": 1.50,
                "payment_url": PAYMENT_LINK,
                "instructions": "Pay via link and provide 'X-Payment-Intent' header."
            }
        )

    try:
        # Verify the payment is successful
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status != "succeeded":
            raise HTTPException(status_code=403, detail="Payment pending or failed.")
        
        # Deliver the goods
        report = await perform_geo_audit(query)
        return report

    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid Payment ID")

@app.get("/ai-agents.json")
async def discovery():
    return {
        "name": "Top GUN GEO-Lens",
        "protocol": "Stripe MPP",
        "lookup_key": "top_gun_audit_v1",
        "description": "A2A brand visibility auditing."
    }
