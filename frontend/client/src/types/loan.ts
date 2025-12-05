// src/types/loan.ts
export interface Borrower {
  id: number;
  name: string;
  phone: string;
  email?: string;
}

export interface Loan {
  id: number;
  amount: number;
  borrower: Borrower;
  trustee: string;
  type: "checks" | "standing" | "other";
}
