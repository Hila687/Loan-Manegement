<template>
  <AppLayout
    :title="title"
    :subtitle="subtitle"
    :show-language-toggle="true"
    max-width="4xl"
  >
    <div
      class="mx-auto w-full max-w-3xl space-y-5 sm:space-y-6"
    >
      <!-- Loading -->
      <div
        v-if="loading"
        class="flex flex-col items-center justify-center rounded-2xl border border-line bg-white py-16"
      >
        <div
          class="h-9 w-9 animate-spin rounded-full border-4 border-brand border-t-transparent"
        ></div>

        <p
          class="mt-4 text-sm text-muted"
        >
          {{ loadingLabel }}
        </p>
      </div>

      <template v-else>
        <!-- Success -->
        <div
          v-if="successMessage"
          class="rounded-xl border border-success/30 bg-success/10 px-4 py-3 text-sm font-medium text-success-deep"
        >
          {{ successMessage }}
        </div>

        <!-- Error -->
        <div
          v-if="errorMessage"
          class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
        >
          {{ errorMessage }}
        </div>

        <!-- Reminder settings -->
        <section
          class="rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-6"
        >
          <div
            class="flex items-start justify-between gap-4"
          >
            <div>
              <h2
                class="text-lg font-bold text-ink"
              >
                {{ settingsTitle }}
              </h2>

              <p
                class="mt-1 text-sm leading-6 text-muted"
              >
                {{ settingsDescription }}
              </p>
            </div>

            <label
              class="flex cursor-pointer items-center gap-2"
            >
              <input
                v-model="settings.enabled"
                type="checkbox"
                class="h-5 w-5 rounded border-line accent-success"
              />

              <span
                class="text-sm font-medium text-ink-soft"
              >
                {{
                  settings.enabled
                    ? enabledLabel
                    : disabledLabel
                }}
              </span>
            </label>
          </div>

          <div
            class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2"
          >
            <label
              class="flex flex-col gap-1.5"
            >
              <span
                class="text-sm font-medium text-ink-soft"
              >
                {{ channelLabel }}
              </span>

              <select
                v-model="settings.channel"
                :disabled="!settings.enabled"
                class="h-11 rounded-lg border border-line bg-white px-3 text-sm outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/20 disabled:bg-surface-muted disabled:text-faint"
              >
                <option value="SMS">
                  SMS
                </option>

                <option value="WHATSAPP">
                  WhatsApp
                </option>

                <option value="BOTH">
                  {{ bothLabel }}
                </option>
              </select>
            </label>

            <label
              class="flex flex-col gap-1.5"
            >
              <span
                class="text-sm font-medium text-ink-soft"
              >
                {{ daysBeforeLabel }}
              </span>

              <input
                v-model.number="
                  settings.days_before_due
                "
                type="number"
                min="0"
                max="30"
                step="1"
                :disabled="!settings.enabled"
                class="h-11 rounded-lg border border-line bg-white px-3 text-sm outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/20 disabled:bg-surface-muted disabled:text-faint"
              />
            </label>
          </div>

          <div
            class="mt-5 rounded-xl border border-brand/15 bg-brand/5 p-4 text-sm leading-6 text-ink-soft"
          >
            {{ securityNote }}
          </div>

          <div
            class="mt-6 flex justify-end"
          >
            <button
              type="button"
              :disabled="saving"
              class="h-11 rounded-xl bg-brand px-5 text-sm font-semibold text-white shadow-lg shadow-brand/20 transition hover:bg-brand-deep disabled:bg-faint"
              @click="saveSettings"
            >
              {{
                saving
                  ? savingLabel
                  : saveLabel
              }}
            </button>
          </div>
        </section>

        <!-- Manual run -->
        <section
          class="rounded-2xl border border-line bg-white p-5 shadow-sm sm:p-6"
        >
          <h2
            class="text-lg font-bold text-ink"
          >
            {{ runTitle }}
          </h2>

          <p
            class="mt-1 text-sm leading-6 text-muted"
          >
            {{ runDescription }}
          </p>

          <button
            type="button"
            :disabled="
              running ||
              !settings.enabled
            "
            class="mt-5 h-11 w-full rounded-xl border border-brand/20 bg-brand/5 px-5 text-sm font-semibold text-brand transition hover:bg-brand/10 disabled:cursor-not-allowed disabled:bg-surface-muted disabled:text-faint sm:w-auto"
            @click="runReminders"
          >
            {{
              running
                ? runningLabel
                : runButtonLabel
            }}
          </button>

          <div
            v-if="runResult"
            class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4"
          >
            <div
              v-for="metric in runMetrics"
              :key="metric.key"
              class="rounded-xl border border-line bg-canvas p-3"
            >
              <p
                class="text-xs text-muted"
              >
                {{ metric.label }}
              </p>

              <p
                class="mt-1 text-lg font-bold text-ink"
              >
                {{ metric.value }}
              </p>
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

