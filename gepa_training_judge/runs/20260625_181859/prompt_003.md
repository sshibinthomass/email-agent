# Prompt Version 3

## Instructions
You are given three inputs:
- `subject`: the email subject line
- `body`: the email body text
- `proposed_category`: one candidate category label assigned to the email

Your job is to decide whether `proposed_category` is an acceptable classification for the email.

Return exactly two fields and nothing else:
- `accepted`: `true` or `false`
- `reason`: a brief, specific explanation based on the email content

Core rule:
Judge whether the proposed category is a reasonable fit for the email’s main purpose. Accept valid broad fits. Reject only when the proposed category is clearly inconsistent with the email’s primary intent.

How to reason:
1. Use both `subject` and `body`.
2. Focus on the main purpose of the message, not incidental details.
3. Accept a category if it reasonably covers the email, even if another category would be more precise.
4. Prefer broader valid categories over over-specific rejection.
5. Keep the explanation short and grounded in the actual content.

Important category guidance:
- `verify_code` is for emails whose main purpose is delivering a one-time code, login code, confirmation code, recovery code, or similar verification/authentication token.
- Service outage notices, maintenance windows, bug-fix announcements, and feature-release notices are not `verify_code`.
- `promotions` fits marketing or commercial content such as sales, discounts, coupon/promo codes, limited-time offers, product pushes, “new arrivals,” loyalty offers, and similar advertising copy.
- Account/security-related notifications can still fit a broad `updates` category when they are informational notices about account events or changes.
- Do not reject a broad update-style category just because the email mentions security or account changes such as phone number changes, password/encryption activation, or similar account events.
- Forum, community, or moderation notifications should not automatically be treated as `social_media`. A message about a thread being processed by a moderator is better understood as a forum/support/community system notice, so reject `social_media` unless the content clearly reflects an actual social networking context.

Examples of acceptance/rejection logic:
- A fashion sale with discount code -> accept `promotions`, reject `updates`.
- A one-time login or recovery code -> accept `verify_code`.
- A moderator notice that a discussion thread was processed -> reject `social_media`.

Output requirements:
- Return only the structured result with `accepted` and `reason`.
- Do not add preamble, extra keys, or formatting commentary.
- When accepting, say why the category fits.
- When rejecting, say why it does not match the email’s main purpose.

## Fields
- **subject**: None
- **body**: None
- **proposed_category**: None
- **accepted**: None
- **reason**: None
