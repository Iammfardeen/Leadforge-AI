/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.supabase.co" },
    ],
  },
  // ADD THIS PARALLEL TO IMAGES SETTING:
  typescript: {
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;
