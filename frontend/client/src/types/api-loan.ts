export interface ApiBorrower {
  name: string;
  phone: string;
  email: string | null;
  id_number?: string;
  address?: string;
}

export interface ApiTrustee {
  name: string;
  phone?: string;
  community?: string;
  notes?: string;
}

export interface ApiLoanListItem {
  loan_id: string;
  loan_type: "checks" | "standing_order";
  amount: string;
  start_date: string;
  status: string;

  borrower: ApiBorrower;
  trustee: ApiTrustee;
}

export interface ApiLoanDetails extends ApiLoanListItem {
  created_at: string;
  form_file_url: string | null;

  details:
    | {
        num_payments: number;
        check_details: string;
        predefined_schedule: boolean;
      }
    | {
        monthly_amount: string;
        charge_day: number;
        stop_date: string | null;
      };
}
