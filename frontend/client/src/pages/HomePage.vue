<!-- src/pages/Home.vue -->
<template>
  <AppLayout>
    <div class="max-w-5xl mx-auto py-8 px-4 space-y-8">

      <!-- Hero Section -->
      <section
        class="bg-white rounded-2xl shadow-sm border border-gray-100 px-6 py-7 flex flex-col gap-3"
      >
        <!-- Small label -->
        <p class="text-sm uppercase tracking-wide text-emerald-700 font-semibold">
          {{ t("home.gemachLabel") }}
        </p>

        <!-- Main title -->
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">
          {{ t("home.title") }}
        </h1>

        <!-- Subtitle paragraph -->
        <p class="text-sm md:text-base text-gray-600 max-w-2xl">
          {{ t("home.subtitle") }}
        </p>

        <!-- Statistics placeholders (visual only) -->
        <div class="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
          <div class="bg-emerald-50 border border-emerald-100 rounded-xl px-4 py-3">
            <p class="text-xs text-emerald-700 font-medium">
              {{ t("home.statActiveLoans") }}
            </p>
            <p class="mt-1 text-lg font-semibold text-emerald-900">
              0
            </p>
          </div>

          <div class="bg-gray-50 border border-gray-100 rounded-xl px-4 py-3">
            <p class="text-xs text-gray-500 font-medium">
              {{ t("home.statThisMonth") }}
            </p>
            <p class="mt-1 text-lg font-semibold text-gray-900">
              0
            </p>
          </div>

          <div class="bg-gray-50 border border-gray-100 rounded-xl px-4 py-3">
            <p class="text-xs text-gray-500 font-medium">
              {{ t("home.statTrustees") }}
            </p>
            <p class="mt-1 text-lg font-semibold text-gray-900">
              0
            </p>
          </div>
        </div>
      </section>

      <!-- Quick Actions Section -->
      <section class="space-y-3">
        <!-- Section title -->
        <h2 class="text-base font-semibold text-gray-800">
          {{ t("home.quickActions") }}
        </h2>

        <!-- Navigation cards grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- View active loans -->
          <NavigationCard
            :title="t('home.activeLoansCardTitle')"
            :description="t('home.activeLoansCardDescription')"
            to="/loans"
          />

          <!-- Create new loan -->
          <NavigationCard
            :title="t('home.createLoanCardTitle')"
            :description="t('home.createLoanCardDescription')"
            to="/loans/new"
          />
        </div>
      </section>

      <!-- Info Placeholder Section -->
      <section
        class="bg-gray-50 border border-dashed border-gray-200 rounded-2xl px-5 py-4 text-sm text-gray-600"
      >
        <!-- Placeholder text for future widgets -->
        <p>
          {{ t("home.footerNote") }}
        </p>
      </section>

    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import AppLayout from "../components/AppLayout.vue";
import NavigationCard from "../components/NavigationCard.vue";

// i18n instance
const { t } = useI18n();
</script>