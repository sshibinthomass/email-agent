# Prompt Version 2

## Instructions
You are given three inputs:
- `subject`: the email subject line
- `body`: the email body text
- `proposed_category`: a single category label that someone assigned to the email

Your task is to judge whether the `proposed_category` is an appropriate classification for the email.

Output exactly two fields:
- `accepted`: `true` if the proposed category is correct, otherwise `false`
- `reason`: a brief explanation grounded in the subject/body content

Decision guidelines:
1. Base your judgment on the actual meaning and primary intent of the email, using both subject and body together.
2. Accept the proposed category if it is a reasonable fit, even if another category might also be more specific or preferable.
3. Do not reject a category merely because you can imagine a better label; reject only when the proposed category is clearly inconsistent with the email’s main purpose.
4. Prefer broader categories when they still validly cover the content.
5. For example:
   - Service outage, maintenance windows, bug fixes, or feature-release notices are not `verify_code`.
   - Sales, discounts, limited-time offers, promo codes, and marketing copy fit `promotions`.
   - Account/security-related notices can still fit a broad `updates` category if they are informational updates about the account, even if a narrower label like security alert might also apply.
6. Be careful with emails that mention security/account changes: notifications such as changed phone number, password/encryption activation, or similar account events should not be rejected from a broad update-style category unless the proposed category is clearly wrong.
7. Keep the reason concise and specific. When accepting, explain why the category fits. When rejecting, explain why it does not fit the email’s main purpose.

Return only the structured result with `accepted` and `reason`.

## Fields
- **subject**: None
- **body**: None
- **proposed_category**: None
- **accepted**: None
- **reason**: None
