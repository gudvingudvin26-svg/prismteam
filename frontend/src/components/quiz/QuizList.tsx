import React, { useState } from 'react';

interface Quiz {
  id: string;
  title: string;
  description: string;
  questionsCount: number;
  createdAt: string;
}

const QuizList: React.FC = () => {
  const [quizzes, setQuizzes] = useState<Quiz[]>([
    { id: '1', title: 'Викторина по истории', description: 'Проверьте свои знания истории России', questionsCount: 10, createdAt: '2024-03-15' },
    { id: '2', title: 'География мира', description: 'Столицы и страны мира', questionsCount: 15, createdAt: '2024-03-18' },
    { id: '3', title: 'Наука и технологии', description: 'Интересные факты о науке', questionsCount: 8, createdAt: '2024-03-20' },
    { id: '4', title: 'Кино и сериалы', description: 'Угадайте фильм по описанию', questionsCount: 12, createdAt: '2024-03-22' }
  ]);

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedQuiz, setSelectedQuiz] = useState<Quiz | null>(null);

  const handleDelete = (quiz: Quiz) => {
    setSelectedQuiz(quiz);
    setDeleteModalOpen(true);
  };

  const confirmDelete = () => {
    if (selectedQuiz) {
      setQuizzes(quizzes.filter(q => q.id !== selectedQuiz.id));
      setDeleteModalOpen(false);
      setSelectedQuiz(null);
    }
  };

  const handleEdit = (quiz: Quiz) => {
    console.log('Редактировать квиз:', quiz);
  };

  const handleCreate = () => {
    console.log('Создать новый квиз');
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Мои квизы</h1>
        <button
          onClick={handleCreate}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          + Создать квиз
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border rounded-lg">
          <thead>
            <tr className="bg-gray-100 border-b">
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">Название</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">Описание</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">Вопросов</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">Дата создания</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">Действия</th>
            </tr>
          </thead>
          <tbody>
            {quizzes.map((quiz) => (
              <tr key={quiz.id} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4 font-medium">{quiz.title}</td>
                <td className="px-6 py-4 text-gray-600">{quiz.description}</td>
                <td className="px-6 py-4 text-center">{quiz.questionsCount}</td>
                <td className="px-6 py-4 text-gray-500">{quiz.createdAt}</td>
                <td className="px-6 py-4">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(quiz)}
                      className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600 text-sm"
                    >
                      Редактировать
                    </button>
                    <button
                      onClick={() => handleDelete(quiz)}
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

      {deleteModalOpen && selectedQuiz && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
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