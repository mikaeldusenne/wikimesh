export function explorerQuery(search: string, identifier: string | null) {
  return {
    ...(search ? { search } : {}),
    ...(identifier ? { identifier } : {}),
  };
}

export function pickIdentifier(current: string | null, identifiers: string[]) {
  return current || identifiers.at(-1) || null;
}
