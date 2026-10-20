<template>
  <div
    class="rounded-2xl border p-4"
    :class="codeLogin ? 'border-brand/20 bg-brand/5' : 'border-amber-200 bg-amber-50'"
  >
    <!-- Password-free: ID number + phone + SMS code -->
    <template v-if="codeLogin">
      <h3 class="text-sm font-bold text-ink">
        {{ title || t("credentials.codeLoginTitle") }}
      </h3>
      <p class="mt-1 text-sm leading-6 text-ink-soft">
        {{ codeLoginText }}
      </p>
    </template>

    <template v-else>
      <h3 class="text-sm font-bold text-amber-900">
        {{ title || t("credentials.title") }}
      </h3>
      <p class="mt-1 text-xs leading-5 text-amber-800">
        {{ t("credentials.noCodeLogin") }}
      </p>
    </template>

    <p
      v-if="!anySendChannel"
      class="mt-3 rounded-lg bg-white/70 px-3 py-2 text-xs leading-5 text-ink-soft"
    >
      {{ t("credentials.manualHandoff") }}
    </p>

    <div v-else class="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
      <button
        v-for="option in (['SMS', 'EMAIL'] as const)"
        :key="option"
        type="button"
        :disabled="!canSendBy(option) || sending !== null"
        :title="canSendBy(option) ? '' : t(option === 'SMS' ? 'credentials.noPhone' : 'credentials.noEmail')"
        class="cursor-pointer whitespace-nowrap rounded-xl border bg-white px-2 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
        :class="codeLogin ? 'border-brand/30 text-brand hover:bg-brand/10' : 'border-amber-300 text-amber-900 hover:bg-amber-100'"
        @click="send(option)"
      >
        {{
          sending === option
            ? t("credentials.sending")
            : option === "SMS"
              ? t("credentials.sendSms")
              : t("credentials.sendEmail")
        }}
      </button>
    </div>


    <p
      v-if="sendResult"
      class="mt-3 rounded-lg px-3 py-2 text-xs font-medium"
      :class="sendResult.ok ? 'bg-success/10 text-success-deep' : 'bg-red-50 text-red-700'"
      role="status"
    >
      {{ sendResult.message }}
    </p>

    <!-- Username + temporary password: the main route when there is no
         ID/phone on file, a collapsed backup otherwise. -->
    <component
      :is="codeLogin ? 'details' : 'div'"
      class="group mt-4"
    >
      <summary
        v-if="codeLogin"
        class="cursor-pointer select-none text-xs font-medium text-muted hover:text-ink"
      >
        {{ t("credentials.passwordFallback") }}
      </summary>

      <div class="mt-3 space-y-3">
        <div>
          <p class="text-xs text-muted">{{ t("credentials.username") }}</p>
          <p dir="ltr" class="mt-1 break-all rounded-lg bg-white px-3 py-2 font-mono text-sm text-ink">
            {{ credentials.username }}
          </p>
        </div>

        <div>
          <p class="text-xs text-muted">{{ t("credentials.temporaryPassword") }}</p>
          <p dir="ltr" class="mt-1 break-all rounded-lg bg-white px-3 py-2 font-mono text-sm text-ink">
            {{ credentials.temporary_password }}
          </p>
        </div>

        <button
          type="button"
          class="w-full cursor-pointer rounded-xl border border-line-strong bg-white px-2 py-2.5 text-sm font-semibold text-ink-soft transition hover:bg-canvas"
          @click="copy"
        >
          {{ copied ? t("credentials.copied") : t("credentials.copy") }}
        </button>
      </div>
    </component>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

import api from "../services/api";
import { useLocale } from "../composables/useLocale";

export type LoginCredentials = {
  username: string;
  temporary_password: string;
  login_hints?: {
    id_number?: string;
    phone?: string;
    email?: string;
  };
  can_send?: boolean;
  can_send_sms?: boolean;
  can_send_email?: boolean;
  phone_masked?: string;
  code_login?: boolean;
};

const props = defineProps<{
  credentials: LoginCredentials;
  title?: string;
}>();

const { t } = useLocale();

const copied = ref(false);
const sending = ref<"SMS" | "EMAIL" | null>(null);
const sendResult = ref<{ ok: boolean; message: string } | null>(null);

const loginUrl = computed(() => `${window.location.origin}/login`);

// Keep numbers like "050-1234567" in left-to-right order inside Hebrew text.
const ltr = (value: string) => `\u2066${value}\u2069`;

// With no SMS / email set up the admin passes the details on in person.
const anySendChannel = computed(() => canSendBy("SMS") || canSendBy("EMAIL"));

function canSendBy(channel: "SMS" | "EMAIL"): boolean {
  if (channel === "EMAIL") {
    return Boolean(props.credentials.can_send_email);
  }

  return Boolean(props.credentials.can_send_sms ?? props.credentials.can_send);
}

const codeLogin = computed(() => Boolean(props.credentials.code_login));

const codeLoginText = computed(() =>
  t("credentials.codeLoginText", {
    id: ltr(props.credentials.login_hints?.id_number || ""),
    phone: ltr(props.credentials.login_hints?.phone || ""),
  })
);

const hintText = computed(() => {
  const hints = props.credentials.login_hints || {};

  if (hints.id_number) {
    return t("credentials.hintIdNumber", { value: ltr(hints.id_number) });
  }

  if (hints.phone) {
    return t("credentials.hintPhone", { value: ltr(hints.phone) });
  }

  return "";
});

async function copy(): Promise<void> {
  const lines = codeLogin.value ? [
    `${t("credentials.site")}: ${loginUrl.value}`,
    codeLoginText.value,
  ] : [
    `${t("credentials.site")}: ${loginUrl.value}`,
    `${t("credentials.username")}: ${props.credentials.username}`,
    `${t("credentials.temporaryPassword")}: ${props.credentials.temporary_password}`,
  ];

  if (!codeLogin.value && hintText.value) {
    lines.push(hintText.value);
  }

  try {
    await navigator.clipboard.writeText(lines.join("\n"));
    copied.value = true;
  } catch {
    copied.value = false;
  }
}

async function send(channel: "SMS" | "EMAIL"): Promise<void> {
  if (sending.value) {
    return;
  }

  sending.value = channel;
  sendResult.value = null;

  try {
    const response = await api.post("/auth/send-credentials/", {
      username: props.credentials.username,
      temporary_password: props.credentials.temporary_password,
      channel,
    });

    sendResult.value = {
      ok: true,
      message: t("credentials.sent", { to: response.data?.sent_to || "" }),
    };
  } catch (error: any) {
    const code = error?.response?.data?.code;

    const messageKey =
      code === "no_phone"
        ? "credentials.noPhone"
        : code === "no_email"
          ? "credentials.noEmail"
        : code === "not_temporary"
          ? "credentials.notTemporary"
          : code === "send_failed"
            ? "credentials.sendFailed"
            : "credentials.sendError";

    sendResult.value = { ok: false, message: t(messageKey) };
  } finally {
    sending.value = null;
  }
}
</script>
