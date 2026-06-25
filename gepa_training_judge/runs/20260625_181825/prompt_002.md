# Prompt Version 2

## Instructions
You are given three inputs:
- `subject`: the email subject line
- `body`: the email body
- `proposed_category`: a category label someone assigned to the email

Your task is to judge whether the `proposed_category` is an acceptable category for the email.

Output exactly:
- `accepted`: `true` or `false`
- `reason`: a brief explanation

Decision rules:
1. Judge the proposed category by whether it is a reasonable fit for the email overall, not whether it is the single best or most specific possible label.
2. Accept broad but plausible categories. A category does not need to be maximally precise to be correct.
3. If the subject and body are inconsistent, noisy, stitched together, or mixed-content, still accept the proposed category if it matches a substantial or plausible part of the message.
4. Do not reject a category merely because:
   - the email contains multiple topics,
   - the subject does not perfectly match the body,
   - the category is somewhat generic (for example, `updates`) but still fits.
5. Reject only when the proposed category is clearly incompatible with the email content.

Guidance from examples:
- Messages with urgent language, suspicious delivery claims, and dubious links are strong indicators of `spam`.
- A generic category like `updates` should be accepted when the email is a service/booking/notification-style message, even if the subject appears mismatched or the content is mixed.
- A message labeled as a digest or discussing threads/discussions can reasonably fit `forum`.

Reason-writing guidance:
- Keep the reason concise.
- Explain why the category is or is not a reasonable fit.
- When accepting, emphasize plausibility/fitness rather than proposing a better alternative.
- When rejecting, state the specific mismatch between the email content and the proposed category.

Return only the requested fields and no extra text.

## Fields
- **subject**: None
- **body**: None
- **proposed_category**: None
- **accepted**: None
- **reason**: None
