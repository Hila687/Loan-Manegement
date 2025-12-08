// Loan Types and Interfaces

export enum LoanType {
  CHECKS = "checks",
  STANDING_ORDERS = "standing_orders",
}

export enum LoanStatus {
  ACTIVE = "active",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
  PENDING = "pending",
}

export interface Borrower {
  id?: string;
  name: string;
  phone: string;
  email?: string;
  address?: string;
}

export interface Trustee {
  id: string;
  name: string;
  community?: string;
  email?: string;
  phone?: string;
}

export interface Loan {
  id: string;
  borrower: Borrower;
  trustee: Trustee;
  amount: number;
  start_date: string;
  num_payments: number;
  type: LoanType;
  status: LoanStatus;
  created_at: string;
  updated_at?: string;
  form_file_url?: string;
}

export interface LoanListItem {
  id: string;
  borrower_name: string;
  borrower_phone: string;
  borrower_email?: string;
  trustee_name: string;
  trustee_community?: string;
  amount: number;
  type: LoanType;
  status: LoanStatus;
  start_date: string;
  num_payments: number;
}

export interface LoanFilters {
  type?: LoanType | "all";
  status?: LoanStatus;
  search?: string;
}

export interface PaginatedLoans {
  loans: LoanListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}