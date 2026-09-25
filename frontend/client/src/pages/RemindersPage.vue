<template>
  <AppLayout
    :title="title"
    :show-language-toggle="true"
    max-width="4xl"
  >
    <div class="mx-auto w-full max-w-3xl space-y-5 sm:space-y-6">
      <div
        v-if="loading"
        class="flex flex-col items-center justify-center rounded-2xl border border-line bg-white py-16"
      >
        <div class="h-9 w-9 animate-spin rounded-full border-4 border-brand border-t-transparent"></div>
        <p class="mt-4 text-sm text-muted">{{ loadingLabel }}</p>
      </div>

      <template v-else>
        <div
          v-if="successMessage"
          class="rounded-xl border border-success/30 bg-success/10 px-4 py-3 text-sm font-medium text-success-deep"
        >
          {{ successMessage }}
        </div>

        <div
          v-if="errorMessage"
          class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
        >
          {{ errorMessage }}
        </div>

        <section class="rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-6">
          <div class="flex items-center justify-between gap-4">
            <h2 class="text-lg font-bold text-ink">
              {{ settingsTitle }}
            </h2>

            <label class="flex cursor-pointer items-center gap-2">
              <input
                v-model="settings.enabled"
                type="checkbox"
                class="h-5 w-5 rounded border-line accent-success"
              />

              <span class="text-sm font-medium text-ink-soft">
                {{ settings.enabled ? enabledLabel : disabledLabel }}
              </span>
            </label>
          </div>

          <div class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <label class="flex flex-col gap-1.5">
              <span class="text-sm font-medium text-ink-soft">
                {{ channelLabel }}
              </span>

              <select
                v-model="settings.channel"
                :disabled="!settings.enabled"
                class="h-11 rounded-lg border border-line bg-white px-3 text-sm outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/20 disabled:bg-surface-muted disabled:text-faint"
              >
                <option value="SMS">SMS</option>
                <option value="WHATSAPP">WhatsApp</option>
                <option value="BOTH">{{ bothLabel }}</option>
              </select>
            </label>

            <label class="flex flex-col gap-1.5">
              <span class="text-sm font-medium text-ink-soft">
                {{ daysBeforeLabel }}
              </span>

              <input
                v-model.number="settings.days_before_due"
                type="number"
                min="0"
                max="30"
                step="1"
                :disabled="!settings.enabled"
                class="h-11 rounded-lg border border-line bg-white px-3 text-sm outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/20 disabled:bg-surface-muted disabled:text-faint"
              />
            </label>
          </div>

          <div class="mt-6 flex justify-end">
            <button
              type="button"
              :disabled="saving"
              class="h-11 cursor-pointer rounded-xl bg-brand px-5 text-sm font-semibold text-white shadow-lg shadow-brand/20 transition hover:bg-brand-deep disabled:cursor-not-allowed disabled:bg-faint"
              @click="saveSettings"
            >
              {{ saving ? savingLabel : saveLabel }}
            </button>
          </div>
        </section>

        <section class="space-y-4">
          <button
            type="button"
            :disabled="running || !settings.enabled"
            class="h-12 w-full cursor-pointer rounded-xl bg-brand px-5 text-sm font-semibold text-white shadow-lg shadow-brand/20 transition hover:bg-brand-deep disabled:cursor-not-allowed disabled:bg-faint sm:w-auto"
            @click="runReminders"
          >
            {{ running ? runningLabel : sendNowButtonLabel }}
          </button>

          <div
            v-if="runResult"
            class="grid grid-cols-2 gap-3 sm:grid-cols-4"
          >
            <div
              v-for="metric in runMetrics"
              :key="metric.key"
              class="rounded-xl border border-line bg-white p-3 shadow-sm"
            >
              <p class="text-xs text-muted">{{ metric.label }}</p>
              <p class="mt-1 text-lg font-bold text-ink">{{ metric.value }}</p>
            </div>
          </div>
        </section>
      </template>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import {
  computed,
  onMounted,
  reactive,
  ref,
} from "vue";

import AppLayout from "../components/AppLayout.vue";
import api from "../services/api";
import { useLocale } from "../composables/useLocale";


type ReminderChannel =
  | "SMS"
  | "WHATSAPP"
  | "BOTH";

type ReminderSettings = {
  enabled: boolean;
  channel: ReminderChannel;
  days_before_due: number;
};

const {
  locale,
} = useLocale();

function text(
  he: string,
  en: string,
  es: string
): string {
  if (locale.value === "he") {
    return he;
  }

  if (locale.value === "es") {
    return es;
  }

  return en;
}

const settings =
  reactive<ReminderSettings>({
    enabled: false,
    channel: "SMS",
    days_before_due: 1,
  });

const loading = ref(true);
const saving = ref(false);
const running = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const runResult = ref<Record<string, any> | null>(null);

const title = computed(() =>
  text(
    "תזכורות תשלום",
    "Payment Reminders",
    "Recordatorios de pago"
  )
);

const loadingLabel = computed(() =>
  text(
    "טוען הגדרות...",
    "Loading settings...",
    "Cargando configuración..."
  )
);

const settingsTitle = computed(() =>
  text(
    "הגדרות תזכורות",
    "Reminder settings",
    "Configuración de recordatorios"
  )
);

