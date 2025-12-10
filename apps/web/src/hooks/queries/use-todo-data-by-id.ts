import { fetchTodoById } from "@/api/fetch-todo-by-id";
import { fetchTodos } from "@/api/fetch-todos";
import { useQuery } from "@tanstack/react-query";

export function useTodoDataById(id: string) {
  return useQuery({
    queryKey: ["todos", id],
    queryFn: () => fetchTodoById(id),
    // refetchInterval: 1000
  });
}
