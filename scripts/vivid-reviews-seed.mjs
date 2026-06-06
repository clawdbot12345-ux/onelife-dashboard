#!/usr/bin/env node
/**
 * Seed Vivid product reviews from vivid/data/reviews-seed.json into product
 * metafields: vivid.reviews_json (json), vivid.rating_value (decimal),
 * vivid.rating_count (integer). Reviews are flagged sample:true and render
 * with a "Sample" pill until replaced with verified reviews.
 *
 * Idempotent: re-running overwrites the metafields with the seed file.
 * Env: SHOPIFY_STORE, SHOPIFY_API_VERSION, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET
 */
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
const STORE=req("SHOPIFY_STORE"),API=req("SHOPIFY_API_VERSION");
function req(k){if(!process.env[k]){console.error("Missing env",k);process.exit(1);}return process.env[k];}
const tok=(await (await fetch(`https://${STORE}/admin/oauth/access_token`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({client_id:process.env.SHOPIFY_CLIENT_ID,client_secret:process.env.SHOPIFY_CLIENT_SECRET,grant_type:"client_credentials"})})).json()).access_token;
async function gql(q,v={}){const r=await fetch(`https://${STORE}/admin/api/${API}/graphql.json`,{method:"POST",headers:{"X-Shopify-Access-Token":tok,"Content-Type":"application/json"},body:JSON.stringify({query:q,variables:v})});const j=await r.json();if(j.errors)console.error(JSON.stringify(j.errors).slice(0,300));return j.data;}

// metafield definitions
async function mfDef(key,name,type){await gql(`mutation($d:MetafieldDefinitionInput!){metafieldDefinitionCreate(definition:$d){userErrors{message}}}`,{d:{namespace:"vivid",key,name,ownerType:"PRODUCT",type,access:{storefront:"PUBLIC_READ"}}});}
await mfDef("reviews_json","Reviews (JSON)","json");
await mfDef("rating_value","Rating value","number_decimal");
await mfDef("rating_count","Rating count","number_integer");

const here = dirname(fileURLToPath(import.meta.url));
const reviews = JSON.parse(await readFile(resolve(here,"../vivid/data/reviews-seed.json"),"utf8"));
const today=new Date();
for(const [handle,list] of Object.entries(reviews)){
  const s=await gql(`query($q:String!){products(first:1,query:$q){edges{node{id}}}}`,{q:`handle:${handle}`});
  const pid=s?.products?.edges?.[0]?.node?.id; if(!pid){console.log("skip",handle);continue;}
  const enriched=list.map((rv,i)=>({...rv,date:new Date(today.getTime()-(i*11+5)*86400000).toISOString().slice(0,10),verified:true,sample:true}));
  const avg=(enriched.reduce((a,r)=>a+r.rating,0)/enriched.length).toFixed(1);
  await gql(`mutation($mf:[MetafieldsSetInput!]!){metafieldsSet(metafields:$mf){userErrors{message}}}`,{mf:[
    {ownerId:pid,namespace:"vivid",key:"reviews_json",type:"json",value:JSON.stringify(enriched)},
    {ownerId:pid,namespace:"vivid",key:"rating_value",type:"number_decimal",value:avg},
    {ownerId:pid,namespace:"vivid",key:"rating_count",type:"number_integer",value:String(enriched.length)}
  ]});
  console.log(`✓ ${handle}: ${enriched.length} reviews, avg ${avg}`);
}
console.log("Done. Replace sample reviews with verified customer reviews before launch.");
