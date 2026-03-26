import sys
import os
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP with standard production settings
# stateless_http=True is the key to letting Smithery scan you without 405/502 errors
mcp = FastMCP(
    "Top GUN GEO-Lens",
    host="0.0.0.0", 
    port=int(os.environ.get("PORT", 10000)),
    stateless_http=True
)

# Your live Vercel API endpoint
TOP_GUN_API_URL = os.getenv("TOP_GUN_API_URL", "https://top-gun-live.vercel.app")

@mcp.tool()
async def audit_brand(query: str, payment_intent: str = None) -> str:
    """
    Perform a high-intensity GEO-Lens visibility audit on a brand or entity.
    This tool requires a $1.50 USD fee via the Stripe-MPP gate.
    """
    headers = {"Content-Type": "application/json"}
    
    if payment_intent:
        headers["X-Payment-Intent"] = payment_intent

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{TOP_GUN_API_URL}/api/v1/audit",
                params={"query": query},
                headers=headers,
                timeout=30.0
            )
            
            data = response.json()

            if response.status_code == 402:
                payment_url = data.get("payment_url", "https://buy.stripe.com/your_link")
                return (
                    f"💰 PAYMENT REQUIRED: This audit costs $1.50 USD.\n"
                    f"Please pay at: {payment_url}\n"
                    f"Once payment is complete, re-run this tool and include your Session ID in the 'payment_intent' field."
                )

            return str(data)
            
        except Exception as e:
            return f"Error connecting to Top GUN API: {str(e)}"

if __name__ == "__main__":
    if "--remote" in sys.argv:
        # Standard SSE run command for Render
        mcp.run(transport="sse")
    else:
        mcp.run()
