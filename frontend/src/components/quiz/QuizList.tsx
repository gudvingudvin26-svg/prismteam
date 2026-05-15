import React, { useState, useEffect } from 'react';
import { quizzesApi } from '../../services/api/quizzes';

interface Quiz {
  id: number;
  title: string;
  description: string;
  questions?: any[];
  created_at?: string;
}

const QuizList: React.FC = () => {
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedQuiz, setSelectedQuiz] = useState<Quiz | null>(null);

  useEffect(() => {
    loadQuizzes();
  }, []);

  const loadQuizzes = async () => {
    try {
      const response = await quizzesApi.getMyQuizzes();
      setQuizzes(response.data);
    } catch (error) {
      console.error('Ошибка загрузки квизов:', error);
    } finally {
      setLoading(false);
    }
  };

  const confirmDelete = async () => {
    if (selectedQuiz) {
      try {
        await quizzesApi.deleteQuiz(selectedQuiz.id);
        await loadQuizzes();
        setDeleteModalOpen(false);
        setSelectedQuiz(null);
      } catch (error) {
        console.error('Ошибка удаления:', error);
        alert('Ошибка при удалении квиза');
      }
    }
  };

  if (loading) {
    return <div className="p-6 text-center">Загрузка...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Мои квизы</h1>
        <button
          onClick={() => window.location.href = '/quizzes/create'}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          + Создать квиз
        </button>
      </div>

      {quizzes.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">У вас пока нет квизов</p>
          <button
            onClick={() => window.location.href = '/quizzes/create'}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
          >
            Создать первый квиз
          </button>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border rounded-lg">
            <thead>
              <tr className="bg-gray-100 border-b">
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">Название</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">Описание</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">Вопросов</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">Действия</th>
               </tr>
            </thead>
            <tbody>
              {quizzes.map((quiz) => (
                <tr key={quiz.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium">{quiz.title}</td>
                  <td className="px-6 py-4 text-gray-600">{quiz.description || '-'}</td>
                  <td className="px-6 py-4 text-center">{quiz.questions?.length || 0}</td>
                  <td className="px-6 py-4">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => window.location.href = `/quizzes/${quiz.id}/edit`}
                        className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600 text-sm"
                      >
                        Редактировать
                      </button>
                      <button
                        onClick={() => {
                          setSelectedQuiz(quiz);
                          setDeleteModalOpen(true);
                        }}
                        className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                      >
                        Удалить
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {deleteModalOpen && selectedQuiz && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Подтверждение удаления</h2>
            <p className="mb-6">
              Вы уверены, что хотите удалить квиз "{selectedQuiz.title}"?
              Это действие нельзя отменить.
            </p>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setDeleteModalOpen(false)}
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Отмена
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuizList;