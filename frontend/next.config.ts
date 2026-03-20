import type { NextConfig } from "next";

import path from "node:path";

const nextConfig: NextConfig = {
  /* config options here */
  // @ts-ignore - Turbopack type might be missing in some Next.js versions
  turbopack: {
    root: path.resolve(__dirname, ".."),
  },
};

export default nextConfig;
