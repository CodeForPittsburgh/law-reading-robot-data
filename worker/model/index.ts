export enum House {
  HOUSE = "HOUSE",
  SENATE = "SENATE",
}

export enum DocumentType {
  BILL = "BILL",
  RESOLUTION = "RESOLUTION",
}

export interface DocumentId {
  readonly house: House;
  readonly type: DocumentType;
  readonly year: number;
  readonly session: number;
  readonly id: number;
}

export interface PrintingId {
  readonly document: DocumentId;
  readonly id: number;
}

export interface ActionId {
  readonly printing: PrintingId;
  readonly id: string;
}

export interface Document extends DocumentId {}

export interface Printing extends PrintingId {
  readonly title: string;
  readonly link: URL;
  readonly description: string;
  readonly pubDate: Date;
  readonly text: string;
  readonly summary?: string;
}

export interface Action extends ActionId {
  readonly description: string;
  readonly pubDate: Date;
}
