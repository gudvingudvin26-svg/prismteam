import api from './api'

export const quizzesApi = {
  getMyQuizzes: () => api.get('/quizzes/'),

  getQuiz: (id: number) => api.get(`/quizzes/${id}/`),

  createQuiz: (data: { title: string; description: string; timer?: number }) =>
    api.post('/quizzes/', data),

  updateQuiz: (id: number, data: { title?: string; description?: string; timer?: number }) =>
    api.put(`/quizzes/${id}/`, data),

  deleteQuiz: (id: number) => api.delete(`/quizzes/${id}/`),

  getQuestions: (quizId: number) => api.get(`/quizzes/${quizId}/questions/`),

  createQuestion: (quizId: number, data: { text: string; order: number; timer?: number; answers: { text: string; is_correct: boolean }[] }) =>
    api.post(`/quizzes/${quizId}/questions/`, data),

  updateQuestion: (questionId: number, data: { text?: string; order?: number; timer?: number }) =>
    api.put(`/questions/${questionId}/`, data),

  deleteQuestion: (questionId: number) => api.delete(`/questions/${questionId}/`),

  createAnswer: (questionId: number, data: { text: string; is_correct: boolean }) =>
    api.post(`/questions/${questionId}/answers/`, data),

  deleteAnswer: (answerId: number) => api.delete(`/answers/${answerId}/`)
}