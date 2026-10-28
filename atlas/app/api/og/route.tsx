// Share image for a year: /api/og?year=2008 (defaults to the latest quarter).
import { readFile } from "node:fs/promises";
import path from "node:path";
import { ImageResponse } from "next/og";

export const runtime = "nodejs";

interface Row {
  date: string;
  public_share: number;
  public_musd: number;
  scope_total_musd: number;
}

export async function GET(req: Request) {
  const rows: Row[] = JSON.parse(await readFile(path.join(process.cwd(), "public", "data", "public_share.json"), "utf8"));
  const yearParam = Number(new URL(req.url).searchParams.get("year"));
  const latest = rows[rows.length - 1];
  const row = (yearParam > 0 && rows.filter((r) => r.date.startsWith(String(yearParam))).at(-1)) || latest;
  const year = row.date.slice(0, 4);
  const pct = (row.public_share * 100).toFixed(1);
  const dots = Array.from({ length: 100 }, (_, i) => i < Math.round(row.public_share * 100));

  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", background: "#f3ecdc", color: "#1b1a33", padding: 64, fontFamily: "serif" }}>
        <div style={{ display: "flex", flexDirection: "column", width: 640 }}>
          <div style={{ fontSize: 26, color: "#f3ecdc", background: "#1b1a33", padding: "4px 12px", alignSelf: "flex-start", letterSpacing: 3, textTransform: "uppercase", fontFamily: "sans-serif" }}>
            {`Hot Potato · ${year}`}
          </div>
          <div style={{ fontSize: 168, lineHeight: 1, marginTop: 36, color: "#1f6fe0", fontWeight: 800 }}>{`${pct}%`}</div>
          <div style={{ fontSize: 40, marginTop: 20, lineHeight: 1.2 }}>of US household debt was held by the public sector</div>
          <div style={{ fontSize: 24, marginTop: "auto", color: "#5d5849", fontFamily: "sans-serif" }}>
            Federal Reserve Z.1 · mortgages and consumer credit
          </div>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", width: 420, height: 420, marginLeft: "auto", alignSelf: "center", gap: 6 }}>
          {dots.map((pub, i) => (
            <div
              key={i}
              style={{ width: 36, height: 36, borderRadius: 18, background: pub ? "#1f6fe0" : "#f2631c" }}
            />
          ))}
        </div>
      </div>
    ),
    { width: 1200, height: 630 },
  );
}
