import { argv, exit } from "node:process";
import * as url from "node:url";

import Client, { AddPrintingArgs } from "../dal/index.js";
import { House } from "../model/index.js";
import { readFeed, PrintingItem } from "../rss_reader/index.js";
import { billDocLinkToText } from "../text_extractor/index.js";

import { CONFIG } from "./config.js";

export const processHouseFeed = async (house: House) => {
  const feed = await readFeed(house);
  let itemCount = 0;
  for (const item of feed.items) {
    // Process one at a time so we never do expensive operations like
    // extracting text or summarizing text multiple times.
    await processPrintingItem(item);
    itemCount++;
    console.log(`Processed ${itemCount} documents`);
  }
};

const processPrintingItem = async (printingItem: PrintingItem) => {
  const client: Client = Client.get(CONFIG.postgres.url);
  const billId = printingItem.document;
  console.log(`Checking if document ${JSON.stringify(billId)} exists`);
  const billExists = await client.docExists(billId);
  console.log(`Checking if printing ${printingItem.id} exists`);
  const printingExists =
    billExists &&
    (await client.printingExists({
      document: printingItem.document,
      id: printingItem.id,
    }));
  console.log("Getting text from link");
  const text = await billDocLinkToText(printingItem.link);
  console.log("Getting summary");
  const summary = await getSummary(text);

  if (!printingExists) {
    console.log("Adding printing since it didn't exist");
    addPrinting({ client, billExists, printingItem, text, summary });
  }
  // TODO(Jared): Add an event to the event table if one was not already recorded.
};

const getSummary = async (text: string): Promise<string> => {
  return `Summarized: ${text.split("\n").slice(0, 3).join("\n")}`;
};

const addPrinting = async ({
  client,
  billExists,
  printingItem,
  text,
  summary,
}: {
  client: Client;
  billExists: boolean;
  printingItem: PrintingItem;
  text: string;
  summary: string;
}) => {
  const billId = printingItem.document;
  const addPrintingArgs: AddPrintingArgs = {
    ...printingItem,
    text,
    summary,
    actions: [],
  };

  // Add the bill to the DB if it does not exist.
  if (!billExists) {
    await client.addDoc({
      ...billId,
      printings: [addPrintingArgs],
    });
  } else {
    // Otherwise just add the printing as the bill already exists.
    await client.addPrinting(billId, addPrintingArgs);
  }
};

const printUsage = () => {
  console.error("Usage: node build/orchestrator/index.js <HOUSE|SENATE>");
};

const parseArgv = (args: string[]): House | null => {
  console.log(`Parsing "${args}" of length ${args.length}`);
  if (args.length !== 3) {
    return null;
  }
  console.log(`Switching on "${args[2]}"`);
  switch (args[2]) {
    case House.HOUSE:
      return House.HOUSE;
    case House.SENATE:
      return House.SENATE;
    default:
      return null;
  }
};

if (import.meta.url.startsWith("file:")) {
  const modulePath = url.fileURLToPath(import.meta.url);
  if (argv[1] === modulePath) {
    const house = parseArgv(argv);
    if (house === null) {
      printUsage();
      exit(1);
    }
    processHouseFeed(house);
  }
}
