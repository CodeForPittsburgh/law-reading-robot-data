import Parser from "rss-parser";

import { House, PrintingId, DocumentType } from "../model/index.js";
import {
  PrintingItem,
  PrintingFeed,
  RssRawBase,
  RssBase,
  BillFeedMetaRaw,
  BillItemRaw,
} from "./model.js";

const printingIdFormat =
  /^(?<year>\d{4})(?<session>\d+)(?<house>H|S)(?<documentType>B|R)(?<id>\d+)P(?<printingId>\d+)$/;

const parsePrintingGuid = (guid: string): PrintingId => {
  const matches = guid.match(printingIdFormat);
  if (!matches || matches.groups === undefined)
    throw Error(`Could not parse bill guid ${guid}`);
  const groups = matches.groups;
  return {
    document: {
      house: groups.house === "H" ? House.HOUSE : House.SENATE,
      type:
        groups.documentType === "B"
          ? DocumentType.BILL
          : DocumentType.RESOLUTION,
      year: parseInt(groups.year),
      session: parseInt(groups.session),
      id: parseInt(groups.id),
    },
    id: parseInt(groups.printingId),
  };
};

const parseRssBase = (raw: RssRawBase): RssBase => ({
  title: raw.title,
  link: new URL(raw.link),
  description: raw.description,
  pubDate: new Date(raw.pubDate),
});

const parseBillItem = (raw: BillItemRaw): PrintingItem => ({
  ...parseRssBase(raw),
  ...parsePrintingGuid(raw.guid),
  lastAction: raw.lastAction,
});

export default async (feedStr: string): Promise<PrintingFeed> => {
  const billParser = new Parser<BillFeedMetaRaw, BillItemRaw>({
    customFields: {
      feed: ["title", "link", "description", "pubDate"],
      item: ["title", "link", "description", "pubDate", "guid"],
    },
  });
  const halfParsedFeed = await billParser.parseString(feedStr);
  return {
    ...parseRssBase(halfParsedFeed),
    items: halfParsedFeed.items.map(parseBillItem),
  };
};
