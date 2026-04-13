/**
 * Onelife Health AI Chatbot — Cloudflare Worker
 *
 * Handles chat requests from the storefront, calls Claude API
 * with Shopify product search capability.
 *
 * Deploy to Cloudflare Workers (free tier: 100K requests/day)
 *
 * Environment variables (set in Cloudflare dashboard):
 *   ANTHROPIC_API_KEY — your Claude API key
 *   SHOPIFY_STOREFRONT_TOKEN — Storefront API access token
 *   SHOPIFY_STORE — store domain (e.g. onelifehealth.myshopify.com)
 */

const SYSTEM_PROMPT = `You are the Onelife Health AI Assistant — a friendly, knowledgeable health supplement advisor for Onelife Health, South Africa's trusted health supermarket with 25+ years of expertise.

ABOUT ONELIFE HEALTH:
- South Africa's leading health supplement retailer since 1999
- 10,000+ products from 200+ trusted brands
- 3 stores in Gauteng: Centurion (117 Galway Ave, Hennopspark), Glen Village (Faerie Glen, Pretoria), Edenvale (Green Valley Shopping Centre)
- Free delivery on orders over R400 nationwide
- Qualified health consultants available for free 15-minute consultations
- Website: onelife.co.za

YOUR ROLE:
1. Help customers find the right supplements for their health goals
2. Answer questions about products, ingredients, dosage, and benefits
3. Check if products are in stock
4. Recommend products based on health conditions or goals
5. Provide general wellness guidance (with appropriate disclaimers)
6. Help with orders, delivery, and store information

RULES:
- Always be warm, professional, and South African-friendly
- Use "R" for Rand currency (e.g. R299.00)
- When recommending products, search the catalogue and provide specific product names with prices
- Never diagnose medical conditions — always recommend consulting a healthcare professional for serious concerns
- If asked about a product you're not sure about, search the catalogue first
- For order-specific queries (tracking, returns), direct them to orders@onelife.co.za or WhatsApp (071) 374 4910
- Mention free delivery over R400 when relevant
- Mention the free health consultation when someone seems unsure about what to take
- Keep responses concise but helpful — max 3-4 paragraphs
- Use simple language, avoid medical jargon unless explaining an ingredient

HEALTH GOAL CATEGORIES:
- Immunity & Cold Season
- Gut Health & Digestion
- Energy & Vitality
- Sleep & Relaxation
- Stress & Mood
- Joints & Mobility
- Weight Management
- Skin, Hair & Nails
- Heart & Cardiovascular
- Blood Sugar
- Brain & Cognitive
- Women's Health
- Men's Health
- Kids Health
- Sports Nutrition

DIETARY FILTERS:
Products are tagged: Vegan, Organic, Halaal, Gluten Free, Sugar Free, Keto, Dairy Free, Vegetarian, Cruelty Free, Non-GMO, SA Made

POPULAR BRANDS:
Solal, Bioharmony, Natroceutics, Sally-Ann Creed, Vivid Health, Metagenics, Viridian, NOW Foods, Solgar, A.Vogel, Willow, NeoGenesis Health, The Real Thing, Faithful to Nature, Go Natural, Soaring Free, Green Pharm, Kura, Terra Nova, Nordic Naturals

When a customer asks about a product or health goal, you will receive search results from the Shopify catalogue. Use these to make specific recommendations with product names and prices.`;

// Search Shopify Storefront API for products
async function searchProducts(query, env) {
  const gql = `{
    search(query: "${query.replace(/"/g, '\\"')}", first: 6, types: PRODUCT) {
      edges {
        node {
          ... on Product {
            title
            handle
            vendor
            productType
            description(truncateAt: 150)
            priceRange {
              minVariantPrice { amount currencyCode }
            }
            availableForSale
            tags
            featuredImage { url }
          }
        }
      }
    }
  }`;

  try {
    const resp = await fetch(`https://${env.SHOPIFY_STORE}/api/2025-01/graphql.json`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Shopify-Storefront-Access-Token': env.SHOPIFY_STOREFRONT_TOKEN,
      },
      body: JSON.stringify({ query: gql }),
    });

    const data = await resp.json();
    const products = data?.data?.search?.edges?.map(e => e.node) || [];

    return products.map(p => ({
      title: p.title,
      url: `https://onelife.co.za/products/${p.handle}`,
      vendor: p.vendor,
      price: `R ${parseFloat(p.priceRange?.minVariantPrice?.amount || 0).toFixed(2)}`,
      available: p.availableForSale,
      description: p.description,
      tags: p.tags?.slice(0, 8)?.join(', '),
    }));
  } catch (err) {
    console.error('Shopify search error:', err);
    return [];
  }
}

