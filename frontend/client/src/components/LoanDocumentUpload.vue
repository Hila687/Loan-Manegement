<script setup lang="ts">
const props = defineProps<{
  title: string;
  label: string;
  file: File | null;
  errorMessage?: string | null;
  isRTL: boolean;
}>();

const emit = defineEmits<{
  select: [file: File];
  remove: [];
}>();

function onFileChange(event: Event) {
  const target = event.target;

  if (!(target instanceof HTMLInputElement)) {
    return;
  }

  const file = target.files?.item(0);

  if (!file) {
    return;
  }

  emit("select", file);

  target.value = "";
}
</script>

<template>
  <div
    class="flex flex-col"
    :dir="props.isRTL ? 'rtl' : 'ltr'"
  >
    <div
      class="mb-3"
      :class="
        props.isRTL
          ? 'text-right'
          : 'text-left'
      "
    >
      <h3
        class="text-base font-semibold text-ink"
      >
        {{ props.title }}
      </h3>

      <p
        class="mt-1 text-xs text-muted"
      >
        PDF, JPG, PNG · 10MB max
      </p>
    </div>

    <label
      v-if="!props.file"
      :class="[
        'flex cursor-pointer flex-col items-center justify-center',
        'rounded-xl border-2 border-dashed p-6 text-center',
        'transition-colors w-full',
        props.errorMessage
          ? 'border-danger bg-danger/5 text-danger'
          : 'border-brand/50 bg-brand/5 text-brand hover:border-brand hover:bg-brand/10',
      ]"
    >
      <div
        :class="[
          'flex size-10 items-center justify-center rounded-full',
          props.errorMessage
            ? 'bg-danger/10'
            : 'bg-brand/10',
        ]"
      >
        <svg
          class="h-5 w-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline
            points="16 16 12 12 8 16"
          />

          <line
            x1="12"
            y1="12"
            x2="12"
            y2="21"
          />

          <path
            d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"
          />
        </svg>
      </div>

      <p
        class="mt-3 text-sm font-medium"
      >
        <span
          class="text-danger"
        >
          *
        </span>

        {{ props.label }}
      </p>

      <p
        class="mt-1 text-xs opacity-80"
      >
        {{
          props.isRTL
            ? "לחצי לבחירת קובץ"
            : "Click to select a file"
        }}
      </p>

      <input
        type="file"
        class="sr-only"
        accept="application/pdf,image/jpeg,image/png,.pdf,.jpg,.jpeg,.png"
        @change="onFileChange"
      />
    </label>

    <div
      v-else
      class="flex items-center gap-3 rounded-xl border border-success bg-success/5 p-4 text-success"
    >
      <svg
        class="h-5 w-5 flex-shrink-0"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polyline
          points="20 6 9 17 4 12"
        />
      </svg>

      <div
        class="min-w-0 flex-1"
      >
        <p
          class="truncate text-sm font-medium"
        >
          {{ props.file.name }}
        </p>

        <p
          class="text-xs opacity-80"
        >
          {{
            (
              props.file.size /
              1024 /
              1024
            ).toFixed(2)
          }}
          MB
        </p>
      </div>

      <button
        type="button"
        class="flex size-8 flex-shrink-0 items-center justify-center rounded-full text-muted transition-colors hover:bg-black/5"
        :aria-label="
          props.isRTL
            ? 'הסר קובץ'
            : 'Remove file'
        "
        @click="emit('remove')"
      >
        <svg
          class="h-4 w-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            d="M18 6 6 18"
          />

          <path
            d="m6 6 12 12"
          />
        </svg>
      </button>
    </div>

    <p
      v-if="props.errorMessage"
      class="mt-2 px-1 text-xs text-danger"
    >
      {{ props.errorMessage }}
    </p>
  </div>
</template>