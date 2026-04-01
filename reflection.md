# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design will include four classes: Owner, Pet, Task, Scheduler.
The owner has the ability to modify the preference list and change the daily time budget. They have also have total minutes available for pet care in a day. 
Pet has the ability to get a summary of the readable description of itself. It also displays the name, species, the age, and its owner.
Task has the ability to convert a priority string to a numeric value. It has a title, duration in minutes, priority, and category.
Lastly, the scheduler is able too add tasks, remove tasks, generate schedules, explain said schedules, and return the current schedule.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design changed. Scheduler is locked to only one pet. If an owner has two pets, there would have to be two separate Scheduler instances with no way to coordinate shared time across them. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The tradeoff that scheduler makes is to move the scoring functionality to Task.schedule_score(). The tradeoff is reasonable because this is a single responsibility and can be reused in filters and sorts in other parts of the code.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Claude Code across four phases: testing (identifying edge cases and drafting test functions), UI integration, UML refinement, and documentation (adding Features and Testing sections to the README).

The prompts and questions that were most helpful were asking "what are the most important edge cases?" before writing tests. This produced a prioritized plan instead of jumping into code. I also Scoped requests like "update app.py to use the Scheduler class" which kept changes focused. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When the AI generated a PlantUML file, I rejected the file creation and told it not to write it into a new code file. I wanted the code as text you could copy instead. I evaluated the suggestion by recognizing that a .puml file in the project wasn't what was needed, and redirected the AI to just output it inline. I  then followed up by asking for a Mermaid.js version instead, which better fit the workflow.

This shows I was reviewing each AI action before accepting it, not just auto-approving every tool call.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The behaviors that I tested were sorting correctness, daily recurrence, one-time tasks, conflict detection, and adjacent boundaries.

These tests were import because sorting is the foundation of the scheduler; If tasks come out in the wrong order, every schedule is wrong
Recurrence has the most moving parts (timedelta math, creating a new Task, re-assigning it to the pet) so it's the most likely place for a bug
Conflict detection relies on an inequality (a_start < b_end and b_start < a_end) where an off-by-one error would either miss real conflicts or flag false ones -- the adjacent-boundary test specifically guards against that


**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

My confidence level is a 4 out of 5 because the tests cover the core logic paths: sorting, recurrence, and conflict detection all pass. The main risk is untested boundary conditions.

The edge cases I would test next are Zero available minutes. Doe|s the scheduler return an empty schedule, or does something break?
I also want to test Pet with no tasks. This would confirm the scheduler handles empty task lists gracefully

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I think the test suite is the strongest part. It's 8 tests across 4 areas all passed on the first run, covering sorting, recurrence, and conflict detection. Having tests in place also made it safe to update app.py without worrying about breaking the scheduling logic.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The generate_schedule() method uses a simple greedy algorithm that skips tasks if they don't fit. With another iteration, you could redesign it to try rearranging shorter tasks to fill gaps, or warn the user which high-priority tasks were dropped so they can adjust their available time. The UI could also let users drag to reorder tasks manually instead of relying entirely on the algorithm.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Designing the UML first and then comparing it against the final code revealed how much a system changes during implementation. The original diagram had direct arrows from Scheduler to Pet and Task that didn't exist in the code. The lesson: treat the diagram as a living document, not a contract. Using AI to do a systematic diagram-vs-code comparison at the end was an efficient way to catch those gaps.