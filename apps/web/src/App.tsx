import { Outlet, Route, Routes } from "react-router-dom";
import { Button } from "./components/ui/button";
import SignInPage from "./pages/sign-in-page";
import SignUpPage from "./pages/sign-up-page";
import IndexPage from "./pages/index-page";
import ChatRoom from "./pages/chatroom";
import CounterPage from "./pages/counter";

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
    </Routes>
  );
}

export default App;
