<script setup lang="ts">
import {
  computed,
  ref,
} from "vue";

import {
  useRouter,
} from "vue-router";

import {
  useLocale,
} from "../composables/useLocale";

import {
  useAuth,
} from "../composables/useAuth";


const router = useRouter();

const {
  t,
  locale,
} = useLocale();

const auth = useAuth();

const currentPassword =
  ref("");

const newPassword =
  ref("");

const confirmPassword =
  ref("");

const errorMessage =
  ref<string | null>(null);

const loading = ref(false);

const isRTL = computed(
  () =>
    locale.value === "he"
);


function extractError(
  error: any
): string {
  const data =
    error?.response?.data;

  if (
    data?.current_password
    ?.length
  ) {
    return String(
      data.current_password[0]
    );
  }

  if (
    data?.new_password
    ?.length
  ) {
    return String(
      data.new_password[0]
    );
  }

  return (
    data?.detail ||
    t(
      "auth.changePassword.error"
    )
  );
}


async function submit() {
  errorMessage.value = null;

  if (
    !currentPassword.value ||
    !newPassword.value ||
    !confirmPassword.value
  ) {
    errorMessage.value =
      t(
        "auth.changePassword.required"
      );

    return;
  }

  if (
    newPassword.value !==
    confirmPassword.value
  ) {
    errorMessage.value =
      t(
        "auth.changePassword.notMatch"
      );

    return;
  }

  if (
    currentPassword.value ===
    newPassword.value
  ) {
    errorMessage.value =
      t(
        "auth.changePassword.samePassword"
      );

    return;
  }

  loading.value = true;

  try {
    await auth.changePassword({
     current_password:
       currentPassword.value,

     new_password:
       newPassword.value,
    });

    await router.replace({
      name: "Home",
    });
  } catch (error: any) {
    errorMessage.value =
      extractError(error);
  } finally {
    loading.value = false;
  }
}
</script>


<template>
  <div
    :dir="
      isRTL
        ? 'rtl'
        : 'ltr'
    "
    class="
      min-h-screen
      bg-gradient-to-br
      from-canvas
      to-canvas-deep
      flex
      items-center
      justify-center
      px-4
      py-8
    "
  >
    <div
      class="
        w-full
        max-w-lg
        bg-white
        rounded-3xl
        border
        border-line/70
        shadow-xl
        shadow-black/5
        p-6
        sm:p-8
      "
    >
      <div
        class="
          flex
          items-start
          gap-4
          mb-7
        "
      >
        <div
          class="
            w-12
            h-12
            rounded-xl
            bg-brand/10
            text-brand
            flex
            items-center
            justify-center
            flex-shrink-0
          "
        >
          <svg
            class="
              w-6
              h-6
            "
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="
                M12 11c0-1.105
                .895-2 2-2
                s2 .895 2 2
                v1
                h1
                a2 2 0 012 2
                v5
                a2 2 0 01-2 2
                H7
                a2 2 0 01-2-2
                v-5
                a2 2 0 012-2
                h1
                v-1
                a4 4 0 118 0
              "
            />
          </svg>
        </div>

        <div>
          <h1
            class="
              text-2xl
              font-bold
              text-ink
            "
          >
            {{
              t(
                "auth.changePassword.title"
              )
            }}
          </h1>

          <p
            class="
              mt-1
              text-sm
              leading-6
              text-muted
            "
          >
            {{
              t(
                "auth.changePassword.subtitle"
              )
            }}
          </p>
        </div>
      </div>

      <form
        class="
          space-y-5
        "
        @submit.prevent="submit"
      >
        <div>
          <label
            for="current-password"
            class="
              block
              text-sm
              font-medium
              text-ink-soft
              mb-2
            "
          >
            {{
              t(
                "auth.changePassword.current"
              )
            }}
          </label>

          <input
            id="current-password"
            v-model="
              currentPassword
            "
            type="password"
            autocomplete="current-password"
            class="
              w-full
              h-12
              px-4
              rounded-xl
              border
              border-line-strong
              outline-none
              transition
              focus:border-brand
              focus:ring-4
              focus:ring-brand/10
            "
          />
        </div>

        <div>
          <label
            for="new-password"
            class="
              block
              text-sm
              font-medium
              text-ink-soft
              mb-2
            "
          >
            {{
              t(
                "auth.changePassword.new"
              )
            }}
          </label>

          <input
            id="new-password"
            v-model="newPassword"
            type="password"
            autocomplete="new-password"
            class="
              w-full
              h-12
              px-4
              rounded-xl
              border
              border-line-strong
              outline-none
              transition
              focus:border-brand
              focus:ring-4
              focus:ring-brand/10
            "
          />
        </div>

        <div>
          <label
            for="confirm-password"
            class="
              block
              text-sm
              font-medium
              text-ink-soft
              mb-2
            "
          >
            {{
              t(
                "auth.changePassword.confirm"
              )
            }}
          </label>

          <input
            id="confirm-password"
            v-model="
              confirmPassword
            "
            type="password"
            autocomplete="new-password"
            class="
              w-full
              h-12
              px-4
              rounded-xl
              border
              border-line-strong
              outline-none
              transition
              focus:border-brand
              focus:ring-4
              focus:ring-brand/10
            "
          />
        </div>

        <div
          v-if="errorMessage"
          role="alert"
          class="
            rounded-xl
            border
            border-red-200
            bg-red-50
            px-4
            py-3
            text-sm
            text-red-700
          "
        >
          {{ errorMessage }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="
            w-full
            h-12
            rounded-xl
            bg-brand
            text-white
            font-semibold
            shadow-lg
            shadow-brand/20
            hover:bg-brand-deep
            transition
            disabled:bg-faint
            disabled:cursor-not-allowed
          "
        >
          {{
            loading
              ? t(
                  "auth.changePassword.saving"
                )
              : t(
                  "auth.changePassword.submit"
                )
          }}
        </button>
      </form>
    </div>
  </div>
</template>