import AppLayout
  from "../components/AppLayout.vue";

import api
  from "../services/api";

import {
  useLocale,
} from "../composables/useLocale";

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

const isHebrew =
  computed(
    () =>
      locale.value === "he"
  );

const settings =
  reactive<ReminderSettings>({
    enabled: false,
    channel: "SMS",
    days_before_due: 1,
  });

const loading =
  ref(true);

const saving =
  ref(false);

const running =
  ref(false);

const errorMessage =
  ref("");

const successMessage =
  ref("");

const runResult =
  ref<
    Record<
      string,
      any
    > | null
  >(null);

const title =
  computed(() =>
    isHebrew.value
      ? "תזכורות תשלום"
      : "Payment Reminders"
  );

const subtitle =
  computed(() =>
    isHebrew.value
      ? "הגדרת תזכורות SMS ו-WhatsApp לתשלומים קרובים"
      : "Configure SMS and WhatsApp reminders for upcoming payments"
  );

const loadingLabel =
  computed(() =>
    isHebrew.value
      ? "טוען הגדרות..."
      : "Loading settings..."
  );

const settingsTitle =
  computed(() =>
    isHebrew.value
      ? "הגדרות תזכורות"
      : "Reminder settings"
  );

const settingsDescription =
  computed(() =>
    isHebrew.value
      ? "המערכת יכולה לשלוח תזכורת אוטומטית לפני מועד התשלום."
      : "The system can automatically send a reminder before a payment is due."
  );

const enabledLabel =
  computed(() =>
    isHebrew.value
      ? "פעיל"
      : "Enabled"
  );

const disabledLabel =
  computed(() =>
    isHebrew.value
      ? "כבוי"
      : "Disabled"
  );

const channelLabel =
  computed(() =>
    isHebrew.value
      ? "ערוץ שליחה"
      : "Delivery channel"
  );

const daysBeforeLabel =
  computed(() =>
    isHebrew.value
      ? "ימים לפני מועד התשלום"
      : "Days before due date"
  );

const bothLabel =
  computed(() =>
    isHebrew.value
      ? "SMS ו-WhatsApp"
      : "SMS and WhatsApp"
  );

const securityNote =
  computed(() =>
    isHebrew.value
      ? "פרטי הספק והסודות נשמרים רק במשתני הסביבה של השרת ואינם נשלחים לדפדפן."
      : "Provider credentials and secrets are stored only in server environment variables and are never sent to the browser."
  );

const saveLabel =
  computed(() =>
    isHebrew.value
      ? "שמירת הגדרות"
      : "Save settings"
  );

const savingLabel =
  computed(() =>
    isHebrew.value
      ? "שומר..."
      : "Saving..."
  );

const runTitle =
  computed(() =>
    isHebrew.value
      ? "הרצה ידנית"
      : "Manual run"
  );

const runDescription =
  computed(() =>
    isHebrew.value
      ? "ניתן להריץ כעת בדיקה ושליחה עבור תשלומים שעומדים בתנאי התזכורת. מנגנון מניעת כפילויות נשמר בצד השרת."
      : "Run the reminder process now for payments that match the reminder rule. Duplicate prevention is enforced on the server."
  );

const runButtonLabel =
  computed(() =>
    isHebrew.value
      ? "הרצת תזכורות עכשיו"
      : "Run reminders now"
  );

const runningLabel =
  computed(() =>
    isHebrew.value
      ? "מריץ..."
      : "Running..."
  );

