<template>
  <div class="space-y-3">
    <h2 class="text-lg font-semibold text-ink">
      {{ t("loanDetails.borrowerInfo") }}
    </h2>

    <div class="grid grid-cols-1 gap-3 text-sm text-ink-soft sm:grid-cols-2">
      <div class="detail-item">
        <span class="detail-label">
          {{ t("loanDetails.name") }}
        </span>
        <span class="font-medium text-ink">
          {{ borrower.name || "—" }}
        </span>
      </div>

      <div class="detail-item">
        <span class="detail-label">
          {{ t("loanDetails.phone") }}
        </span>

        <a
          v-if="borrower.phone"
          :href="phoneHref(borrower.phone)"
          dir="ltr"
          class="w-fit font-semibold text-brand hover:underline"
        >
          {{ borrower.phone }}
        </a>

        <span v-else>—</span>
      </div>

      <div class="detail-item">
        <span class="detail-label">
          {{ t("loanDetails.email") }}
        </span>

        <a
          v-if="borrower.email"
          :href="`mailto:${borrower.email}`"
          dir="ltr"
          class="w-fit break-all font-semibold text-brand hover:underline"
        >
          {{ borrower.email }}
        </a>

        <span v-else>—</span>
      </div>

      <div class="detail-item">
        <span class="detail-label">
          {{ t("loanDetails.address") }}
        </span>
        <span>
          {{ borrower.address || "—" }}
        </span>
      </div>

      <div class="detail-item">
        <span class="detail-label">
          {{ t("loanDetails.idNumber") }}
        </span>
        <span dir="ltr" class="w-fit">
          {{ borrower.idNumber || "—" }}
        </span>
      </div>

      <div class="detail-item">
        <span class="detail-label">
          {{ t("loanDetails.createdAt") }}
        </span>
        <span>
          {{ formatDate(borrower.createdAt) }}
        </span>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
import {
  useI18n,
} from "vue-i18n";

import type {
  Borrower,
} from "../../types/loan";


const props =
  defineProps<{
    borrower: Borrower;
  }>();


const {
  t,
  locale,
} = useI18n();


function phoneHref(
  phone: string
): string {
  const cleaned =
    String(phone || "")
      .replace(
        /[^\d+]/g,
        ""
      );

  return `tel:${cleaned}`;
}


function formatDate(
  date?: string
): string {
  if (!date) {
    return "—";
  }

  const normalized =
    date.length === 10
      ? `${date}T00:00:00`
      : date;

  const value =
    new Date(
      normalized
    );

  if (
    Number.isNaN(
      value.getTime()
    )
  ) {
    return date;
  }

  const formatterLocale =
    locale.value === "he"
      ? "he-IL"
      : locale.value === "es"
        ? "es-ES"
        : "en-US";

  return value.toLocaleDateString(
    formatterLocale
  );
}
</script>


<style scoped>
.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-radius: 0.75rem;
  background: var(--color-canvas);
  padding: 0.75rem;
}

.detail-label {
  color: var(--color-muted);
  font-size: 0.75rem;
  line-height: 1rem;
  font-weight: 500;
}
</style>
