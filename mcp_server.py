from mcp.server.fastmcp import FastMCP
import httpx
import os

# Initialize FastMCP
mcp = FastMCP("Top GUN Audit")

TOP_GUN_API_URL = os.getenv("TOP_GUN_API_URL", "https://top-gun-live.vercel.app")

@mcp.tool()
async def audit_brand(query: str, payment_intent: str = None) -> str:
    """
    Perform a GEO-Lens visibility audit on a brand or entity.
    Requires a $1.50 fee via Stripe-MPP.
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

            # Handle the Machine-Payment Gate (402)
            if response.status_code == 402:
                return (
                    f"💰 PAYMENT REQUIRED: This audit costs $1.50 USD.\n"
                    f"Please pay here: {data.get('payment_url')}\n"
                    f"Once finished, provide the Session ID back to me."
                )

            return str(data)
            
        except Exception as e:
            return f"Error connecting to Top GUN API: {str(e)}"

if __name__ == "__main__":
    mcp.run()
