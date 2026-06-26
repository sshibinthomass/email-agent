You are given three inputs:
- subject: the email subject line
- body: the email body
- proposed_category: a candidate label for the email

Your task is to decide whether the proposed category is the correct classification for the email.

The 6 allowed categories are:
1. forum: emails about forum threads, community discussions, or community rule changes.
2. verify_code: authentication codes, one-time passwords (OTPs), verification PINs, or password reset tokens.
3. promotions: marketing, sales, discounts, offers, or newsletters promoting products/services.
4. social_media: friend requests, new followers, profile updates, or activity notifications from social networks (e.g. LinkedIn, Twitter).
5. spam: deceptive/fraudulent messages, phishing scams, lotteries, or malicious links.
6. updates: informational account/system notices, order/shipping updates, flight/hotel bookings, policy notices, or maintenance windows.

Core decision rules:
- These 6 categories are mutually exclusive.
- Accept (accepted = true) only if the proposed_category is the correct and best-fitting classification for the email.
- Reject (accepted = false) if the proposed_category is incorrect, or if the email clearly fits a more specific allowed category (e.g., do not accept 'updates' if the email is actually a forum thread or a social media invitation).
- Reject 'updates' for phishing/scam/fraudulent emails (these should be 'spam' instead).

Reason writing:
- Keep the reason concise and specific.
- If accepted = true, briefly say why the category is the correct classification.
- If accepted = false, briefly state why it is incorrect and identify the correct category from the list.

Examples of correct behavior:
- Moderation notice mentioning community guidelines update + updates → reject (should be forum).
- Verizon payment overdue warning pointing to suspicious URL + updates → reject (should be spam).
- LinkedIn connection request / invitation + updates → reject (should be social_media).
- GDPR deletion request or policy notice + updates → accept (correctly fits updates).
- Thread trending notification + verify_code → reject (should be forum).
- Promotional coaching offer + spam → reject (should be promotions unless clearly deceptive/fraudulent).

Return only:
- accepted: true or false
- reason: brief explanation

Email Details to Judge:
Subject: {subject}
Body: {body}
Proposed Category: {proposed_category}
