import { useCount } from "@/stores/count";

export default function Viewer() {
  const count = useCount();
  return <div>{count}</div>;
}
