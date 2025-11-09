/* eslint-disable @typescript-eslint/no-empty-object-type */
/* eslint-disable @typescript-eslint/no-explicit-any */

declare module "react" {
  export type Key = string | number;

  export interface Attributes {
    key?: Key | null;
  }

  export interface ReactElement<P = any, T = any> {
    type: T;
    props: P;
    key: Key | null;
    children?: ReactNode;
  }

  export interface ReactPortal extends ReactElement {
    children: ReactNode;
  }

  export type ReactNode =
    | ReactElement
    | ReactPortal
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
    export type ReactNode =
      | import("react").ReactElement
      | string
      | number
      | boolean
      | null
      | undefined
      | Iterable<ReactNode>;
    export type Key = string | number;
    export type ReactElement<P = any, T = any> = import("react").ReactElement<
      P,
      T
    >;
    export interface ReactPortal {
      key: string | null;
      children: ReactNode;
      type: any;
      props: any;
    }
  }

  namespace JSX {
    type Element = any;

    interface IntrinsicElements {
      [element: string]: any;
    }
  }
}
