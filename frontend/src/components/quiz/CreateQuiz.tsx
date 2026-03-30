import React, { useState } from 'react';
import QuestionForm from './QuestionForm';
import { quizzesApi } from '../../services/api/quizzes';

interface QuestionType {
  id: string;
  text: string;
  order: number;
  options: { text: string; is_correct: boolean }[];
}

const CreateQuiz: React.FC = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [questions, setQuestions] = useState<QuestionType[]>([]);
  const [errors, setErrors] = useState<{ title?: string; questions?: string }>({});
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const newErrors: { title?: string; questions?: string } = {};
    if (!title.trim()) newErrors.title = 'Название обязательно';
    if (questions.length === 0) newErrors.questions = 'Добавьте хотя бы один вопрос';
    for (const q of questions) {
      if (!q.text.trim()) {
        newErrors.questions = 'Все вопросы должны быть заполнены';
        break;
      }
      if (q.options.some(opt => !opt.text.trim())) {
        newErrors.questions = 'Все варианты ответов должны быть заполнены';
        break;
      }
      if (!q.options.some(opt => opt.is_correct)) {
        newErrors.questions = 'В каждом вопросе должен быть выбран правильный ответ';
        break;
      }
    }
    return newErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);
    try {
      const response = await quizzesApi.createQuiz({ title, description });
      const quizId = response.data.id;

      for (let i = 0; i < questions.length; i++) {
        const q = questions[i];
        await quizzesApi.createQuestion(quizId, {
          text: q.text,
          order: i + 1,
          answers: q.options
        });
      }

      window.location.href = '/quizzes';
    } catch (error) {
      console.error('Ошибка создания квиза:', error);
      alert('Ошибка при создании квиза');
    } finally {
      setLoading(false);
    }
  };

  const addQuestion = () => {
    const newQuestion: QuestionType = {
      id: Date.now().toString(),
      text: '',
      order: questions.length + 1,
      options: [
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ]
    };
    setQuestions([...questions, newQuestion]);
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Создание квиза</h1>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">Название квиза</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border rounded"
          />
          {errors.title && <p className="text-red-500 text-sm">{errors.title}</p>}
        </div>

        <div className="mb-4">
          <label className="block mb-1 text-sm font-medium">Описание</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 border rounded"
            rows={3}
          />
        </div>

        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-2">Вопросы</h2>
          {questions.map((question, index) => (
            <QuestionForm
              key={question.id}
              question={question}
              index={index}
              onChange={(updated) => {
                const newQuestions = [...questions];
                newQuestions[index] = updated;
                setQuestions(newQuestions);
              }}
              onDelete={() => {
                setQuestions(questions.filter((_, i) => i !== index));
              }}
            />
          ))}
          {errors.questions && <p className="text-red-500 text-sm">{errors.questions}</p>}

          <button
            type="button"
            onClick={addQuestion}
            className="px-4 py-2 bg-gray-500 text-white rounded"
            disabled={loading}
          >
            + Добавить вопрос
          </button>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          {loading ? 'Создание...' : 'Создать квиз'}
        </button>
      </form>
    </div>
  );
};

export default CreateQuiz;