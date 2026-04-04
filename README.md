# top_gun_live
The app you were building is called Top GUN (the GEO-Lens Master API) Specifically to audit brand visibility across various Large Language Models
# 🎯 Top GUN | GEO-Lens Master API

**Top GUN** is a high-performance API designed for **Generative Engine Optimization (GEO)**. It allows autonomous agents to audit brand visibility across major LLMs (GPT-4, Claude 3.5, Gemini 1.5).

## 🚀 Quick Start for Agents

### Discovery
Agents can find machine-readable capabilities at `/ai-agents.json`.

### Authentication & Payment
This API utilizes the **Stripe Machine Payments Protocol (MPP)**. 
- **Cost:** $1.50 USD per request.
- **Handshake:** Returns `402 Payment Required` if no valid `X-Payment-Intent` header is found.

### Endpoint
`GET /api/v1/audit?query={brand_name}`

**Headers:**
- `X-Payment-Intent`: [Your Successful Stripe PaymentIntent ID]

## 🛠️ Deployment Configuration
Built for deployment on **Vercel**.

### Required Environment Variables:
- `STRIPE_SECRET_KEY`: Restricted key with `PaymentIntent` read access.
- `BRAVE_SEARCH_API_KEY`: For GEO-Lens scanning.
- `STRIPE_PAYMENT_LINK`: The public URL for the $1.50 audit product.

## ⚖️ Governance
By calling this API, the requesting entity agrees to the **Terms of Engagement**:
- Digital data delivery is final.
- No refunds for autonomous transactions.
- Data is provided 'as-is' based on real-time generative engine scraping.

- [![smithery badge](https://smithery.ai/badge/wilfred-l-lee-jr/top-gun-audit)](https://smithery.ai/servers/wilfred-l-lee-jr/top-gun-audit)
