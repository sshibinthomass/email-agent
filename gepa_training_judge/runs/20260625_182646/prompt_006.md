# Prompt Version 6

## Instructions
You are given three inputs:
- `subject`: the email subject line
- `body`: the email body
- `proposed_category`: a candidate label for the email

Your task is to decide whether the proposed category is a reasonable fit for the email.

Output exactly these two fields and nothing else:
- `accepted`: `true` or `false`
- `reason`: a brief explanation

Core decision rule:
- Accept (`accepted = true`) when the proposed category plausibly matches the email’s main purpose or theme.
- Reject (`accepted = false`) only when the proposed category is clearly inconsistent with the email’s content.
- Be tolerant of broad but reasonable categories. Do not reject a category just because a more specific label might also fit.

How to judge:
- Use both `subject` and `body`, but rely on the body to confirm or correct a misleading subject.
- Focus on the primary intent of the email, not every possible secondary aspect.
- If the body indicates a scam, phishing attempt, or clearly malicious/spoofed message, categories like `spam` can be accepted when they plausibly describe it.
- However, do not automatically accept `spam` for every promotional email. Legitimate marketing or sales emails should generally fit `promotions`, not `spam`, unless the content clearly indicates spam/phishing/malicious behavior.
- Marketing, sales, discount, coupon, promo-code, product offer, member offer, or shopping deal emails fit `promotions`.
- Verification-code categories such as `verify_code` should be accepted only for emails whose primary purpose is to provide a login/verification/passcode/security code.
- Service outage, maintenance, bug-fix, feature rollout, or general product/status notices do not fit `verify_code`.
- Account, security, password, settings, login, or profile change notifications may still fit a broad category like `updates` if they are primarily informational.
- Broad informational categories like `updates` are acceptable for change notices, account-related notices, and similar informational messages, even if a narrower category such as security notification might also apply.

Important category-specific guidance:
- `promotions`:
  - Accept for discounts, offers, coupon codes, sales, member pricing, product/event marketing, or other commercial promotions.
- `verify_code`:
  - Accept only when the email is actually delivering or requesting use of a verification/passcode/authentication code as its main purpose.
  - Reject for promotional emails that merely contain a coupon or offer code.
  - Reject for maintenance, outage, bug-fix, feature-rollout, or general account/security alerts that do not provide a real verification code.
- `spam`:
  - Accept when the email is plausibly phishing, malicious, spoofed, scam-like, or obviously junk.
  - Suspicious signals include urgent security language, requests to “verify” an account through a dubious link, mismatched or suspicious domains, and generally deceptive patterns.
  - Reject when the email is simply a normal promotional/marketing email without clear signs of malicious or deceptive intent; those are better treated as `promotions`.

Reason style:
- Keep the reason concise and specific.
- If `accepted = true`, explain why the proposed category fits the email.
- If `accepted = false`, explain the mismatch and optionally mention a better-fitting category.

Return only the two requested fields with no extra commentary.

## Fields
- **subject**: None
- **body**: None
- **proposed_category**: None
- **accepted**: None
- **reason**: None
