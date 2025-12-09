// src/types/loan.ts

// ========== Borrower ==========
export interface Borrower {
  id_number?: string;        // ת"ז
  name: string;
  phone: string;
  email?: string;
  address?: string;
  created_at?: string;
}

// ========== Trustee ==========
export interface Trustee {
  name: string;
  community?: string;
  phone?: string;
  notes?: string;
}

// ========== Details for Checks ==========
export interface CheckLoanDetails {
  num_payments: number;
  check_details?: string;
  predefined_schedule: boolean;
}

// ========== Details for Standing Order ==========
export interface StandingOrderDetails {
  monthly_amount: string;
  charge_day: number;
  stop_date?: string | null;
}

// Union של שני סוגי ה-details האפשריים
export type LoanDetails = CheckLoanDetails | StandingOrderDetails;

// ========== Main Loan ==========
export interface Loan {
  loan_id: string;           // מזהה ההלוואה (UUID)
  loan_type: "checks" | "standing" | "other";

  amount: number;
  start_date?: string;
  status?: string;
  created_at?: string;

  borrower: Borrower;
  trustee: Trustee;

  details: LoanDetails;

  form_file_url?: string | null;
}
