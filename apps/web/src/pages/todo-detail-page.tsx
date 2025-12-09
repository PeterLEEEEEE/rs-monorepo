import { useTodoDataById } from "@/hooks/queries/use-todo-data-by-id";
import { useParams } from "react-router-dom";

export default function TodoDetailPage() {
    const { id } = useParams<{ id: string }>();

    const { data, isLoading, error } = useTodoDataById(Number(id));
    if (isLoading) {
        return <div>Loading...</div>;
    }
    if (error || !data) {
        return <div>Error loading todo detail</div>;
    }

    return <div>Todo Detail Page for ID: {id}, Content: {data.content}</div>;
}