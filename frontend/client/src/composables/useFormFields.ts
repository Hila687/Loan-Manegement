import { computed } from "vue";

export interface FormField {
  name: string;
  ref: any;
  order: number;
}

export function useFormFields() {
  // Map of field name -> field definition (ref + order)
  const fields = new Map<string, FormField>();

  // Register or update a field
  function registerField(name: string, refObj: any, order: number) {
    fields.set(name, { name, ref: refObj, order });
  }

  // Sorted list of field names by order
  const fieldOrder = computed(() => {
    return Array.from(fields.values())
      .sort((a, b) => a.order - b.order)
      .map((f) => f.name);
  });

  // Focus a specific field by name
  function focusField(fieldName: string) {
    const field = fields.get(fieldName);
    const target = field?.ref?.value;
    if (target && typeof target.focus === "function") {
      target.focus();
    }
  }

  // Focus the next field in order
  function focusNextField(currentFieldName: string) {
    const order = fieldOrder.value;
    const index = order.indexOf(currentFieldName);
    if (index !== -1 && index < order.length - 1) {
      focusField(order[index + 1]);
    }
  }

  // Focus the previous field in order
  function focusPreviousField(currentFieldName: string) {
    const order = fieldOrder.value;
    const index = order.indexOf(currentFieldName);
    if (index > 0) {
      focusField(order[index - 1]);
    }
  }

  return {
    registerField,
    focusField,
    focusNextField,
    focusPreviousField,
    fieldOrder,
  };
}
