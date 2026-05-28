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
  points?: number;
  question_type: 'single' | 'multiple';
  answers: AnswerForm[];
}

const MIN_QUESTION_LENGTH = 5;
const MIN_ANSWER_LENGTH = 1;

const MIN_ANSWERS_SINGLE = 2;
const MIN_ANSWERS_MULTIPLE = 3;

const MAX_REPEATED_CHAR_RATIO = 0.7;

const LETTER_REGEX = /[A-Za-zА-Яа-яЁё]/;

const CreateQuiz: React.FC = () => {
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const [globalTimer, setGlobalTimer] = useState<number | undefined>(undefined);
  const [globalPoints, setGlobalPoints] = useState<number>(100);

  const [questions, setQuestions] = useState<QuestionForm[]>([
    {
      text: '',
      points: 100,
      question_type: 'single',
      answers: [
        { text: '', is_correct: false },
        { text: '', is_correct: false },
      ],
    },
  ]);

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [createdQuizId, setCreatedQuizId] = useState<number | null>(null);

  // =========================================================
  // Helpers
  // =========================================================

  const isMeaningfulText = (text: string): boolean => {
    if (typeof text !== 'string') {
      return false;
    }

    const normalized = text.trim();

    if (!normalized) {
      return false;
    }

    // Должна быть хотя бы одна буква
    if (!LETTER_REGEX.test(normalized)) {
      return false;
    }

    // Удаляем пробелы
    const compact = normalized.replace(/\s+/g, '');

    if (!compact.length) {
      return false;
    }

    // Проверка на спам одного символа
    const charMap: Record<string, number> = {};

    for (const char of compact) {
      charMap[char] = (charMap[char] || 0) + 1;
    }

    const maxCount = Math.max(...Object.values(charMap));
    const ratio = maxCount / compact.length;

    return ratio <= MAX_REPEATED_CHAR_RATIO;
  };

  const getMinAnswersCount = (
    questionType: 'single' | 'multiple'
  ): number => {
    return questionType === 'multiple'
      ? MIN_ANSWERS_MULTIPLE
      : MIN_ANSWERS_SINGLE;
  };

  // =========================================================
  // Questions
  // =========================================================

  const addQuestion = () => {
    setQuestions([
      ...questions,
      {
        text: '',
        points: globalPoints,
        question_type: 'single',
        answers: [
          { text: '', is_correct: false },
          { text: '', is_correct: false },
        ],
      },
    ]);
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

  const moveQuestionUp = (index: number) => {
    if (index <= 0) return;

    const newQuestions = [...questions];

    [newQuestions[index - 1], newQuestions[index]] = [
      newQuestions[index],
      newQuestions[index - 1],
    ];

    setQuestions(newQuestions);
  };

  const moveQuestionDown = (index: number) => {
    if (index >= questions.length - 1) return;

    const newQuestions = [...questions];

    [newQuestions[index], newQuestions[index + 1]] = [
      newQuestions[index + 1],
      newQuestions[index],
    ];

    setQuestions(newQuestions);
  };

  const updateQuestionText = (qIndex: number, text: string) => {
    const newQuestions = [...questions];
    newQuestions[qIndex].text = text;

    setQuestions(newQuestions);
  };

  const updateQuestionTimer = (
    qIndex: number,
    timer: number | undefined
  ) => {
    const newQuestions = [...questions];
    newQuestions[qIndex].timer = timer;

    setQuestions(newQuestions);
  };

  const updateQuestionPoints = (qIndex: number, points: number) => {
    const newQuestions = [...questions];
    newQuestions[qIndex].points = points;

    setQuestions(newQuestions);
  };

  const updateQuestionType = (
    qIndex: number,
    question_type: 'single' | 'multiple'
  ) => {
    const newQuestions = [...questions];
    const currentQuestion = newQuestions[qIndex];

    currentQuestion.question_type = question_type;

    // Для multiple должно быть минимум 3 ответа
    if (
      question_type === 'multiple' &&
      currentQuestion.answers.length < MIN_ANSWERS_MULTIPLE
    ) {
      currentQuestion.answers.push({
        text: '',
        is_correct: false,
      });
    }

    // Если был multiple → single
    // оставляем только первый правильный ответ
    if (question_type === 'single') {
      let foundCorrect = false;

      currentQuestion.answers.forEach((answer) => {
        if (answer.is_correct && !foundCorrect) {
          foundCorrect = true;
        } else {
          answer.is_correct = false;
        }
      });
    }

    setQuestions(newQuestions);
  };

  // =========================================================
  // Answers
  // =========================================================

  const addAnswer = (qIndex: number) => {
    const newQuestions = [...questions];

    newQuestions[qIndex].answers.push({
      text: '',
      is_correct: false,
    });

    setQuestions(newQuestions);
  };

  const removeAnswer = (qIndex: number, aIndex: number) => {
    const newQuestions = [...questions];

    const question = newQuestions[qIndex];

    const minAnswers = getMinAnswersCount(question.question_type);

    if (question.answers.length <= minAnswers) {
      setError(
        question.question_type === 'multiple'
          ? `У вопроса с множественным выбором должно быть минимум ${MIN_ANSWERS_MULTIPLE} варианта`
          : `У вопроса должно быть минимум ${MIN_ANSWERS_SINGLE} варианта`
      );

      return;
    }

    question.answers.splice(aIndex, 1);

    setQuestions(newQuestions);
    setError('');
  };

  const updateAnswerText = (
    qIndex: number,
    aIndex: number,
    text: string
  ) => {
    const newQuestions = [...questions];

    newQuestions[qIndex].answers[aIndex].text = text;

    setQuestions(newQuestions);
  };

  const setCorrectAnswer = (qIndex: number, aIndex: number) => {
    const newQuestions = [...questions];

    const question = newQuestions[qIndex];

    if (question.question_type === 'single') {
      question.answers.forEach((answer, idx) => {
        answer.is_correct = idx === aIndex;
      });
    } else {
      question.answers[aIndex].is_correct =
        !question.answers[aIndex].is_correct;
    }

    setQuestions(newQuestions);
  };

  // =========================================================
  // Validation
  // =========================================================

  const validate = (): boolean => {
    // =========================
    // Quiz title
    // =========================

    if (!title.trim()) {
      setError('Введите название квиза');
      return false;
    }

    if (!isMeaningfulText(title)) {
      setError('Название квиза содержит бессмысленный текст');
      return false;
    }

    // =========================
    // Global timer
    // =========================

    if (
      globalTimer !== undefined &&
      (Number.isNaN(globalTimer) || globalTimer <= 0)
    ) {
      setError('Таймер квиза должен быть больше 0');
      return false;
    }

    // =========================
    // Points
    // =========================

    if (globalPoints <= 0) {
      setError('Количество баллов должно быть больше 0');
      return false;
    }

    // =========================
    // Questions
    // =========================

    if (questions.length < 2) {
      setError('Квиз должен содержать минимум 2 вопроса');
      return false;
    }

    for (let i = 0; i < questions.length; i++) {
      const question = questions[i];

      const questionText = question.text.trim();

      // -------------------------
      // Question text
      // -------------------------

      if (!questionText) {
        setError(`Вопрос ${i + 1}: введите текст вопроса`);
        return false;
      }

      if (questionText.length < MIN_QUESTION_LENGTH) {
        setError(
          `Вопрос ${i + 1}: текст должен содержать минимум ${MIN_QUESTION_LENGTH} символов`
        );
        return false;
      }

      if (!isMeaningfulText(questionText)) {
        setError(
          `Вопрос ${i + 1}: текст содержит бессмысленные символы`
        );
        return false;
      }

      // -------------------------
      // Question timer
      // -------------------------

      if (
        question.timer !== undefined &&
        (Number.isNaN(question.timer) || question.timer <= 0)
      ) {
        setError(
          `Вопрос ${i + 1}: таймер должен быть больше 0`
        );
        return false;
      }

      // -------------------------
      // Points
      // -------------------------

      if (
        question.points !== undefined &&
        question.points <= 0
      ) {
        setError(
          `Вопрос ${i + 1}: количество баллов должно быть больше 0`
        );
        return false;
      }

      // -------------------------
      // Answers count
      // -------------------------

      const minAnswers = getMinAnswersCount(
        question.question_type
      );

      if (question.answers.length < minAnswers) {
        setError(
          question.question_type === 'multiple'
            ? `Вопрос ${i + 1}: для множественного выбора нужно минимум ${MIN_ANSWERS_MULTIPLE} варианта ответа`
            : `Вопрос ${i + 1}: должно быть минимум ${MIN_ANSWERS_SINGLE} варианта ответа`
        );

        return false;
      }

      // -------------------------
      // Answers validation
      // -------------------------

      let correctAnswersCount = 0;

      for (let j = 0; j < question.answers.length; j++) {
        const answer = question.answers[j];

        const answerText = answer.text.trim();

        if (!answerText) {
          setError(
            `Вопрос ${i + 1}: вариант ${j + 1} не может быть пустым`
          );

          return false;
        }

        if (answerText.length < MIN_ANSWER_LENGTH) {
          setError(
            `Вопрос ${i + 1}: вариант ${j + 1} слишком короткий`
          );

          return false;
        }

        if (!isMeaningfulText(answerText)) {
          setError(
            `Вопрос ${i + 1}: вариант ${j + 1} содержит бессмысленный текст`
          );

          return false;
        }

        if (answer.is_correct) {
          correctAnswersCount++;
        }
      }

      // -------------------------
      // Correct answers logic
      // -------------------------

      if (
        question.question_type === 'single' &&
        correctAnswersCount !== 1
      ) {
        setError(
          `Вопрос ${i + 1}: для одиночного выбора должен быть ровно один правильный ответ`
        );

        return false;
      }

      if (
        question.question_type === 'multiple' &&
        correctAnswersCount < 2
      ) {
        setError(
          `Вопрос ${i + 1}: для множественного выбора нужен хотя бы один правильный ответ`
        );

        return false;
      }
    }

    setError('');
    return true;
  };

  // =========================================================
  // Submit
  // =========================================================

  const handleSubmit = async () => {
    if (!validate()) {
      return;
    }

    setLoading(true);
    setCreatedQuizId(null);
    setError('');

    try {
      const quizRes = await quizzesApi.createQuiz({
        title: title.trim(),
        description: description.trim(),
        timer: globalTimer,
        points_per_question: globalPoints,
      });

      const newQuizId = quizRes.data.id;

      setCreatedQuizId(newQuizId);

      for (let i = 0; i < questions.length; i++) {
        const question = questions[i];

        await quizzesApi.createQuestion(newQuizId, {
          text: question.text.trim(),
          order: i + 1,
          timer: question.timer,
          points: question.points || globalPoints,
          question_type: question.question_type,
          answer_options: question.answers.map((answer) => ({
            text: answer.text.trim(),
            is_correct: answer.is_correct,
          })),
        });
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

      const status = err.response?.status;

      if (status === 401) {
        setError('Сессия истекла. Войдите снова');
        navigate('/login');
      } else if (status === 403) {
        setError('У вас нет прав на создание квиза');
      } else if (err.response?.data) {
        const backendError =
          typeof err.response.data === 'string'
            ? err.response.data
            : JSON.stringify(err.response.data);

        setError(`Ошибка: ${backendError}`);
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
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900">
              Создание нового квиза
            </h1>

            <Button
              variant="outline"
              onClick={() => navigate(-1)}
              className="!text-black bg-white hover:bg-gray-100"
            >
              Назад
            </Button>
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
              label="Таймер на весь квиз (секунды)"
              type="number"
              min={1}
              value={globalTimer || ''}
              onChange={(e) =>
                setGlobalTimer(
                  e.target.value
                    ? Number(e.target.value)
                    : undefined
                )
              }
            />

            <Input
              label="Баллов за правильный ответ"
              type="number"
              min={1}
              value={globalPoints}
              onChange={(e) =>
                setGlobalPoints(Number(e.target.value))
              }
            />
          </Card>

          {questions.map((q, qIdx) => (
            <Card
              key={qIdx}
              className="p-6 mb-6 bg-white shadow-md"
            >
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-semibold mb-4 text-gray-900">
                    Вопрос {qIdx + 1}
                  </h3>

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

                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => removeQuestion(qIdx)}
                >
                  Удалить вопрос
                </Button>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Тип вопроса
                </label>

                <select
                  value={q.question_type}
                  onChange={(e) =>
                    updateQuestionType(
                      qIdx,
                      e.target.value as 'single' | 'multiple'
                    )
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"
                >
                  <option value="single">
                    Одиночный выбор
                  </option>

                  <option value="multiple">
                    Множественный выбор
                  </option>
                </select>
              </div>

              <Input
                label="Текст вопроса"
                value={q.text}
                onChange={(e) =>
                  updateQuestionText(qIdx, e.target.value)
                }
                required
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Таймер на вопрос (секунды)"
                  type="number"
                  min={1}
                  value={q.timer || ''}
                  onChange={(e) =>
                    updateQuestionTimer(
                      qIdx,
                      e.target.value
                        ? Number(e.target.value)
                        : undefined
                    )
                  }
                />

                <Input
                  label="Баллов за вопрос"
                  type="number"
                  min={1}
                  value={q.points || globalPoints}
                  onChange={(e) =>
                    updateQuestionPoints(
                      qIdx,
                      Number(e.target.value)
                    )
                  }
                />
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Варианты ответов{' '}
                  {q.question_type === 'multiple' &&
                    '(можно выбрать несколько)'}
                </label>

                {q.answers.map((ans, aIdx) => (
                  <div
                    key={aIdx}
                    className="flex items-center gap-2 mb-2"
                  >
                    <input
                      type={
                        q.question_type === 'multiple'
                          ? 'checkbox'
                          : 'radio'
                      }
                      name={`correct-${qIdx}`}
                      checked={ans.is_correct}
                      onChange={() =>
                        setCorrectAnswer(qIdx, aIdx)
                      }
                      className="h-4 w-4 text-blue-600"
                    />

                    <Input
                      placeholder={`Вариант ${aIdx + 1}`}
                      value={ans.text}
                      onChange={(e) =>
                        updateAnswerText(
                          qIdx,
                          aIdx,
                          e.target.value
                        )
                      }
                      className="flex-1"
                    />

                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() =>
                        removeAnswer(qIdx, aIdx)
                      }
                    >
                      ×
                    </Button>
                  </div>
                ))}

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => addAnswer(qIdx)}
                >
                  + Добавить вариант
                </Button>
              </div>
            </Card>
          ))}

          <div className="flex gap-4 mt-4">
            <Button
              variant="outline"
              onClick={addQuestion}
            >
              + Добавить вопрос
            </Button>

            <Button
              variant="primary"
              onClick={handleSubmit}
              isLoading={loading}
            >
              Сохранить квиз
            </Button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CreateQuiz;