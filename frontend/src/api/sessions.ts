import api from './api'

export const sessionsApi = {
  createSession: (quizId: number) =>
    api.post('/sessions/', { quiz_id: quizId }),

  joinSession: (code: string, nickname: string) =>
    api.post('/sessions/join/', { code, nickname }),

  startSession: (sessionId: number) =>
    api.post(`/sessions/${sessionId}/start/`),

  endSession: (sessionId: number) =>
    api.post(`/sessions/${sessionId}/end/`),

  getSession: (sessionId: number) =>
    api.get(`/sessions/${sessionId}/`),

  getCurrentQuestion: (sessionId: number) =>
    api.get(`/sessions/${sessionId}/current-question/`),

  submitAnswer: (sessionId: number, questionId: number, answerId: number) =>
    api.post(`/sessions/${sessionId}/answer/`, {
      question_id: questionId,
      answer_id: answerId
    }),

  getMyResult: (sessionId: number) =>
    api.get(`/sessions/${sessionId}/my-result/`),

  getResults: (sessionId: number) =>
    api.get(`/sessions/${sessionId}/results/`),

  getQuestionsStats: (sessionId: number) =>
    api.get(`/sessions/${sessionId}/questions-stats/`)
}