/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    // No remote images in Pass 2 — showcase uses CSS-only placeholders.
    remotePatterns: [],
  },
};

export default nextConfig;
