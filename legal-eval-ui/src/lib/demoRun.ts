/** Public demo run — share token allows anonymous read-only access via the API. */

export const DEMO_RUN_ID =
  process.env.NEXT_PUBLIC_DEMO_RUN_ID ?? "demo";

export const DEMO_SHARE_TOKEN =
  process.env.NEXT_PUBLIC_DEMO_SHARE_TOKEN ?? "le_demo_public_v1";

export function demoRunPath(
  view: "summary" | "grid" | "samples" = "summary",
): string {
  const params = new URLSearchParams({ token: DEMO_SHARE_TOKEN });
  return `/runs/${DEMO_RUN_ID}/${view}?${params.toString()}`;
}
