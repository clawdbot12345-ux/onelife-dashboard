#!/usr/bin/env node
/**
 * Create the Vivid "Subscribe & Save" selling-plan group (10% off, monthly /
 * every-2-months) and attach it to all non-bundle products.
 * Idempotent-ish: re-running creates a second group, so check first.
 *
 * Env: SHOPIFY_STORE, SHOPIFY_API_VERSION, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET
 */
const STORE = req("SHOPIFY_STORE"), API = req("SHOPIFY_API_VERSION");
function req(k){ if(!process.env[k]){ console.error("Missing env",k); process.exit(1);} return process.env[k]; }
const tok = (await (await fetch(`https://${STORE}/admin/oauth/access_token`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({client_id:process.env.SHOPIFY_CLIENT_ID,client_secret:process.env.SHOPIFY_CLIENT_SECRET,grant_type:"client_credentials"})})).json()).access_token;
async function gql(q,v={}){const r=await fetch(`https://${STORE}/admin/api/${API}/graphql.json`,{method:"POST",headers:{"X-Shopify-Access-Token":tok,"Content-Type":"application/json"},body:JSON.stringify({query:q,variables:v})});const j=await r.json();if(j.errors)console.error(JSON.stringify(j.errors).slice(0,400));return j.data;}

const existing = await gql(`{sellingPlanGroups(first:10){edges{node{name}}}}`);
if ((existing?.sellingPlanGroups?.edges||[]).some(e=>e.node.name==="Subscribe & Save")) {
  console.log("Subscribe & Save group already exists — skipping create."); process.exit(0);
}
const plan = (label, count) => ({
  name: `${label} — save 10%`, category:"SUBSCRIPTION", options:[label],
  billingPolicy:{recurring:{interval:"MONTH",intervalCount:count}},
  deliveryPolicy:{recurring:{interval:"MONTH",intervalCount:count}},
  pricingPolicies:[{fixed:{adjustmentType:"PERCENTAGE",adjustmentValue:{percentage:10.0}}}]
});
const r = await gql(`mutation($input:SellingPlanGroupInput!){sellingPlanGroupCreate(input:$input){sellingPlanGroup{id} userErrors{field message}}}`,{
  input:{ name:"Subscribe & Save", merchantCode:"subscribe-and-save",
    description:"Subscribe and save 10% on every delivery. Skip, pause, or cancel anytime.",
    options:["Delivery frequency"], sellingPlansToCreate:[plan("Every month",1), plan("Every 2 months",2)] }
});
const gid = r?.sellingPlanGroupCreate?.sellingPlanGroup?.id;
if (!gid) { console.error("create failed", JSON.stringify(r)); process.exit(1); }
let products=[],cur=null;
for(;;){const pr=await gql(`query($a:String){products(first:100,after:$a){edges{node{id handle}} pageInfo{hasNextPage endCursor}}}`,{a:cur});for(const e of pr.products.edges)products.push(e.node);if(!pr.products.pageInfo.hasNextPage)break;cur=pr.products.pageInfo.endCursor;}
const eligible=products.filter(p=>!/bundle|pack|stack/.test(p.handle));
for(let i=0;i<eligible.length;i+=25){await gql(`mutation($id:ID!,$ids:[ID!]!){sellingPlanGroupAddProducts(id:$id,productIds:$ids){userErrors{message}}}`,{id:gid,ids:eligible.slice(i,i+25).map(p=>p.id)});}
console.log(`✓ Subscribe & Save created (${gid}) and attached to ${eligible.length} products.`);
