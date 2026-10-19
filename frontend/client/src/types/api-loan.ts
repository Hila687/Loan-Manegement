export interface ApiBorrower {
  name: string;
  phone: string;
  email: string | null;

  id_number?: string;
  address?: string;
  created_at?: string;
}


export interface ApiTrustee {
  name: string;
  phone?: string;
  community?: string;
  notes?: string | null;
}


export interface ApiLoanListItem {
  loan_id: string;

  loan_type:
    | "checks"
    | "standing_order";

  amount:
    | string
    | number;

  start_date: string;

  status:
    | "ACTIVE"
    | "OVERDUE"
    | "CLOSED";

  remaining_amount?: string | number;
  paid_amount?: string | number;
  payments_total?: number;
  payments_paid?: number;
  next_payment?: { due_date: string; amount: string | number } | null;
  problem?: {
    count: number;
    missing_amount: string | number;
    notes: string[];
    payments: {
      due_date: string;
      amount: string | number;
      missing: string | number;
      status: string;
      note: string;
    }[];
  } | null;

  borrower:
    ApiBorrower;

  trustee:
    | ApiTrustee
    | null;
}


export interface ApiLoanChecksDetails {
  num_payments: number;

  check_details:
    | string
    | null;

  predefined_schedule:
    boolean;
}


export interface ApiLoanStandingOrderDetails {
  num_payments: number;

  monthly_amount:
    | string
    | number;

  charge_day: number;

  stop_date:
    | string
    | null;
}


export interface ApiLoanDetails
  extends ApiLoanListItem {
  created_at: string;

  trustee_id:
    | string
    | null;

  form_file_url:
    | string
    | null;

  standing_order_form_file_url?:
    | string
    | null;

  details:
    | ApiLoanChecksDetails
    | ApiLoanStandingOrderDetails;
}


export interface ApiLoanUpdatePayload {
  amount: number;
  start_date: string;
  number_of_payments: number;
  trustee_id: string;

  status:
    | "ACTIVE"
    | "OVERDUE"
    | "CLOSED";
}