<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useLocale } from "../composables/useLocale";
import LanguageSelector from "../components/LanguageSelector.vue";
import { useAuth } from "../composables/useAuth";
import api from "../services/api";

const router = useRouter();
const route = useRoute();
const { t, locale } = useLocale();
const auth = useAuth();

const isRTL = computed(() => locale.value === "he");

// "code" = ID number + phone + SMS code (default, no password).
// "password" = username / ID / phone + password (fallback, e.g. admins).
const mode = ref<"code" | "password">("code");

// Which code channels the server has switched on. With no SMS and no
// email set up, the only way in is ID number / username + password.
const codeChannels = ref<("SMS" | "EMAIL")[]>([]);
const codeLoginAvailable = computed(() => codeChannels.value.length > 0);

onMounted(async () => {
  try {
    const { data } = await api.get("/auth/config/");
    const channels: ("SMS" | "EMAIL")[] = [];
    if (data?.code_login?.sms) channels.push("SMS");
    if (data?.code_login?.email) channels.push("EMAIL");
    codeChannels.value = channels;
  } catch {
    codeChannels.value = [];
  }

  if (!codeChannels.value.length) {
    mode.value = "password";
  } else if (!codeChannels.value.includes(channel.value)) {
    channel.value = codeChannels.value[0];
  }
});

// --- code sign-in -------------------------------------------------------
const step = ref<"details" | "code">("details");
const idNumber = ref("");
const phone = ref("");
const email = ref("");
const code = ref("");
const channel = ref<"SMS" | "EMAIL">("SMS");

// ID number + the phone (SMS) or the email (EMAIL) the code goes to.
function identity() {
  return channel.value === "EMAIL"
    ? { id_number: idNumber.value.trim(), email: email.value.trim(), channel: channel.value }
    : { id_number: idNumber.value.trim(), phone: phone.value.trim(), channel: channel.value };
}
const sendingCode = ref(false);
const devCode = ref("");
const resendIn = ref(0);
let resendTimer: number | undefined;

// --- password sign-in ---------------------------------------------------
const username = ref("");
const password = ref("");
const showPassword = ref(false);

const errorMessage = ref<string | null>(null);
const infoMessage = ref<string | null>(null);
const showForgotHelp = ref(false);

function digitsOnly(value: string): string {
  return value.replace(/\D/g, "");
}

function startResendTimer(seconds: number): void {
  resendIn.value = seconds;
  window.clearInterval(resendTimer);
  resendTimer = window.setInterval(() => {
    resendIn.value -= 1;
    if (resendIn.value <= 0) {
      window.clearInterval(resendTimer);
    }
  }, 1000);
}

onBeforeUnmount(() => window.clearInterval(resendTimer));

function switchMode(next: "code" | "password"): void {
  mode.value = next;
  errorMessage.value = null;
  infoMessage.value = null;
}

function messageForError(error: any): string {
  if (!error?.response) {
    return t("auth.login.network");
  }

  const status = error.response.status;
  const errorCode = error.response.data?.code;

  const byCode: Record<string, string> = {
    too_many_attempts: "auth.login.tooManyAttempts",
    rate_limited: "auth.login.tooManyAttempts",
    too_soon: "auth.code.tooSoon",
    ambiguous_identifier: "auth.login.ambiguous",
    no_access: "auth.login.noAccess",
    invalid_code: "auth.code.invalid",
    expired: "auth.code.expired",
    send_failed: "auth.code.sendFailed",
    missing_fields: "auth.code.required",
  };

  if (errorCode && byCode[errorCode]) {
    return t(byCode[errorCode]);
  }

  if (status === 429) {
    return t("auth.login.tooManyAttempts");
  }

  if (status === 403) {
    return t("auth.login.noAccess");
  }

  return t("auth.login.invalid");
}

async function afterLogin(mustChangePassword: boolean): Promise<void> {
  if (mustChangePassword) {
    await router.replace({ name: "ChangePassword" });
    return;
  }

  const redirect =
    typeof route.query.redirect === "string" ? route.query.redirect : "/";

  await router.replace(redirect);
}

