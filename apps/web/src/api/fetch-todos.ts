import { API_URL } from "@/lib/constants";
import type { Todo } from "@/types/todos";

export async function fetchTodos() {
  const response = await fetch(`${API_URL}/todos`);
  if (!response.ok) {
    throw new Error("Failed to fetch todos");
  }
  const data: Todo[] = await response.json();
  return data;
}
