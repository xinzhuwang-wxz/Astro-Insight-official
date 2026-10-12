"use client";
// import { Geist, Geist_Mono } from "next/font/google";
import "@/styles/globals.css";
import "@copilotkit/react-ui/styles.css";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotPopup } from "@copilotkit/react-ui";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeProvider } from "@/components/theme-provider";
import { Starfield } from "../components/Starfield";
import { COPILOT_RUNTIME_URL } from "@/config/copilot";




export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();

  const segments = pathname.split("/").filter(Boolean);
  const isHome = pathname === "/";

  const crumbItems = [
    <li key="home">
      {isHome ? (
        <span className="text-gray-300">首页</span>
      ) : (
        <Link href="/" className="text-blue-300 hover:underline">首页</Link>
      )}
    </li>,
    ...segments.map((seg, idx) => {
      const href = "/" + segments.slice(0, idx + 1).join("/");
      const isLast = idx === segments.length - 1;
      return (
        <li key={href} className="flex items-center gap-1">
          <span className="text-gray-500">/</span>
          {isLast ? (
            <span className="text-gray-100 capitalize">{seg}</span>
          ) : (
            <Link href={href} className="text-blue-300 hover:underline capitalize">{seg}</Link>
          )}
        </li>
      );
    }),
  ];
  return (
    <html lang="zh-CN" suppressHydrationWarning className="dark">
      <body className="antialiased bg-black text-white transition-colors overflow-y-scroll [scrollbar-gutter:stable]">
        <ThemeProvider>
        <div
          style={
            {
              // 保持 CopilotKit 原有浅色样式，不受局部 dark 影响
              "--copilot-kit-background-color": "rgba(255, 255, 255, 1)",
              "--copilot-kit-contrast-color": "rgba(255, 255, 255, 1)",
              "--copilot-kit-primary-color": "rgba(0, 0, 0, 1)",
              "--copilot-kit-secondary-color": "rgba(37, 249, 0, 1)",
            } as CopilotKitCSSProperties
          }
          className="min-h-dvh"
        >
          <Starfield />
          <CopilotKit
            runtimeUrl={COPILOT_RUNTIME_URL}
            agent="quickstart_agent"
            showDevConsole={true} 

          >
            {/* 全局导航栏 */}
            <header className="sticky top-0 z-30 w-full border-b border-white/10 bg-neutral-900/70 backdrop-blur">
              <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <Link href="/" className="text-lg font-semibold tracking-wide text-white hover:text-blue-300">天文agent</Link>
                </div>
                <div className="flex items-center gap-2">
                  <Link
                    href="/settings"
                    className="rounded-md px-3 py-1.5 text-sm text-white/80 transition hover:bg-white/10 hover:text-white"
                  >
                    设置
                  </Link>
                </div>
              </div>
            </header>
            {/* 面包屑 */}
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 mt-2">
              <ol className="flex flex-wrap items-center gap-1 text-sm text-white/80" aria-label="Breadcrumb">
                {crumbItems}
              </ol>
            </div>
            {/* 主体内容 */}
            <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4 text-white">
              {children}
            </main>
            {/* 全局 CopilotPopup：放在 layout 中保证在所有页面显示 */}
            <CopilotPopup
              instructions={"欢迎向我咨询任何天文相关的问题！"}
              defaultOpen={false}
              imageUploadsEnabled={true}
              labels={{ title: "超级助手", initial: "Need any help?" }}
            />
          </CopilotKit>
        </div>
        </ThemeProvider>
      </body>
    </html>
  );
}

// Astro Integration v27: provider wiring reviewed; kept unchanged until runtime compatibility validation.


{/* Astro runtime integration v33 review marker: existing provider tree preserved. */}
