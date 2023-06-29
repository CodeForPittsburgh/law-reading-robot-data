import { JSDOM } from "jsdom";
import { argv, exit } from "node:process";

export async function processHouseBillHtml(path: string): Promise<string> {
  const dom = await JSDOM.fromFile(path);
  // Select all the strikethrough elements and delete them
  dom.window.document.querySelectorAll("s").forEach(ele => ele.remove());
  const text = dom.window.document.body.textContent || "";
  // Remove excess whitespace and empty lines.
  return text
    ?.split("\n")
    .map(l => l.trim())
    .filter(l => l.length !== 0)
    .join("\n");
}

if (require.main === module) {
  if (argv.length !== 3) {
    console.error("Usage: node process.js <path/to/house_bill.html>");
    exit(1);
  }
  processHouseBillHtml(argv[2]).then(console.log);
}
