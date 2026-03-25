import os
import httpx
import stripe
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# 1. Setup - Variables from Vercel Environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
PAYMENT_LINK = os.getenv("STRIPE_PAYMENT_LINK")
BASE_URL = "https://top-gun-live.vercel.app"

app = FastAPI(title="Top GUN GEO-Lens API")

# 2. Security - CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[BASE_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Serve Landing Page ---
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serves the index.html file from the root directory."""
    try:
        index_path = os.path.join(os.getcwd(), "index.html")
        with open(index_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Top GUN API Live</h1><p>Check GitHub root for index.html.</p>"

# --- GEO Audit Logic ---
async def perform_geo_audit(query: str):
    headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
    params = {"q": f"{query} brand mentions and llm citations", "count": 5}
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params=params)
        data = response.json()
        results = data.get("web", {}).get("results", [])
        score = min(len(results) * 15, 100)
        return {
            "query": query,
            "visibility_score": f"{score}%",
            "top_citations": [r.get("url") for r in results[:3]],
            "engine": "Top GUN v1.0",
            "status": "Verified Paid"
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
                "instructions": "Include PaymentIntent ID in 'X-Payment-Intent' header."
            }
        )
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status != "succeeded":
            raise HTTPException(status_code=403, detail="Payment incomplete.")
        return await perform_geo_audit(query)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Payment ID")

@app.get("/ai-agents.json")
async def discovery():
    return {
        "name": "Top GUN GEO-Lens",
        "api_url": f"{BASE_URL}/api/v1/audit",
        "protocol": "Stripe-MPP",
        "pricing": "1.50 USD",
        "lookup_key": "top_gun_audit_v1"
    }
