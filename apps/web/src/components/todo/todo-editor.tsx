import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { useState } from "react";
import { useCreateTodoMutation } from "@/hooks/mutations/create-todo-mutation";

export default function TodoEditor() {
  const { mutate, isPending } = useCreateTodoMutation();
  const [content, setContent] = useState("");

  const handleAddClick = () => {
    if (content.trim() === "") {
      return;
    }
    mutate(content);
    setContent("");
  };

  return (
    <div>
      <Input value={content} onChange={(e) => setContent(e.target.value)} />
      <Button disabled={isPending} onClick={handleAddClick}>
        추가
      </Button>
    </div>
  );
}
