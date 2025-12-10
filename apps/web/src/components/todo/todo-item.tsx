import { Link } from "react-router-dom";
import { Button } from "../ui/button";

export default function TodoItem({
  id,
  content,
}: {
  id: string;
  content: string;
}) {
  return (
    <div>
      <Link to={`/todos/${id}`}>{content}</Link>
      <Button>삭제</Button>
    </div>
  );
}