const enabledLabel = computed(() =>
  text("פעיל", "Enabled", "Activo")
);

const disabledLabel = computed(() =>
  text("כבוי", "Disabled", "Desactivado")
);

const channelLabel = computed(() =>
  text("ערוץ שליחה", "Delivery channel", "Canal de envío")
);

const daysBeforeLabel = computed(() =>
  text(
    "ימים לפני מועד התשלום",
    "Days before due date",
    "Días antes del vencimiento"
  )
);

const bothLabel = computed(() =>
  text(
    "SMS ו-WhatsApp",
    "SMS and WhatsApp",
    "SMS y WhatsApp"
  )
);

const saveLabel = computed(() =>
  text("שמירת הגדרות", "Save settings", "Guardar configuración")
);

const savingLabel = computed(() =>
  text("שומר...", "Saving...", "Guardando...")
);


const sendNowButtonLabel = computed(() =>
  text(
    "שליחת תזכורת עכשיו",
    "Send reminders now",
    "Enviar recordatorios ahora"
  )
);

const runningLabel = computed(() =>
  text("שולח...", "Sending...", "Enviando...")
);

const runMetrics = computed(() => {
  if (!runResult.value) {
    return [];
  }

  const source = runResult.value;

  const definitions = [
    {
      key: "checked",
      aliases: ["checked", "processed", "payments_checked"],
      label: text("נבדקו", "Checked", "Revisados"),
    },
    {
      key: "sent",
      aliases: ["sent", "sent_count"],
      label: text("נשלחו", "Sent", "Enviados"),
    },
    {
      key: "skipped",
      aliases: ["skipped", "skipped_count"],
      label: text("דולגו", "Skipped", "Omitidos"),
    },
    {
      key: "failed",
      aliases: ["failed", "failed_count", "errors"],
      label: text("נכשלו", "Failed", "Fallidos"),
    },
  ];

  return definitions.map((definition) => {
    const alias = definition.aliases.find(
      (key) =>
        source[key] !== undefined &&
        source[key] !== null
    );

    return {
      key: definition.key,
      label: definition.label,
      value: Number(alias ? source[alias] : 0),
    };
  });
});

function normalizeSettings(
  data: any
): void {
  settings.enabled =
    Boolean(data?.enabled ?? false);

  const channel =
    String(data?.channel || "SMS").toUpperCase();

  settings.channel =
    channel === "WHATSAPP" ||
    channel === "BOTH"
      ? channel
      : "SMS";

  const days =
    Number(
      data?.days_before_due ??
      data?.days_before ??
      1
    );

  settings.days_before_due =
    Number.isInteger(days) &&
    days >= 0
      ? Math.min(days, 30)
      : 1;
}

async function loadSettings(): Promise<void> {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response =
      await api.get(
        "/reminders/settings/"
      );

    normalizeSettings(
      response.data || {}
    );
  } catch (
    requestError: any
  ) {
    errorMessage.value =
      requestError?.response?.data?.detail ||
      text(
        "טעינת הגדרות התזכורות נכשלה.",
        "Failed to load reminder settings.",
        "No se pudo cargar la configuración de recordatorios."
      );
  } finally {
    loading.value = false;
  }
}

async function saveSettings(): Promise<void> {
  if (saving.value) {
    return;
  }

  const days =
    Number(settings.days_before_due);

  if (
    !Number.isInteger(days) ||
    days < 0 ||
    days > 30
  ) {
    errorMessage.value =
      text(
        "מספר הימים חייב להיות בין 0 ל-30.",
        "Days before due date must be between 0 and 30.",
        "Los días deben estar entre 0 y 30."
      );
    return;
  }

  saving.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const response =
      await api.patch(
        "/reminders/settings/",
        {
          enabled: settings.enabled,
          channel: settings.channel,
          days_before_due: days,
        }
      );

    normalizeSettings(
      response.data || settings
    );

    successMessage.value =
      text(
        "הגדרות התזכורות נשמרו.",
        "Reminder settings saved.",
        "Configuración guardada."
      );
  } catch (
    requestError: any
  ) {
    errorMessage.value =
      requestError?.response?.data?.detail ||
      requestError?.response?.data?.days_before_due?.[0] ||
      requestError?.response?.data?.channel?.[0] ||
      text(
        "שמירת ההגדרות נכשלה.",
        "Failed to save reminder settings.",
        "No se pudo guardar la configuración."
      );
  } finally {
    saving.value = false;
  }
}

async function runReminders(): Promise<void> {
  if (
    running.value ||
    !settings.enabled
  ) {
    return;
  }

  running.value = true;
  errorMessage.value = "";
  successMessage.value = "";
  runResult.value = null;

  try {
    const response =
      await api.post(
        "/reminders/run/",
        {}
      );

    runResult.value =
      response.data &&
      typeof response.data === "object"
        ? response.data
        : {};

    successMessage.value =
      text(
        "שליחת התזכורות הסתיימה.",
        "Reminder sending completed.",
        "El envío de recordatorios ha finalizado."
      );
  } catch (
    requestError: any
  ) {
    errorMessage.value =
      requestError?.response?.data?.detail ||
      text(
        "שליחת התזכורות נכשלה.",
        "Failed to send reminders.",
        "No se pudieron enviar los recordatorios."
      );
  } finally {
    running.value = false;
  }
}

onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
