## Some Results

| Model    | Config | Accuracy in Test Set Web Arena |
| -------- | ------- | ------- |
| Generic - Screenshot off  | Mono | 18.4   |
| Generic - Plan Flag On | Mono | None    |
| Planner/Controller - Fixed Plan | Modular |  12.1  |
| Planner/Controller    | Modular | 10.4    |

Observations
- In CP: I see that sometimes in the screenshot a step has been clearly succesful but the step keeps being part of the plan
- In CP: I want to try making the inner cycle of the planner controller just a retry of 1. Basically this makes the planner revaluate at every step
- In CPFixed: Maybe setting the History flag to False might be useful -> Update: Accuracy went down
- 
