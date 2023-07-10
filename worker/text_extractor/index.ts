import { dirname, parse, format } from "node:path";
import { readFile, writeFile } from "node:fs/promises";

import spawn from "@npmcli/promise-spawn";
import got from "got";
import { JSDOM } from "jsdom";
import { convertToHtml } from "mammoth";

export const billDocLinkToText = async (link: URL): Promise<string> => {
  const doc = await getBillDoc(link);
  const docx = await billDocToDocx(doc);
  const html = await billDocxToHtml(docx);
  return billHtmlToText(html);
};

const billHtmlToText = (html: string): string => {
  const dom = new JSDOM(html);
  // Select all the strikethrough elements and delete them
  dom.window.document.querySelectorAll("s").forEach(ele => ele.remove());
  const text = dom.window.document.body.textContent || "";
  // Remove excess whitespace and empty lines.
  return text
    ?.split("\n")
    .map(l => l.trim())
    .filter(l => l.length !== 0)
    .join("\n");
};

const getBillDoc = async (link: URL): Promise<Buffer> => {
  const resp = await got.get(link, { throwHttpErrors: true });
  return resp.rawBody;
};

const billDocToDocx = async (doc: Buffer): Promise<Buffer> => {
  const docFileName = (await spawn("mktemp", ["--suffix", ".doc"])).stdout;
  const parsedDocFileName = parse(docFileName);
  const docxFileName = format({
    ...parsedDocFileName,
    ext: ".docx",
    base: undefined,
  });
  const dirName = dirname(docFileName);
  await writeFile(docFileName, doc);
  await spawn("lowriter", [
    "--convert-to",
    "docx",
    "--outdir",
    dirName,
    docFileName,
  ]);
  return readFile(docxFileName);
};

type PromiseResult<P> = P extends Promise<infer R> ? R : never;
const billDocxToHtml = async (docx: Buffer): Promise<string> => {
  const compactHtml = (await convertToHtml({ buffer: docx })).value;
  const tidyPromise = spawn("tidy", ["-config", `./.tidyrc`], {
    stdio: "pipe",
  });
  const stdin = tidyPromise.process.stdin!;
  await new Promise<void>(resolve => stdin.end(compactHtml, resolve));

  try {
    return (await tidyPromise).stdout;
  } catch (err: any) {
    const typedError: PromiseResult<typeof tidyPromise> & Error = err;
    if (typedError.code !== 1) {
      throw typedError;
    }
    return typedError.stdout;
  }
};
