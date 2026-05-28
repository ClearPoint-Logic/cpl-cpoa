/** @type {import('next').NextConfig} */
const API_BASE = process.env.CPOA_API_BASE || "http://localhost:8080";

const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  async rewrites() {
    // Proxy /api/* to the FastAPI backend (local dev and single-origin deploy).
    return [{ source: "/api/:path*", destination: `${API_BASE}/api/:path*` }];
  },
};

export default nextConfig;
