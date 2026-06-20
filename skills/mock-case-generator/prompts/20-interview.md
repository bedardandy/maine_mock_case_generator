# Prompt: Simulate the intake interview

Write `intake_interview` as a realistic intake conversation that *surfaces the facts*
already in the matter (it should be consistent with the fact pattern, not contradict it).

Produce:
- `interviewer` (e.g. "Intake Attorney")
- `interviewee_role` (canonical role of the person interviewed, e.g. "plaintiff")
- `date` (ISO yyyy-mm-dd)
- `exchanges`: 4–6 items, each `{topic, question, answer}` (optionally `follow_up`).
  Cover at least: the client's goal, the core facts/timeline, the other parties,
  money/assets at stake, any urgency or safety concerns, and what documents the
  client has.

Voice: the answers are in the client's words and may be incomplete or uncertain —
that realism is useful for testing downstream extraction. Keep it fictional and
respectful, especially for sensitive matters (abuse, guardianship, death).
