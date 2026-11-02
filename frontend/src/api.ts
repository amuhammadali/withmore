let csrfToken = localStorage.getItem("wm_csrf") || "";
let shopToken = localStorage.getItem("wm_shop_token") || "";

export function setCsrf(token: string) {
  csrfToken = token;
  localStorage.setItem("wm_csrf", token);
}

export function setShopToken(token: string) {
  shopToken = token;
  localStorage.setItem("wm_shop_token", token);
}

export function getShopToken() {
  return shopToken;
}

export async function adminFetch<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (csrfToken) {
    headers.set("x-csrf-token", csrfToken);
  }
  const res = await fetch(path, {
    ...options,
    headers,
    credentials: "include",
  });
  if (!res.ok) {
    let msg = `Error ${res.status}`;
    try {
      const data = await res.json();
      msg = data.detail || msg;
    } catch {
      // ignore
    }
    const err: any = new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
    err.status = res.status;
    if (res.status === 401 && !path.includes("/login")) {
      if (window.location.pathname.startsWith("/admin") && window.location.pathname !== "/admin/login") {
        setTimeout(() => {
          window.location.href = "/admin/login";
        }, 1200);
      }
    }
    throw err;
  }
  return res.json();
}

export async function shopFetch<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (shopToken) {
    headers.set("x-shop-token", shopToken);
  }
  const res = await fetch(path, { ...options, headers });
  if (!res.ok) {
    let msg = `Error ${res.status}`;
    try {
      const data = await res.json();
      msg = data.detail || msg;
    } catch {
      // ignore
    }
    const err: any = new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
    err.status = res.status;
    if (res.status === 401 && !path.includes("/login")) {
      if (window.location.pathname.startsWith("/admin") && window.location.pathname !== "/admin/login") {
        setTimeout(() => {
          window.location.href = "/admin/login";
        }, 1200);
      }
    }
    throw err;
  }
  return res.json();
}

