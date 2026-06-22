16:05:50.137 Running build in Washington, D.C., USA (East) – iad1
16:05:50.137 Build machine configuration: 2 cores, 8 GB
16:05:50.151 Cloning github.com/Iammfardeen/Leadforge-AI (Branch: main, Commit: b43fed7)
16:05:50.152 Skipping build cache, deployment was triggered without cache.
16:05:50.441 Cloning completed: 289.000ms
16:05:50.964 Running "vercel build"
16:05:51.023 Vercel CLI 54.14.0
16:05:51.342 Installing dependencies...
16:06:22.019 npm warn deprecated inflight@1.0.6: This module is not supported, and leaks memory. Do not use it. Check out lru-cache if you want a good and tested way to coalesce async requests by a key value, which is much more comprehensive and powerful.
16:06:22.885 npm warn deprecated rimraf@3.0.2: Rimraf versions prior to v4 are no longer supported
16:06:23.827 npm warn deprecated @humanwhocodes/object-schema@2.0.3: Use @eslint/object-schema instead
16:06:23.846 npm warn deprecated @humanwhocodes/config-array@0.11.14: Use @eslint/config-array instead
16:06:23.964 npm warn deprecated glob@7.2.3: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
16:06:24.915 npm warn deprecated glob@10.3.10: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
16:06:26.170 npm warn deprecated recharts@2.12.7: 1.x and 2.x branches are no longer active. Bump to Recharts v3 to receive latest features and bugfixes. See https://github.com/recharts/recharts/wiki/3.0-migration-guide
16:06:26.519 npm warn deprecated eslint@8.57.0: This version is no longer supported. Please see https://eslint.org/version-support for other options.
16:06:30.548 npm warn deprecated next@14.2.5: This version has a security vulnerability. Please upgrade to a patched version. See https://nextjs.org/blog/security-update-2025-12-11 for more details.
16:06:30.818 
16:06:30.818 added 448 packages in 39s
16:06:30.823 
16:06:30.823 158 packages are looking for funding
16:06:30.824   run `npm fund` for details
16:06:30.884 Detected Next.js version: 14.2.5
16:06:30.893 Running "npm run build"
16:06:30.998 
16:06:30.998 > leadforge-ai-frontend@0.1.0 build
16:06:30.999 > next build
16:06:30.999 
16:06:31.550 Attention: Next.js now collects completely anonymous telemetry regarding usage.
16:06:31.551 This information is used to shape Next.js' roadmap and prioritize features.
16:06:31.551 You can learn more, including how to opt-out if you'd not like to participate in this anonymous program, by visiting the following URL:
16:06:31.551 https://nextjs.org/telemetry
16:06:31.552 
16:06:31.606   ▲ Next.js 14.2.5
16:06:31.607 
16:06:31.625    Creating an optimized production build ...
16:06:46.528 request to https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap failed, reason: 
16:06:46.529 
16:06:46.530 Retrying 1/3...
16:06:46.530 request to https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100..800&display=swap failed, reason: 
16:06:46.530 
16:06:46.531 Retrying 1/3...
16:06:53.057  ✓ Compiled successfully
16:06:53.059    Linting and checking validity of types ...
16:06:57.629 Failed to compile.
16:06:57.629 
16:06:57.629 ./src/app/(dashboard)/dashboard/page.tsx:36:51
16:06:57.630 Type error: Property 'suffix' does not exist on type '{ readonly key: "total_leads"; readonly label: "Total Leads"; readonly icon: ForwardRefExoticComponent<Omit<LucideProps, "ref"> & RefAttributes<SVGSVGElement>>; } | ... 4 more ... | { ...; }'.
16:06:57.630 
16:06:57.630   34 |
16:06:57.630   35 |       <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-6">
16:06:57.630 > 36 |         {STAT_DEFS.map(({ key, label, icon: Icon, suffix }) => {
16:06:57.630      |                                                   ^
16:06:57.631   37 |           const value = stats[key];
16:06:57.632   38 |           return (
16:06:57.632   39 |             <Card key={key} className="p-4">
16:06:57.697 Error: Command "npm run build" exited with 1
