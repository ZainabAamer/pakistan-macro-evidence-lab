# Test the completed tool with real people (not yet conducted)

## Question

Can an aspiring analyst find and correct numerical errors in SBP monetary policy briefs more accurately or faster using the Macro Decision Room than using the original SBP statements alone?

## Before recruiting

The current application gives players one incorrect claim per round, so they know an error exists. The PDF-only condition must give the **same two claims and tell participants that one is incorrect**. Otherwise a difference in accuracy is caused by the instructions, not the tool. This is an educational usability pilot, not a randomized trial of a novel LLM (no live model runs in the current app).

Use two different rounds per participant. Alternate their order and condition: half start with the original PDF and half with the tool. Never reuse a statement for the same person in both conditions; make sure both conditions contain each statement across participants. A suggested minimum is 6 consenting participants, each making two attempts (12 tasks); results will be exploratory, not statistically generalizable.

## PDF-only condition

Give the participant `research/pdf_only_test.html` and assign a specific statement date. The sheet presents the linked original PDF and the same two claim sentences displayed in the corresponding app round; it records a timer and lets the participant download a local JSON record. Tell them: “One claim is incorrect. Find it, point to the passage you used, and tell us if you are unsure.” Do not show the answer key or market outcome before completion. The original PDF link needs internet access on the participant's device.

## Tool condition

Ask the participant to use the app, select the incorrect claim, and lock the decision. The app's optional JSON export includes `elapsed_sec` from the start of the round. The market-direction decision is an **extra step** in the app; for the speed comparison, it must be removed from the measured interval in a later study-specific version, or report the app's time as a conservative upper bound. Score **only the fact-checking question**. Collect any spontaneously reported confusion without coaching.

## Record (one row per attempt)

`anonymous_id,statement_date,condition,task_order,incorrect_claim_selected,evidence_paragraph,seconds_to_complete,correct,participant_confidence_1_to_5,notes`

Do not record names, emails or workplace details. Ask whether the person permits their anonymous results to be used in a project write-up. Keep unconsented notes private and out of the published dataset. Count nonresponses and dropped tasks. An observer should independently verify answers against the linked SBP passage.

## Report honestly

Publish: participant and task counts; number correct in each condition; median seconds per correct answer (and all-attempt median); order effects; instances where the tool's wording misled people; anonymous feedback; and limitations including convenience sampling and practice effects. If no participants complete it, report **no measured user impact**. Do not call pilot results proof of improved analyst productivity.

## Next version required for AI impact

To evaluate an LLM rather than the current hand-authored game, create a larger independently reviewed test set with unseen documents, run an actual model, verify all cited passages against the source PDFs, and only then compare users using the AI tool versus users using search/PDFs. Save raw predictions, model version, prompts, latency, cost and abstentions. Do not count the current 30 contrast claims as independent examples: each supported/contradicted pair comes from the same fact.
