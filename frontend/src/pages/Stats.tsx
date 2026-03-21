import React from 'react';
import ResultsTable from '../components/quiz/ResultsTable';

const Stats: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <ResultsTable />
    </div>
  );
};

export default Stats;