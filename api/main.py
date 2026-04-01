import os
import httpx
import stripe
import json
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastapi import FastApiServerTransport
from mcp.server import Server
from mcp.types import Tool, TextContent

# 1. Setup - Identity: Wilfred L. Lee Jr.
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
PAYMENT_LINK = os.getenv("STRIPE_PAYMENT_LINK")
BASE_URL = "https://top-gun-live.vercel.app"

# Disable auto-generated OpenAPI to use our manual openapi.json
app = FastAPI(
    title="Top GUN GEO-Lens API",
    openapi_url=None,
    docs_url=None,
    redoc_url=None
)

# 2. Security - Updated CORS for xpay.sh and AI Agents
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows xpay.sh and agent platforms to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MCP Server Infrastructure ---
mcp_server = Server("top-gun-geo-lens")

@mcp_server.list_tools()
async def handle_list_tools():
    """Tells the AI Agent what capabilities this server has."""
    return [
        Tool(
            name="geo_audit",
            description="Perform a GEO audit to see brand mentions and LLM citations via Brave Search.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The brand, keyword, or company to audit"}
                },
                "required": ["query"]
            }
        )
    ]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Executes the tool when the AI Agent requests it."""
    if name == "geo_audit":
        query = arguments.get("query")
        if not query:
            return [TextContent(type="text", text="Error: No query provided.")]
        
        # Calls your core logic function defined below
        results = await perform_geo_audit(query)
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
    
    raise ValueError(f"Tool not found: {name}")

# Initialize the Transport (the bridge between MCP and FastAPI)
mcp_transport = FastApiServerTransport(mcp_server, url_prefix="/mcp")

# --- MCP Connection Endpoints ---
@app.get("/mcp/sse")
async def sse_endpoint(request: Request):
    """The entry point for xpay.sh to start an SSE connection."""
    async with mcp_transport.connect_sse(request.scope, request.receive, request._send) as sse:
        await sse.handle_sse_event()

@app.post("/mcp/messages")
async def messages_endpoint(request: Request):
    """Where the JSON-RPC messages are sent back and forth."""
    await mcp_transport.handle_post_message(request.scope, request.receive, request._send)

# --- Helper: File Loader ---
def load_root_file(filename: str):
    try:
        path = os.path.join(os.getcwd(), filename)
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None

# --- Static & Discovery Routes ---
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    content = load_root_file("index.html")
    return content if content else "<h1>Top GUN Live</h1>"

@app.get("/openapi.json")
async def get_manual_spec():
    try:
        path = os.path.join(os.getcwd(), "openapi.json")
        with open(path, "r") as f:
            return JSONResponse(content=json.load(f))
    except Exception:
        return JSONResponse(status_code=404, content={"error": "openapi.json not found."})

# --- Core Logic: GEO Audit ---
async def perform_geo_audit(query: str):
    """The engine that queries Brave Search and scores visibility."""
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
        except Exception:
            return {"error": "Upstream data failure from Brave Search."}

# Original REST endpoint (kept for backward compatibility)
@app.get("/api/v1/audit")
async def geo_audit_rest(query: str, request: Request):
    payment_intent_id = request.headers.get("X-Payment-Intent")
    if not payment_intent_id:
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={"error": "Payment Required", "amount": 1.50, "payment_url": PAYMENT_LINK}
        )
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status != "succeeded":
            raise HTTPException(status_code=403, detail="Payment not cleared.")
        return await perform_geo_audit(query)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Payment ID")
