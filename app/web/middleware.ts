import { NextRequest, NextResponse } from "next/server";

// Gate the entire judge site with HTTP basic auth (FR-076). The browser sends the
// Basic credential on every same-origin request, including the proxied /api/* calls,
// so data loads without a second prompt. Enforced only when creds are configured.
const USER = process.env.CPOA_JUDGE_BASIC_AUTH_USER;
const PASS = process.env.CPOA_JUDGE_BASIC_AUTH_PASS;

export function middleware(req: NextRequest) {
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
    headers: { "WWW-Authenticate": 'Basic realm="ClearPoint Onboarding Agent — Judge Access"' },
  });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
