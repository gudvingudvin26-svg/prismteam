import React, { useState } from 'react';

interface Result {
  id: string;
  participantName: string;
  score: number;
  totalQuestions: number;
  completedAt: string;
}

const ResultsTable: React.FC = () => {
  const [results, setResults] = useState<Result[]>([
    { id: '1', participantName: 'Иван Петров', score: 8, totalQuestions: 10, completedAt: '2024-03-15 14:30' },
    { id: '2', participantName: 'Мария Сидорова', score: 9, totalQuestions: 10, completedAt: '2024-03-15 15:45' },
    { id: '3', participantName: 'Алексей Иванов', score: 7, totalQuestions: 10, completedAt: '2024-03-16 10:20' },
    { id: '4', participantName: 'Елена Петрова', score: 10, totalQuestions: 10, completedAt: '2024-03-16 11:15' },
    { id: '5', participantName: 'Дмитрий Соколов', score: 6, totalQuestions: 10, completedAt: '2024-03-17 09:45' }
  ]);

  const [sortField, setSortField] = useState<'score' | 'participantName' | 'completedAt'>('score');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  const handleSort = (field: 'score' | 'participantName' | 'completedAt') => {
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
    } else if (sortField === 'participantName') {
      comparison = a.participantName.localeCompare(b.participantName);
    } else {
      comparison = new Date(a.completedAt).getTime() - new Date(b.completedAt).getTime();
    }
    return sortDirection === 'asc' ? comparison : -comparison;
  });

  const exportToCSV = () => {
    const headers = ['Участник', 'Баллы', 'Всего вопросов', 'Процент', 'Дата завершения'];
    const data = sortedResults.map(r => [
      r.participantName,
      r.score.toString(),
      r.totalQuestions.toString(),
      `${Math.round((r.score / r.totalQuestions) * 100)}%`,
      r.completedAt
    ]);

    const csv = [headers, ...data].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'results.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const getSortIcon = (field: string) => {
    if (sortField !== field) return ' ↕️';
    return sortDirection === 'asc' ? ' ↑' : ' ↓';
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Результаты участников</h2>
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
                onClick={() => handleSort('participantName')}
              >
                Участник{getSortIcon('participantName')}
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
                onClick={() => handleSort('completedAt')}
              >
                Дата завершения{getSortIcon('completedAt')}
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedResults.map((result) => (
              <tr key={result.id} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4 font-medium">{result.participantName}</td>
                <td className="px-6 py-4">
                  <span className={`font-bold ${
                    result.score >= 8 ? 'text-green-600' :
                    result.score >= 5 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {result.score}
                  </span>
                </td>
                <td className="px-6 py-4">{result.totalQuestions}</td>
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        className="bg-blue-500 rounded-full h-2"
                        style={{ width: `${(result.score / result.totalQuestions) * 100}%` }}
                      ></div>
                    </div>
                    <span>{Math.round((result.score / result.totalQuestions) * 100)}%</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-gray-500">{result.completedAt}</td>
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