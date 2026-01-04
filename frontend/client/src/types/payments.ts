export type PaymentStatus = "PAID" | "PENDING";

export interface PaymentRow {
  payment_id: string;
  due_date: string;       // YYYY-MM-DD
  amount_due: number;
  amount_paid: number;
  status: PaymentStatus;
}

export interface PaymentSummary {
  total_amount: number;
  paid_amount: number;
  total_payments: number;
  paid_payments: number;
}

export interface PaymentScheduleResponse {
  loan_id: string;
  summary: PaymentSummary;
  payments: PaymentRow[];
}

