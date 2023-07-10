import { Printing } from "../model/index.js";

export interface RssRawBase {
  title: string;
  link: string;
  description: string;
  pubDate: string;
}

export interface RssBase {
  title: string;
  link: URL;
  description: string;
  pubDate: Date;
}

export type BillFeedMetaRaw = RssRawBase;

export interface BillItemRaw extends RssRawBase {
  lastAction: string;
  guid: string;
}

export interface PrintingFeed extends RssBase {
  readonly items: PrintingItem[];
}

export interface PrintingItem extends Omit<Printing, "summary" | "text"> {
  readonly lastAction: string;
}
