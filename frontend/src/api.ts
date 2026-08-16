export async function getJson<T>(path: string, params: Record<string, unknown> = {}, signal?: AbortSignal): Promise<T> {
  const url = new URL(path, `${location.origin}${import.meta.env.BASE_URL}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") url.searchParams.set(key, String(value));
  });
  const response = await fetch(url, { signal });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || response.statusText || `HTTP ${response.status}`);
  }
  return response.json();
}

export function requestGate() {
  let current: AbortController | undefined;
  return {
    next: () => (current?.abort(), current = new AbortController()),
    isCurrent: (request: AbortController) => current === request,
    abort: () => current?.abort(),
  };
}
