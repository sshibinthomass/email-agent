# Prompt Version 5

## Instructions
You are given three inputs:
- `subject`: the email subject line
- `body`: the email body text
- `proposed_category`: one candidate category label assigned to the email

Your task is to determine whether `proposed_category` is an acceptable label for the email.

Return exactly two fields and nothing else:
- `accepted`: `true` or `false`
- `reason`: a brief, specific explanation grounded in the email content

Decision standard:
Accept the proposed category if it is a reasonable fit for the email’s main purpose, even if another category might be more precise. Reject only when the proposed category is clearly inconsistent with the email’s primary intent.

Reasoning rules:
1. Use both `subject` and `body`.
2. Identify the email’s main purpose, not side details.
3. Prefer accepting valid broad categories rather than rejecting because they are not the single best label.
4. Keep the explanation short, concrete, and tied to the actual message content.
5. Do not infer facts that are not supported by the email.

Category guidance:
- `verify_code`:
  - Accept only when the email’s main purpose is to provide a one-time verification, login, confirmation, authentication, or recovery code/token.
  - Reject for service alerts, maintenance notices, outage reports, bug-fix announcements, feature releases, community notices, or any message that does not actually deliver a verification/authentication code.
- `promotions`:
  - Accept for marketing/commercial emails such as sales, discounts, coupon or promo codes, limited-time offers, product pushes, “new arrivals,” loyalty offers, and similar advertising.
- `updates`:
  - Accept for broad informational notices, including account or security-related events and changes.
  - Do not reject `updates` just because the email mentions security/account matters such as password changes, encryption activation, phone number changes, or similar account notifications.
- `social_media`:
  - Use only when the content clearly reflects a true social networking context.
  - Do not automatically treat forum, community, discussion-board, or moderation notices as `social_media`.
  - Messages about threads, moderators, locked discussions, community processing, or forum activity are better understood as forum/community/system notices, so reject `social_media` unless the message is plainly from a social networking platform.
- `spam`:
  - Do not accept `spam` merely because the email is promotional, unsolicited, or low-quality.
  - Treat `spam` as appropriate only when the email clearly indicates junk/malicious/deceptive spam rather than ordinary marketing.
  - Legitimate promotional or advertising content is better treated as something like `promotions`, so reject `spam` for normal commercial offers and services.

Examples of intended behavior:
- A fashion sale with a discount code -> accept `promotions`; reject `updates`.
- A one-time login or recovery code -> accept `verify_code`.
- A moderator notice that a discussion thread was processed or locked -> reject `social_media`; reject `verify_code`.
- An unsolicited coaching/service advertisement with “first session free” -> reject `spam` unless the content clearly shows actual spam/junk behavior.

Output requirements:
- Return only:
  - `accepted`: `true` or `false`
  - `reason`: short explanation
- No preamble, no extra keys, no markdown.
- When `accepted` is `true`, explain why the proposed category fits the email’s main purpose.
- When `accepted` is `false`, explain why the proposed category does not match the email’s main purpose.

## Fields
- **subject**: None
- **body**: None
- **proposed_category**: None
- **accepted**: None
- **reason**: None
