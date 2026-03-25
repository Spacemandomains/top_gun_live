import os
import httpx
import stripe
import json
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# 1. Setup - Identity: Wilfred L. Lee Jr.
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
PAYMENT_LINK = os.getenv("STRIPE_PAYMENT_LINK")
BASE_URL = "https://top-gun-live.vercel.app"

app = FastAPI(title="Top GUN GEO-Lens API by Wilfred L. Lee Jr.")

# 2. Security - CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[BASE_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper: File Loader ---
def load_root_file(filename: str):
    """Helper to read files from the root directory."""
    try:
        path = os.path.join(os.getcwd(), filename)
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None

# --- Static & Discovery Routes ---

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serves the main Top GUN terminal landing page."""
    content = load_root_file("index.html")
    if content:
        return content
    return "<h1>Top GUN Live</h1><p>Index file missing in root.</p>"

@app.get("/privacy", response_class=HTMLResponse)
async def serve_privacy():
    """Serves the Privacy Policy for Wilfred L. Lee Jr."""
    content = load_root_file("privacy.html")
    if content:
        return content
    return "<h1>Privacy Policy</h1><p>Policy file missing in root.</p>"

@app.get("/openapi.json")
async def get_openapi():
    """Serves the OpenAPI spec for AI Agent integration."""
    try:
        path = os.path.join(os.getcwd(), "openapi.json")
        with open(path, "r") as f:
            return JSONResponse(content=json.load(f))
    except Exception:
        return JSONResponse(status_code=404, content={"error": "Spec not found."})

@app.get("/ai-agents.json")
async def discovery():
    """Standardized Agent Discovery Manifest."""
    return {
        "name": "Top GUN GEO-Lens by Wilfred L. Lee Jr.",
        "api_url": f"{BASE_URL}/api/v1/audit",
        "protocol": "Stripe-MPP",
        "pricing": "1.50 USD",
        "lookup_key": "top_gun_audit_v1"
    }

# --- Core Logic: GEO Audit ---

async def perform_geo_audit(query: str):
    """The engine: Scanning the generative landscape."""
    headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
    params = {"q": f"{query} brand mentions and llm citations", "count": 5}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get("web", {}).get("results", [])
            
            score = min(len(results) * 15, 100) 
            
            return {
                "query": query,
                "visibility_score": f"{score}%",
                "llm_index_status": "High" if score > 70 else "Low",
                "top_citations": [r.get("url") for r in results[:3]],
                "engine": "Top GUN v1.0",
                "provider": "Wilfred L. Lee Jr."
            }
        except Exception as e:
            return {"error": f"Upstream data failure: {str(e)}"}

@app.get("/api/v1/audit")
async def geo_audit(query: str, request: Request):
    """Paid endpoint for Agentic Clients."""
    payment_intent_id = request.headers.get("X-Payment-Intent")

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
            raise HTTPException(status_code=403, detail="Payment not cleared.")
        
        return await perform_geo_audit(query)

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Payment ID")
