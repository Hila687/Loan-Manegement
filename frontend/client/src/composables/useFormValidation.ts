import { ref } from "vue";

export interface ValidationState {
  [key: string]: boolean;
}

export interface FieldErrorMessages {
  [key: string]: string;
}

export function useFormValidation() {
  const validationErrors = ref<ValidationState>({});
  const fieldErrorMessages = ref<FieldErrorMessages>({});

  function clearFieldError(field: string) {
    validationErrors.value[field] = false;
    fieldErrorMessages.value[field] = "";
  }

  function setFieldError(field: string, message: string) {
    validationErrors.value[field] = true;
    fieldErrorMessages.value[field] = message;
  }

  function clearAllErrors() {
    validationErrors.value = {};
    fieldErrorMessages.value = {};
  }

  function hasErrors(): boolean {
    return Object.values(validationErrors.value).some((v) => v === true);
  }

  return {
    validationErrors,
    fieldErrorMessages,
    clearFieldError,
    setFieldError,
    clearAllErrors,
    hasErrors,
  };
}