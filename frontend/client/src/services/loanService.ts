// src/services/loanService.ts
import api from "./api";
import type { LoanListItem, LoanFilters } from "../types/loan";

async function getLoans(type: string): Promise<LoanListItem[]> {
  const params = type !== "all" ? { type } : {};
  const res = await api.get<LoanListItem[]>("/loans", { params });
  return res.data;
}

async function getActiveLoans(filters: LoanFilters): Promise<LoanListItem[]> {
  const type = filters.type ?? "all";
  return getLoans(type);
}

export default {
  getLoans,
  getActiveLoans,
};
