import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard" },
  { to: "/expenses", label: "Expenses" },
  { to: "/budgets", label: "Budgets" },
  { to: "/settings", label: "Settings" },
];

export function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex">
      <aside className="w-56 shrink-0 bg-ink text-paper flex flex-col">
        <div className="px-6 py-7">
          <h1 className="font-display text-2xl italic">Ledgerly</h1>
        </div>
        <nav className="flex-1 px-3 space-y-0.5">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `block px-3 py-2 text-sm transition-colors ${
                  isActive ? "bg-paper/10 text-paper" : "text-paper/60 hover:text-paper"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-6 py-5 border-t border-paper/10 text-sm">
          <p className="text-paper/90">{user?.name}</p>
          <button
            onClick={logout}
            className="text-paper/50 hover:text-paper text-xs mt-1 transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 px-10 py-8 max-w-5xl">{children}</main>
    </div>
  );
}
