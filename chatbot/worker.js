/**
 * Onelife Health AI Chatbot — Cloudflare Worker
 * Uses Claude Sonnet 4.6 + Shopify GraphQL for real product search
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
- When you receive PRODUCT SEARCH RESULTS, you MUST use them to give specific product names, prices, and links
- ALWAYS include the product URL when mentioning a product
- Do NOT say you cannot check prices or stock — the search results have this info
- Do NOT output JSON, function calls, or code — only natural conversational text
- Mention free delivery over R400 when relevant
- Mention free health consultations when someone seems unsure
- Keep responses concise — max 2-3 short paragraphs
- Format product recommendations as a numbered list with name, price, and link
- For general wellness (immunity, energy, sleep, gut health) from healthy adults — recommend products freely

SAFETY RULES (CRITICAL — NEVER BREAK THESE):
- NEVER diagnose any medical condition
- NEVER recommend specific supplements for cancer, heart disease, diabetes, epilepsy, kidney disease, liver disease, or any serious medical condition. Say: "For this condition, please consult your doctor before taking any supplements. Our health consultants can also help — book a free consultation or WhatsApp us at (071) 374 4910."
- NEVER advise on drug interactions. If someone mentions medication, say: "Please check with your doctor or pharmacist before combining supplements with medication."
- NEVER recommend supplements for pregnant or breastfeeding women. Say: "Please consult your doctor or midwife for pregnancy-safe supplements."
- NEVER recommend dosages for children. Say: "For children, please consult your paediatrician for age-appropriate recommendations."
- NEVER encourage stopping prescribed medication. Say: "Please do not stop prescribed medication without your doctor's guidance. Supplements can complement treatment but should not replace it."
- NEVER provide specific dosage advice. Say: "Follow the dosage on the product label, or consult a healthcare professional."
- When in doubt, err on the side of caution and recommend professional consultation

DIETARY FILTERS: Vegan, Organic, Halaal, Gluten Free, Sugar Free, Keto, Dairy Free, Vegetarian, Cruelty Free, Non-GMO, SA Made

POPULAR BRANDS: Solal, Bioharmony, Natroceutics, Sally-Ann Creed, Vivid Health, Metagenics, Viridian, NOW Foods, Solgar, A.Vogel, Willow, NeoGenesis Health, The Real Thing`;

async function getShopifyToken(env) {
  const resp = await fetch('https://' + STORE + '/admin/oauth/access_token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'grant_type=client_credentials&client_id=' + env.SHOPIFY_CLIENT_ID + '&client_secret=' + env.SHOPIFY_CLIENT_SECRET,
  });
  const data = await resp.json();
  return data.access_token;
}

async function searchProducts(query, env) {
  try {
    const token = await getShopifyToken(env);
    const gql = JSON.stringify({
      query: '{ products(first: 6, query: "status:active ' + query.replace(/"/g, '') + '") { edges { node { title handle vendor tags totalInventory description(truncateAt: 120) priceRangeV2 { minVariantPrice { amount } } } } } }'
    });

    const resp = await fetch('https://' + STORE + '/admin/api/2025-01/graphql.json', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Shopify-Access-Token': token },
      body: gql,
    });

    const data = await resp.json();
    const products = (data.data && data.data.products && data.data.products.edges) ? data.data.products.edges.map(function(e) { return e.node; }) : [];

    return products.map(function(p) {
      var price = (p.priceRangeV2 && p.priceRangeV2.minVariantPrice) ? p.priceRangeV2.minVariantPrice.amount : '0.00';
      var inStock = (p.totalInventory || 0) > 0;
      return {
        title: p.title,
        url: 'https://onelife.co.za/products/' + p.handle,
        vendor: p.vendor,
        price: 'R ' + parseFloat(price).toFixed(2),
        available: inStock ? 'In Stock' : 'Out of Stock',
        description: p.description || '',
        tags: (p.tags || []).slice(0, 6).join(', '),
      };
    });
  } catch (err) {
    console.error('Search error:', err);
    return [];
  }
}

function shouldSearch(message) {
  var triggers = [
    'recommend','suggest','looking for','need','want','help with',
    'supplement','vitamin','product','buy','price','cost','stock',
    'available','best for','good for','what can','do you have',
    'immunity','immune','sleep','energy','stress','weight','joint',
    'gut','skin','hair','brain','heart','collagen','probiotic',
    'omega','magnesium','vitamin d','vitamin c','zinc','iron',
    'ashwagandha','turmeric','melatonin','protein','bcaa','creatine',
    'vegan','gluten free','organic','halaal','keto','sugar free',
    'natroceutics','solal','vivid','sally-ann','metagenics','vogel',
  ];
  var lower = message.toLowerCase();
  for (var i = 0; i < triggers.length; i++) {
    if (lower.indexOf(triggers[i]) !== -1) return true;
  }
  return false;
}

function extractSearchTerms(message) {
  var stop = ['i','me','my','am','is','are','the','a','an','and','or','but',
    'do','you','have','any','can','what','which','for','to','of','in','on',
    'looking','need','want','help','please','thanks','hi','hello','hey',
    'something','anything','recommend','suggest','good','best','take','some'];
  var words = message.toLowerCase().replace(/[?!.,]/g, '').split(/\s+/);
  var terms = [];
  for (var i = 0; i < words.length; i++) {
    if (stop.indexOf(words[i]) === -1 && words[i].length > 2) terms.push(words[i]);
  }
  return terms.slice(0, 4).join(' ');
}

async function callClaude(messages, systemAddendum, env) {
  var resp = await fetch('https://api.anthropic.com/v1/messages', {
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
  var data = await resp.json();
  if (data && data.content && data.content[0]) return data.content[0].text;
  return "I'm sorry, I'm having trouble right now. Please WhatsApp us at (071) 374 4910.";
}

export default {
  async fetch(request, env) {
    var cors = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    if (request.method === 'OPTIONS') return new Response(null, { headers: cors });
    if (request.method !== 'POST') return new Response('Method not allowed', { status: 405, headers: cors });
    try {
      var body = await request.json();
      var messages = body.messages;
      if (!messages || !messages.length) return new Response(JSON.stringify({ error: 'No messages' }), { status: 400, headers: Object.assign({}, cors, { 'Content-Type': 'application/json' }) });

      var lastMsg = messages[messages.length - 1].content || '';
      var addendum = '';

      if (shouldSearch(lastMsg)) {
        var terms = extractSearchTerms(lastMsg);
        if (terms) {
          var products = await searchProducts(terms, env);
          if (products.length) {
            addendum = 'PRODUCT SEARCH RESULTS for "' + terms + '":\n' +
              products.map(function(p, i) {
                return (i+1) + '. ' + p.title + '\n   Brand: ' + p.vendor + ' | Price: ' + p.price + ' | ' + p.available + '\n   Tags: ' + p.tags + '\n   URL: ' + p.url + '\n   ' + p.description;
              }).join('\n\n') +
              '\n\nIMPORTANT: Use these ACTUAL results to recommend products. Include the exact product names, prices, and URLs from above. Do NOT say you cannot check prices or stock.';
          }
        }
      }

      var recent = messages.slice(-10);
      var reply = await callClaude(recent, addendum, env);
      return new Response(JSON.stringify({ reply: reply }), { headers: Object.assign({}, cors, { 'Content-Type': 'application/json' }) });
    } catch (err) {
      return new Response(JSON.stringify({ reply: "Something went wrong. Please WhatsApp us at (071) 374 4910." }), {
        status: 500, headers: Object.assign({}, cors, { 'Content-Type': 'application/json' })
      });
    }
  },
};
