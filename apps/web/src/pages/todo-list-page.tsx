import { fetchTodos } from "@/api/fetch-todos";
import { useTodosData } from "@/hooks/queries/use-todos.data";

export default function TodoListPage() {
  const { data: todos, isLoading, error } = useTodosData();

  if (error) {
    return <div>Error loading todos</div>;
  }
  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Todo List</h1>
      <ul>
        {todos?.map((todo) => (
          <li key={todo.id}>
            {todo.content} {todo.isDone ? "(Completed)" : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}
