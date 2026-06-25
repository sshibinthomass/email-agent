# Prompt Version 2

## Instructions
You are given three inputs:
- `subject`: the email subject line
- `body`: the email body
- `proposed_category`: a candidate label for the email

Your task is to judge whether the proposed category is a reasonable fit for the email.

Output exactly:
- `accepted`: `true` or `false`
- `reason`: a brief explanation

Decision rule:
- Accept the proposed category if it plausibly matches the main purpose/theme of the email.
- Reject it only when it is clearly inconsistent with the email’s content.
- Be tolerant of broad but reasonable categories. Do not reject a category just because a more specific label might exist.
- In particular, categories like `updates` can be acceptable when the email is generally informing the user about a change, notice, or account-related update, even if a narrower category such as security or account notification could also apply.
- If the email is plainly about a different topic than the proposed category, set `accepted` to `false` and explain the mismatch.

Guidance:
- Focus on the primary intent of the email, using both subject and body.
- Use the body to confirm or correct potentially misleading subject lines.
- Marketing/sales/discount/promo-code emails fit `promotions`.
- Service outage, maintenance, bug-fix, or feature-rollout messages do not fit `verify_code`.
- Account/security/settings change notifications may still fit a broad category like `updates` if they are fundamentally informational.

Reason style:
- Keep the reason concise and specific.
- When `accepted = true`, explain why the category fits.
- When `accepted = false`, explain why it does not fit and, optionally, mention a better-fitting type.

Return only the two requested fields and no extra commentary.

## Fields
- **subject**: None
- **body**: None
- **proposed_category**: None
- **accepted**: None
- **reason**: None
