export interface User {
  id: number;
  username: string;
  email: string;
  phone?: string;
}

export interface AnswerOption {
  id?: number;
  text: string;
  is_correct: boolean;
}

export interface Question {
  id?: number;
  text: string;
  order: number;
  timer?: number;
  answer_options: AnswerOption[];
}

export interface Quiz {
  id?: number;
  title: string;
  description?: string;
  created_by?: number;
  access_token?: string;
  questions?: Question[];
  created_at?: string;
}

export interface SessionResult {
  id: number;
  participant_name: string;
  score: number;
  total_questions: number;
  completed_at: string;
}

export interface CurrentQuestion {
  id: number;
  text: string;
  timer?: number;
  answers: { id: number; text: string }[];
}