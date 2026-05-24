import React, { useState } from 'react';
import Button from '../ui/Button';

interface QuestionFormProps {
  question: {
    id: string;
    text: string;
    order: number;
    options: { text: string; is_correct: boolean }[];
  };
  index: number;
  onChange: (updated: any) => void;
  onDelete: () => void;
}

const QuestionForm: React.FC<QuestionFormProps> = ({ question, index, onChange, onDelete }) => {
  const [errors, setErrors] = useState<{ text?: string; options?: string }>({});

  const validate = () => {
    const newErrors: { text?: string; options?: string } = {};
    if (!question.text.trim()) newErrors.text = 'Текст вопроса обязателен';
    if (question.options.some(opt => !opt.text.trim())) newErrors.options = 'Все варианты должны быть заполнены';
    if (!question.options.some(opt => opt.is_correct)) newErrors.options = 'Выберите правильный ответ';
    return newErrors;
  };

  const handleBlur = () => {
    setErrors(validate());
  };

  const addOption = () => {
    onChange({
      ...question,
      options: [...question.options, { text: '', is_correct: false }]
    });
  };

  return (
    <div className="border p-4 mb-4 rounded">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-medium">Вопрос {index + 1}</h3>
        <Button variant="danger" size="sm" onClick={onDelete}>Удалить</Button>
      </div>

      <div className="mb-4">
        <label htmlFor={`question-text-${question.id}`} className="block mb-1 text-sm font-medium">
          Текст вопроса
        </label>
        <input
          id={`question-text-${question.id}`}
          value={question.text}
          onChange={(e) => onChange({ ...question, text: e.target.value })}
          onBlur={handleBlur}
          className="w-full px-3 py-2 border rounded"
        />
        {errors.text && <p className="text-red-500 text-sm">{errors.text}</p>}
      </div>

      <div className="mb-4">
        <label className="block mb-1 text-sm font-medium">Варианты ответов</label>
        {question.options.map((option, optIndex) => (
          <div key={optIndex} className="flex items-center mb-2">
            <input
              type="radio"
              name={`correct-${question.id}`}
              checked={option.is_correct}
              onChange={() => {
                const newOptions = [...question.options];
                newOptions.forEach((_, i) => newOptions[i].is_correct = false);
                newOptions[optIndex].is_correct = true;
                onChange({ ...question, options: newOptions });
              }}
              className="mr-2"
            />
            <input
              value={option.text}
              onChange={(e) => {
                const newOptions = [...question.options];
                newOptions[optIndex].text = e.target.value;
                onChange({ ...question, options: newOptions });
              }}
              onBlur={handleBlur}
              placeholder={`Вариант ${optIndex + 1}`}
              className="flex-1 px-3 py-2 border rounded"
            />
            <Button variant="danger" size="sm" onClick={() => {
              const newOptions = [...question.options];
              newOptions.splice(optIndex, 1);
              onChange({ ...question, options: newOptions });
            }}>×</Button>
          </div>
        ))}
        {errors.options && <p className="text-red-500 text-sm">{errors.options}</p>}

        <Button variant="outline" size="sm" onClick={addOption}>
          + Добавить вариант
        </Button>
      </div>
    </div>
  );
};

export default QuestionForm;