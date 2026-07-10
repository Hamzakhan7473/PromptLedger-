/**
 * Firebase ID token bridge for API requests.
 * Register a token getter from AuthProvider (client-side).
 */

export type AuthTokenGetter = () => Promise<string | null>;

let authTokenGetter: AuthTokenGetter | null = null;

export function setAuthTokenGetter(getter: AuthTokenGetter): void {
  authTokenGetter = getter;
}

export async function getSessionToken(): Promise<string | null> {
  if (!authTokenGetter) return null;
  return authTokenGetter();
}

export async function isAuthenticated(): Promise<boolean> {
  const token = await getSessionToken();
  return Boolean(token);
}
