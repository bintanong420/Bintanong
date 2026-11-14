import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  agentRules: false,
  allowedDevOrigins: process.env.SITE_ORIGIN ? [new URL(process.env.SITE_ORIGIN).hostname] : [],
};

export default nextConfig;
