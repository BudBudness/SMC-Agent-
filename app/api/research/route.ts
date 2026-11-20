import { NextResponse } from "next/server";
import { gunzipSync } from "node:zlib";
import { getCloudflareContext } from "@opennextjs/cloudflare";

const BASE = "https://github.com/BudBudness/SMC-Agent-/releases/download/research-data";

async function rel(name: string) {
  const response = await fetch(BASE + "/" + name, { cache: "no-store" });
  if (!response.ok) throw new Error("release unavailable: " + name);
  return response;
}

async function canonical() {
  const [reportResponse, mtfResponse] = await Promise.all([
    rel("EURUSD_research_report.json"),
    rel("EURUSD_MTF_dashboard.json.gz"),
  ]);
  return {
    report: await reportResponse.json() as Record<string, any>,
    mtf: JSON.parse(gunzipSync(Buffer.from(await mtfResponse.arrayBuffer())).toString("utf8")) as Record<string, any>,
  };
}

function researchApiUrl(path: string): string {
  return path;
}

async function proxy(request: Request, path: string, init: RequestInit = {}) {
  const accessJwt = request.headers.get("Cf-Access-Jwt-Assertion");
  const headers = new Headers(init.headers);
  if (accessJwt) headers.set("Cf-Access-Jwt-Assertion", accessJwt);
  if (init.body) headers.set("Content-Type", "application/json");
  const { env } = getCloudflareContext();
  const response = await env.RESEARCH_API.fetch(new Request("https://research-api.internal" + researchApiUrl(path), {
    ...init,
    headers,
  }));
  const body = await response.text();
  return new Response(body, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("Content-Type") || "application/json",
      "Cache-Control": "no-store",
    },
  });
}

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const resource = url.searchParams.get("resource");
    if (resource) {
      const query = url.searchParams.toString();
      return await proxy(request, "/api/research?" + query);
    }
    const data = await canonical();
    return NextResponse.json({
      report: data.report,
      mtf: data.mtf,
      source: data.report?.dataset || {},
    });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Research data unavailable" },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    return await proxy(request, "/api/research", {
      method: "POST",
      body: JSON.stringify(body),
    });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Research operation failed" },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }
}
