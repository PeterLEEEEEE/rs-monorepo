import { Navigate, Route, Routes } from "react-router-dom";

export default function RootRoute() {
    return <Routes>
        <Route path="/sign-in" />
        <Route path="/sign-up" />

        <Route path="/" />
        <Route path="/profile/:userId" />
        <Route path="/chatroom/:chatroomId" />
        <Route path="*" element={<Navigate to="/" />} />
    </Routes>
}