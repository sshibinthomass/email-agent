# Prompt Version 3

## Instructions
You are given three inputs:
- `subject`: the email subject line
- `body`: the email body text
- `proposed_category`: a suggested category for the email

Your task is to judge whether the `proposed_category` is correct for the email.

Output exactly:
- `accepted`: `true` or `false`
- `reason`: a short explanation grounded in the email content

Decision rules:
1. Use the actual email content, with the body taking priority when subject and body conflict or suggest different things.
2. Be alert to misleading subjects. If the body clearly indicates a different email type, judge based on the body/main content.
3. Accept `verify_code` only when the email is वास्तवially a one-time code / login confirmation / verification message, typically containing a code and instructions to use it for sign-in, verification, or authentication.
4. Do not accept `updates` for chat-message/activity notifications such as “X new messages,” group chat activity, replies, or conversation notifications. Those are not considered `updates` for this task.
5. If the proposed category does not match the true email type, set `accepted` to `false` and explain briefly why. You may mention a better-fitting category in the reason if it is obvious, but this is optional.

Guidance from prior examples:
- A subject like “23 new messages in "Book Club" chat” with chat activity in the body should NOT be accepted as `updates`.
- An email with a misleading appointment-related subject but a body about Terms of Service changes should NOT be accepted as `verify_code`; judge it by the body content.
- An email containing a numeric code for login confirmation/verification SHOULD be accepted as `verify_code`.

Keep the reason concise and specific to the evidence in the email.

## Fields
- **subject**: None
- **body**: None
- **proposed_category**: None
- **accepted**: None
- **reason**: None
