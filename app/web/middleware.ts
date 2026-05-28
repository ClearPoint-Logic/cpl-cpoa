import { NextRequest, NextResponse } from "next/server";

// Gate the judge site with HTTP basic auth (FR-076). The browser sends the
// Basic credential on every same-origin request, including the proxied /api/* calls,
// so data loads without a second prompt. Enforced only when creds are configured.
//
// Public discovery surfaces (A2A Agent Card + A2A v1 endpoints) are explicitly
// EXEMPT from the gate — A2A discoverability requires that peer enterprise
// agents reach `/.well-known/agent.json` without credentials. The API itself
// still enforces auth on state-changing surfaces (POST /a2a/v1/message:send).
const USER = process.env.CPOA_JUDGE_BASIC_AUTH_USER;
const PASS = process.env.CPOA_JUDGE_BASIC_AUTH_PASS;

const PUBLIC_PATHS = ["/.well-known/agent.json"];

export function middleware(req: NextRequest) {
  if (PUBLIC_PATHS.includes(req.nextUrl.pathname)) return NextResponse.next();
  if (!USER || !PASS) return NextResponse.next();
  const header = req.headers.get("authorization");
  if (header?.startsWith("Basic ")) {
    try {
      const [u, p] = atob(header.slice(6)).split(":");
      if (u === USER && p === PASS) return NextResponse.next();
    } catch {
      // fall through to 401
    }
  }
  return new NextResponse("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="ClearPoint Onboarding Agent Judge Access"' },
  });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
