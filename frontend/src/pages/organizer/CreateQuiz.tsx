import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Input, Card } from '../../components/ui';
import { quizzesApi } from '../../api';

interface AnswerForm {
  text: string;
  is_correct: boolean;
}

interface QuestionForm {
  text: string;
  timer?: number;
  answers: AnswerForm[];
}

const CreateQuiz: React.FC = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [globalTimer, setGlobalTimer] = useState<number | undefined>(undefined);
  const [questions, setQuestions] = useState<QuestionForm[]>([
    { text: '', answers: [{ text: '', is_correct: false }, { text: '', is_correct: false }] }
  ]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [createdQuizId, setCreatedQuizId] = useState<number | null>(null);

  const addQuestion = () => {
    setQuestions([...questions, { text: '', answers: [{ text: '', is_correct: false }, { text: '', is_correct: false }] }]);
  };

  const removeQuestion = (index: number) => {
    if (questions.length === 1) {
      setError('Должен быть хотя бы один вопрос');
      return;
    }
    const newQuestions = [...questions];
    newQuestions.splice(index, 1);
    setQuestions(newQuestions);
    setError('');
  };

  const updateQuestionText = (qIndex: number, text: string) => {
    const newQuestions = [...questions];
    newQuestions[qIndex].text = text;
    setQuestions(newQuestions);
  };

  const updateQuestionTimer = (qIndex: number, timer: number | undefined) => {
    const newQuestions = [...questions];
    newQuestions[qIndex].timer = timer;
    setQuestions(newQuestions);
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
    newQuestions[qIndex].answers.forEach((ans, idx) => {
      ans.is_correct = idx === aIndex;
    });
    setQuestions(newQuestions);
  };

  const validate = (): boolean => {
    if (!title.trim()) {
      setError('Введите название квиза');
      return false;
    }
    if (questions.length >= 0) {
      setError('Добавьте хотя бы два вопроса');
      return false;
    }
    for (let i = 0; i < questions.length; i++) {
      const q = questions[i];
      if (!q.text.trim()) {
        setError(`Вопрос ${i + 1}: введите текст вопроса`);
        return false;
      }
      if (q.answers.length < 2) {
        setError(`Вопрос ${i + 1}: должно быть минимум 2 варианта ответа`);
        return false;
      }
      let hasCorrect = false;
      for (let j = 0; j < q.answers.length; j++) {
        if (!q.answers[j].text.trim()) {
          setError(`Вопрос ${i + 1}: вариант ${j + 1} не может быть пустым`);
          return false;
        }
        if (q.answers[j].is_correct) hasCorrect = true;
      }
      if (!hasCorrect) {
        setError(`Вопрос ${i + 1}: выберите правильный вариант`);
        return false;
      }
    }
    setError('');
    return true;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    setLoading(true);
    setCreatedQuizId(null);

    try {
      const quizRes = await quizzesApi.createQuiz({
        title,
        description,
        timer: globalTimer,
      });
      const newQuizId = quizRes.data.id;
      setCreatedQuizId(newQuizId);

      for (let i = 0; i < questions.length; i++) {
        const q = questions[i];
        if (newQuizId) {
          await quizzesApi.createQuestion(newQuizId, {
            text: q.text,
            order: i + 1,
            timer: q.timer,
            answer_options: q.answers.map(a => ({ text: a.text, is_correct: a.is_correct })),
          });
        }
      }
      navigate('/quizzes');
    } catch (err: any) {
      console.error('Full error:', err);
      if (createdQuizId) {
        try {
          await quizzesApi.deleteQuiz(createdQuizId);
        } catch (deleteErr) {
          console.error('Failed to delete quiz:', deleteErr);
        }
      }
      if (err.response) {
        console.error('Error response data:', err.response.data);
        setError(`Ошибка: ${JSON.stringify(err.response.data)}`);
      } else {
        setError('Ошибка при создании квиза. Попробуйте позже.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-xl p-6">
          <h1 className="text-2xl font-bold mb-6 text-gray-900">Создание нового квиза</h1>

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
              onChange={(e) => setGlobalTimer(e.target.value ? Number(e.target.value) : undefined)}
            />
          </Card>

          {questions.map((q, qIdx) => (
            <Card key={qIdx} className="p-6 mb-6 bg-white shadow-md">
              <div className="flex justify-between items-start">
                <h3 className="text-lg font-semibold mb-4 text-gray-900">Вопрос {qIdx + 1}</h3>
                <Button variant="danger" size="sm" onClick={() => removeQuestion(qIdx)}>Удалить вопрос</Button>
              </div>
              <Input
                label="Текст вопроса"
                value={q.text}
                onChange={(e) => updateQuestionText(qIdx, e.target.value)}
                required
              />
              <Input
                label="Таймер на вопрос (секунды, опционально)"
                type="number"
                value={q.timer || ''}
                onChange={(e) => updateQuestionTimer(qIdx, e.target.value ? Number(e.target.value) : undefined)}
              />

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Варианты ответов</label>
                {q.answers.map((ans, aIdx) => (
                  <div key={aIdx} className="flex items-center gap-2 mb-2">
                    <input
                      type="radio"
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
            <Button variant="primary" onClick={handleSubmit} isLoading={loading}>Сохранить квиз</Button>
          </div>

          {error && <div className="mt-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>}
        </div>
      </div>
    </div>
  );
};

export default CreateQuiz;