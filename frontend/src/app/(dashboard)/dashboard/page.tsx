import { createSupabaseServerClient } from "@/utils/supabase/server";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = createSupabaseServerClient();

  try {
    const { data: { user } } = await supabase.auth.getUser();

    // If no user session exists on the server side, bounce to login cleanly
    if (!user) {
      redirect("/login");
    }
  } catch (error) {
    console.error("Layout Authentication Error:", error);
    // Fallback redirect if client initialization parameters are blank
    redirect("/login");
  }

  return (
    <div className="min-h-screen bg-background">
      {/* If you have a Sidebar or Navbar component, render it here */}
      <main className="p-6">{children}</main>
    </div>
  );
}
