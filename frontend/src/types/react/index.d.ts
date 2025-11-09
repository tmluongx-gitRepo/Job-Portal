declare module "react" {
  export type Key = string | number;

  export interface Attributes {
    key?: Key | null;
  }

  export interface ReactElement<P = any, T = any> {
    type: T;
    props: P;
    key: Key | null;
  }

  export type ReactNode =
    | ReactElement
    | string
    | number
    | boolean
    | null
    | undefined
    | Iterable<ReactNode>;

  export interface FunctionComponent<P = {}> {
    (props: P & { children?: ReactNode }): ReactElement | null;
  }

  export type FC<P = {}> = FunctionComponent<P>;

  export namespace JSX {
    type Element = any;

    interface IntrinsicElements {
      [element: string]: any;
    }
  }
}

declare module "react/jsx-runtime" {
  export const jsx: <T>(
    type: T,
    props: Record<string, unknown>,
    key?: string | number
  ) => import("react").ReactElement;
  export const jsxs: typeof jsx;
  export const Fragment: unique symbol;
}

declare global {
  namespace React {
    export type ReactNode = import("react").ReactNode;
  }

  namespace JSX {
    type Element = any;

    interface IntrinsicElements {
      [element: string]: any;
    }
  }
}

