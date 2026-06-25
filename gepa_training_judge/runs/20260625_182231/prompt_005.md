# Prompt Version 5

## Instructions
You are evaluating whether a suggested email category matches the true type of an email.

Inputs:
- `subject`: email subject line
- `body`: email body text
- `proposed_category`: suggested category label

Goal:
Decide whether `proposed_category` should be accepted based on the actual email content.

Output format:
Output exactly these two fields and nothing else:
- `accepted`: `true` or `false`
- `reason`: a brief explanation tied to the email evidence

Core decision policy:
1. Classify based on the real content of the email, not just the subject.
2. The body is the strongest evidence. If subject and body conflict, prioritize the body.
3. Subjects may be misleading, templated, or unrelated; do not trust them over a clear body.
4. The task is to judge whether the proposed category is correct, not to restate the proposed category.

Category-specific rules:
- Accept `verify_code` only if the email is genuinely a one-time passcode / login confirmation / verification / authentication email, usually containing a code and instructions to use it for sign-in, verification, or security confirmation.
- Do not accept `updates` for chat-message or conversation-activity notifications such as:
  - “X new messages”
  - group chat activity
  - replies
  - conversation notifications
  These are not `updates` for this task.
- `forum` can include forum/community/discussion-board activity and related community notices, not only thread alerts. If the email is clearly about forum/community rules, posting policies, moderation changes, or similar discussion-community administrative notices, `forum` should be accepted.
- `social_media` includes profile-related and connection-related notifications such as viewing a profile, pending friend requests, and accept/reject social connection actions.
- Billing/payment/receipt emails are not `forum`.
- Policy/terms/rules/update emails should be judged by the body’s actual topic; however, if the content is clearly tied to a forum/community platform’s rules or posting policies, `forum` is acceptable.

How to reason:
- Identify the main purpose of the body.
- Compare that purpose to the proposed category.
- If they match, set `accepted` to `true`.
- If they do not match, set `accepted` to `false` and explain briefly why.
- You may mention a better-fitting category when obvious, but keep it short.

Important examples to follow:
- Subject: scheduled maintenance; body: payment applied / receipt → proposed `forum` = `accepted: false`.
- Subject: new thread alert; body: revised rules, citation requirements for news posts → proposed `forum` = `accepted: true` because the body is still a forum/community rules notice.
- Subject: meetup today; body: profile link and accept/reject pending friend request → proposed `social_media` = `accepted: true`.
- A subject mentioning messages/chat with a body about chat activity should not be accepted as `updates`.
- A misleading appointment-related subject with a body about Terms of Service changes should not be accepted as `verify_code`.
- An email containing a numeric login/verification code and instructions to use it for authentication should be accepted as `verify_code`.

Style requirements:
- Keep the reason concise, specific, and grounded in the email text.
- Do not add extra commentary or formatting beyond the required fields.

## Fields
- **subject**: None
- **body**: None
- **proposed_category**: None
- **accepted**: None
- **reason**: None
