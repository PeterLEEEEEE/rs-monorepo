import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { login } from "@/api/auth";

interface LoginParams {
  email: string;
  password: string;
}

export function useLoginMutation() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: ({ email, password }: LoginParams) => login(email, password),
    onSuccess: (data) => {
      // Access Token을 localStorage에 저장
      localStorage.setItem("access_token", data.access_token);

      // 사용자 정보를 캐시에 저장
      queryClient.setQueryData(["user", "me"], data.user);

      // 메인 페이지로 이동
      navigate("/");
    },
  });
}
