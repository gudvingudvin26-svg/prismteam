import api from './api'

export const quizzesApi = {
  getMyQuizzes: () => api.get('/api/organizer/quizzes/'),

  getQuiz: (id: number) => api.get(`/api/organizer/quizzes/${id}/`),

  createQuiz: (data: { title: string; description: string; timer?: number }) =>
    api.post('/api/organizer/quizzes/', data),

  updateQuiz: (id: number, data: { title?: string; description?: string; timer?: number }) =>
    api.put(`/api/organizer/quizzes/${id}/`, data),

  deleteQuiz: (id: number) => api.delete(`/api/organizer/quizzes/${id}/`),

  getQuestions: (quizId: number) => api.get(`/api/organizer/quizzes/${quizId}/questions/`),

  createQuestion: (quizId: number, data: { text: string; order: number; timer?: number; answer_options: { text: string; is_correct: boolean }[] }) =>
    api.post(`/api/organizer/questions/`, { ...data, quiz: quizId }),

  updateQuestion: (questionId: number, data: { text?: string; order?: number; timer?: number }) =>
    api.put(`/api/organizer/questions/${questionId}/`, data),

  deleteQuestion: (questionId: number) => api.delete(`/api/organizer/questions/${questionId}/`),

  createAnswer: (questionId: number, data: { text: string; is_correct: boolean }) =>
    api.post(`/api/organizer/questions/${questionId}/answers/`, data),

  deleteAnswer: (answerId: number) => api.delete(`/api/organizer/answers/${answerId}/`)
}