// Determine if we should search for products based on the message
function shouldSearch(message) {
  const searchTriggers = [
    'recommend', 'suggest', 'looking for', 'need', 'want', 'help with',
    'supplement', 'vitamin', 'product', 'buy', 'price', 'cost', 'stock',
    'available', 'best for', 'good for', 'what can', 'do you have',
    'immunity', 'sleep', 'energy', 'stress', 'weight', 'joint', 'gut',
    'skin', 'hair', 'brain', 'heart', 'collagen', 'probiotic', 'omega',
    'magnesium', 'vitamin d', 'vitamin c', 'zinc', 'iron', 'ashwagandha',
    'turmeric', 'melatonin', 'protein', 'bcaa', 'creatine', 'pre-workout',
    'vegan', 'gluten free', 'organic', 'halaal', 'keto', 'sugar free',
  ];
  const lower = message.toLowerCase();
  return searchTriggers.some(t => lower.includes(t));
}

// Extract search terms from the message
function extractSearchTerms(message) {
  // Remove common words, keep the health/product-related terms
  const stopWords = ['i', 'me', 'my', 'am', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but',
    'do', 'you', 'have', 'any', 'can', 'what', 'which', 'for', 'to', 'of', 'in', 'on',
    'looking', 'need', 'want', 'help', 'please', 'thanks', 'hi', 'hello', 'hey',
    'something', 'anything', 'recommend', 'suggest', 'good', 'best'];

  const words = message.toLowerCase().replace(/[?!.,]/g, '').split(/\s+/);
  const terms = words.filter(w => !stopWords.includes(w) && w.length > 2);
  return terms.slice(0, 4).join(' ');
}

// Call Claude API
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
      max_tokens: 600,
      system: SYSTEM_PROMPT + (systemAddendum ? '\n\n' + systemAddendum : ''),
      messages: messages,
    }),
  });

  const data = await resp.json();
  return data?.content?.[0]?.text || "I'm sorry, I'm having trouble right now. Please try again or contact us on WhatsApp at (071) 374 4910.";
}

// Main handler
export default {
  async fetch(request, env) {
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405, headers: corsHeaders });
    }

    try {
      const { messages } = await request.json();

      if (!messages || !messages.length) {
        return new Response(JSON.stringify({ error: 'No messages provided' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      const lastMessage = messages[messages.length - 1]?.content || '';

      // Search products if relevant
      let systemAddendum = '';
      if (shouldSearch(lastMessage)) {
        const searchTerms = extractSearchTerms(lastMessage);
        if (searchTerms) {
          const products = await searchProducts(searchTerms, env);
          if (products.length > 0) {
            systemAddendum = `PRODUCT SEARCH RESULTS for "${searchTerms}":\n` +
              products.map((p, i) =>
                `${i + 1}. ${p.title}\n   Brand: ${p.vendor} | Price: ${p.price} | ${p.available ? 'In Stock' : 'Out of Stock'}\n   Tags: ${p.tags}\n   URL: ${p.url}\n   ${p.description}`
              ).join('\n\n') +
              '\n\nUse these results to make specific recommendations. Include product names, prices, and links.';
          }
        }
      }

      // Keep conversation to last 10 messages for context
      const recentMessages = messages.slice(-10);

      const reply = await callClaude(recentMessages, systemAddendum, env);

      return new Response(JSON.stringify({ reply }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });

    } catch (err) {
      console.error('Error:', err);
      return new Response(JSON.stringify({
        reply: "I'm sorry, something went wrong. Please try again or reach us on WhatsApp at (071) 374 4910."
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }
  },
};
