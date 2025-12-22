export function adaptLoanListItem(api: any) {
  return {
    id: api.loan_id,
    type: api.loan_type,
    amount: Number(api.amount),

    borrower: {
      name: api.borrower.name,
      phone: api.borrower.phone,
      email: api.borrower.email || "-",
    },

    trustee: {
      name: api.trustee.name,
      community: api.trustee.community || "",
    },
  };
}

export function adaptLoanDetails(api: any) {
  return {
    ...adaptLoanListItem(api),
    trustee_id: api.trustee_id,

    details: api.details,
    startDate: api.start_date,
    status: api.status,
    createdAt: api.created_at,
  };
}
