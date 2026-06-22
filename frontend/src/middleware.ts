import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/signup"];

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  });

  // 1. Fallbacks prevent the middleware container from crashing if Vercel blanks out the variables at runtime
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder-project.supabase.co";
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "placeholder-anon-key";

  // 2. Modern Next.js 14+ cookie schema using getAll() and setAll() to prevent invocation failures
  const supabase = createServerClient(
    supabaseUrl,
    supabaseAnonKey,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => request.cookies.set({ name, value, ...options }));
          response = NextResponse.next({
            request: {
              headers: request.headers,
            },
          });
          cookiesToSet.forEach(({ name, value, options }) => response.cookies.set({ name, value, ...options }));
        },
      },
    }
  );

  // If environment variables were truly missing or placeholder values are active, skip auth check safely
  if (supabaseUrl.includes("placeholder")) {
    return response;
  }

  try {
    const { data: { user } } = await supabase.auth.getUser();
    const isPublicPath = PUBLIC_PATHS.some((path) => request.nextUrl.pathname.startsWith(path));

    if (!user && !isPublicPath) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("redirectedFrom", request.nextUrl.pathname);
      return NextResponse.redirect(loginUrl);
    }

    if (user && isPublicPath) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  } catch (error) {
    // Catch-all prevents Edge routing from returning a hard 500 server error to visitors
    console.error("Middleware Auth Error:", error);
  }

  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|api/auth).*)"],
};
