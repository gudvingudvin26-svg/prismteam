/**
 * @fileoverview
 */

export type UserRole = 'organizer' | 'participant';

export interface User {
  id: number;
  email: string;
  role: UserRole;
  first_name?: string;
  last_name?: string;
  date_joined: string;
}

export interface Quiz {
  id: number;
  title: string;
  description: string;
  author: number;
  timer?: number;
  created_at: string;
  questions_count?: number;
  sessions_count?: number;
}

export interface Answer {
  id: number;
  text: string;
  is_correct?: boolean;
  question: number;
}

export interface Question {
  id: number;
  text: string;
  order: number;
  quiz: number;
  timer?: number;
  answers: Answer[];
}

export interface QuizSession {
  id: number;
  quiz: number;
  status: 'preparation' | 'active' | 'completed';
  code: string;
  started_at: string;
}

export interface Participant {
  id: number;
  session: number;
  user?: number;
  nickname: string;
}

export interface UserAnswer {
  id: number;
  participant: number;
  question: number;
  answer: number;
  answer_text?: string;
  answered_at: string;
}

export interface ParticipantResult {
  participant_id: number;
  nickname: string;
  score: number;
  correct_answers: number;
  rank?: number;
}

export interface QuestionStat {
  question_id: number;
  question_text: string;
  total_answers: number;
  correct_count: number;
  correct_percent: number;
}

export interface CurrentQuestion {
  id: number;
  text: string;
  order: number;
  timer?: number;
  answers: {
    id: number;
    text: string;
  }[];
}

export interface CreateQuizData {
  title: string;
  description: string;
  timer?: number;
}

export interface CreateQuestionData {
  text: string;
  order: number;
  timer?: number;
  answers: {
    text: string;
    is_correct: boolean;
  }[];
}