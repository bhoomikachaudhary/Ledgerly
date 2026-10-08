export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Category {
  id: string;
  name: string;
  color: string;
  icon: string;
}

export interface Expense {
  id: string;
  category_id: string;
  amount: string;
  spent_on: string;
  note: string | null;
  receipt_key: string | null;
  created_at: string;
}

export interface ExpenseListResponse {
  items: Expense[];
  total: number;
  limit: number;
  offset: number;
}

export interface ExpenseFilters {
  category_id?: string;
  date_from?: string;
  date_to?: string;
  min_amount?: string;
  max_amount?: string;
  sort_by?: "spent_on" | "amount" | "created_at";
  sort_dir?: "asc" | "desc";
  limit?: number;
  offset?: number;
}

export interface Budget {
  id: string;
  category_id: string;
  month: string;
  limit_amount: string;
}

export interface CategorySummary {
  category_id: string;
  category_name: string;
  spent: string;
  budget: string | null;
}

export interface SummaryResponse {
  month: string;
  categories: CategorySummary[];
  total_spent: string;
  total_budget: string;
}

export interface TrendPoint {
  month: string;
  total_spent: string;
}

export interface TrendResponse {
  months: TrendPoint[];
}
