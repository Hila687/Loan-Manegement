export type LoanStatus = "PENDING" | "ACTIVE" | "PAID" | "REJECTED";

export enum LoanType {
  CHECKS = "checks",
  STANDING_ORDER = "standing_order",
}

export interface Borrower {
  name: string;
  phone: string;
  email?: string;
  idNumber?: string;
  address?: string;
  createdAt?: string;
}

export interface Trustee {
  name: string;
  community?: string;
  phone?: string;
  notes?: string | null;
}

/* -------- LIST -------- */

export interface LoanListItem {
  id: string;
  type: LoanType;
  status: LoanStatus;
  amount: number;
  startDate: string;

  borrower: Borrower;
  trustee: Trustee | null;
}

/* -------- DETAILS -------- */

export interface LoanChecksDetails {
  numPayments: number;              // מספר תשלומים
  predefinedSchedule: boolean;      // לפי לוח מוגדר
  checkDetails?: string | null;     // פרטי צ'קים
}

export interface LoanStandingOrderDetails {
  monthlyAmount: number;
  chargeDay: number;
  stopDate?: string | null;
}

export type LoanDetailsUnion =
  | LoanChecksDetails
  | LoanStandingOrderDetails
  | {};

export interface Loan {
  id: string;
  amount: number;
  type: LoanType;
  status: LoanStatus;
  startDate: string;
  createdAt: string;
  formFileUrl?: string | null;

  borrower: Borrower;
  trustee: Trustee | null;

  details: LoanDetailsUnion;
}

export interface LoanFilters {
  type?: "all" | LoanType;
  status?: LoanStatus | "all" | string;
  search?: string;
}
