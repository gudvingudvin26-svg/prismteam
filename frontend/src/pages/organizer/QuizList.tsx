import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Card, Modal } from '../../components/ui';
import { quizzesApi, sessionsApi, authApi } from '../../api';
import { Quiz } from '../../types';
import { useAppStore } from '../../store/appStore';

const QuizList: React.FC = () => {
  const navigate = useNavigate();
  const user = useAppStore((state) => state.user);
  const setUser = useAppStore((state) => state.setUser);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [sessionCode, setSessionCode] = useState('');
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);

  useEffect(() => {
    loadQuizzes();
  }, []);

  const loadQuizzes = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await quizzesApi.getMyQuizzes();
      setQuizzes(res.data);
    } catch (err: any) {
      const status = err.response?.status;
      if (status === 401) {
        navigate('/login');
      } else if (status === 403) {
        setError('У вас нет доступа к этому списку');
      } else {
        setError('Ошибка загрузки квизов');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm('Удалить квиз? Все связанные сессии и ответы будут удалены.')) {
      try {
        await quizzesApi.deleteQuiz(id);
        await loadQuizzes();
      } catch (err: any) {
        const status = err.response?.status;
        if (status === 403) {
          setError('У вас нет прав на удаление этого квиза');
        } else if (status === 404) {
          setError('Квиз не найден');
        } else {
          setError('Ошибка при удалении');
        }
      }
    }
  };

  const handleEdit = (id: number) => {
    navigate(`/quizzes/${id}/edit`);
  };

  const handleRun = async (quizId: number) => {
    const participantName = user?.first_name || user?.username || 'Участник';

    try {
      const res = await sessionsApi.createSession(quizId);
      setSessionCode(res.data.code);
      setSelectedSessionId(res.data.id);

      await sessionsApi.joinSession(res.data.code, participantName);

      setModalOpen(true);
    } catch (err: any) {
      const status = err.response?.status;
      if (status === 401) {
        navigate('/login');
      } else if (status === 403) {
        setError('У вас нет прав на создание сессии для этого квиза');
      } else if (status === 404) {
        setError('Квиз не найден');
      } else {
        setError('Не удалось создать сессию');
      }
      console.error(err);
    }
  };

  const handleLogout = () => {
    authApi.logout();
    setUser(null);
    navigate('/login');
  };

  const closeModal = () => {
    setModalOpen(false);
    setSessionCode('');
    setSelectedSessionId(null);
  };

  if (loading) return <div className="flex justify-center items-center h-screen text-white">Загрузка...</div>;

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
        <Card className="p-8 text-center max-w-md bg-white/90 backdrop-blur-sm">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Ошибка</h2>
          <p className="text-gray-700 mb-6">{error}</p>
          <Button onClick={() => loadQuizzes()}>Повторить</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-white">Мои квизы</h1>
          <div className="flex gap-4">
            <Link to="/dashboard">
              <Button variant="outline" className="!text-black bg-white hover:bg-gray-100">
                Панель управления
              </Button>
            </Link>
            <Link to="/quizzes/create">
              <Button variant="primary" className="!text-black bg-white hover:bg-gray-100">Создать новый квиз</Button>
            </Link>
            <Button variant="danger" onClick={handleLogout} className="!text-black bg-white hover:bg-gray-100">
              Выйти
            </Button>
          </div>
        </div>

        {quizzes.length === 0 ? (
          <Card className="p-8 text-center text-gray-500 bg-white/90 backdrop-blur-sm">
            У вас пока нет квизов. Нажмите «Создать новый квиз».
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 gap-6">
            {quizzes.map((quiz) => (
              <Card key={quiz.id} className="p-5 bg-white/90 backdrop-blur-sm">
                <h3 className="text-xl font-semibold mb-2 text-gray-900">{quiz.title}</h3>
                <p className="text-gray-600 mb-4">{quiz.description || 'Без описания'}</p>
                <div className="text-sm text-gray-500 mb-4">
                  Создан: {new Date(quiz.created_at || Date.now()).toLocaleDateString()}
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button size="sm" variant="primary" onClick={() => quiz.id && handleRun(quiz.id)}>Запустить</Button>
                  <Button size="sm" variant="outline" onClick={() => quiz.id && handleEdit(quiz.id)}>Редактировать</Button>
                  <Button size="sm" variant="danger" onClick={() => quiz.id && handleDelete(quiz.id)}>Удалить</Button>
                  <Button size="sm" variant="outline" onClick={() => navigate('/stats')}>Статистика</Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        <Modal isOpen={modalOpen} onClose={closeModal} title="Сессия создана">
          <p className="mb-4">Код для участников:</p>
          <p className="text-3xl font-bold text-center text-blue-600 mb-6">{sessionCode}</p>
          <p className="text-sm text-gray-500">Сообщите код участникам, чтобы они могли присоединиться.</p>
          <div className="mt-6 flex justify-end gap-2">
            <Button variant="outline" onClick={closeModal}>Закрыть</Button>
            <Button variant="primary" onClick={() => selectedSessionId && navigate(`/play/${selectedSessionId}`)}>Начать игру</Button>
          </div>
        </Modal>
      </div>
    </div>
  );
};

export default QuizList;