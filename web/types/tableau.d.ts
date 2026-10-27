// JSX typing for the Tableau Embedding API v3 web component.
import type { DetailedHTMLProps, HTMLAttributes } from "react";

declare module "react" {
  namespace JSX {
    interface IntrinsicElements {
      "tableau-viz": DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement> & {
        src?: string;
        token?: string;
        toolbar?: "top" | "bottom" | "hidden";
        "hide-tabs"?: boolean;
        device?: string;
        width?: string;
        height?: string;
      };
    }
  }
}
