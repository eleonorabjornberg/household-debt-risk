import type { Metadata } from "next";
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { DraftBanner } from "@/components/pages/DraftBanner";
import { REPO_TREE } from "@/content/build";
import { site } from "@/content/story";

// /plugin (R1, 2026-11-15: Eleonora asked for the plugin to be easy to get). Download, install, what's inside. The zip is
// built from plugin/ by scripts/plugin-zip.mjs on every build. Claude-draft copy, under a banner until she approves it.
export const metadata: Metadata = {
  title: "Fed Data Desk plugin · Hot Potato",
  description: "Download the Fed Data Desk Claude Code plugin: skills, reviewer subagents and the household-credit MCP server.",
};

// Counts and names are read from the plugin folder at build time, so they cannot drift from what the zip holds.
const PLUGIN = path.join(process.cwd(), "..", "plugin", "fed-data-desk");
function inside() {
  const names = (dir: string, files: boolean) =>
    readdirSync(path.join(PLUGIN, dir), { withFileTypes: true })
      .filter((d) => (files ? d.isFile() && d.name.endsWith(".md") : d.isDirectory()))
      .map((d) => d.name.replace(/\.md$/, ""))
      .sort();
  const skills = names("skills", false);
  const commands = names("commands", true).map((c) => `/fed-data-desk:${c}`);
  const agents = names("agents", true);
  const mcp = Object.keys(JSON.parse(readFileSync(path.join(PLUGIN, ".mcp.json"), "utf8")).mcpServers ?? {});
  const n = (k: number, one: string, many: string) => `${k} ${k === 1 ? one : many}`;
  return [
    { name: n(skills.length, "skill", "skills"), body: skills.join(", ") },
    { name: n(commands.length, "command", "commands"), body: commands.join(", ") },
    { name: n(agents.length, "subagent", "subagents"), body: agents.join(", ") },
    { name: n(mcp.length, "MCP server", "MCP servers"), body: `${mcp.join(", ")}: read-only Fed Z.1 and NY Fed data, with series IDs and vintages` },
  ];
}

export default function PluginPage() {
  return (
    <main>
      <section className="band band--build band--page" aria-labelledby="plugin-h">
        <div className="wrap">
          <DraftBanner testId="plugin-draft-banner" />
          <h1 id="plugin-h" className="page-h">Fed Data Desk</h1>
          <p className="band__lede">The Claude Code plugin behind this site: the skills, reviewer subagents and MCP server, packaged for reuse.</p>
          <div className="hero__buttons">
            <a className="btn btn--primary" href="/downloads/fed-data-desk-plugin.zip" download>Download the plugin (.zip)</a>
            <a className="btn" href={`${REPO_TREE}/plugin/fed-data-desk`}>Browse it on GitHub</a>
          </div>
        </div>
      </section>

      <section className="band" aria-labelledby="install-h">
        <div className="wrap wrap--narrow">
          <h2 id="install-h">Install</h2>
          <p>It reads the project&apos;s register, validation and data files, so run Claude Code from the root of a clone.</p>
          <h3>From GitHub</h3>
          <pre className="cmd"><code>{`git clone ${site.repo}.git
cd household-debt-risk
claude plugin marketplace add eleonorabjornberg/household-debt-risk
claude plugin install fed-data-desk@household-debt-risk`}</code></pre>
          <h3>From the zip</h3>
          <pre className="cmd"><code>{`unzip fed-data-desk-plugin.zip
claude plugin marketplace add ./fed-data-desk-plugin
claude plugin install fed-data-desk@household-debt-risk`}</code></pre>
          <p className="pg-caption">The MCP server needs <code>uv</code>. No secrets are in the plugin.</p>
        </div>
      </section>

      <section className="band band--tight" aria-labelledby="inside-h">
        <div className="wrap">
          <h2 id="inside-h">What&apos;s inside</h2>
          <ul className="tiles tiles--two">
            {inside().map((x) => (
              <li key={x.name}><div className="tile tile--static"><strong>{x.name}</strong><span>{x.body}</span></div></li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}
