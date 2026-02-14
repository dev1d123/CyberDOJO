// DTOs para el sistema de onboarding

export interface AnswerOption {
  option_id: number;
  question: number;
  content: string;
  risk_value: number;
  display_order: number;
}

export interface OnboardingQuestion {
  question_id: number;
  content: string;
  response_type: 'multiple_choice' | 'yes_no' | 'scale' | 'age';
  risk_weight: number;
  display_order: number;
  is_active: boolean;
  options: AnswerOption[];
}

export interface OnboardingResponse {
  user: number;
  question: number;
  option: number | null;
  open_answer?: string;
}

// Registro tal cual lo devuelve el backend (GET /onboarding/responses/*)
export interface OnboardingResponseRecord {
  response_id: number;
  user: number;
  question: number;
  option: number | null;
  open_answer: string | null;
  submitted_at: string;
}

export interface UserAnswer {
  question_id: number;
  question_content: string;
  option_id: number;
  option_content: string;
  risk_value: number;
  risk_weight: number;
}

export interface OnboardingResult {
  answers: UserAnswer[];
  total_risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  recommendations: string[];
}
