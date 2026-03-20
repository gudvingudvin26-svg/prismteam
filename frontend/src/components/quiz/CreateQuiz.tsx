import React, { useState } from 'react';
import QuestionForm from './QuestionForm';

interface Question {
  id: string;
  text: string;
  options: { text: string; isCorrect: boolean }[];
}

const CreateQuiz: React.FC = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [errors, setErrors] = useState<{ title?: string; questions?: string }>({});

  const validate = () => {
    const newErrors: { title?: string; questions?: string } = {};
    if (!title.trim()) newErrors.title = 'Название обязательно';
    if (questions.length === 0) newErrors.questions = 'Добавьте хотя бы один вопрос';
    return newErrors;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    console.log({ title, description, questions });
  };

  const addQuestion = () => {
    const newQuestion: Question = {
      id: Date.now().toString(),
      text: '',
      options: [
        { text: '', isCorrect: false },
        { text: '', isCorrect: false }
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
          >
            + Добавить вопрос
          </button>
        </div>

        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          Создать квиз
        </button>
      </form>
    </div>
  );
};

export default CreateQuiz;