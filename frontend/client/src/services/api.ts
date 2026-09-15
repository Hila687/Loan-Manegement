import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api";

let csrfToken = "";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 20000,
  headers: {
    Accept: "application/json",
  },
});

function readCookie(
  name: string
): string {
  if (
    typeof document ===
    "undefined"
  ) {
    return "";
  }

  const prefix =
    `${name}=`;

  const cookies =
    document.cookie.split(";");

  for (
    const cookie
    of cookies
  ) {
    const value =
      cookie.trim();

    if (
      value.startsWith(
        prefix
      )
    ) {
      return decodeURIComponent(
        value.slice(
          prefix.length
        )
      );
    }
  }

  return "";
}

export function setCsrfToken(
  value: string
): void {
  csrfToken =
    value || "";
}

export async function ensureCsrf():
  Promise<string> {
  const response =
    await api.get(
      "/auth/csrf/"
    );

  const token =
    String(
      response.data
        ?.csrfToken ||
      response.data
        ?.csrf_token ||
      ""
    );

  if (token) {
    setCsrfToken(
      token
    );
  }

  return (
    csrfToken ||
    readCookie(
      "csrftoken"
    )
  );
}

api.interceptors.request.use(
  (config) => {
    const method =
      String(
        config.method ||
        "get"
      ).toLowerCase();

    const unsafeMethod =
      ![
        "get",
        "head",
        "options",
        "trace",
      ].includes(
        method
      );

    if (unsafeMethod) {
      const token =
        csrfToken ||
        readCookie(
          "csrftoken"
        );

      if (token) {
        config.headers.set(
          "X-CSRFToken",
          token
        );
      }
    }

    return config;
  }
);

export default api;