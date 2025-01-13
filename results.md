## Some Results

| Model    | Config | Accuracy in Test Set Web Arena |
| -------- | ------- | ------- |
| Generic - Screenshot off  | Mono | 18.4   |
| Generic - Plan Flag On | Mono | 16.8    |
| Planner/Controller - Fixed Plan | Modular |  12.1  |
| Planner/Controller    | Modular | 10.4    |

Observations
- In CP: I see that sometimes in the screenshot a step has been clearly succesful but the step keeps being part of the plan
- In CP: I want to try making the inner cycle of the planner controller just a retry of 1. Basically this makes the planner revaluate at every step
- In CPFixed: Maybe setting the History flag to False might be useful -> Update: Accuracy went down
- Run Fixed Plan with 4o as a Planner

| Model    | Config | Accuracy in 100 Web Arena |
| -------- | ------- | ------- |
| Generic - Screenshot On  | Mono | 18.0   |
| Planner/Controller - Previous Plan Off    | Modular | 16.0    |
| Planner/Controller - Previous Plan On    | Modular | 21.0    |

Still have issues with maps and sending user info
