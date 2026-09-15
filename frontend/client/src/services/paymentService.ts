import api from "./api";

import type {
  PaymentExceptionPayload,
  PaymentRow,
  PaymentScheduleResponse,
} from "../types/payments";

export async function getLoanPayments(
  loanId: string
): Promise<PaymentScheduleResponse> {
  const response =
    await api.get<PaymentScheduleResponse>(
      `/loans/${encodeURIComponent(
        loanId
      )}/payments/`
    );

  return response.data;
}

export async function updatePaymentException(
  paymentId: string,
  payload: PaymentExceptionPayload
): Promise<PaymentRow> {
  const response =
    await api.patch<PaymentRow>(
      `/payments/${encodeURIComponent(
        paymentId
      )}/exception/`,
      payload
    );

  return response.data;
}