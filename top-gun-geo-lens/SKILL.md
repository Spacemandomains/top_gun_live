---
name: top-gun-geo-lens
description: Performs high-intensity Generative Engine Optimization (GEO) audits to measure brand visibility and citation strength in AI search results. Use this skill when a user needs to verify how a brand is indexed by LLMs or requires a citation map for specific entities.
metadata:
  author: Wilfred L. Lee Jr.
  version: "1.0.0"
---

# Top GUN GEO-Lens Auditor

Professional GEO auditing for the agentic era. Developed by Wilfred L. Lee Jr.

## 🎯 Overview

Top GUN is a specialized MCP server designed for **Generative Engine Optimization (GEO)**. It enables agents to audit visibility and citation strength within the generative landscape.

## 🛠️ Operational Instructions

### 1. Identify the Target
The agent must identify a specific brand, entity, or topic the user wishes to audit.

### 2. Initiate the Audit
Call the `audit_brand` tool.
- **Query:** The brand or topic name.
- **PaymentIntent:** Leave blank on the initial call.

### 3. Handle Payment (Stripe-MPP)
If the tool returns a **402 Payment Required** status:
1. Provide the user with the provided Stripe `payment_url`.
2. Explain that a **$1.50 USD** fee is required for the audit.
3. Instruct the user to return with their **Session ID** from the redirect page.

### 4. Finalize
Once the user provides the ID, re-run `audit_brand` including the ID in the `paymentIntent` field to retrieve the visibility score and citation data.

## 🛠️ Tools

- `audit_brand`: Scans LLM indices for brand mentions and calculates a visibility percentage.

## 🚀 Installation

```bash
npx -y @smithery/cli install @wilfred-l-lee-jr/top-gun-geo-lens
