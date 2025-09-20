import React from 'react';

const TestComponent = () => {
  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">App is Working!</h1>
        <p className="text-gray-600">If you can see this, React is rendering correctly.</p>
        <div className="mt-4">
          <button 
            onClick={() => console.log('Button clicked!')}
            className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
          >
            Test Button
          </button>
        </div>
      </div>
    </div>
  );
};

export default TestComponent;
