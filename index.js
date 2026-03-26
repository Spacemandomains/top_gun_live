#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

/**
 * Top GUN GEO-Lens MCP Server
 * Built by Wilfred L. Lee Jr.
 * Implements the Stripe-MPP (Machine-Payable Protocol)
 */

const server = new Server(
  {
    name: "top-gun-audit",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const TOP_GUN_API_URL = process.env.TOP_GUN_API_URL || "https://top-gun-live.vercel.app";

// 1. List available tools to the LLM
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "audit_brand",
        description: "Perform a GEO-Lens visibility audit on a brand or entity. Requires a $1.50 fee via Stripe-MPP.",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "The brand name or topic to audit",
            },
            paymentIntent: {
              type: "string",
              description: "The Stripe Session ID or PaymentIntent ID (required after payment)",
            },
          },
          required: ["query"],
        },
      },
    ],
  };
});

// 2. Handle the tool execution and 402 Payment Gate
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== "audit_brand") {
    throw new Error("Tool not found");
  }

  const { query, paymentIntent } = request.params.arguments;
  const headers = { "Content-Type": "application/json" };
  
  if (paymentIntent) {
    headers["X-Payment-Intent"] = paymentIntent;
  }

  try {
    const response = await fetch(`${TOP_GUN_API_URL}/api/v1/audit?query=${encodeURIComponent(query)}`, {
      headers
    });

    const data = await response.json();

    // Handle the Machine-Payment Gate (HTTP 402)
    if (response.status === 402) {
      return {
        content: [{
          type: "text",
          text: `💰 PAYMENT REQUIRED: This audit costs $1.50 USD. 
Please pay at: ${data.payment_url}
Once completed, re-run this tool with your Session ID in the 'paymentIntent' field.`
        }],
        isError: true // Marked as error so the agent stops and asks the user
      };
    }

    return {
      content: [{
        type: "text",
        text: JSON.stringify(data, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error connecting to Top GUN API: ${error.message}`
      }],
      isError: true
    };
  }
});

// 3. Main entry point to start the server over Standard Input/Output
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Top GUN MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
