export function formatActionLabel(action: string): string {
  return action
    .toLowerCase()
    .split("_")
    .map((word) => (word ? word.charAt(0).toUpperCase() + word.slice(1) : ""))
    .join(" ");
}

export function shortUserLabel(id: string | null | undefined): string {
  if (!id) return "User";
  return "User " + id.slice(0, 8);
}

