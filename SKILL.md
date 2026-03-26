---
name: Top GUN GEO-Lens Auditor
description: Professional GEO (Generative Engine Optimization) auditing tool for AI agents. Developed by Wilfred L. Lee Jr.
---

# Top GUN GEO-Lens Auditor

**Developer:** Wilfred L. Lee Jr.  
**Protocol:** Stripe-MPP (Machine-Payable Protocol)

## 🎯 Overview
Top GUN is a specialized Model Context Protocol (MCP) server designed for **Generative Engine Optimization (GEO)** auditing. It allows AI agents to measure brand visibility, citation strength, and indexing status within the generative search landscape.

## 🛠️ Tools

### `audit_brand`
Performs a high-intensity GEO-Lens scan on a specific brand, entity, or topic.
- **Parameters:**
  - `query` (string, required): The brand or topic to audit.
  - `paymentIntent` (string, optional): The Stripe PaymentIntent or Session ID for authorization.

## 💳 Payment & Pricing
This is a **metered agentic service**. Each audit requires a flat fee of **$1.50 USD**.

1. **Initiate:** Run the `audit_brand` tool with your query.
2. **Authorize:** If no payment ID is provided, the tool returns a Stripe payment URL.
3. **Execute:** Complete the payment, retrieve your **Session ID** from the redirect page, and re-run the tool with the ID included.

## 🚀 Installation

Install via the Smithery CLI:

```bash
npx -y @smithery/cli install @wilfred-l-lee-jr/top-gun-geo-lens
