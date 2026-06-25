EMAIL_CLASSIFIER_PROMPT = """You are an expert email classification system.
Analyze the email below and classify it into exactly one of the target categories:
- forum (discussion boards, mailing lists, forum updates, online groups)
- verify_code (one-time verification codes, security codes, login OTPs, password reset links)
- promotions (marketing offers, sales, ads, discount coupons, commercial newsletters)
- social_media (notifications and updates from social networks, direct messages from chats)
- spam (unsolicited junk, commercial spam, scam attempts, phishing emails)
- updates (transaction receipts, order confirmations, shipping updates, bills, system/account notifications)

Email Details:
Subject: {subject}
Body: {body}"""
