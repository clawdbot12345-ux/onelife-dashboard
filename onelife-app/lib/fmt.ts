/**
 * Formatters. All money is stored as integer cents (ZAR), rendered through
 * TabularPrice — never hand-rolled .toFixed.
 */

const zarNarrow = new Intl.NumberFormat("en-ZA", {
  style: "currency",
  currency: "ZAR",
  maximumFractionDigits: 0,
  currencyDisplay: "narrowSymbol",
});

const zarFull = new Intl.NumberFormat("en-ZA", {
  style: "currency",
  currency: "ZAR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
  currencyDisplay: "narrowSymbol",
});

export function formatZar(cents: number, format: "narrow" | "full" = "full") {
  const rands = cents / 100;
  const str = (format === "narrow" ? zarNarrow : zarFull).format(rands);
  // Intl outputs "R 249,00" in en-ZA; normalise to "R 249.00" (decimal point)
  // because the dashboard, Shopify prices, and printed labels all use points.
  return str.replace(/\u00A0/g, " ").replace(",", ".");
}

export function formatTimeSA(iso: string) {
  return new Date(iso).toLocaleTimeString("en-ZA", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

export function formatDayShort(iso: string) {
  return new Date(iso).toLocaleDateString("en-ZA", {
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}
