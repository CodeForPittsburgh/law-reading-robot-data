import { argv, exit } from "node:process";
import { fileURLToPath } from "node:url";

import got from "got";

import { House } from "../model/index.js";
export * from "./model.js";
import { PrintingFeed } from "./model.js";
import parseFeed from "./parser.js";

const Feed = {
  [House.HOUSE]: new URL(
    "https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml",
  ),
  [House.SENATE]: new URL(
    "https://www.legis.state.pa.us/WU01/LI/RSS/SenateBills.xml",
  ),
};

export const readFeed = async (house: House): Promise<PrintingFeed> => {
  const response = await got.get(Feed[house]);
  return await parseFeed(response.body);
};

const isHouse = (billTypeStr: string): billTypeStr is House =>
  Object.values<string>(House).includes(billTypeStr);

if (argv[1] === fileURLToPath(import.meta.url)) {
  const usage = "Usage: node index.js <HOUSE|SENATE>";
  if (argv.length !== 3) {
    console.log(usage);
    exit(1);
  }
  const billType = argv[2];
  if (!isHouse(billType)) {
    console.log(usage);
    exit(1);
  }
  (async () => {
    const feed = await readFeed(billType);
    console.log(JSON.stringify(feed));
  })();
}
