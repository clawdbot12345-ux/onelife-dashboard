# Onelife Health AI Chatbot

## Architecture
- **Frontend**: Chat widget snippet on Shopify theme
- **Backend**: Cloudflare Worker (free tier: 100K requests/day)
- **AI**: Claude Sonnet 4.6 (fast, smart, cost-effective for chat)
- **Product Search**: Shopify Storefront API (real-time product lookup)

## Deployment

### Step 1: Create Shopify Storefront API Token
1. Shopify Admin → Settings → Apps and sales channels → Develop apps
2. Create app "Onelife Chatbot"
3. Configure Storefront API scopes: `unauthenticated_read_product_listings`
4. Install and copy the Storefront access token

### Step 2: Deploy Cloudflare Worker
1. Sign up at https://workers.cloudflare.com (free)
2. Create a new Worker
3. Paste contents of `worker.js`
4. Add environment variables:
   - `ANTHROPIC_API_KEY` = your Claude API key
   - `SHOPIFY_STOREFRONT_TOKEN` = from Step 1
   - `SHOPIFY_STORE` = onelifehealth.myshopify.com
5. Deploy → copy the Worker URL (e.g. https://onelife-chat.yourname.workers.dev)

### Step 3: Add to Shopify Theme
1. Upload `chat-widget.liquid` as `snippets/onelife-chatbot.liquid`
2. Add `{%- render 'onelife-chatbot' -%}` to `layout/theme.liquid` before `</body>`
3. Set the Worker URL: Shopify Admin → Settings → Custom data → Shop metafield
   - Namespace: onelife
   - Key: chatbot_url
   - Value: your Cloudflare Worker URL

## Cost Estimate
- Cloudflare Workers: FREE (100K requests/day)
- Claude Sonnet 4.6: ~$0.003 per chat message (~R0.06)
- At 100 chats/day with 5 messages each: ~$1.50/day (~R28/day)
