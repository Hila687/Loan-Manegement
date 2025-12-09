<template>
  <router-link
    :to="to"
    :class="[
      'group relative flex flex-col overflow-hidden rounded-2xl border-2 transition-all duration-300',
      'hover:scale-[1.02] hover:shadow-2xl active:scale-[0.98]',
      variant === 'primary'
        ? 'border-[#007AFF] bg-gradient-to-br from-[#007AFF] to-[#0051D5] text-white shadow-xl shadow-[#007AFF]/30'
        : 'border-[#E5E5EA] bg-white text-[#111827] hover:border-[#007AFF]/50 hover:shadow-[#007AFF]/10',
    ]"
  >
    <!-- Animated background decoration -->
    <div
      :class="[
        'absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100',
        variant === 'primary'
          ? 'bg-gradient-to-br from-white/10 to-transparent'
          : 'bg-gradient-to-br from-[#007AFF]/5 to-transparent',
      ]"
    />

    <!-- Sparkle effect on hover (primary only) -->
    <div
      v-if="variant === 'primary'"
      class="absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-500"
      style="
        background-image: radial-gradient(circle at 50% 50%, white 1px, transparent 1px);
        background-size: 20px 20px;
      "
    />

    <!-- Content -->
    <div class="relative flex flex-1 flex-col p-6 md:p-7">
      <!-- Icon container with animation -->
      <div
        :class="[
          'mb-4 flex h-14 w-14 md:h-16 md:w-16 items-center justify-center rounded-2xl transition-all duration-300',
          'group-hover:scale-110 group-hover:rotate-3',
          variant === 'primary'
            ? 'bg-white/20 backdrop-blur-sm shadow-lg'
            : 'bg-[#007AFF]/10',
        ]"
      >
        <!-- Icon SVG based on iconType prop -->
        <svg
          v-if="iconType === 'plus'"
          :class="[
            'w-7 h-7 md:w-8 md:h-8 transition-transform duration-300 group-hover:scale-110',
            variant === 'primary' ? 'text-white' : 'text-[#007AFF]',
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2.5"
            d="M12 4v16m8-8H4"
          />
        </svg>

        <svg
          v-else-if="iconType === 'list'"
          :class="[
            'w-7 h-7 md:w-8 md:h-8 transition-transform duration-300 group-hover:scale-110',
            variant === 'primary' ? 'text-white' : 'text-[#007AFF]',
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2.5"
            d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"
          />
        </svg>

        <svg
          v-else-if="iconType === 'dashboard'"
          :class="[
            'w-7 h-7 md:w-8 md:h-8 transition-transform duration-300 group-hover:scale-110',
            variant === 'primary' ? 'text-white' : 'text-[#007AFF]',
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2.5"
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>

        <svg
          v-else
          :class="[
            'w-7 h-7 md:w-8 md:h-8 transition-transform duration-300 group-hover:scale-110',
            variant === 'primary' ? 'text-white' : 'text-[#007AFF]',
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2.5"
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
      </div>

      <!-- Title -->
      <h3
        :class="[
          'text-xl md:text-2xl font-bold mb-2 transition-colors',
          variant === 'primary' ? 'text-white' : 'text-[#111827] group-hover:text-[#007AFF]',
        ]"
      >
        {{ title }}
      </h3>

      <!-- Description -->
      <p
        :class="[
          'text-sm md:text-base flex-1 leading-relaxed',
          variant === 'primary'
            ? 'text-white/90'
            : 'text-[#6B7280] group-hover:text-[#111827]',
        ]"
      >
        {{ description }}
      </p>

      <!-- Badge (optional) -->
      <div v-if="badge" class="mt-4">
        <span
          :class="[
            'inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold transition-all',
            variant === 'primary'
              ? 'bg-white/20 text-white backdrop-blur-sm group-hover:bg-white/30'
              : 'bg-[#34C759]/10 text-[#34C759] group-hover:bg-[#34C759]/20',
          ]"
        >
          <svg
            class="w-3 h-3"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clip-rule="evenodd"
            />
          </svg>
          {{ badge }}
        </span>
      </div>

      <!-- Arrow icon with RTL support -->
      <div class="mt-5 flex items-center justify-end">
        <div
          :class="[
            'flex h-10 w-10 md:h-12 md:w-12 items-center justify-center rounded-full transition-all duration-300',
            'group-hover:scale-110',
            variant === 'primary'
              ? 'bg-white/20 group-hover:bg-white/30 backdrop-blur-sm'
              : 'bg-[#007AFF]/10 group-hover:bg-[#007AFF]/20',
          ]"
        >
          <svg
            :class="[
              'w-5 h-5 md:w-6 md:h-6 transition-transform duration-300',
              isRTL
                ? 'group-hover:-translate-x-1'
                : 'group-hover:translate-x-1',
              variant === 'primary' ? 'text-white' : 'text-[#007AFF]',
            ]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2.5"
              :d="
                isRTL
                  ? 'M15 19l-7-7 7-7'
                  : 'M9 5l7 7-7 7'
              "
            />
          </svg>
        </div>
      </div>
    </div>

    <!-- Bottom accent line (secondary variant only) -->
    <div
      v-if="variant === 'secondary'"
      class="h-1 w-0 bg-gradient-to-r from-[#007AFF] to-[#0051D5] transition-all duration-500 group-hover:w-full"
    />
  </router-link>
</template>

<script setup lang="ts">
defineProps<{
  to: string;
  title: string;
  description: string;
  iconType?: "plus" | "list" | "dashboard" | "default";
  variant?: "primary" | "secondary";
  badge?: string;
  isRTL?: boolean;
}>();
</script>

<style scoped>
/* Smooth transitions for all interactive elements */
a {
  will-change: transform, box-shadow;
}

/* Ensure proper layering */
.relative {
  z-index: 1;
}

/* Optimize animations */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>