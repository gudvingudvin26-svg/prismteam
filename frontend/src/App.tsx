import Results from './pages/Results';
import QuizList from './pages/organizer/QuizList';
import CreateQuiz from './pages/organizer/CreateQuiz';
import Stats from './pages/Stats';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/join" element={<JoinQuiz />} />
        <Route path="/play/:sessionId" element={<QuizSession />} />
        <Route path="/results/:sessionId" element={<Results />} />

        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/quizzes" element={<QuizList />} />
        <Route path="/quizzes/create" element={<CreateQuiz />} />
        <Route path="/stats/:sessionId" element={<Stats />} />

        <Route
          path="/quizzes/:id/edit"
          element={
            <PrivateRoute>
              <div>Редактирование квиза (в разработке)</div>
            </PrivateRoute>
          }
        />

        <Route path="*" element={<div className="p-6 text-center">404 - Страница не найдена</div>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;