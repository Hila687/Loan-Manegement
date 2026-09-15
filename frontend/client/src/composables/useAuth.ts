import {
  computed,
  ref,
} from "vue";

import api, {
  ensureCsrf,
} from "../services/api";

export type UserRole =
  | "admin"
  | "trustee"
  | "borrower"
  | "donor";

export type AuthUser = {
  id:
    | string
    | number;

  username:
    string;

  first_name:
    string;

  last_name:
    string;

  email:
    string;

  role:
    UserRole;

  must_change_password:
    boolean;
};

type LoginPayload = {
  username:
    string;

  password:
    string;
};

type ChangePasswordPayload = {
  current_password:
    string;

  new_password:
    string;
};

const user =
  ref<AuthUser | null>(
    null
  );

const loading =
  ref(false);

const initialized =
  ref(false);

function normalizeRole(
  value: unknown
): UserRole | null {
  const role =
    String(
      value || ""
    )
      .trim()
      .toLowerCase();

  if (
    role === "admin"
  ) {
    return "admin";
  }

  if (
    role === "trustee"
  ) {
    return "trustee";
  }

  if (
    role === "borrower"
  ) {
    return "borrower";
  }

  if (
    role === "donor"
  ) {
    return "donor";
  }

  return null;
}

function normalizeUser(
  data: any
): AuthUser | null {
  if (!data) {
    return null;
  }

  const source =
    data.user ||
    data;

  if (
    data.authenticated ===
    false
  ) {
    return null;
  }

  const role =
    normalizeRole(
      data.role ||
      source.role ||
      source.role_name ||
      source.profile
        ?.role
        ?.name ||
      source.profile
        ?.role
    );

  if (!role) {
    return null;
  }

  return {
    id:
      source.id ??
      source.user_id ??
      "",

    username:
      String(
        source.username ||
        ""
      ),

    first_name:
      String(
        source.first_name ||
        ""
      ),

    last_name:
      String(
        source.last_name ||
        ""
      ),

    email:
      String(
        source.email ||
        ""
      ),

    role,

    must_change_password:
      Boolean(
        data
          .must_change_password ??
        source
          .must_change_password ??
        source.profile
          ?.must_change_password ??
        false
      ),
  };
}

async function initialize():
  Promise<void> {
  if (
    initialized.value ||
    loading.value
  ) {
    return;
  }

  loading.value =
    true;

  try {
    const response =
      await api.get(
        "/auth/me/"
      );

    user.value =
      normalizeUser(
        response.data
      );
  } catch {
    user.value =
      null;
  } finally {
    initialized.value =
      true;

    loading.value =
      false;
  }
}

async function login(
  payload:
    LoginPayload
): Promise<AuthUser> {
  loading.value =
    true;

  try {
    await ensureCsrf();

    const response =
      await api.post(
        "/auth/login/",
        payload
      );

    const normalized =
      normalizeUser(
        response.data
      );

    if (!normalized) {
      throw new Error(
        "Invalid login response"
      );
    }

    user.value =
      normalized;

    initialized.value =
      true;

    return normalized;
  } finally {
    loading.value =
      false;
  }
}

async function logout():
  Promise<void> {
  loading.value =
    true;

  try {
    await ensureCsrf();

    await api.post(
      "/auth/logout/",
      {}
    );
  } finally {
    user.value =
      null;

    initialized.value =
      true;

    loading.value =
      false;
  }
}

async function changePassword(
  payload:
    ChangePasswordPayload
): Promise<void> {
  loading.value =
    true;

  try {
    await ensureCsrf();

    await api.post(
      "/auth/change-password/",
      payload
    );

    if (
      user.value
    ) {
      user.value = {
        ...user.value,

        must_change_password:
          false,
      };
    }
  } finally {
    loading.value =
      false;
  }
}

const role =
  computed<
    UserRole | null
  >(
    () =>
      user.value
        ?.role ||
      null
  );

const isAuthenticated =
  computed(
    () =>
      Boolean(
        user.value
      )
  );

const isAdmin =
  computed(
    () =>
      role.value ===
      "admin"
  );

const isTrustee =
  computed(
    () =>
      role.value ===
      "trustee"
  );

const isBorrower =
  computed(
    () =>
      role.value ===
      "borrower"
  );

const isDonor =
  computed(
    () =>
      role.value ===
      "donor"
  );

const mustChangePassword =
  computed(
    () =>
      Boolean(
        user.value
          ?.must_change_password
      )
  );

const displayName =
  computed(() => {
    if (
      !user.value
    ) {
      return "";
    }

    const fullName =
      `${user.value.first_name} ${user.value.last_name}`
        .trim();

    return (
      fullName ||
      user.value.username
    );
  });

export function useAuth() {
  return {
    user,
    loading,
    initialized,

    role,
    isAuthenticated,
    isAdmin,
    isTrustee,
    isBorrower,
    isDonor,

    mustChangePassword,
    displayName,

    initialize,
    login,
    logout,
    changePassword,
  };
}