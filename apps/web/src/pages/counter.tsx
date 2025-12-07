import { Button } from "@/components/ui/button";
import { useCountStore } from "@/stores/count";

export default function CounterPage() {
  const { count, increase, decrease } = useCountStore();

  return (
    <div>
      <h1 className="text-2xl font-bold">Counter Page</h1>
      <div>
        <Button onClick={decrease}>-</Button>
        <span>{count}</span>
        <Button onClick={increase}>+</Button>
      </div>
    </div>
  );
}
