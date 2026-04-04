export type FeedbackStatus = 'correct' | 'close' | 'wrong';

export type GuessFeedback = {
    team: FeedbackStatus;
    conference: FeedbackStatus;
    division: FeedbackStatus;
    position: FeedbackStatus;
    height: FeedbackStatus;
    age: FeedbackStatus;
    jersey: FeedbackStatus;
};
