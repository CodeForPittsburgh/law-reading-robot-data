import { env } from "node:process";

class PostgresConfig {
  constructor(
    readonly hostname: string,
    readonly port: number,
    readonly username: string,
    readonly password: string,
  ) {}
  get url(): string {
    return `postgresql://${this.username}:${this.password}@${this.hostname}:${this.port}`;
  }
}

export interface Config {
  postgres: PostgresConfig;
}
const postgresPort = parseInt(env["POSTGRES_PORT"] || "");

export const CONFIG: Config = {
  postgres: new PostgresConfig(
    env["POSTGRES_HOSTNAME"] || "postgres",
    isNaN(postgresPort) ? 5432 : postgresPort,
    env["POSTGRES_USERNAME"] || "postgres",
    env["POSTGRES_PASSWORD"] || "password",
  ),
};
