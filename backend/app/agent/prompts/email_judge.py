EMAIL_JUDGE_PROMPT = """You are given three inputs:
- subject: the email subject line
- body: the email body
- proposed_category: a candidate label for the email

Your task is to decide whether the proposed category is a reasonable fit for the email’s main purpose.

Output exactly these two fields and nothing else:
- accepted: true or false
- reason: a brief explanation

Core decision rule:
- Accept (accepted = true) when the proposed category is a plausible label for the email’s primary intent/theme.
- Reject (accepted = false) only when the proposed category is clearly inconsistent with the email content.
- Be tolerant of broad but reasonable labels. Do not reject merely because a more precise category could also exist.

How to judge:
- Use both subject and body, with the body as the stronger signal when they differ.
- Focus on the main purpose of the message, not minor details.
- Ask: “Would a reasonable person consider this category to fit this email at all?” If yes, accept it unless there is a clear mismatch.

Important category guidance:
- Broad informational categories like updates are acceptable for emails that mainly inform the user about a change, notice, status update, account-related update, policy notice, feature rollout, maintenance, outage, or similar informational message.
- Account/security/settings change notifications can still reasonably fit updates if they are primarily informational.
- Marketing, sales, discounts, offers, promo codes, newsletters pushing products/services, and similar commercial outreach fit promotions.
- Service outage, maintenance, bug-fix, feature-rollout, forum activity, event reminders, or general notifications do not fit verify_code.
- social_media should be reserved for emails genuinely about social-network activity or platform interactions; general event/session notices do not fit it.
- Do not treat ordinary unsolicited advertising or sales outreach as spam by default. spam should be accepted only when the email is clearly junk/abusive/deceptive in nature, not merely because it is promotional. Legitimate marketing or business solicitation is better treated as a normal promotional/marketing email, so a proposed category of spam should usually be rejected unless the content itself strongly supports it.

Reason writing:
- Keep the reason concise and specific.
- If accepted = true, briefly say why the category fits the email’s main purpose.
- If accepted = false, briefly state the mismatch and optionally mention a better-fitting type.
- Do not add extra commentary beyond the two fields.

Examples of intended behavior:
- AMA/event starting-time notice + social_media → reject, because it is an event/update notice, not social-media activity.
- Forum/thread/trending-content notification + verify_code → reject, because it is a content/activity notification, not a verification-code email.
- Promotional coaching offer + spam → reject unless the email is clearly deceptive/junk; being unsolicited promotion alone is not enough to accept spam.

Return only:
- accepted: true or false
- reason: brief explanation

Email Details to Judge:
Subject: {subject}
Body: {body}
Proposed Category: {proposed_category}"""
