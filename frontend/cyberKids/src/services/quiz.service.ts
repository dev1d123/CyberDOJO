import { API_CONFIG } from "@/config/api.config";

const API_BASE = API_CONFIG.BASE_URL;

/* =========================
   HELPERS
========================= */

const tryJson = async (res: Response) => {
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? await res.json() : null;
};

const getAuthHeaders = () => {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("No access token found");
  }

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
};

/* =========================
   TYPES
========================= */

export type QuizProgress = {
  answered: number;
  total: number;
  correct: number;
  percentage: number;
};

export type QuizListItem = {
  id: number;
  title: string;
  description?: string | null;
  difficulty: number | null;
  base_points: number;
  time_limit_seconds?: number | null;
  category?: string;
  segment?: string;
  image_url?: string | null;
  progress?: QuizProgress | null;
  status?: "not_started" | "in_progress" | "completed";
};

export type QuizSession = {
  id: number;
  quiz_id: number;
  status: "in_progress" | "completed";
  attempt_number: number;
  total_answered: number;
  total_correct: number;
  coins_earned: number;
  points_earned: number;
  started_at: string;
  ended_at?: string | null;
};

export type SubmitAnswerRequest = {
  session_id: number;
  question_id: number;
  selected_alternative_id: number;
  time_spent_seconds?: number;
};

export type SubmitAnswerResponse = {
  is_correct: boolean;
  feedback: string;
  explanation?: string;
  correct_alternative?: string;
  quiz_completed?: boolean;
  total_correct?: number;
  total_answered?: number;
  coins_earned?: number;
  points_earned?: number;
  percentage?: number;
  cybercreds_balance?: number;
};

/* =========================
   SERVICE
========================= */

export class QuizService {
  static QUIZ_BASE = `${API_BASE}/quiz/quizzes`;

  static async getAll(): Promise<QuizListItem[]> {
    const res = await fetch(`${this.QUIZ_BASE}/`, {
      headers: getAuthHeaders(),
    });

    if (!res.ok) {
      throw new Error(`Could not fetch quizzes list: ${res.status}`);
    }

    const data = await tryJson(res);

    if (!data) return [];

    return Array.isArray(data) ? data : data.results ?? [];
  }

  static async getQuizById(id: string | number): Promise<any> {
    const res = await fetch(`${this.QUIZ_BASE}/${id}/`, {
      headers: getAuthHeaders(),
    });

    if (!res.ok) {
      throw new Error(`Could not fetch quiz ${id}: ${res.status}`);
    }

    const data = await tryJson(res);
    return data ?? {};
  }

  static async startQuizSession(
    quizId: number,
    options?: { confirmRetry?: boolean }
  ): Promise<any> {
    const body = options?.confirmRetry ? JSON.stringify({ confirm_retry: true }) : undefined;
    const res = await fetch(`${this.QUIZ_BASE}/${quizId}/start/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body,
    });

    if (!res.ok) {
      throw new Error(`Could not start quiz session: ${res.status}`);
    }

    const data = await tryJson(res);
    return data ?? {};
  }

  static async submitAnswer(quizId: number, payload: SubmitAnswerRequest): Promise<SubmitAnswerResponse> {
    const res = await fetch(`${this.QUIZ_BASE}/${quizId}/submit/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const error = await tryJson(res);
      console.error('❌ Error del backend:', error);
      const errorMessage = error?.detail 
        || error?.message 
        || JSON.stringify(error) 
        || `Could not submit answer: ${res.status}`;
      throw new Error(errorMessage);
    }

    const data = await tryJson(res);
    return data ?? {};
  }
}