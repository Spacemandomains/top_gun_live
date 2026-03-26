import sys
import os
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware

# 1. Define the 'No Buffer' Middleware
# This tells Render/Nginx to stream data immediately, fixing 502/504 errors
class NoBufferMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Force the proxy to pass the stream through without waiting
        response.headers["X-Accel-Buffering"] = "no"
        response.headers["Cache-Control"] = "no-cache, no-transform"
        response.headers["Connection"] = "keep-alive"
        return response

# 2. Initialize FastMCP with specialized settings for Smithery/Render
mcp = FastMCP(
    "Top GUN GEO-Lens",
    host="0.0.0.0", 
    port=int(os.environ.get("PORT", 10000)),
    stateless_http=True  # Enables standard HTTP discovery for Smithery
)

# 3. Apply the Middleware to the MCP server
mcp.add_middleware(NoBufferMiddleware)

# Your live Vercel API endpoint
TOP_GUN_API_URL = os.getenv("TOP_GUN_API_URL", "https://top-gun-live.vercel.app")

@mcp.tool()
async def audit_brand(query: str, payment_intent: str = None) -> str:
    """
    Perform a high-intensity GEO-Lens visibility audit on a brand or entity.
    This tool requires a $1.50 USD fee via the Stripe-MPP gate.
    """
    headers = {"Content-Type": "application/json"}
    
    # Pass the Session ID to the Vercel API if provided by the user
    if payment_intent:
        headers["X-Payment-Intent"] = payment_intent

    async with httpx.AsyncClient() as client:
        try:
            # Call your Vercel Python API
            response = await client.get(
                f"{TOP_GUN_API_URL}/api/v1/audit",
                params={"query": query},
                headers=headers,
                timeout=30.0
            )
            
            data = response.json()

            # Handle the Machine-Payment Gate (402 Payment Required)
            if response.status_code == 402:
                payment_url = data.get("payment_url", "https://buy.stripe.com/your_link")
                return (
                    f"💰 PAYMENT REQUIRED: This audit costs $1.50 USD.\n"
                    f"Please pay at: {payment_url}\n"
                    f"Once payment is complete, re-run this tool and include your Session ID in the 'payment_intent' field."
                )

            # Return the successful audit data
            return str(data)
            
        except Exception as e:
            return f"Error connecting to Top GUN API: {str(e)}"

if __name__ == "__main__":
    # Check if we are running on Render (using the --remote flag)
    if "--remote" in sys.argv:
        print(f"🚀 Top GUN starting in REMOTE mode on port {os.environ.get('PORT', 10000)}")
        # Use SSE transport for the remote server
        mcp.run(transport="sse")
    else:
        # Default mode for local use (stdio)
        mcp.run()