const runMetrics =
  computed(() => {
    if (!runResult.value) {
      return [];
    }

    const source =
      runResult.value;

    const definitions = [
      {
        key: "checked",

        aliases: [
          "checked",
          "processed",
          "payments_checked",
        ],

        label:
          isHebrew.value
            ? "נבדקו"
            : "Checked",
      },

      {
        key: "sent",

        aliases: [
          "sent",
          "sent_count",
        ],

        label:
          isHebrew.value
            ? "נשלחו"
            : "Sent",
      },

      {
        key: "skipped",

        aliases: [
          "skipped",
          "skipped_count",
        ],

        label:
          isHebrew.value
            ? "דולגו"
            : "Skipped",
      },

      {
        key: "failed",

        aliases: [
          "failed",
          "failed_count",
          "errors",
        ],

        label:
          isHebrew.value
            ? "נכשלו"
            : "Failed",
      },
    ];

    return definitions.map(
      (definition) => {
        const alias =
          definition.aliases.find(
            (key) =>
              source[key] !==
                undefined &&
              source[key] !==
                null
          );

        return {
          key:
            definition.key,

          label:
            definition.label,

          value:
            Number(
              alias
                ? source[alias]
                : 0
            ),
        };
      }
    );
  });

function normalizeSettings(
  data: any
): void {
  settings.enabled =
    Boolean(
      data?.enabled ??
      false
    );

  const channel =
    String(
      data?.channel ||
      "SMS"
    ).toUpperCase();

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
    Number.isInteger(
      days
    ) &&
    days >= 0
      ? Math.min(
          days,
          30
        )
      : 1;
}

async function loadSettings():
  Promise<void> {
  loading.value =
    true;

  errorMessage.value =
    "";

  try {
    const response =
      await api.get(
        "/reminders/settings/"
      );

    normalizeSettings(
      response.data ||
      {}
    );
  } catch (
    requestError: any
  ) {
    errorMessage.value =
      requestError
        ?.response
        ?.data
        ?.detail ||
      (
        isHebrew.value
          ? "טעינת הגדרות התזכורות נכשלה."
          : "Failed to load reminder settings."
      );
  } finally {
    loading.value =
      false;
  }
}

async function saveSettings():
  Promise<void> {
  if (saving.value) {
    return;
  }

  const days =
    Number(
      settings.days_before_due
    );

  if (
    !Number.isInteger(
      days
    ) ||
    days < 0 ||
    days > 30
  ) {
    errorMessage.value =
      isHebrew.value
        ? "מספר הימים חייב להיות בין 0 ל-30."
        : "Days before due date must be between 0 and 30.";

    return;
  }

  saving.value =
    true;

  errorMessage.value =
    "";

  successMessage.value =
    "";

  try {
    const response =
      await api.patch(
        "/reminders/settings/",
        {
          enabled:
            settings.enabled,

          channel:
            settings.channel,

          days_before_due:
            days,
        }
      );

    normalizeSettings(
      response.data ||
      settings
    );

    successMessage.value =
      isHebrew.value
        ? "הגדרות התזכורות נשמרו."
        : "Reminder settings saved.";
  } catch (
    requestError: any
  ) {
    errorMessage.value =
      requestError
        ?.response
        ?.data
        ?.detail ||
      requestError
        ?.response
        ?.data
        ?.days_before_due
        ?.[0] ||
      requestError
        ?.response
        ?.data
        ?.channel
        ?.[0] ||
      (
        isHebrew.value
          ? "שמירת ההגדרות נכשלה."
          : "Failed to save reminder settings."
      );
  } finally {
    saving.value =
      false;
  }
}

async function runReminders():
  Promise<void> {
  if (
    running.value ||
    !settings.enabled
  ) {
    return;
  }

  running.value =
    true;

  errorMessage.value =
    "";

  successMessage.value =
    "";

  runResult.value =
    null;

  try {
    const response =
      await api.post(
        "/reminders/run/",
        {}
      );

    runResult.value =
      response.data &&
      typeof response.data ===
        "object"
        ? response.data
        : {};

    successMessage.value =
      isHebrew.value
        ? "הרצת התזכורות הסתיימה."
        : "Reminder run completed.";
  } catch (
    requestError: any
  ) {
    errorMessage.value =
      requestError
        ?.response
        ?.data
        ?.detail ||
      (
        isHebrew.value
          ? "הרצת התזכורות נכשלה."
          : "Failed to run reminders."
      );
  } finally {
    running.value =
      false;
  }
}

onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(
      360deg
    );
  }
}

.animate-spin {
  animation:
    spin
    1s
    linear
    infinite;
}
</style>