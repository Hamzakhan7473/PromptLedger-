const STORAGE_KEY = "legal_eval_org_api_key";

export function getOrgApiKey(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(STORAGE_KEY);
}

export function setOrgApiKey(key: string): void {
  localStorage.setItem(STORAGE_KEY, key);
}

export function clearOrgApiKey(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export function hasOrgApiKey(): boolean {
  return Boolean(getOrgApiKey());
}
