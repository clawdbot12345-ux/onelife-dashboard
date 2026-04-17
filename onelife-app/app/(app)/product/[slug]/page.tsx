import { notFound } from "next/navigation";
import { findProduct, MOCK_PRODUCTS, reviewsFor } from "@/lib/mock";
import { ProductDetail } from "@/components/ProductDetail";

export function generateStaticParams() {
  return MOCK_PRODUCTS.map((p) => ({ slug: p.slug }));
}

export default function ProductPage({ params }: { params: { slug: string } }) {
  const product = findProduct(params.slug);
  if (!product) notFound();

  const pairsWith = product.pairsWith
    .map((id) => MOCK_PRODUCTS.find((p) => p.id === id))
    .filter((p): p is NonNullable<typeof p> => Boolean(p));

  return (
    <ProductDetail
      product={product}
      reviews={reviewsFor(product.id)}
      pairsWith={pairsWith}
    />
  );
}
