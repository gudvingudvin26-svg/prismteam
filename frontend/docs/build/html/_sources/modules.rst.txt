UI Components
=============

Button
------

Button component with variants: primary, outline, danger, success.

Properties:
- `variant` - button style (primary, outline, danger, success)
- `size` - button size (sm, md, lg)
- `isLoading` - show loading state
- `fullWidth` - stretch to full width

Example:

.. code-block:: tsx

   <Button variant="primary" onClick={() => console.log('click')}>
     Click me
   </Button>

Input
-----

Input field with label and error support.

Properties:
- `label` - input label text
- `error` - error message text
- `fullWidth` - stretch to full width
- `multiline` - enable textarea mode

Card
----

Card component with shadow and rounded corners.

Modal
-----

Modal dialog with overlay.

Pages
=====

Home
----

Landing page. Contains Hero section, features, and CTA.

Login
-----

Login form with email and password fields.

Register
--------

Registration form with username, email, password, and password confirmation.

Dashboard
---------

Organizer dashboard. Displays statistics and quiz list.

JoinQuiz
--------

Participant join page by quiz code.

QuizSession
-----------

Quiz gameplay page. Shows current question, timer, and answer options.

Results
-------

Results page. Shows participant score and leaderboard.

Stats
-----

Statistics page for organizer.

API
===

api.ts
------

Configured Axios instance with interceptors for token handling and error processing.

auth.ts
-------

Authentication methods: `login`, `register`, `logout`, `getCurrentUser`.

quizzes.ts
----------

Quiz management methods: `createQuiz`, `getMyQuizzes`, `updateQuiz`, `deleteQuiz`, plus question and answer management.

sessions.ts
-----------

Session management methods: `createSession`, `joinSession`, `startSession`, `endSession`, `submitAnswer`, `getResults`, `getQuestionsStats`.

Types
=====

All types defined in `src/types/index.ts`. Main types:

- `User` - user entity
- `Quiz` - quiz entity
- `Question` - question entity
- `Answer` - answer option entity
- `QuizSession` - game session entity
- `ParticipantResult` - participant result
- `QuestionStat` - question statistics

Store
=====

appStore.ts
-----------

Zustand store for global state:

- `user` - current user
- `isLoading` - loading flag
- `setUser` - set user
- `setLoading` - set loading flag