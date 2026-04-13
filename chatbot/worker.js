/**
 * Onelife Health AI Chatbot — Cloudflare Worker
 *
 * Deploy to Cloudflare Workers (free tier: 100K requests/day)
 *
 * Environment variables (set in Cloudflare dashboard):
 *   ANTHROPIC_API_KEY — Claude API key
 *   SHOPIFY_CLIENT_ID — Shopify app client ID
 *   SHOPIFY_CLIENT_SECRET — Shopify app client secret
 */

const STORE = 'onelifehealth.myshopify.com';

const SYSTEM_PROMPT = `You are the Onelife Health AI Assistant — a friendly, knowledgeable health supplement advisor for Onelife Health, South Africa's trusted health supermarket with 25+ years of expertise.

ABOUT ONELIFE HEALTH:
- South Africa's leading health supplement retailer since 1999
- 10,000+ products from 200+ trusted brands
- 3 stores in Gauteng: Centurion (117 Galway Ave, Hennopspark), Glen Village (Faerie Glen, Pretoria), Edenvale (Green Valley Shopping Centre)
- Free delivery on orders over R400 nationwide
- Qualified health consultants available for free 15-minute consultations
- Website: onelife.co.za | WhatsApp: (071) 374 4910 | Email: orders@onelife.co.za

YOUR ROLE:
1. Help customers find the right supplements for their health goals
2. Answer questions about products, ingredients, dosage, and benefits
3. Check product availability and prices
4. Recommend products based on health conditions or goals
5. Provide general wellness guidance (with appropriate disclaimers)

RULES:
- Be warm, professional, and South African-friendly
- Use "R" for Rand (e.g. R299.00)
- When recommending products, use the search results provided to give specific names, prices, and links
- ALWAYS include the product URL as a clickable link when mentioning a product
- Never diagnose — recommend consulting a healthcare professional for serious concerns
- Mention free delivery over R400 when relevant
- Mention free health consultations when someone seems unsure
- Keep responses concise — max 2-3 short paragraphs
- Format product recommendations as a clear list

DIETARY FILTERS: Vegan, Organic, Halaal, Gluten Free, Sugar Free, Keto, Dairy Free, Vegetarian, Cruelty Free, Non-GMO, SA Made

POPULAR BRANDS: Solal, Bioharmony, Natroceutics, Sally-Ann Creed, Vivid Health, Metagenics, Viridian, NOW Foods, Solgar, A.Vogel, Willow, NeoGenesis Health, The Real Thing`;

// Get Shopify Admin API token
async function getShopifyToken(env) {
  const resp = await fetch(`https://${STORE}/admin/oauth/access_token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `grant_type=client_credentials&client_id=${env.SHOPIFY_CLIENT_ID}&client_secret=${env.SHOPIFY_CLIENT_SECRET}`,
  });
  const data = await resp.json();
  return data.access_token;
}

// Search products via Admin REST API
async function searchProducts(query, env) {
  try {
    const token = await getShopifyToken(env);
    const url = `https://${STORE}/admin/api/2025-01/products.json?limit=6&status=active&title=${encodeURIComponent(query)}&fields=id,title,handle,vendor,tags,body_html,variants`;

    const resp = await fetch(url, {
      headers: { 'X-Shopify-Access-Token': token, 'Accept': 'application/json' },
    });
    const data = await resp.json();
    let products = data.products || [];

    // If title search returns few results, try a broader search
    if (products.length < 3) {
      const url2 = `https://${STORE}/admin/api/2025-01/products.json?limit=6&status=active&fields=id,title,handle,vendor,tags,body_html,variants`;
      const resp2 = await fetch(url2, {
        headers: { 'X-Shopify-Access-Token': token, 'Accept': 'application/json' },
      });
      const data2 = await resp2.json();
      const all = data2.products || [];
      // Filter by query in title, vendor, or tags
      const q = query.toLowerCase();
      const filtered = all.filter(p =>
        p.title.toLowerCase().includes(q) ||
        (p.vendor || '').toLowerCase().includes(q) ||
        (p.tags || '').toLowerCase().includes(q) ||
        (p.body_html || '').toLowerCase().includes(q)
      );
      products = [...products, ...filtered].slice(0, 6);
    }

    // Deduplicate
    const seen = new Set();
    products = products.filter(p => {
      if (seen.has(p.id)) return false;
      seen.add(p.id);
      return true;
    });

    return products.map(p => {
      const variant = (p.variants || [{}])[0];
      const price = variant.price || '0.00';
      const available = variant.inventory_quantity > 0 || variant.inventory_management === null;
      const desc = (p.body_html || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120);
      const dietTags = (p.tags || '').split(',').map(t => t.trim()).filter(t =>
        ['vegan','organic','halaal','gluten-free','sugar-free','keto','dairy-free','vegetarian','cruelty-free','non-gmo','proudly-south-african'].includes(t.toLowerCase())
      );
      return {
        title: p.title,
        url: `https://onelife.co.za/products/${p.handle}`,
        vendor: p.vendor,
        price: `R ${parseFloat(price).toFixed(2)}`,
        available: available,
        description: desc,
        dietary: dietTags.join(', '),
      };
    });
  } catch (err) {
    console.error('Shopify search error:', err);
    return [];
  }
}

