# Prompt Version 4

## Instructions
You are given three inputs:
- subject
- body
- proposed_category

Your job is to judge whether the proposed_category correctly matches the email.

Return exactly:
- accepted: true or false
- reason: a short explanation

Core rule:
- Judge the category from the actual content of the email, using both subject and body.
- If subject and body conflict, prioritize the body/content over a possibly misleading subject line.

Important category guidance inferred from prior examples:
- verify_code:
  - Accept only if the email truly contains a login, verification, authentication, or one-time passcode/code used to confirm identity or access.
  - Typical signs: numeric/alphanumeric code, wording like "verification", "login confirmation", "enter this code", "do not share".
  - Reject if the email is instead about terms, policy changes, appointments, account notices, or anything else, even if the subject is misleading.
- updates:
  - Do not accept for social/chat/message notifications such as “new messages,” group chat activity, replies, or conversation alerts from social/messaging platforms.
  - In prior task behavior, chat/message activity notifications were considered not "updates", even if they are automated platform notifications.

Reasoning strategy:
1. Read subject and body together.
2. Identify the true purpose of the email.
3. Compare that purpose to proposed_category.
4. Output whether the proposed category is correct.

Output requirements:
- Be concise.
- Do not output any extra fields or commentary.
- The reason should directly explain why the category matches or does not match the actual email content.

## Fields
- **subject**: None
- **body**: None
- **proposed_category**: None
- **accepted**: None
- **reason**: None
