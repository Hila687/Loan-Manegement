<script setup lang="ts">
import {
  computed,
  ref,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import {
  useLocale,
} from "../composables/useLocale";

import LanguageSelector
  from "../components/LanguageSelector.vue";

import {
  useAuth,
} from "../composables/useAuth";


const router = useRouter();
const route = useRoute();

const {
  t,
  locale,
} = useLocale();

const auth = useAuth();

const username = ref("");
const password = ref("");
const errorMessage =
  ref<string | null>(null);

const isRTL = computed(
  () =>
    locale.value === "he"
);



async function submit() {
  errorMessage.value = null;

  if (
    !username.value.trim() ||
    !password.value
  ) {
    errorMessage.value =
      t(
        "auth.login.required"
      );

    return;
  }

  try {
    const user =
      await auth.login({
      username:
        username.value.trim(),

     password:
      password.value,
    });

    if (
      user.must_change_password
    ) {
      await router.replace({
        name:
          "ChangePassword",
      });

      return;
    }

    const redirect =
      typeof route.query
        .redirect === "string"
        ? route.query.redirect
        : "/";

    await router.replace(
      redirect
    );
  } catch (error: any) {
    const status =
      error?.response?.status;

    if (status === 429) {
      errorMessage.value =
        t(
          "auth.login.tooManyAttempts"
        );

      return;
    }

    errorMessage.value =
      error?.response?.data
        ?.detail ||
      t(
        "auth.login.invalid"
      );
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
      via-surface-muted
      to-brand-soft
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
        max-w-md
      "
    >
      <div
        class="
          bg-white/90
          backdrop-blur-xl
          rounded-3xl
          shadow-2xl
          shadow-brand/10
          border
          border-white
          overflow-visible
          relative
        "
      >
        <div
          class="
            px-6
            sm:px-8
            pt-8
            pb-6
            text-center
          "
        >
          <div
            class="
              mx-auto
              w-16
              h-16
              rounded-2xl
              bg-gradient-to-br
              from-brand
              to-brand-deep
              flex
              items-center
              justify-center
              shadow-lg
              shadow-brand/25
              mb-5
            "
          >
            <svg
              class="
                w-9
                h-9
                text-white
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
                  M3 12l2-3
                  m0 0l7-4
                  7 4
                  M5 9v10
                  a1 1 0 001 1
                  h12
                  a1 1 0 001-1
                  V9
                "
              />
            </svg>
          </div>

          <p
            class="
              text-sm
              font-semibold
              text-brand
              mb-1
            "
          >
            {{
              t(
                "auth.login.organization"
              )
            }}
          </p>

          <h1
            class="
              text-2xl
              sm:text-3xl
              font-bold
              text-ink
            "
          >
            {{
              t(
                "auth.login.title"
              )
            }}
          </h1>

          <p
            class="
              mt-2
              text-sm
              text-muted
            "
          >
            {{
              t(
                "auth.login.subtitle"
              )
            }}
          </p>
        </div>

        <form
          class="
            px-6
            sm:px-8
            pb-8
            space-y-5
          "
          @submit.prevent="submit"
        >
          <div>
            <label
              for="username"
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
                  "auth.login.username"
                )
              }}
            </label>

            <input
              id="username"
              v-model="username"
              type="text"
              autocomplete="username"
              required
              class="
                w-full
                h-12
                px-4
                rounded-xl
                border
                border-line-strong
                bg-white
                text-ink
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
              for="password"
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
                  "auth.login.password"
                )
              }}
            </label>

            <input
              id="password"
              v-model="password"
              type="password"
              autocomplete="current-password"
              required
              class="
                w-full
                h-12
                px-4
                rounded-xl
                border
                border-line-strong
                bg-white
                text-ink
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
            role="alert"
          >
            {{ errorMessage }}
          </div>

          <button
            type="submit"
            :disabled="
              auth.loading.value
            "
            class="
              w-full
              h-12
              rounded-xl
              bg-gradient-to-r
              from-brand
              to-brand-deep
              text-white
              font-semibold
              shadow-lg
              shadow-brand/20
              transition-all
              hover:shadow-xl
              hover:shadow-brand/25
              active:scale-[0.99]
              disabled:opacity-60
              disabled:cursor-not-allowed
            "
          >
            {{
              auth.loading.value
                ? t(
                    "auth.login.loading"
                  )
                : t(
                    "auth.login.submit"
                  )
            }}
          </button>

          <div class="relative z-50 flex justify-center">
            <LanguageSelector />
          </div>
        </form>
      </div>

      <p
        class="
          mt-5
          text-center
          text-xs
          text-muted
        "
      >
        {{
          t(
            "auth.login.securityNote"
          )
        }}
      </p>
    </div>
  </div>
</template>