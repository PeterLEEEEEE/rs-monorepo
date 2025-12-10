import { fetchTodos } from "@/api/fetch-todos";
import TodoEditor from "@/components/todo/todo-editor";
import TodoItem from "@/components/todo/todo-item";
import { useTodosData } from "@/hooks/queries/use-todos-data";

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
      <TodoEditor />
      <ul>
        {todos?.map((todo) => (
          <TodoItem key={todo.id} id={todo.id} content={todo.content} />
        ))}
      </ul>
    </div>
  );
}
