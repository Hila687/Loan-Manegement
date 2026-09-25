<template>
  <AppLayout
    :title="pageTitle"
    :show-language-toggle="true"
    max-width="full"
  >
    <div class="space-y-5 sm:space-y-6">
      <div class="flex items-center gap-2 sm:gap-3">
        <div class="relative min-w-0 flex-1 sm:max-w-md">
          <span
            :class="[
              'pointer-events-none absolute inset-y-0 flex items-center text-muted',
              isRTL ? 'right-0 pr-4' : 'left-0 pl-4',
            ]"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8" stroke-width="2" />
              <path d="m21 21-4.35-4.35" stroke-width="2" stroke-linecap="round" />
            </svg>
          </span>

          <input
            v-model="searchQuery"
            type="search"
            :placeholder="searchPlaceholder"
            :dir="isRTL ? 'rtl' : 'ltr'"
            :class="[
              'h-12 w-full rounded-xl border border-line bg-white text-sm text-ink outline-none transition placeholder:text-transparent sm:placeholder:text-muted focus:border-brand focus:ring-2 focus:ring-brand/20',
              isRTL ? 'pr-11 pl-4' : 'pl-11 pr-4',
            ]"
          />
        </div>

        <button
          v-if="showCreateButton"
          type="button"
          class="flex h-12 w-12 flex-shrink-0 cursor-pointer items-center justify-center rounded-xl bg-brand text-white shadow-lg shadow-brand/20 transition hover:bg-brand-deep active:scale-[0.98]"
          :title="createLabel"
          :aria-label="createLabel"
          @click="openCreateModal"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M12 5v14m7-7H5" />
          </svg>
        </button>
      </div>

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

      <div
        v-if="loading"
        class="flex flex-col items-center justify-center rounded-2xl border border-line bg-white py-16"
      >
        <div class="h-9 w-9 animate-spin rounded-full border-4 border-brand border-t-transparent"></div>
        <p class="mt-4 text-sm text-muted">{{ loadingLabel }}</p>
      </div>

      <div
        v-else-if="filteredItems.length === 0"
        class="rounded-2xl border border-line bg-white px-6 py-14 text-center"
      >
        <h3 class="text-base font-semibold text-ink">{{ emptyTitle }}</h3>
        <p class="mt-1 text-sm text-muted">{{ emptyDescription }}</p>
      </div>

      <div
        v-else
        class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3"
      >
        <article
          v-for="item in filteredItems"
          :key="getItemId(item)"
          class="rounded-2xl border border-line bg-white p-5 shadow-sm transition hover:shadow-md"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0">
              <h2 class="truncate text-base font-bold text-ink">
                {{ getPrimaryLabel(item) }}
              </h2>

              <p
                v-if="getSecondaryLabel(item)"
                class="mt-1 truncate text-sm text-muted"
              >
                {{ getSecondaryLabel(item) }}
              </p>
            </div>

            <span
              v-if="getStatusLabel(item)"
              class="flex-shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold"
              :class="getStatusClass(item)"
            >
              {{ getStatusLabel(item) }}
            </span>
          </div>

          <dl class="mt-5 space-y-3">
            <div
              v-for="detail in getDetails(item)"
              :key="detail.label"
              class="flex items-start justify-between gap-4 border-b border-surface-muted pb-2 last:border-b-0 last:pb-0"
            >
              <dt class="text-xs font-medium text-muted">
                {{ detail.label }}
              </dt>
              <dd class="max-w-[65%] break-words text-end text-sm font-medium text-ink-soft">
                <a
                  v-if="detail.href"
                  :href="detail.href"
                  dir="ltr"
                  class="inline-flex cursor-pointer items-center gap-1 text-brand underline-offset-2 hover:underline"
                >
                  {{ detail.value }}
                </a>

                <span v-else>
                  {{ detail.value }}
                </span>
              </dd>
            </div>
          </dl>

          <div
            v-if="canEdit"
            class="mt-5 flex gap-2 border-t border-line pt-4"
          >
            <button
              type="button"
              class="flex-1 cursor-pointer rounded-lg border border-brand/20 bg-brand/5 px-3 py-2 text-sm font-semibold text-brand transition hover:bg-brand/10"
              @click="openEditModal(item)"
            >
              {{ editLabel }}
            </button>

            <button
              type="button"
              class="cursor-pointer rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-sm font-semibold text-red-600 transition hover:bg-red-100"
              @click="requestDelete(item)"
            >
              {{ deleteLabel }}
            </button>
          </div>
        </article>
      </div>
    </div>

    <Teleport to="body">
      <div
        v-if="modalOpen"
        class="fixed inset-0 z-[100] flex items-center justify-center bg-black/45 p-3 backdrop-blur-sm sm:p-4"
        :dir="isRTL ? 'rtl' : 'ltr'"
        @click.self="closeModal"
      >
        <div class="max-h-[92vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-white p-5 shadow-2xl sm:p-6">
          <div class="flex items-start justify-between gap-4">
            <h2 class="text-xl font-bold text-ink">
              {{ modalTitle }}
            </h2>

            <button
              type="button"
              class="flex h-9 w-9 cursor-pointer items-center justify-center rounded-lg text-xl text-muted transition hover:bg-canvas-deep hover:text-ink"
              @click="closeModal"
            >
              ×
            </button>
          </div>

          <div
            v-if="!temporaryCredentials"
            class="mt-5 space-y-4"
          >
            <template v-if="section === 'trustees'">
              <TextField v-model="form.first_name" :label="firstNameLabel" :required="true" />
              <TextField v-model="form.last_name" :label="lastNameLabel" :required="true" />
              <TextField v-model="form.email" :label="emailLabel" type="email" />
              <TextField v-model="form.phone" :label="phoneLabel" type="tel" />
              <TextField v-model="form.community" :label="communityLabel" :required="true" />
              <TextAreaField v-model="form.notes" :label="notesLabel" />
            </template>

            <template v-else-if="section === 'donors'">
              <TextField v-model="form.first_name" :label="firstNameLabel" :required="true" />
              <TextField v-model="form.last_name" :label="lastNameLabel" :required="true" />
              <TextField v-model="form.email" :label="emailLabel" type="email" />
              <TextField v-model="form.phone" :label="phoneLabel" type="tel" />
              <TextAreaField v-model="form.notes" :label="notesLabel" />
            </template>

            <template v-else-if="section === 'admins'">
              <div
                v-if="!editingItem"
                class="rounded-xl border border-brand/15 bg-brand/5 px-4 py-3 text-sm leading-6 text-ink-soft"
              >
                {{ adminLoginHint }}
              </div>

              <div
                v-if="editingItem && currentUsername"
                class="rounded-xl bg-surface-muted px-4 py-3"
              >
                <p class="text-xs font-medium text-muted">{{ usernameLabel }}</p>
                <p class="mt-1 text-sm font-semibold text-ink">{{ currentUsername }}</p>
              </div>

              <TextField v-model="form.first_name" :label="firstNameLabel" :required="true" />
              <TextField v-model="form.last_name" :label="lastNameLabel" :required="true" />
              <TextField v-model="form.email" :label="emailLabel" type="email" :required="true" />
              <TextField v-model="form.phone" :label="phoneLabel" type="tel" />
            </template>

            <template v-else-if="section === 'borrowers'">
              <TextField v-model="form.id_number" :label="idNumberLabel" :required="true" />
              <TextField v-model="form.first_name" :label="firstNameLabel" :required="true" />
              <TextField v-model="form.last_name" :label="lastNameLabel" :required="true" />
              <TextField v-model="form.phone" :label="phoneLabel" type="tel" />
              <TextField v-model="form.email" :label="emailLabel" type="email" />
              <TextField v-model="form.address" :label="addressLabel" :required="true" />

              <label class="flex flex-col gap-1.5">
                <span class="text-sm font-medium text-ink-soft">{{ trusteeLabel }}</span>
                <select
                  v-model="form.trustee"
                  class="h-11 rounded-lg border border-line bg-white px-3 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
                >
                  <option value="">—</option>
                  <option
                    v-for="trustee in trusteeOptions"
                    :key="trustee.id"
                    :value="trustee.id"
                  >
                    {{ trustee.label }}
                  </option>
                </select>
              </label>
            </template>

            <template v-else-if="section === 'donations'">
              <label class="flex flex-col gap-1.5">
                <span class="text-sm font-medium text-ink-soft">{{ donorLabel }} *</span>
                <select
                  v-model="form.donor"
                  class="h-11 rounded-lg border border-line bg-white px-3 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
                >
                  <option value="" disabled>{{ selectDonorLabel }}</option>
                  <option
                    v-for="donor in donorOptions"
                    :key="donor.id"
                    :value="donor.id"
                  >
                    {{ donor.label }}
                  </option>
                </select>
              </label>

              <TextField v-model="form.amount" :label="amountLabel" type="number" :required="true" />
              <TextField v-model="form.donation_date" :label="dateLabel" type="date" :required="true" />
              <TextAreaField v-model="form.notes" :label="notesLabel" />
            </template>

            <div
              v-if="modalError"
              class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
            >
              {{ modalError }}
            </div>

            <div class="flex flex-col-reverse gap-2 pt-2 sm:flex-row sm:justify-end">
              <button
                type="button"
                :disabled="saving"
                class="h-11 cursor-pointer rounded-xl border border-line bg-white px-5 text-sm font-semibold text-ink-soft transition hover:bg-surface-muted disabled:opacity-50"
                @click="closeModal"
              >
                {{ cancelLabel }}
              </button>

              <button
                type="button"
                :disabled="saving"
                class="h-11 cursor-pointer rounded-xl bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-deep disabled:bg-faint"
                @click="saveItem"
              >
                {{ saving ? savingLabel : saveLabel }}
              </button>
            </div>
          </div>

          <div
            v-else
            class="mt-5"
          >
            <div class="rounded-2xl border border-amber-200 bg-amber-50 p-4">
              <h3 class="text-sm font-bold text-amber-900">
                {{ credentialsTitle }}
              </h3>
              <p class="mt-1 text-xs leading-5 text-amber-800">
                {{ credentialsNotice }}
              </p>

              <div class="mt-4 space-y-3">
                <div>
                  <p class="text-xs text-amber-800">{{ usernameLabel }}</p>
                  <p dir="ltr" class="mt-1 break-all rounded-lg bg-white px-3 py-2 font-mono text-sm text-ink">
                    {{ temporaryCredentials.username }}
                  </p>
                </div>

                <div>
                  <p class="text-xs text-amber-800">{{ temporaryPasswordLabel }}</p>
                  <p dir="ltr" class="mt-1 break-all rounded-lg bg-white px-3 py-2 font-mono text-sm text-ink">
                    {{ temporaryCredentials.temporary_password }}
                  </p>
                </div>
              </div>

              <button
                type="button"
                class="mt-4 w-full cursor-pointer rounded-xl border border-amber-300 bg-white px-4 py-2.5 text-sm font-semibold text-amber-900 transition hover:bg-amber-100"
                @click="copyCredentials"
              >
                {{ credentialsCopied ? copiedLabel : copyLabel }}
              </button>
            </div>

            <button
              type="button"
              class="mt-4 h-11 w-full cursor-pointer rounded-xl bg-brand px-5 text-sm font-semibold text-white transition hover:bg-brand-deep"
              @click="finishCredentials"
            >
              {{ doneLabel }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div
        v-if="deleteCandidate"
        class="fixed inset-0 z-[110] flex items-center justify-center bg-black/45 p-4 backdrop-blur-sm"
        :dir="isRTL ? 'rtl' : 'ltr'"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <h2 class="text-lg font-bold text-ink">{{ deleteConfirmTitle }}</h2>
          <p class="mt-2 text-sm leading-6 text-muted">{{ deleteConfirmText }}</p>

          <div class="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button
              type="button"
              :disabled="deleting"
              class="h-11 cursor-pointer rounded-xl border border-line bg-white px-5 text-sm font-semibold text-ink-soft"
              @click="deleteCandidate = null"
            >
              {{ cancelLabel }}
            </button>

            <button
              type="button"
              :disabled="deleting"
              class="h-11 cursor-pointer rounded-xl bg-danger px-5 text-sm font-semibold text-white disabled:opacity-50"
              @click="confirmDelete"
            >
              {{ deleting ? deletingLabel : deleteLabel }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>

<script setup lang="ts">
import {
  computed,
  defineComponent,
  h,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue";

import AppLayout from "../components/AppLayout.vue";
import api from "../services/api";
import { useLocale } from "../composables/useLocale";
import { useAuth } from "../composables/useAuth";


type SectionName =
  | "borrowers"
  | "trustees"
  | "donors"
  | "donations"
  | "admins";

type ListItem =
  Record<string, any>;

type OptionItem = {
  id: string;
  label: string;
};

type TemporaryCredentials = {
  username: string;
  temporary_password: string;
};

const props =
  defineProps<{
    section: SectionName;
  }>();

const {
  locale,
  isRTL,
} = useLocale();

const auth = useAuth();

const items = ref<ListItem[]>([]);
const loading = ref(false);
const saving = ref(false);
const deleting = ref(false);
const searchQuery = ref("");
const errorMessage = ref("");
const successMessage = ref("");
const modalError = ref("");
const modalOpen = ref(false);
const editingItem = ref<ListItem | null>(null);
const deleteCandidate = ref<ListItem | null>(null);
const temporaryCredentials = ref<TemporaryCredentials | null>(null);
const credentialsCopied = ref(false);
const trusteeOptions = ref<OptionItem[]>([]);
const donorOptions = ref<OptionItem[]>([]);

const form =
  reactive<Record<string, any>>({});

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

const endpointMap: Record<SectionName, string> = {
  borrowers: "/borrowers/",
  trustees: "/trustees/",
  donors: "/donors/",
  donations: "/donations/",
  admins: "/admin-users/",
};

const titleMap = computed<Record<SectionName, string>>(() => ({
  borrowers: text("לווים", "Borrowers", "Prestatarios"),
  trustees: text("נאמנים", "Trustees", "Responsables"),
  donors: text("תורמים", "Donors", "Donantes"),
  donations: text("תרומות", "Donations", "Donaciones"),
  admins: text("מנהלי מערכת", "Administrators", "Administradores"),
}));

const pageTitle = computed(() =>
  titleMap.value[props.section]
);

const searchPlaceholder = computed(() => {
  const values: Record<SectionName, string> = {
    borrowers: text(
      "חיפוש לפי שם, תעודת זהות, טלפון או אימייל",
      "Search by name, ID, phone, or email",
      "Buscar por nombre, identificación, teléfono o correo"
    ),
    trustees: text(
      "חיפוש לפי שם, קהילה, טלפון או אימייל",
      "Search by name, community, phone, or email",
      "Buscar por nombre, comunidad, teléfono o correo"
    ),
    donors: text(
      "חיפוש לפי שם, טלפון או אימייל",
      "Search by name, phone, or email",
      "Buscar por nombre, teléfono o correo"
    ),
    donations: text(
      "חיפוש לפי תורם, סכום, תאריך או הערה",
      "Search by donor, amount, date, or note",
      "Buscar por donante, importe, fecha o nota"
    ),
    admins: text(
      "חיפוש לפי שם, שם משתמש או אימייל",
      "Search by name, username, or email",
      "Buscar por nombre, usuario o correo"
    ),
  };

  return values[props.section];
});

const loadingLabel = computed(() => text("טוען נתונים...", "Loading...", "Cargando..."));
const editLabel = computed(() => text("עריכה", "Edit", "Editar"));
const deleteLabel = computed(() => text("מחיקה", "Delete", "Eliminar"));
const cancelLabel = computed(() => text("ביטול", "Cancel", "Cancelar"));
const saveLabel = computed(() => text("שמירה", "Save", "Guardar"));
const savingLabel = computed(() => text("שומר...", "Saving...", "Guardando..."));
const deletingLabel = computed(() => text("מוחק...", "Deleting...", "Eliminando..."));
const doneLabel = computed(() => text("סיום", "Done", "Finalizar"));
const firstNameLabel = computed(() => text("שם פרטי", "First name", "Nombre"));
const lastNameLabel = computed(() => text("שם משפחה", "Last name", "Apellido"));
const emailLabel = computed(() => text("אימייל", "Email", "Correo electrónico"));
const phoneLabel = computed(() => text("טלפון", "Phone", "Teléfono"));
const communityLabel = computed(() => text("קהילה", "Community", "Comunidad"));
const notesLabel = computed(() => text("הערות", "Notes", "Notas"));
const idNumberLabel = computed(() => text("תעודת זהות", "ID number", "Identificación"));
const addressLabel = computed(() => text("כתובת", "Address", "Dirección"));
const trusteeLabel = computed(() => text("נאמן", "Trustee", "Responsable"));
const donorLabel = computed(() => text("תורם", "Donor", "Donante"));
const amountLabel = computed(() => text("סכום", "Amount", "Importe"));
const dateLabel = computed(() => text("תאריך", "Date", "Fecha"));
const usernameLabel = computed(() => text("שם משתמש", "Username", "Usuario"));
const temporaryPasswordLabel = computed(() => text("סיסמה זמנית", "Temporary password", "Contraseña temporal"));
const selectDonorLabel = computed(() => text("בחר תורם", "Select donor", "Selecciona donante"));
const copyLabel = computed(() => text("העתקת פרטי כניסה", "Copy login details", "Copiar datos de acceso"));
const copiedLabel = computed(() => text("הועתק", "Copied", "Copiado"));
const adminLoginHint = computed(() =>
  text(
    "שם המשתמש ייווצר אוטומטית מהשם הפרטי ושם המשפחה. לאחר השמירה תוצג סיסמה זמנית לכניסה הראשונה.",
    "The username is generated automatically from the first and last name. A temporary password will be shown after saving.",
    "El usuario se genera automáticamente a partir del nombre y apellido. Después de guardar se mostrará una contraseña temporal."
  )
);

const credentialsTitle = computed(() =>
  text(
    "פרטי כניסה לאתר",
    "Website login details",
    "Datos de acceso al sitio"
  )
);

const credentialsNotice = computed(() =>
  text(
    "יש להעביר למשתמש את שם המשתמש והסיסמה. בכניסה הראשונה הוא יתבקש להחליף סיסמה.",
    "Give the user this username and password. They will be asked to change the password on first login.",
    "Entrega al usuario este nombre y contraseña. En el primer acceso deberá cambiar la contraseña."
  )
);

const canEdit = computed(() =>
  auth.isAdmin.value
);

const showCreateButton = computed(() =>
  auth.isAdmin.value
);

const createLabel = computed(() => {
  const labels: Record<SectionName, string> = {
    borrowers: text("לווה חדש", "New borrower", "Nuevo prestatario"),
    trustees: text("נאמן חדש", "New trustee", "Nuevo responsable"),
    donors: text("תורם חדש", "New donor", "Nuevo donante"),
    donations: text("תרומה חדשה", "New donation", "Nueva donación"),
    admins: text("מנהל חדש", "New administrator", "Nuevo administrador"),
  };

  return labels[props.section];
});

const emptyTitle = computed(() => text("לא נמצאו נתונים", "No records found", "No se encontraron registros"));
const emptyDescription = computed(() => text("אין כרגע רשומות להצגה.", "There are currently no records to display.", "No hay registros para mostrar."));

const modalTitle = computed(() =>
  editingItem.value
    ? text("עריכת פרטים", "Edit details", "Editar datos")
    : createLabel.value
);

const deleteConfirmTitle = computed(() => text("אישור מחיקה", "Confirm deletion", "Confirmar eliminación"));
const deleteConfirmText = computed(() => text("האם להמשיך בפעולה?", "Do you want to continue?", "¿Quieres continuar?"));

const currentUsername = computed(() => {
  if (!editingItem.value) {
    return "";
  }

  const user = getUserDetails(editingItem.value);
  return String(
    editingItem.value.username ||
    user.username ||
    ""
  );
});

const filteredItems = computed(() => {
  const query =
    searchQuery.value.trim().toLowerCase();

  if (!query) {
    return items.value;
  }

  return items.value.filter((item) =>
    JSON.stringify(item)
      .toLowerCase()
      .includes(query)
  );
});

function getItemId(item: ListItem): string {
  return String(
    item.borrower_id ||
    item.trustee_id ||
    item.donor_id ||
    item.donation_id ||
    item.user_id ||
    item.id ||
    ""
  );
}

function getUserDetails(item: ListItem): ListItem {
  return item.user_details || item.user || {};
}

function getPersonName(item: ListItem): string {
  const user = getUserDetails(item);
  const first = String(item.first_name || user.first_name || "").trim();
  const last = String(item.last_name || user.last_name || "").trim();
  const fullName = `${first} ${last}`.trim();

  return fullName || String(user.username || item.username || "").trim();
}

function getPrimaryLabel(item: ListItem): string {
  if (props.section === "donations") {
    const donor = item.donor_details || item.donor || {};
    return getPersonName(donor) || text("תרומה", "Donation", "Donación");
  }

  return getPersonName(item) || getItemId(item) || "—";
}

function getSecondaryLabel(item: ListItem): string {
  if (props.section === "trustees") {
    return String(item.community || "");
  }

  if (props.section === "donations") {
    return formatCurrency(item.amount || 0);
  }

  const user = getUserDetails(item);
  return String(item.email || user.email || "");
}

function getStatusLabel(item: ListItem): string {
  const user = getUserDetails(item);
  const isActive = item.is_active ?? user.is_active;

  if (typeof isActive !== "boolean") {
    return "";
  }

  if (props.section === "admins" && isActive) {
    return "";
  }

  return isActive
    ? text("פעיל", "Active", "Activo")
    : text("לא פעיל", "Inactive", "Inactivo");
}

function getStatusClass(item: ListItem): string {
  const user = getUserDetails(item);
  const isActive = item.is_active ?? user.is_active;

  return isActive === false
    ? "bg-danger/10 text-danger"
    : "bg-success/10 text-success-deep";
}

function formatCurrency(value: any): string {
  const formatterLocale =
    locale.value === "he"
      ? "he-IL"
      : locale.value === "es"
        ? "es-ES"
        : "en-US";

  return new Intl.NumberFormat(
    formatterLocale,
    {
      style: "currency",
      currency: "ILS",
      maximumFractionDigits: 2,
    }
  ).format(Number(value || 0));
}

function formatDate(value: any): string {
  if (!value) {
    return "—";
  }

  const raw = String(value);
  const date = new Date(
    raw.length === 10
      ? `${raw}T00:00:00`
      : raw
  );

  if (Number.isNaN(date.getTime())) {
    return raw;
  }

  const formatterLocale =
    locale.value === "he"
      ? "he-IL"
      : locale.value === "es"
        ? "es-ES"
        : "en-US";

  return date.toLocaleDateString(formatterLocale);
}

type DetailItem = {
  label: string;
  value: string;
  href?: string;
};

function phoneHref(value: unknown): string | undefined {
  const phone = String(value || "").trim();

  if (!phone || phone === "—") {
    return undefined;
  }

  const normalized = phone.replace(/[^\d+]/g, "");

  return normalized
    ? `tel:${normalized}`
    : undefined;
}

function emailHref(value: unknown): string | undefined {
  const email = String(value || "").trim();

  if (!email || email === "—") {
    return undefined;
  }

  return `mailto:${email}`;
}

function getDetails(item: ListItem): DetailItem[] {
  const user = getUserDetails(item);

  if (props.section === "borrowers") {
    return [
      { label: idNumberLabel.value, value: String(item.id_number || "—") },
      {
        label: phoneLabel.value,
        value: String(item.phone || user.phone || "—"),
        href: phoneHref(item.phone || user.phone),
      },
      { label: emailLabel.value, value: String(item.email || user.email || "—"), href: emailHref(item.email || user.email) },
      { label: addressLabel.value, value: String(item.address || "—") },
    ];
  }

  if (props.section === "trustees") {
    return [
      { label: communityLabel.value, value: String(item.community || "—") },
      {
        label: phoneLabel.value,
        value: String(item.phone || user.phone || "—"),
        href: phoneHref(item.phone || user.phone),
      },
      { label: emailLabel.value, value: String(item.email || user.email || "—"), href: emailHref(item.email || user.email) },
    ];
  }

  if (props.section === "donors") {
    return [
      {
        label: phoneLabel.value,
        value: String(item.phone || user.phone || "—"),
        href: phoneHref(item.phone || user.phone),
      },
      { label: emailLabel.value, value: String(item.email || user.email || "—"), href: emailHref(item.email || user.email) },
      { label: notesLabel.value, value: String(item.notes || "—") },
    ];
  }

  if (props.section === "donations") {
    return [
      { label: amountLabel.value, value: formatCurrency(item.amount) },
      { label: dateLabel.value, value: formatDate(item.donation_date || item.date) },
      { label: notesLabel.value, value: String(item.notes || "—") },
    ];
  }

  return [
    { label: emailLabel.value, value: String(item.email || user.email || "—"), href: emailHref(item.email || user.email) },
    {
        label: phoneLabel.value,
        value: String(item.phone || user.phone || "—"),
        href: phoneHref(item.phone || user.phone),
      },
    { label: usernameLabel.value, value: String(item.username || user.username || "—") },
  ];
}

function resetForm(): void {
  for (const key of Object.keys(form)) {
    delete form[key];
  }

  Object.assign(form, {
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    community: "",
    notes: "",
    id_number: "",
    address: "",
    trustee: "",
    donor: "",
    amount: "",
    donation_date: new Date().toISOString().slice(0, 10),
  });
}

function populateForm(item: ListItem): void {
  resetForm();
  const user = getUserDetails(item);

  form.first_name = item.first_name || user.first_name || "";
  form.last_name = item.last_name || user.last_name || "";
  form.email = item.email || user.email || "";
  form.phone = item.phone || user.phone || "";
  form.community = item.community || "";
  form.notes = item.notes || "";
  form.id_number = item.id_number || "";
  form.address = item.address || "";
  form.trustee = item.trustee_id || item.trustee || "";
  form.donor = item.donor_id || (typeof item.donor === "string" ? item.donor : item.donor?.donor_id) || "";
  form.amount = item.amount || "";
  form.donation_date = item.donation_date || item.date || new Date().toISOString().slice(0, 10);
}

function openCreateModal(): void {
  editingItem.value = null;
  temporaryCredentials.value = null;
  credentialsCopied.value = false;
  modalError.value = "";
  resetForm();
  modalOpen.value = true;
}

function openEditModal(item: ListItem): void {
  editingItem.value = item;
  temporaryCredentials.value = null;
  credentialsCopied.value = false;
  modalError.value = "";
  populateForm(item);
  modalOpen.value = true;
}

function closeModal(): void {
  modalOpen.value = false;
  editingItem.value = null;
  temporaryCredentials.value = null;
  credentialsCopied.value = false;
  modalError.value = "";
}

function finishCredentials(): void {
  closeModal();
}

async function copyCredentials(): Promise<void> {
  if (!temporaryCredentials.value) {
    return;
  }

  const value =
    `${usernameLabel.value}: ${temporaryCredentials.value.username}\n` +
    `${temporaryPasswordLabel.value}: ${temporaryCredentials.value.temporary_password}`;

  try {
    await navigator.clipboard.writeText(value);
    credentialsCopied.value = true;
  } catch {
    credentialsCopied.value = false;
  }
}

function buildPayload(): Record<string, any> {
  if (props.section === "trustees") {
    return {
      first_name: String(form.first_name || "").trim(),
      last_name: String(form.last_name || "").trim(),
      email: String(form.email || "").trim(),
      phone: String(form.phone || "").trim(),
      community: String(form.community || "").trim(),
      notes: String(form.notes || "").trim(),
    };
  }

  if (props.section === "donors") {
    return {
      first_name: String(form.first_name || "").trim(),
      last_name: String(form.last_name || "").trim(),
      email: String(form.email || "").trim(),
      phone: String(form.phone || "").trim(),
      notes: String(form.notes || "").trim(),
    };
  }

  if (props.section === "admins") {
    return {
      first_name: String(form.first_name || "").trim(),
      last_name: String(form.last_name || "").trim(),
      email: String(form.email || "").trim(),
      phone: String(form.phone || "").trim(),
    };
  }

  if (props.section === "borrowers") {
    return {
      id_number: String(form.id_number || "").trim(),
      first_name: String(form.first_name || "").trim(),
      last_name: String(form.last_name || "").trim(),
      phone: String(form.phone || "").trim(),
      email: String(form.email || "").trim(),
      address: String(form.address || "").trim(),
      trustee: form.trustee || null,
    };
  }

  return {
    donor: form.donor,
    amount: Number(form.amount),
    donation_date: form.donation_date,
    notes: String(form.notes || "").trim(),
  };
}

function normalizeApiError(requestError: any): string {
  const data = requestError?.response?.data;

  if (typeof data?.detail === "string") {
    return data.detail;
  }

  if (data && typeof data === "object") {
    for (const value of Object.values(data)) {
      if (typeof value === "string") {
        return value;
      }

      if (Array.isArray(value) && value.length) {
        return String(value[0]);
      }
    }
  }

  return text(
    "הפעולה נכשלה.",
    "The operation failed.",
    "La operación falló."
  );
}

function extractCredentials(data: any): TemporaryCredentials | null {
  const source =
    data?.credentials ||
    data?.temporary_credentials ||
    data?.user_credentials ||
    data;

  const username = source?.username;
  const password = source?.temporary_password;

  if (!username || !password) {
    return null;
  }

  return {
    username: String(username),
    temporary_password: String(password),
  };
}

async function saveItem(): Promise<void> {
  if (saving.value) {
    return;
  }

  modalError.value = "";
  saving.value = true;

  try {
    const payload = buildPayload();
    let response;

    if (editingItem.value) {
      const id = getItemId(editingItem.value);
      response = await api.patch(
        `${endpointMap[props.section]}${encodeURIComponent(id)}/`,
        payload
      );
    } else {
      response = await api.post(
        endpointMap[props.section],
        payload
      );
    }

    const credentials = extractCredentials(response.data);

    if (credentials) {
      temporaryCredentials.value = credentials;
      credentialsCopied.value = false;
      await loadItems(false);
      return;
    }

    closeModal();
    successMessage.value = text(
      "הנתונים נשמרו בהצלחה.",
      "Saved successfully.",
      "Guardado correctamente."
    );
    await loadItems(false);
  } catch (
    requestError: any
  ) {
    modalError.value = normalizeApiError(requestError);
  } finally {
    saving.value = false;
  }
}

function requestDelete(item: ListItem): void {
  deleteCandidate.value = item;
}

async function confirmDelete(): Promise<void> {
  if (!deleteCandidate.value || deleting.value) {
    return;
  }

  deleting.value = true;
  errorMessage.value = "";

  try {
    const id = getItemId(deleteCandidate.value);
    await api.delete(
      `${endpointMap[props.section]}${encodeURIComponent(id)}/`
    );

    deleteCandidate.value = null;
    successMessage.value = text(
      "הרשומה עודכנה בהצלחה.",
      "Record updated successfully.",
      "Registro actualizado correctamente."
    );
    await loadItems(false);
  } catch (
    requestError: any
  ) {
    errorMessage.value = normalizeApiError(requestError);
  } finally {
    deleting.value = false;
  }
}

async function loadSupportingData(): Promise<void> {
  const requests: Promise<any>[] = [];

  if (props.section === "borrowers") {
    requests.push(
      api.get("/trustees/").then((response) => {
        const data = Array.isArray(response.data) ? response.data : [];
        trusteeOptions.value = data
          .map((item: any) => ({
            id: String(item.trustee_id || item.id || ""),
            label: getPersonName(item) || String(item.community || "—"),
          }))
          .filter((item: OptionItem) => Boolean(item.id));
      })
    );
  }

  if (props.section === "donations" && auth.isAdmin.value) {
    requests.push(
      api.get("/donors/").then((response) => {
        const data = Array.isArray(response.data) ? response.data : [];
        donorOptions.value = data
          .map((item: any) => ({
            id: String(item.donor_id || item.id || ""),
            label: getPersonName(item) || String(item.donor_id || "—"),
          }))
          .filter((item: OptionItem) => Boolean(item.id));
      })
    );
  }

  if (requests.length) {
    await Promise.allSettled(requests);
  }
}

async function loadItems(
  showLoader = true
): Promise<void> {
  if (showLoader) {
    loading.value = true;
  }

  errorMessage.value = "";

  try {
    const response =
      await api.get(
        endpointMap[props.section]
      );

    items.value =
      Array.isArray(response.data)
        ? response.data
        : [];

    await loadSupportingData();
  } catch (
    requestError: any
  ) {
    items.value = [];
    errorMessage.value = normalizeApiError(requestError);
  } finally {
    if (showLoader) {
      loading.value = false;
    }
  }
}

const TextField = defineComponent({
  props: {
    modelValue: {
      type: [String, Number],
      default: "",
    },
    label: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      default: "text",
    },
    required: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["update:modelValue"],
  setup(fieldProps, { emit }) {
    return () =>
      h(
        "label",
        {
          class: "flex flex-col gap-1.5",
        },
        [
          h(
            "span",
            {
              class: "text-sm font-medium text-ink-soft",
            },
            `${fieldProps.label}${fieldProps.required ? " *" : ""}`
          ),
          h("input", {
            value: fieldProps.modelValue,
            type: fieldProps.type,
            required: fieldProps.required,
            class: "h-11 rounded-lg border border-line bg-white px-3 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20",
            onInput: (event: Event) => {
              const target = event.target;
              if (target instanceof HTMLInputElement) {
                emit("update:modelValue", target.value);
              }
            },
          }),
        ]
      );
  },
});

const TextAreaField = defineComponent({
  props: {
    modelValue: {
      type: String,
      default: "",
    },
    label: {
      type: String,
      required: true,
    },
  },
  emits: ["update:modelValue"],
  setup(fieldProps, { emit }) {
    return () =>
      h(
        "label",
        {
          class: "flex flex-col gap-1.5",
        },
        [
          h(
            "span",
            {
              class: "text-sm font-medium text-ink-soft",
            },
            fieldProps.label
          ),
          h("textarea", {
            value: fieldProps.modelValue,
            rows: 3,
            maxlength: 1000,
            class: "rounded-lg border border-line bg-white px-3 py-2 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20",
            onInput: (event: Event) => {
              const target = event.target;
              if (target instanceof HTMLTextAreaElement) {
                emit("update:modelValue", target.value);
              }
            },
          }),
        ]
      );
  },
});

onMounted(() => {
  resetForm();
  loadItems();
});

watch(
  () => props.section,
  () => {
    searchQuery.value = "";
    successMessage.value = "";
    errorMessage.value = "";
    closeModal();
    loadItems();
  }
);
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
