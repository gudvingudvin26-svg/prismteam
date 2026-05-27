import api from './api'

export const sessionsApi = {
  createSession: (quizId: number) =>
    api.post('/api/organizer/sessions/', { quiz: quizId }),

  joinSession: (code: string, nickname: string) =>
    api.post('/api/organizer/sessions/join/', { code, nickname }),

  startSession: (sessionId: number) =>
    api.post(`/api/organizer/sessions/${sessionId}/start/`),

  endSession: (sessionId: number) =>
    api.post(`/api/organizer/sessions/${sessionId}/end/`),

  getSession: (sessionId: number) =>
    api.get(`/api/organizer/sessions/${sessionId}/`),

  getSessionsForQuiz: (quizId: number) =>
    api.get(`/api/organizer/sessions/?quiz=${quizId}`),

  getCurrentQuestion: (sessionId: number, index: number = 0) =>
    api.get(`/api/organizer/sessions/${sessionId}/?index=${index}`),

  submitAnswer: (sessionId: number, questionId: number, answerId: number) =>
    api.post(`/api/organizer/sessions/${sessionId}/answer/`, {
      question_id: questionId,
      answer_id: answerId
    }),

  submitMultipleAnswers: (sessionId: number, questionId: number, answerIds: number[]) =>
    api.post(`/api/organizer/sessions/${sessionId}/answer/`, {
      question_id: questionId,
      answer_ids: answerIds
    }),

  getMyResult: (sessionId: number) =>
    api.get(`/api/organizer/sessions/${sessionId}/my_result/`),

  getResults: (sessionId: number) =>
    api.get(`/api/organizer/sessions/${sessionId}/results/`),

  getQuestionsStats: (sessionId: number) =>
    api.get(`/api/organizer/sessions/${sessionId}/questions_stats/`)
}