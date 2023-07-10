import {
  PrismaClient,
  House as SqlHouse,
  DocumentType as SqlDocumentType,
  Prisma,
} from "@prisma/client";
import {
  DocumentId,
  PrintingId,
  Printing,
  Action,
  Document,
  House,
  DocumentType,
} from "../model/index.js";

export interface ActionSpecifier {
  printing: PrintingId;
  description: string;
  pubDate: Date;
}

export type AddActionArgs = Omit<Action, "id" | "printing">;

export interface AddPrintingArgs
  extends Omit<Printing, "actions" | "document"> {
  actions: AddActionArgs[];
}

export interface AddDocArgs extends Document {
  printings: AddPrintingArgs[];
}

export default class Client {
  public static get(url?: string) {
    let client = Client.clients.get(url);
    if (client === undefined) {
      client = new Client(url);
      Client.clients.set(url, client);
    }
    return client;
  }

  async docExists(id: DocumentId): Promise<boolean> {
    // Maybe use count to reduce overhead?
    const doc = await this.prisma.doc.findUnique({
      where: { house_type_year_session_id: id },
    });
    return doc !== null;
  }

  async printingExists(id: PrintingId): Promise<boolean> {
    const printing = await this.prisma.printing.findUnique({
      where: {
        docHouse_docType_docYear_docSession_docId_id: {
          docHouse: id.document.house,
          docType: id.document.type,
          docYear: id.document.year,
          docSession: id.document.session,
          docId: id.document.id,
          id: id.id,
        },
      },
    });
    return printing !== null;
  }

  async getMostRecentPrinting(docId: DocumentId): Promise<Printing> {
    const sqlPrinting = await this.prisma.printing.findFirstOrThrow({
      where: {
        docHouse: docId.house,
        docYear: docId.year,
        docSession: docId.session,
        docId: docId.id,
      },
      orderBy: { pubDate: "desc" },
    });
    return {
      document: {
        house:
          sqlPrinting.docHouse === SqlHouse.HOUSE ? House.HOUSE : House.SENATE,
        type:
          sqlPrinting.docType === SqlDocumentType.BILL
            ? DocumentType.BILL
            : DocumentType.RESOLUTION,
        year: sqlPrinting.docYear,
        session: sqlPrinting.docSession,
        id: sqlPrinting.docId,
      },
      id: sqlPrinting.id,
      title: sqlPrinting.title,
      link: new URL(sqlPrinting.link),
      description: sqlPrinting.description,
      text: sqlPrinting.text,
      pubDate: sqlPrinting.pubDate,
      summary: sqlPrinting.summary === null ? undefined : sqlPrinting.summary,
    };
  }

  async actionExists(spec: ActionSpecifier | string): Promise<boolean> {
    const action =
      typeof spec === "string"
        ? this.prisma.action.findUnique({ where: { id: spec } }) !== null
        : this.prisma.action.findUnique({
            where: {
              docHouse_docType_docYear_docSession_docId_printingId_description_pubDate:
                {
                  docHouse: spec.printing.document.house,
                  docType: spec.printing.document.type,
                  docYear: spec.printing.document.year,
                  docSession: spec.printing.document.session,
                  docId: spec.printing.document.id,
                  printingId: spec.printing.id,
                  description: spec.description,
                  pubDate: spec.pubDate,
                },
            },
          });
    return action !== null;
  }

  async addDoc(doc: AddDocArgs): Promise<void> {
    const printings: Prisma.PrintingCreateWithoutDocInput[] = doc.printings.map(
      printing => {
        return {
          id: printing.id,
          title: printing.title,
          description: printing.description,
          text: printing.text,
          pubDate: printing.pubDate,
          link: printing.link.toString(),
          actions: { create: printing.actions },
        };
      },
    );
    await this.prisma.doc.create({
      data: {
        house: doc.house,
        type: doc.type,
        year: doc.year,
        session: doc.session,
        id: doc.id,
        printings: { create: printings },
      },
    });
  }

  async addPrinting(
    docId: DocumentId,
    printing: AddPrintingArgs,
  ): Promise<void> {
    await this.prisma.printing.create({
      data: {
        docHouse: docId.house,
        docType: docId.type,
        docYear: docId.year,
        docSession: docId.session,
        docId: docId.id,
        id: printing.id,
        title: printing.title,
        description: printing.description,
        text: printing.text,
        pubDate: printing.pubDate,
        link: printing.link.toString(),
        actions: { create: printing.actions },
      },
    });
  }

  async addAction(
    printingId: PrintingId,
    action: AddActionArgs,
  ): Promise<void> {
    await this.prisma.action.create({
      data: {
        docHouse: printingId.document.house,
        docType: printingId.document.type,
        docYear: printingId.document.year,
        docSession: printingId.document.session,
        docId: printingId.document.id,
        printingId: printingId.id,
        description: action.description,
        pubDate: action.pubDate,
      },
    });
  }

  async addPrintingSummary(
    printingId: PrintingId,
    summary: string,
  ): Promise<void> {
    await this.prisma.printing.update({
      where: {
        docHouse_docType_docYear_docSession_docId_id: {
          docHouse: printingId.document.house,
          docType: printingId.document.type,
          docYear: printingId.document.year,
          docSession: printingId.document.session,
          docId: printingId.document.id,
          id: printingId.id,
        },
      },
      data: { summary },
    });
  }

  private prisma: PrismaClient;
  private static clients: Map<string | undefined, Client> = new Map();
  private constructor(url?: string) {
    this.prisma =
      url === undefined
        ? new PrismaClient()
        : new PrismaClient({ datasources: { db: { url } } });
  }
}
