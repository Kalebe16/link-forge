const API_URL = import.meta.env.VITE_API_URL;

type RegisterPayload = {
  email: string | null;
  password: string | null;
};

type LoginPayload = {
  email: string | null;
  password: string | null;
};

type CreateLinkPayload = {
  url: string | null;
};

type UpdateLinkPayload = {
  id: number | null;
  url: string | null;
};

type DeleteLinkPayload = {
  id: number | null;
};

const fetchWithAutoRefresh = async (req: Request) => {
  let resp = await fetch(req.clone());

  if (resp.status == 401) {
    const refreshResp = await refresh();

    if (refreshResp.ok) {
      resp = await fetch(req.clone());
    }
  }

  return resp;
};

const register = async ({ email, password }: RegisterPayload) => {
  const resp = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email,
      password: password,
    }),
  });
  return resp;
};

const login = async ({ email, password }: LoginPayload) => {
  const resp = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email,
      password: password,
    }),
  });
  return resp;
};

const refresh = async () => {
  const resp = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });
  return resp;
};

const logout = async () => {
  const req = new Request(`${API_URL}/auth/logout`, {
    method: "GET",
    credentials: "include",
  });
  const resp = await fetchWithAutoRefresh(req);
  return resp;
};

const me = async () => {
  const req = new Request(`${API_URL}/auth/me`,{
    method: "GET",
    credentials: "include"
  });
  const resp = await fetchWithAutoRefresh(req);
  return resp;
}

const listLinks = async () => {
  const req = new Request(`${API_URL}/links`, {
    method: "GET",
    credentials: "include",
  });
  const resp = await fetchWithAutoRefresh(req);
  return resp;
};

const createLink = async ({ url }: CreateLinkPayload) => {
  const req = new Request(`${API_URL}/links`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      url: url,
    }),
  });
  const resp = await fetchWithAutoRefresh(req);
  return resp;
};

const updateLink = async ({ id, url }: UpdateLinkPayload) => {
  const req = new Request(`${API_URL}/links/${id}`, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      url: url,
    }),
  });
  const resp = await fetchWithAutoRefresh(req);
  return resp;
};

const deleteLink = async ({ id }: DeleteLinkPayload) => {
  const req = new Request(`${API_URL}/links/${id}`, {
    method: "DELETE",
    credentials: "include",
  });
  const resp = await fetchWithAutoRefresh(req);
  return resp;
};

export {
  register,
  login,
  refresh,
  logout,
  me,
  listLinks,
  createLink,
  updateLink,
  deleteLink,
};
