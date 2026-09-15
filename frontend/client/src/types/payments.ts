export type PaymentStatus =
  | "PENDING"
  | "PAID"
  | "LATE";

export interface PaymentRow {
  payment_id: string;
  due_date: string;

  amount_due:
    | number
    | string;

  amount_paid:
    | number
    | string;

  status: PaymentStatus;

  is_manual_exception: boolean;

  exception_note: string;
}

export interface PaymentSummary {
  total_amount:
    | number
    | string;

  paid_amount:
    | number
    | string;

  total_payments: number;

  paid_payments: number;

  late_payments: number;
}

export interface PaymentScheduleResponse {
  loan_id: string;

  loan_status:
    | "ACTIVE"
    | "OVERDUE"
    | "CLOSED";

  summary: PaymentSummary;

  payments: PaymentRow[];
}

export interface PaymentExceptionPayload {
  status?: PaymentStatus;

  amount_paid?: number;

  note?: string;

  clear_exception?: boolean;
}