async function sendCode(): Promise<void> {
  errorMessage.value = null;
  infoMessage.value = null;

  const contactMissing =
    channel.value === "EMAIL"
      ? !email.value.includes("@")
      : digitsOnly(phone.value).length < 9;

  if (digitsOnly(idNumber.value).length < 5 || contactMissing) {
    errorMessage.value = t("auth.code.required");
    return;
  }

  sendingCode.value = true;

  try {
    const result = await auth.requestLoginCode(identity());

    devCode.value = result.dev_code || "";
    step.value = "code";
    code.value = "";
    infoMessage.value = t(
      channel.value === "EMAIL" ? "auth.code.sentEmail" : "auth.code.sent"
    );
    startResendTimer(result.resend_in || 60);
  } catch (error: any) {
    errorMessage.value = messageForError(error);

    const retryAfter = Number(error?.response?.data?.retry_after || 0);
    if (error?.response?.data?.code === "too_soon" && retryAfter) {
      step.value = "code";
      startResendTimer(retryAfter);
    }
  } finally {
    sendingCode.value = false;
  }
}

async function submitCode(): Promise<void> {
  errorMessage.value = null;

  if (digitsOnly(code.value).length !== 6) {
    errorMessage.value = t("auth.code.codeRequired");
    return;
  }

  try {
    const user = await auth.loginWithCode({
      ...identity(),
      code: digitsOnly(code.value),
    });

    await afterLogin(user.must_change_password);
  } catch (error: any) {
    errorMessage.value = messageForError(error);
  }
}

function editDetails(): void {
  step.value = "details";
  code.value = "";
  devCode.value = "";
  errorMessage.value = null;
  infoMessage.value = null;
}

