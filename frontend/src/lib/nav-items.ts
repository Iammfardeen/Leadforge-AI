import {
  LayoutDashboard,
  Search,
  ScanLine,
  Camera,
  Sparkles,
  MessageCircle,
  FileText,
  Users,
  BarChart3,
  Settings,
  type LucideIcon,
} from "lucide-react";

export type NavItem = {
  label: string;
  href: string;
  icon: LucideIcon;
};

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Lead Finder", href: "/leads", icon: Search },
  { label: "Website Analyzer", href: "/analyzer", icon: ScanLine },
  { label: "Screenshots", href: "/screenshots", icon: Camera },
  { label: "AI Redesign", href: "/redesign", icon: Sparkles },
  { label: "WhatsApp Generator", href: "/whatsapp", icon: MessageCircle },
  { label: "Proposal Generator", href: "/proposals", icon: FileText },
  { label: "CRM", href: "/crm", icon: Users },
  { label: "Reports", href: "/reports", icon: BarChart3 },
  { label: "Settings", href: "/settings", icon: Settings },
];
