import React from 'react';
import { useParams } from 'react-router-dom';
import ResultsTable from '../components/quiz/ResultsTable';

const Stats: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();

  if (!sessionId) {
    return <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 flex items-center justify-center">
      <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-xl p-6">
        <p className="text-gray-900">ID сессии не указан</p>
      </div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-xl p-6">
          <ResultsTable sessionId={parseInt(sessionId)} />
        </div>
      </div>
    </div>
  );
};

export default Stats;