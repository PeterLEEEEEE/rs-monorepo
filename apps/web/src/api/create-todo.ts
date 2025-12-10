import { API_URL } from "@/lib/constants";

export async function createTodo(content: string) {
  const response = await fetch(`${API_URL}/todos`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content, isDone: false }),
  });

  if (!response.ok) {
    throw new Error("Failed to create todo");
  }

  const data = await response.json();
  return data;
}
