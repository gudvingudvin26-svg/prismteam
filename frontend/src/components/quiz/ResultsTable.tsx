import React, { useState, useEffect } from 'react';
import { sessionsApi } from '../../api/sessions';

interface Result {
  id: number;
  participant_name: string;
  score: number;
  total_questions: number;
  completed_at: string;
}

interface ResultsTableProps {
  sessionId: number;
}

const ResultsTable: React.FC<ResultsTableProps> = ({ sessionId }) => {
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortField, setSortField] = useState<'score' | 'participant_name' | 'completed_at'>('score');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    loadResults();
  }, [sessionId]);

  const loadResults = async () => {
    try {
      const response = await sessionsApi.getResults(sessionId);
      setResults(response.data);
    } catch (error) {
      console.error('Ошибка загрузки результатов:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: 'score' | 'participant_name' | 'completed_at') => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedResults = [...results].sort((a, b) => {
    let comparison = 0;
    if (sortField === 'score') {
      comparison = a.score - b.score;
    } else if (sortField === 'participant_name') {
      comparison = a.participant_name.localeCompare(b.participant_name);
    } else {
      comparison = new Date(a.completed_at).getTime() - new Date(b.completed_at).getTime();
    }
    return sortDirection === 'asc' ? comparison : -comparison;
  });

  const exportToCSV = () => {
    const headers = ['Участник', 'Баллы', 'Всего вопросов', 'Процент', 'Дата завершения'];
    const data = sortedResults.map(r => [
      r.participant_name,
      r.score.toString(),
      r.total_questions.toString(),
      `${Math.round((r.score / r.total_questions) * 100)}%`,
      new Date(r.completed_at).toLocaleString()
    ]);

    const csv = [headers, ...data].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `results_session_${sessionId}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const getSortIcon = (field: string) => {
    if (sortField !== field) return ' ↕️';
    return sortDirection === 'asc' ? ' ↑' : ' ↓';
  };

  if (loading) return <div className="text-center text-white py-8">Загрузка...</div>;

  if (results.length === 0) {
    return <div className="p-6 text-center text-gray-600">Нет результатов</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Результаты участников</h2>
        <button
          onClick={exportToCSV}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          📥 Экспорт в CSV
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border rounded-lg">
          <thead>
            <tr className="bg-gray-100 border-b">
              <th
                className="px-6 py-3 text-left text-sm font-medium text-gray-600 cursor-pointer hover:bg-gray-200"
                onClick={() => handleSort('participant_name')}
              >
                Участник{getSortIcon('participant_name')}
              </th>
              <th
                className="px-6 py-3 text-left text-sm font-medium text-gray-600 cursor-pointer hover:bg-gray-200"
                onClick={() => handleSort('score')}
              >
                Баллы{getSortIcon('score')}
              </th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">
                Всего вопросов
              </th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">
                Процент
              </th>
              <th
                className="px-6 py-3 text-left text-sm font-medium text-gray-600 cursor-pointer hover:bg-gray-200"
                onClick={() => handleSort('completed_at')}
              >
                Дата завершения{getSortIcon('completed_at')}
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedResults.map((result) => (
              <tr key={result.id} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4 font-medium text-gray-900">{result.participant_name}</td>
                <td className="px-6 py-4">
                  <span className={`font-bold ${
                    result.score >= 8 ? 'text-green-600' :
                    result.score >= 5 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {result.score}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-700">{result.total_questions}</td>
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        className="bg-blue-500 rounded-full h-2"
                        style={{ width: `${(result.score / result.total_questions) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-gray-700">{Math.round((result.score / result.total_questions) * 100)}%</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-gray-500">
                  {new Date(result.completed_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Всего участников: {results.length}
      </div>
    </div>
  );
};

export default ResultsTable;