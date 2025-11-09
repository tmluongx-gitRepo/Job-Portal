/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-unused-vars */

declare module "zod" {
  const z: any;

  namespace z {
    type ZodTypeAny = any;
    type ZodSchema<T = any> = any;
    type ZodIssue = any;
    type infer<T> = any;
  }

  export { z };
  export type ZodTypeAny = z.ZodTypeAny;
  export type ZodSchema<T = any> = z.ZodSchema<T>;
  export type ZodIssue = z.ZodIssue;
  export type infer<T> = z.infer<T>;
}

declare module "clsx" {
  export type ClassValue =
    | string
    | number
    | null
    | undefined
    | Record<string, boolean>
    | ClassValue[];

  export function clsx(...classValues: ClassValue[]): string;
  export default clsx;
}

declare module "tailwind-merge" {
  export function twMerge(
    ...classLists: Array<string | undefined | null | false>
  ): string;
  export default twMerge;
}

declare module "tailwindcss" {
  export interface Config {
    content?: Array<string>;
    theme?: Record<string, unknown>;
    plugins?: Array<(...args: any[]) => any>;
    [key: string]: unknown;
  }
}

declare const process: {
  env: Record<string, string | undefined>;
};