async function submitPassword(): Promise<void> {
  errorMessage.value = null;

  if (!username.value.trim() || !password.value) {
    errorMessage.value = t("auth.login.required");
    return;
  }

  try {
    const user = await auth.login({
      username: username.value.trim(),
      password: password.value,
    });

    await afterLogin(user.must_change_password);
  } catch (error: any) {
    errorMessage.value = messageForError(error);
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

        <div class="space-y-5 px-6 pb-8 sm:px-8">
          <!-- Sign in with ID number + phone + SMS code -->
          <form
            v-if="mode === 'code' && step === 'details'"
            class="space-y-5"
            novalidate
            @submit.prevent="sendCode"
          >
            <div>
              <label for="id-number" class="mb-2 block text-sm font-medium text-ink-soft">
                {{ t("auth.code.idNumber") }}
              </label>
              <input
                id="id-number"
                v-model="idNumber"
                type="text"
                dir="ltr"
                inputmode="numeric"
                autocomplete="off"
                maxlength="12"
                class="h-12 w-full rounded-xl border border-line-strong bg-white px-4 text-ink outline-none transition focus:border-brand focus:ring-4 focus:ring-brand/10"
              />
            </div>

            <fieldset v-if="codeChannels.length > 1">
              <legend class="mb-2 block text-sm font-medium text-ink-soft">{{ t("auth.code.sendBy") }}</legend>
              <div class="grid grid-cols-2 gap-2">
                <label
                  v-for="option in codeChannels"
                  :key="option"
                  class="flex h-11 cursor-pointer items-center justify-center rounded-xl border text-sm font-semibold transition"
                  :class="channel === option
                    ? 'border-brand bg-brand/5 text-brand'
                    : 'border-line-strong bg-white text-ink-soft hover:border-brand/40'"
                >
                  <input v-model="channel" type="radio" :value="option" class="sr-only" />
                  {{ option === "SMS" ? t("auth.code.bySms") : t("auth.code.byEmail") }}
                </label>
              </div>
            </fieldset>

            <div v-if="channel === 'SMS'">
              <label for="phone" class="mb-2 block text-sm font-medium text-ink-soft">
                {{ t("auth.code.phone") }}
              </label>
              <input
                id="phone"
                v-model="phone"
                type="tel"
                dir="ltr"
                inputmode="tel"
                autocomplete="tel"
                :placeholder="t('auth.login.usernamePlaceholder')"
                aria-describedby="phone-help"
                class="h-12 w-full rounded-xl border border-line-strong bg-white px-4 text-ink outline-none transition focus:border-brand focus:ring-4 focus:ring-brand/10"
              />
              <p id="phone-help" class="mt-2 text-xs leading-5 text-muted">
                {{ t("auth.code.phoneHelp") }}
              </p>
            </div>

            <div v-else>
              <label for="email" class="mb-2 block text-sm font-medium text-ink-soft">
                {{ t("auth.code.email") }}
              </label>
              <input
                id="email"
                v-model="email"
                type="email"
                dir="ltr"
                inputmode="email"
                autocomplete="email"
                aria-describedby="email-help"
                class="h-12 w-full rounded-xl border border-line-strong bg-white px-4 text-ink outline-none transition focus:border-brand focus:ring-4 focus:ring-brand/10"
              />
              <p id="email-help" class="mt-2 text-xs leading-5 text-muted">
                {{ t("auth.code.emailHelp") }}
              </p>
            </div>


            <div
              v-if="errorMessage"
              class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
              role="alert"
            >
              {{ errorMessage }}
            </div>

            <button type="submit" :disabled="sendingCode" class="h-12 w-full cursor-pointer rounded-xl bg-gradient-to-r from-brand to-brand-deep font-semibold text-white shadow-lg shadow-brand/20 transition-all hover:shadow-xl hover:shadow-brand/25 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60">
              {{ sendingCode ? t("auth.code.sending") : t("auth.code.send") }}
            </button>
          </form>

          <form
            v-else-if="mode === 'code'"
            class="space-y-5"
            novalidate
            @submit.prevent="submitCode"
          >
            <div
              v-if="infoMessage"
              class="rounded-xl border border-brand/15 bg-brand/5 px-4 py-3 text-sm leading-6 text-ink-soft"
              role="status"
            >
              {{ infoMessage }}
            </div>

            <div
              v-if="devCode"
              class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
            >
              {{ t("auth.code.devCode") }}
              <span dir="ltr" class="ms-1 font-mono text-base font-bold tracking-widest">{{ devCode }}</span>
            </div>

            <div>
              <label for="code" class="mb-2 block text-sm font-medium text-ink-soft">
                {{ t("auth.code.code") }}
              </label>
              <input
                id="code"
                v-model="code"
                type="text"
                dir="ltr"
                inputmode="numeric"
                autocomplete="one-time-code"
                maxlength="6"
                placeholder="••••••"
                class="h-12 w-full rounded-xl border border-line-strong bg-white px-4 text-ink outline-none transition focus:border-brand focus:ring-4 focus:ring-brand/10 text-center font-mono text-2xl tracking-[0.5em]"
                autofocus
              />
            </div>

            <div
              v-if="errorMessage"
              class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
              role="alert"
            >
              {{ errorMessage }}
            </div>

            <button type="submit" :disabled="auth.loading.value" class="h-12 w-full cursor-pointer rounded-xl bg-gradient-to-r from-brand to-brand-deep font-semibold text-white shadow-lg shadow-brand/20 transition-all hover:shadow-xl hover:shadow-brand/25 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60">
              {{ auth.loading.value ? t("auth.login.loading") : t("auth.login.submit") }}
            </button>

            <div class="flex items-center justify-between gap-3">
              <button type="button" class="cursor-pointer text-sm font-medium text-brand underline-offset-2 hover:underline disabled:cursor-not-allowed disabled:text-muted disabled:no-underline" @click="editDetails">
                {{ t("auth.code.editDetails") }}
              </button>

              <button
                type="button"
                class="cursor-pointer text-sm font-medium text-brand underline-offset-2 hover:underline disabled:cursor-not-allowed disabled:text-muted disabled:no-underline"
                :disabled="resendIn > 0 || sendingCode"
                @click="sendCode"
              >
                {{ resendIn > 0 ? t("auth.code.resendIn", { seconds: resendIn }) : t("auth.code.resend") }}
              </button>
            </div>
          </form>

          <!-- Fallback: username / ID / phone + password -->
          <form
            v-else
            class="space-y-5"
            novalidate
            @submit.prevent="submitPassword"
          >
            <div>
              <label for="username" class="mb-2 block text-sm font-medium text-ink-soft">
                {{ t("auth.login.username") }}
              </label>
              <input
                id="username"
                v-model="username"
                type="text"
                dir="ltr"
                autocomplete="username"
                autocapitalize="none"
                spellcheck="false"
                class="h-12 w-full rounded-xl border border-line-strong bg-white px-4 text-ink outline-none transition focus:border-brand focus:ring-4 focus:ring-brand/10"
              />
            </div>

            <div>
              <label for="password" class="mb-2 block text-sm font-medium text-ink-soft">
                {{ t("auth.login.password") }}
              </label>
              <div class="relative">
                <input
                  id="password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  dir="ltr"
                  autocomplete="current-password"
                  class="h-12 w-full rounded-xl border border-line-strong bg-white px-4 text-ink outline-none transition focus:border-brand focus:ring-4 focus:ring-brand/10"
                  :class="isRTL ? 'pl-12' : 'pr-12'"
                />
                <button
                  type="button"
                  class="absolute inset-y-0 flex w-12 cursor-pointer items-center justify-center text-muted transition hover:text-ink"
                  :class="isRTL ? 'left-0' : 'right-0'"
                  :aria-label="showPassword ? t('auth.login.hidePassword') : t('auth.login.showPassword')"
                  :title="showPassword ? t('auth.login.hidePassword') : t('auth.login.showPassword')"
                  @click="showPassword = !showPassword"
                >
                  <svg v-if="!showPassword" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.5 12S6 5 12 5s9.5 7 9.5 7-3.5 7-9.5 7-9.5-7-9.5-7Z" />
                    <circle cx="12" cy="12" r="3" stroke-width="2" />
                  </svg>
                  <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3l18 18M10.6 5.1A9.9 9.9 0 0 1 12 5c6 0 9.5 7 9.5 7a17 17 0 0 1-3.1 4.1M6.6 6.6C3.9 8.4 2.5 12 2.5 12s3.5 7 9.5 7a9.6 9.6 0 0 0 5.4-1.6M9.9 9.9a3 3 0 0 0 4.2 4.2" />
                  </svg>
                </button>
              </div>
            </div>

            <div
              v-if="errorMessage"
              class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
              role="alert"
            >
              {{ errorMessage }}
            </div>

            <button type="submit" :disabled="auth.loading.value" class="h-12 w-full cursor-pointer rounded-xl bg-gradient-to-r from-brand to-brand-deep font-semibold text-white shadow-lg shadow-brand/20 transition-all hover:shadow-xl hover:shadow-brand/25 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60">
              {{ auth.loading.value ? t("auth.login.loading") : t("auth.login.submit") }}
            </button>
          </form>

          <div class="space-y-3 border-t border-line pt-4 text-center">
            <button
              v-if="codeLoginAvailable"
              type="button"
              class="cursor-pointer text-sm font-medium text-brand underline-offset-2 hover:underline disabled:cursor-not-allowed disabled:text-muted disabled:no-underline"
              @click="switchMode(mode === 'code' ? 'password' : 'code')"
            >
              {{ mode === "code" ? t("auth.code.usePassword") : t("auth.code.useCode") }}
            </button>

            <div>
              <button
                type="button"
                class="cursor-pointer text-xs text-muted underline-offset-2 hover:underline"
                :aria-expanded="showForgotHelp"
                @click="showForgotHelp = !showForgotHelp"
              >
                {{ codeLoginAvailable ? t("auth.code.trouble") : t("auth.login.forgot") }}
              </button>

              <div
                v-if="showForgotHelp"
                class="mt-3 rounded-xl border border-brand/15 bg-brand/5 px-4 py-3 text-start text-sm leading-6 text-ink-soft"
                role="note"
              >
                {{ codeLoginAvailable ? t("auth.code.troubleText") : t("auth.login.forgotText") }}
              </div>
            </div>

            <div class="relative z-50 flex justify-center">
              <LanguageSelector />
            </div>
          </div>
        </div>
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