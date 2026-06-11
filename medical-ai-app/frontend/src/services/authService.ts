import { api } from "./api";

export type LoginPayload = {
  username: string;
  password: string;
};

export type AuthUser = {
  username: string;
  full_name: string;
  role: string;
  active: boolean;
  must_change_password: boolean;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>("/auth/login", payload);
  return data;
}

export async function getMe(): Promise<AuthUser> {
  const { data } = await api.get<AuthUser>("/auth/me");
  return data;
}
