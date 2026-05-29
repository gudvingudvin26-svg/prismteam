import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button, Input, Card } from '../components/ui';
import { quizzesApi } from '../api';

interface AnswerForm {
  id?: number;
  text: string;
  is_correct: boolean;
}

interface QuestionForm {
  id?: number;
  text: string;
  timer?: number;
  points?: number;
  order: number;
  question_type: string;
  answers: AnswerForm[];
}

const EditQuiz: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [globalTimer, setGlobalTimer] = useState<number | undefined>(undefined);
  const [globalPoints, setGlobalPoints] = useState<number>(100);
  const [questions, setQuestions] = useState<QuestionForm[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchQuiz = async () => {
      if (!id) return;
      try {
        const response = await quizzesApi.getQuiz(parseInt(id));
        const quizData = response.data;
        setTitle(quizData.title || '');
        setDescription(quizData.description || '');
        setGlobalTimer(quizData.timer);
        setGlobalPoints(quizData.points_per_question || 100);

        if (quizData.questions && Array.isArray(quizData.questions)) {
          const sortedQuestions = [...quizData.questions].sort((a, b) => a.order - b.order);
          const formattedQuestions = sortedQuestions.map((q: any) => ({
            id: q.id,
            text: q.text || '',
            timer: q.timer,
            points: q.points,
            order: q.order,
            question_type: q.question_type || 'single',
            answers: (q.answer_options || []).map((a: any) => ({
              id: a.id,
              text: a.text || '',
              is_correct: a.is_correct || false,
            })),
          }));
          setQuestions(formattedQuestions);
        }
      } catch (err) {
        console.error(err);
        setError('Ошибка загрузки квиза');
      } finally {
        setLoading(false);
      }
    };
    fetchQuiz();
  }, [id]);

  const validate = (): string => {
    if (questions.length < 2) return 'Добавьте хотя бы два вопроса';
    if (!title.trim()) return 'Введите название квиза';

    if (globalTimer && globalTimer > 0) {
      for (let i = 0; i < questions.length; i++) {
        const q = questions[i];
        if (q.timer && q.timer > globalTimer) {
          return `Вопрос ${i + 1}: таймер вопроса (${q.timer} сек) не может превышать таймер всего квиза (${globalTimer} сек)`;
        }
      }
    }

    for (let i = 0; i < questions.length; i++) {
      const q = questions[i];
      if (!q.text.trim()) return `Вопрос ${i + 1}: введите текст вопроса`;
      if (q.answers.length < 2) return `Вопрос ${i + 1}: должно быть минимум 2 варианта ответа`;

      let hasCorrect = false;
      const answerTexts = new Set();
      for (let j = 0; j < q.answers.length; j++) {
        if (!q.answers[j].text.trim()) return `Вопрос ${i + 1}: вариант ${j + 1} не может быть пустым`;
        const normalizedText = q.answers[j].text.trim().toLowerCase();
        if (answerTexts.has(normalizedText)) return `Вопрос ${i + 1}: вариант "${q.answers[j].text}" повторяется`;
        answerTexts.add(normalizedText);
        if (q.answers[j].is_correct) hasCorrect = true;
      }
      if (!hasCorrect) return `Вопрос ${i + 1}: выберите правильный вариант`;

      if (q.question_type === 'multiple') {
        const correctCount = q.answers.filter(a => a.is_correct).length;
        if (correctCount === q.answers.length) return `Вопрос ${i + 1}: нельзя отмечать ВСЕ варианты как правильные`;
      }
    }
    return '';
  };

  const updateQuestion = (index: number, field: string, value: any) => {
    const newQuestions = [...questions];
    newQuestions[index] = { ...newQuestions[index], [field]: value };
    setQuestions(newQuestions);
  };

  const addQuestion = () => {
    setQuestions([...questions, {
      text: '',
      points: globalPoints,
      order: questions.length + 1,
      question_type: 'single',
      answers: [{ text: '', is_correct: false }, { text: '', is_correct: false }]
    }]);
  };

  const removeQuestion = (index: number) => {
    if (questions.length <= 2) {
      setError('Должно быть минимум 2 вопроса');
      return;
    }
    const newQuestions = [...questions];
    newQuestions.splice(index, 1);
    setQuestions(newQuestions.map((q, idx) => ({ ...q, order: idx + 1 })));
    setError('');
  };

  const moveQuestionUp = (index: number) => {
    if (index > 0) {
      const newQuestions = [...questions];
      [newQuestions[index - 1], newQuestions[index]] = [newQuestions[index], newQuestions[index - 1]];
      setQuestions(newQuestions.map((q, idx) => ({ ...q, order: idx + 1 })));
    }
  };

  const moveQuestionDown = (index: number) => {
    if (index < questions.length - 1) {
      const newQuestions = [...questions];
      [newQuestions[index], newQuestions[index + 1]] = [newQuestions[index + 1], newQuestions[index]];
      setQuestions(newQuestions.map((q, idx) => ({ ...q, order: idx + 1 })));
    }
  };

  const addAnswer = (qIndex: number) => {
    const newQuestions = [...questions];
    newQuestions[qIndex].answers.push({ text: '', is_correct: false });
    setQuestions(newQuestions);
  };

  const removeAnswer = (qIndex: number, aIndex: number) => {
    const newQuestions = [...questions];
    if (newQuestions[qIndex].answers.length <= 2) {
      setError('У вопроса должно быть минимум 2 варианта');
      return;
    }
    newQuestions[qIndex].answers.splice(aIndex, 1);
    if (newQuestions[qIndex].question_type === 'single') {
      const hasCorrect = newQuestions[qIndex].answers.some(a => a.is_correct);
      if (!hasCorrect && newQuestions[qIndex].answers.length > 0) {
        newQuestions[qIndex].answers[0].is_correct = true;
      }
    }
    setQuestions(newQuestions);
    setError('');
  };

  const updateAnswerText = (qIndex: number, aIndex: number, text: string) => {
    const newQuestions = [...questions];
    newQuestions[qIndex].answers[aIndex].text = text;
    setQuestions(newQuestions);
  };

  const setCorrectAnswer = (qIndex: number, aIndex: number) => {
    const newQuestions = [...questions];
    const questionType = newQuestions[qIndex].question_type;

    if (questionType === 'single') {
      newQuestions[qIndex].answers.forEach((ans, idx) => {
        ans.is_correct = idx === aIndex;
      });
    } else {
      newQuestions[qIndex].answers[aIndex].is_correct = !newQuestions[qIndex].answers[aIndex].is_correct;
    }
    setQuestions(newQuestions);
  };

  const handleSubmit = async () => {
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    if (!id) return;

    setSaving(true);
    setError('');

    try {
      await quizzesApi.updateQuiz(parseInt(id), {
        title,
        description,
        timer: globalTimer,
        points_per_question: globalPoints,
      });

      for (let i = 0; i < questions.length; i++) {
        const q = questions[i];
        const questionData = {
          text: q.text,
          order: i + 1,
          timer: q.timer,
          points: q.points || globalPoints,
          question_type: q.question_type,
          answer_options: q.answers.map(a => ({ text: a.text, is_correct: a.is_correct })),
        };

        if (q.id) {
          await quizzesApi.updateQuestion(q.id, questionData);
        } else {
          await quizzesApi.createQuestion(parseInt(id), questionData);
        }
      }

      navigate('/quizzes');
    } catch (err: any) {
      console.error('Save error:', err);
      if (err.response?.data) {
        const errorData = err.response.data;
        if (typeof errorData === 'object') {
          const firstError = Object.values(errorData)[0];
          setError(Array.isArray(firstError) ? firstError[0] : String(firstError));
        } else {
          setError(String(errorData));
        }
      } else {
        setError('Ошибка при сохранении квиза');
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-white">Загрузка...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Редактирование квиза</h1>
            <div className="flex gap-3">
              <Button variant="outline" onClick={() => navigate('/quizzes')}>← Назад к квизам</Button>
              <Button variant="primary" onClick={handleSubmit} isLoading={saving}>Сохранить изменения</Button>
            </div>
          </div>

          <Card className="p-6 mb-6 bg-white shadow-md">
            <Input
              label="Название квиза"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <Input
              label="Описание"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              multiline
              rows={3}
            />
            <Input
              label="Таймер на весь квиз (секунды, опционально)"
              type="number"
              value={globalTimer || ''}
              onChange={(e) => {
                const value = e.target.value ? Number(e.target.value) : undefined;
                setGlobalTimer((value !== undefined && value <= 0) ? undefined : value);
              }}
              min="1"
              step="1"
            />
            <Input
              label="Баллов за правильный ответ (по умолчанию)"
              type="number"
              value={globalPoints}
              onChange={(e) => setGlobalPoints(Number(e.target.value))}
              min="1"
            />
          </Card>

          {questions.map((q, qIdx) => (
            <Card key={q.id || qIdx} className="p-6 mb-6 bg-white shadow-md">
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-semibold mb-4 text-gray-900">Вопрос {qIdx + 1}</h3>
                  <div className="flex gap-1 mb-4">
                    <button
                      type="button"
                      onClick={() => moveQuestionUp(qIdx)}
                      className="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
                      disabled={qIdx === 0}
                    >
                      ↑
                    </button>
                    <button
                      type="button"
                      onClick={() => moveQuestionDown(qIdx)}
                      className="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
                      disabled={qIdx === questions.length - 1}
                    >
                      ↓
                    </button>
                  </div>
                </div>
                <Button variant="danger" size="sm" onClick={() => removeQuestion(qIdx)}>Удалить вопрос</Button>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Тип вопроса</label>
                <select
                  value={q.question_type}
                  onChange={(e) => updateQuestion(qIdx, 'question_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"
                >
                  <option value="single">Одиночный выбор</option>
                  <option value="multiple">Множественный выбор</option>
                </select>
              </div>

              <Input
                label="Текст вопроса"
                value={q.text}
                onChange={(e) => updateQuestion(qIdx, 'text', e.target.value)}
                required
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Таймер на вопрос (секунды, опционально)"
                  type="number"
                  value={q.timer || ''}
                  onChange={(e) => {
                    const value = e.target.value ? Number(e.target.value) : undefined;
                    if (globalTimer && value && value > globalTimer) {
                      setError(`Таймер вопроса не может превышать таймер всего квиза (${globalTimer} сек)`);
                    } else {
                      setError('');
                      updateQuestion(qIdx, 'timer', (value !== undefined && value <= 0) ? undefined : value);
                    }
                  }}
                  min="1"
                  step="1"
                />
                <Input
                  label="Баллов за вопрос"
                  type="number"
                  value={q.points || globalPoints}
                  onChange={(e) => updateQuestion(qIdx, 'points', Number(e.target.value))}
                  min="1"
                />
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Варианты ответов {q.question_type === 'multiple' && '(можно выбрать несколько)'}
                </label>
                {q.answers.map((ans, aIdx) => (
                  <div key={ans.id || aIdx} className="flex items-center gap-2 mb-2">
                    <input
                      type={q.question_type === 'multiple' ? 'checkbox' : 'radio'}
                      name={`correct-${qIdx}`}
                      checked={ans.is_correct}
                      onChange={() => setCorrectAnswer(qIdx, aIdx)}
                      className="h-4 w-4 text-blue-600"
                    />
                    <Input
                      placeholder={`Вариант ${aIdx + 1}`}
                      value={ans.text}
                      onChange={(e) => updateAnswerText(qIdx, aIdx, e.target.value)}
                      className="flex-1"
                    />
                    <Button variant="danger" size="sm" onClick={() => removeAnswer(qIdx, aIdx)}>×</Button>
                  </div>
                ))}
                <Button variant="outline" size="sm" onClick={() => addAnswer(qIdx)}>+ Добавить вариант</Button>
              </div>
            </Card>
          ))}

          <div className="flex gap-4 mt-4">
            <Button variant="outline" onClick={addQuestion}>+ Добавить вопрос</Button>
            <Button variant="primary" onClick={handleSubmit} isLoading={saving}>Сохранить изменения</Button>
          </div>

          {error && <div className="mt-4 p-3 bg-red-100 text-red-700 rounded whitespace-pre-wrap">{error}</div>}
        </div>
      </div>
    </div>
  );
};

export default EditQuiz;