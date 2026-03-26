import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "Top GUN GEO-Lens",
  version: "1.0.0",
});

// The tool that agents will see and call
server.tool(
  "audit_brand",
  "Perform a GEO-Lens visibility audit on a brand or entity",
  {
    query: z.string().describe("The brand or topic to audit"),
    paymentIntent: z.string().optional().describe("The Stripe PaymentIntent or Session ID"),
  },
  async ({ query, paymentIntent }) => {
    const baseUrl = process.env.TOP_GUN_API_URL || "https://top-gun-live.vercel.app";
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    
    if (paymentIntent) {
      headers["X-Payment-Intent"] = paymentIntent;
    }

    try {
      const response = await fetch(`${baseUrl}/api/v1/audit?query=${encodeURIComponent(query)}`, {
        headers
      });

      const data = await response.json();

      // Handle the Machine-Payment Gate (402)
      if (response.status === 402) {
        return {
          content: [{ 
            type: "text", 
            text: `PAYMENT REQUIRED: This audit requires a $1.50 fee. Please pay here: ${data.payment_url}. Once finished, provide the Session ID back to me.` 
          }]
        };
      }

      return {
        content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: `Error connecting to Top GUN API: ${error}` }]
      };
    }
  }
);

// Start the server using Stdio transport
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
