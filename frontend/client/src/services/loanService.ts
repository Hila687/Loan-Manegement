// src/services/loanService.ts
import api from "./api";

export default {
  async getLoans(type: string) {
    const params = type !== "all" ? { type } : {};
    const res = await api.get("/loans", { params });
    return res.data;
  },
};
