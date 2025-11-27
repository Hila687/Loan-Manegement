<script setup lang="ts">
import { ref, onMounted } from "vue";
import type { AxiosError } from "axios";
import { useLocale } from "../composables/useLocale";
import AppLayout from "../components/AppLayout.vue";
import FormCard from "../components/FormCard.vue";
import api from "../services/api";

const { t } = useLocale();

interface User {
  id: number | string;
  username: string;
  role_name?: string;
  role?: string;
  is_superuser?: boolean;
}

const users = ref<User[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

/** Load users from the backend */
async function loadUsers() {
  loading.value = true;
  error.value = null;

  try {
    const res = await api.get<User[]>("/users/");
    users.value = res.data;
  } catch (e: unknown) {
    console.error("Users API error:", e);

    const axiosError = e as AxiosError<{ detail?: string }>;
    const backendDetail = axiosError.response?.data?.detail;

    // Developer debug only
    if (backendDetail) {
      console.debug("Backend error detail:", backendDetail);
    }

    // Always localize on screen
    error.value = t("usersList.messages.errorDetails");
  } finally {
    loading.value = false;
  }
}

/** Main button (Load / Refresh) */
function handlePrimaryClick() {
  loadUsers();
}

onMounted(loadUsers);
</script>

<template>
  <AppLayout
    :title="t('usersList.title')"
    :subtitle="loading ? t('usersList.loading') : ''"
    :showLanguageToggle="true"
    :showBackButton="true"
    maxWidth="md"
  >
    <div class="flex flex-col gap-4">
      <FormCard>
        <!-- Main blue button -->
        <button
          type="button"
          @click="handlePrimaryClick"
          class="flex w-full cursor-pointer items-center justify-center rounded-lg h-12 px-5 bg-[#007AFF] text-white text-sm font-semibold tracking-wide hover:bg-[#0067E0] active:bg-[#0052BA] transition-colors"
        >
          {{ users.length ? t("usersList.buttons.refresh") : t("usersList.buttons.loadUsers") }}
        </button>

        <!-- Loading State -->
        <div
          v-if="loading"
          class="flex flex-col items-center justify-center py-10"
        >
          <div class="w-8 h-8 border-4 border-[#007AFF] border-t-transparent rounded-full animate-spin" />
          <p class="mt-4 text-sm text-[#8A8A8E] text-center">
            {{ t("usersList.loading") }}
          </p>
        </div>

        <!-- Error State -->
        <div
          v-else-if="error"
          class="flex flex-col items-center gap-3 rounded-lg bg-[rgba(255,59,48,0.08)] border border-[#FFCDD2] p-4 text-center"
        >
          <svg
            class="w-7 h-7 text-[#FF3B30]"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm-.75-5.5a.75.75 0 011.5 
              0v1.5a.75.75 0 01-1.5 0v-1.5zm0-7a.75.75 0 011.5 
              0v5a.75.75 0 01-1.5 0v-5z"
              clip-rule="evenodd"
            />
          </svg>

          <!-- Error title -->
          <h3 class="text-[#FF3B30] text-base font-bold">
            {{ t("usersList.messages.loadFailed") }}
          </h3>

          <!-- Error details -->
          <p class="text-sm text-[#1C1C1E]">
            {{ error }}
          </p>

          <button
            type="button"
            @click="handlePrimaryClick"
            class="mt-2 rounded-lg h-9 px-4 bg-[#007AFF]/10 text-[#007AFF] text-sm font-semibold hover:bg-[#007AFF]/15 transition"
          >
            {{ t("usersList.buttons.retry") }}
          </button>
        </div>

        <!-- Users List -->
        <div v-else class="flex flex-col">
          <!-- Header -->
          <div
            class="flex items-center px-4 py-2 border-b-2 border-[#E5E5EA] bg-[#F9F9F9]"
          >
            <p class="w-1/2 text-center text-[#8A8A8E] text-xs font-bold uppercase">
              {{ t("usersList.table.username") }}
            </p>
            <p class="w-1/2 text-center text-[#8A8A8E] text-xs font-bold uppercase">
              {{ t("usersList.table.role") }}
            </p>
          </div>

          <!-- User rows -->
          <div v-if="users.length" class="flex flex-col">
            <div
              v-for="u in users"
              :key="u.id"
              class="flex items-center px-4 py-3 border-b border-[#E5E5EA]"
            >
              <!-- Username -->
              <div class="w-1/2 text-center">
                <p class="truncate text-[#1C1C1E] text-base">{{ u.username }}</p>
                <p class="text-xs text-[#8A8A8E]">
                  {{ t("usersList.idLabel") }} {{ u.id }}
                </p>
              </div>

              <!-- Role -->
              <div class="w-1/2 text-center">
                <p class="truncate text-[#1C1C1E] text-base">
                  {{
                    u.role_name ||
                    u.role ||
                    (u.is_superuser ? t("usersList.roles.admin") : t("usersList.noRole"))
                  }}
                </p>
              </div>
            </div>
          </div>

          <!-- Empty state -->
          <div v-else class="flex flex-col items-center justify-center py-10 px-4 text-center">
            <svg
              class="w-10 h-10 text-[#E5E5EA]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M20 13V7a2 2 0 00-2-2h-3l-2-2H9L7 
                5H4a2 2 0 00-2 2v6m18 0v6a2 2 0 01-2 
                2H4a2 2 0 01-2-2v-6m18 0H2"
              />
            </svg>

            <p class="mt-4 text-sm text-[#8A8A8E]">
              {{ t("usersList.noUsers") }}
            </p>
          </div>
        </div>
      </FormCard>
    </div>
  </AppLayout>
</template>
