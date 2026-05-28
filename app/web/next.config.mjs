/** @type {import('next').NextConfig} */
const API_BASE = process.env.CPOA_API_BASE || "http://localhost:8080";

// Production security headers — applied to every response. HSTS is set with
// includeSubDomains but without `preload` so the domain remains reversible (we
// haven't submitted it to the Chromium preload list).
const SECURITY_HEADERS = [
  { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  {
    key: "Permissions-Policy",
    value: [
      "camera=()",
      "microphone=()",
      "geolocation=()",
      "interest-cohort=()",
      "payment=()",
      "usb=()",
    ].join(", "),
  },
  { key: "X-DNS-Prefetch-Control", value: "off" },
  // CSP is deliberately permissive for the judge demo (Next.js inline scripts
  // require either 'unsafe-inline' or a per-request nonce; nonces would mean
  // moving header injection into middleware). Tight but functional defaults:
  {
    key: "Content-Security-Policy",
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "img-src 'self' data: https:",
      "font-src 'self' https://fonts.gstatic.com",
      "connect-src 'self'",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join("; "),
  },
];

const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  async rewrites() {
    // Proxy /api/* to the FastAPI backend (local dev and single-origin deploy),
    // plus the A2A discovery surfaces so peer enterprise agents can reach the
    // Agent Card and submit tasks at the canonical paths.
    return [
      { source: "/api/:path*", destination: `${API_BASE}/api/:path*` },
      { source: "/.well-known/agent.json", destination: `${API_BASE}/.well-known/agent.json` },
      { source: "/a2a/:path*", destination: `${API_BASE}/a2a/:path*` },
    ];
  },
  async headers() {
    return [{ source: "/:path*", headers: SECURITY_HEADERS }];
  },
};

export default nextConfig;
