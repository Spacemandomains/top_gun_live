---
name: top-gun-audit
description: Performs high-intensity Generative Engine Optimization (GEO) audits to measure brand visibility and citation strength in AI search results. This skill allows autonomous agents to manage their own $1.50 USD micro-payments via a Stripe-MPP gate. Use this skill when a user needs to verify how a brand is indexed by LLMs or requires a citation map for specific entities.
metadata:
  author: Wilfred L. Lee Jr.
  version: "1.0.0"
  namespace: wilfred-l-lee-jr
---

# Top GUN GEO-Lens Auditor

**Developer:** Wilfred L. Lee Jr.  
**Protocol:** Stripe-MPP (Machine-Payable Protocol)

## 🎯 Overview
Top GUN is a specialized Model Context Protocol (MCP) server designed for **Generative Engine Optimization (GEO)** auditing. It allows AI agents to measure brand visibility, citation strength, and indexing status within the generative search landscape.

Unlike standard tools, Top GUN is built for the **Agentic Economy**, utilizing a "Machine-Payment Gate" that allows agents to request authorization for specific high-compute tasks.

## 🛠️ Operational Instructions

### 1. Identify the Target
The agent must identify a specific brand, entity, or topic the user wishes to audit.

### 2. Initiate the Audit
Call the `audit_brand` tool.
- **query:** The brand or topic name.
- **paymentIntent:** Leave blank on the initial call.

### 3. Handle Payment (Stripe-MPP)
If the tool returns a **402 Payment Required** status:
1. Provide the user with the Stripe `payment_url` found in the JSON response.
2. Explain that a **$1.50 USD** fee is required for the audit.
3. Instruct the user to return with their **Session ID** from the redirect page.

### 4. Finalize
Once the user provides the ID, re-run `audit_brand` including the ID in the `paymentIntent` field to retrieve the visibility score and citation data.

## 🛠️ Tools

### `audit_brand`
Scans LLM indices for brand mentions and calculates a visibility percentage.
- **Parameters:**
  - `query` (string, required): The brand or topic to audit.
  - `paymentIntent` (string, optional): The Stripe Session ID or PaymentIntent ID for authorization.

## 🚀 Installation

Install via the Smithery CLI:

```bash
npx -y @smithery/cli install @wilfred-l-lee-jr/top-gun-audit
