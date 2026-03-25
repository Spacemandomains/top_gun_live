import os
import httpx
import stripe
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# 1. Setup - Variables must match Vercel Environment Keys exactly
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
PAYMENT_LINK = os.getenv("STRIPE_PAYMENT_LINK")
BASE_URL = "https://top-gun-live.vercel.app"

app = FastAPI(title="Top GUN GEO-Lens API")

# 2. Security - CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[BASE_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def perform_geo_audit(query: str):
    """The 'Secret Sauce': Scanning the generative landscape via Brave Search."""
    if not BRAVE_API_KEY:
        return {"error": "Brave API Key not configured on server."}

    headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
    params = {"q": f"{query} brand mentions and llm citations", "count": 5}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get("web", {}).get("results", [])
            
            # Top GUN Scoring Heuristic
            score = min(len(results) * 15, 100) 
            
            return {
                "query": query,
                "visibility_score": score,
                "llm_index_status": "High" if score > 70 else "Low",
                "top_citations": [r.get("url") for r in results[:3]],
                "engine": "Top GUN v1.0"
            }
        except Exception as e:
            return {"error": f"Upstream data failure: {str(e)}"}

@app.get("/api/v1/audit")
async def geo_audit(query: str, request: Request):
    """Main billable endpoint for Agentic Clients."""
    payment_intent_id = request.headers.get("X-Payment-Intent")

    # The 402 Handshake
    if not payment_intent_id:
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={
                "error": "Payment Required",
                "amount": 1.50,
                "payment_url": PAYMENT_LINK,
                "instructions": "Pay via Stripe and include the PaymentIntent ID in the 'X-Payment-Intent' header."
            }
        )

    try:
        # Verify Payment with Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status != "succeeded":
            raise HTTPException(status_code=403, detail="Payment exists but has not succeeded.")
        
        # Execute Audit
        return await perform_geo_audit(query)

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Payment ID or Authentication Error")

@app.get("/ai-agents.json")
async def discovery():
    """Agentic discovery file."""
    return {
        "name": "Top GUN GEO-Lens",
        "api_url": f"{BASE_URL}/api/v1/audit",
        "protocol": "Stripe-MPP",
        "pricing": "1.50 USD",
        "lookup_key": "top_gun_audit_v1"
    }
