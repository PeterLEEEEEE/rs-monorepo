import { createTodo } from "@/api/create-todo";
import { useMutation } from "@tanstack/react-query";

export function useCreateTodoMutation() {
  return useMutation({
    mutationFn: createTodo,

    onSuccess: () => {
      // Invalidate and refetch
      // queryClient.invalidateQueries({ queryKey: ["todos"] });
      window.location.reload();
    },
    onError: (error) => {
      console.error("Error creating todo:", error);
    },
  });
}
