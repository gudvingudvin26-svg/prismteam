import React from 'react';
import { useParams } from 'react-router-dom';
import ResultsTable from '../components/quiz/ResultsTable';

const Stats: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();

  if (!sessionId) {
    return <div className="p-6 text-center">ID сессии не указан</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <ResultsTable sessionId={parseInt(sessionId)} />
    </div>
  );
};

export default Stats;