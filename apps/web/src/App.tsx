import { Outlet, Route, Routes } from "react-router-dom";
import { Button } from "./components/ui/button";
import SignInPage from "./pages/sign-in-page";
import SignUpPage from "./pages/sign-up-page";
import IndexPage from "./pages/index-page";
import ChatRoom from "./pages/chatroom";
import CounterPage from "./pages/counter";
import TodoListPage from "./pages/todo-list-page";
import TodoDetailPage from "./pages/todo-detail-page";
import ComplexDetailPage from "./pages/complex-detail-page";
import MarketPage from "./pages/market-page";

function AuthLayout() {
  return (
    <div>
      <h1>Auth Layout</h1>
      <Outlet />
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<IndexPage />} />
      <Route path="/counter" element={<CounterPage />} />
      <Route element={<AuthLayout />}>
        <Route path="/sign-in" element={<SignInPage />} />
        <Route path="/sign-up" element={<SignUpPage />} />
      </Route>
      <Route path="/chatroom" element={<ChatRoom />} />
      <Route path="/todos" element={<TodoListPage />} />
      <Route path="/todos/:id" element={<TodoDetailPage />} />
      <Route path="/complex" element={<ComplexDetailPage />} />
      <Route path="/complex/:complexId" element={<ComplexDetailPage />} />
      <Route path="/market" element={<MarketPage />} />
      <Route path="/market/:regionCode" element={<MarketPage />} />
    </Routes>
  );
}

export default App;
