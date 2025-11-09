declare module "next" {
  export interface NextConfig {
    reactStrictMode?: boolean;
    output?: "standalone" | "export" | "app" | undefined;
    experimental?: Record<string, unknown>;
    [key: string]: unknown;
  }

  export interface Metadata {
    title?: string | { default?: string; template?: string };
    description?: string;
    icons?: unknown;
    keywords?: string | string[];
    authors?: Array<{ name: string; url?: string } | string>;
    other?: Record<string, unknown>;
    [key: string]: unknown;
  }
}