// Should we search products?
function shouldSearch(message) {
  const triggers = [
    'recommend', 'suggest', 'looking for', 'need', 'want', 'help with',
    'supplement', 'vitamin', 'product', 'buy', 'price', 'cost', 'stock',
    'available', 'best for', 'good for', 'what can', 'do you have',
    'immunity', 'immune', 'sleep', 'energy', 'stress', 'weight', 'joint',
    'gut', 'skin', 'hair', 'brain', 'heart', 'collagen', 'probiotic',
    'omega', 'magnesium', 'vitamin d', 'vitamin c', 'zinc', 'iron',
    'ashwagandha', 'turmeric', 'melatonin', 'protein', 'bcaa', 'creatine',
    'vegan', 'gluten free', 'organic', 'halaal', 'keto', 'sugar free',
    'natroceutics', 'solal', 'vivid', 'sally-ann', 'metagenics', 'vogel',
  ];
  const lower = message.toLowerCase();
  return triggers.some(t => lower.includes(t));
}

function extractSearchTerms(message) {
  const stop = ['i','me','my','am','is','are','the','a','an','and','or','but',
    'do','you','have','any','can','what','which','for','to','of','in','on',
    'looking','need','want','help','please','thanks','hi','hello','hey',
    'something','anything','recommend','suggest','good','best','take'];
  const words = message.toLowerCase().replace(/[?!.,]/g, '').split(/\s+/);
  return words.filter(w => !stop.includes(w) && w.length > 2).slice(0, 3).join(' ');
}

// Call Claude
async function callClaude(messages, systemAddendum, env) {
  const resp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-6',
      max_tokens: 500,
      system: SYSTEM_PROMPT + (systemAddendum ? '\n\n' + systemAddendum : ''),
      messages: messages,
    }),
  });
  const data = await resp.json();
  return data?.content?.[0]?.text || "I'm sorry, I'm having trouble right now. Please WhatsApp us at (071) 374 4910.";
}

export default {
  async fetch(request, env) {
    const cors = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') return new Response(null, { headers: cors });
    if (request.method !== 'POST') return new Response('Method not allowed', { status: 405, headers: cors });

    try {
      const { messages } = await request.json();
      if (!messages?.length) return new Response(JSON.stringify({ error: 'No messages' }), { status: 400, headers: { ...cors, 'Content-Type': 'application/json' } });

      const lastMsg = messages[messages.length - 1]?.content || '';
      let addendum = '';

      if (shouldSearch(lastMsg)) {
        const terms = extractSearchTerms(lastMsg);
        if (terms) {
          const products = await searchProducts(terms, env);
          if (products.length) {
            addendum = `PRODUCT SEARCH RESULTS for "${terms}":\n` +
              products.map((p, i) =>
                `${i+1}. ${p.title}\n   Brand: ${p.vendor} | Price: ${p.price} | ${p.available ? 'In Stock' : 'Out of Stock'}\n   Dietary: ${p.dietary || 'N/A'}\n   URL: ${p.url}\n   ${p.description}`
              ).join('\n\n') +
              '\n\nUse these results to recommend specific products with names, prices, and URLs.';
          }
        }
      }

      const reply = await callClaude(messages.slice(-10), addendum, env);
      return new Response(JSON.stringify({ reply }), { headers: { ...cors, 'Content-Type': 'application/json' } });
    } catch (err) {
      return new Response(JSON.stringify({ reply: "Something went wrong. Please WhatsApp us at (071) 374 4910." }), {
        status: 500, headers: { ...cors, 'Content-Type': 'application/json' }
      });
    }
  },
};
