// src/types/api-loan.ts

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
  loan_type: "checks" | "standing_order";
  amount: string;         
  start_date: string;    
  status: string;       

  borrower: ApiBorrower;
  trustee: ApiTrustee | null;
}

export interface ApiLoanDetails extends ApiLoanListItem {
  created_at: string;          // obj.created_at
  form_file_url: string | null;

  details:
    | {
        // LoanChecks
        num_payments: number;
        check_details: string;
        predefined_schedule: boolean;
      }
    | {
        // LoanStandingOrder
        monthly_amount: string;  
        charge_day: number;
        stop_date: string | null;
      };
}
