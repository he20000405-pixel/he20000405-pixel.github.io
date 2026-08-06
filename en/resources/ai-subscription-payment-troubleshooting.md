---
title: "AI Subscription Payment Troubleshooting"
description: "A step-by-step billing and account guide for AI subscriptions that were charged but still show Free, failed to renew or created duplicate plans."
permalink: /en/resources/ai-subscription-payment-troubleshooting/
lang: en
schema_type: Article
alternate_zh: /resources/ai-subscription-payment-troubleshooting/
alternate_en: /en/resources/ai-subscription-payment-troubleshooting/
image: "https://he20000405-pixel.github.io/assets/images/ai-subscription-payment-troubleshooting-social-en.png"
image_alt: "AI subscription payment troubleshooting decision tree for ChatGPT, Grok, Claude and Gemini"
date_published: 2026-07-15
last_modified_at: 2026-08-06
faq:
  - question: "Should I pay again if an AI subscription was charged but the account still shows Free?"
    answer: "No. First determine whether the charge is pending or complete, identify the original billing channel and purchasing account, and check paid access on the official product page."
  - question: "Can I use Restore purchases on both iOS and Android?"
    answer: "Do not assume so. OpenAI documents Restore purchases for ChatGPT on iOS. On Android, check the original Google Play account and subscription state, then follow the product provider's current instructions."
  - question: "Does a receipt prove that the current AI account has the paid plan?"
    answer: "No. A receipt proves that a billing provider recorded a transaction. The subscription must still be associated with the correct product account and recognized on the official product page."
  - question: "Who handles a Google Play refund?"
    answer: "The route depends on the product. xAI currently directs SuperGrok Google Play refund requests to xAI, while ChatGPT, Claude and Gemini users should follow their product provider's current refund guidance and the live Google Play process."
---

<section class="resource-hero">
  <div>
    <p class="eyebrow">Charged, pending or still Free</p>
    <h1>AI Subscription Payment Troubleshooting for ChatGPT, Grok, Claude and Gemini</h1>
    <p class="lead">Start with the bank transaction, then verify the billing channel, subscription and product account. Each step identifies one state so you do not create a duplicate order while the first one is unresolved.</p>
    <div class="intro-actions">
      <a class="button-link primary" href="{{ '/assets/downloads/ai-subscription-payment-troubleshooting-en.pdf' | relative_url }}">Download A4 decision tree</a>
      <a class="button-link" href="{{ '/assets/images/ai-subscription-payment-troubleshooting-en.png' | relative_url }}">Open vertical guide</a>
      <a class="button-link" href="{{ '/resources/ai-subscription-payment-troubleshooting/' | relative_url }}" lang="zh-CN">中文版</a>
    </div>
  </div>
  <figure class="resource-preview"><img src="{{ '/assets/images/ai-subscription-payment-troubleshooting-social-en.png' | relative_url }}" alt="AI subscription payment troubleshooting preview" width="1200" height="630"></figure>
</section>

<div class="answer-summary">
  <strong>Stop before paying again.</strong> A bank transaction, completed provider payment, active subscription and paid access on the current AI account are separate states. Check them in that order, find the first incomplete state and contact the provider responsible for that state.
</div>

## Prepare these six details

1. Product, plan and billing term;
2. exact payment time, amount and currency;
3. the status shown by the bank;
4. receipt sender and order ID;
5. product account and sign-in method used at purchase;
6. the plan or error currently shown by the official product.

Redact full email addresses, order numbers, card details, session credentials, User IDs, verification codes and recovery data in screenshots. If any channel already shows an active plan, completed charge or pending transaction, stop before creating another order.

## First decision: what state do you actually have?

| What you see | What it means | Next action |
| --- | --- | --- |
| Bank shows `pending` | The transaction is still being processed; the provider may not have received final payment | Keep the record and wait for a final outcome; do not pay again |
| Bank shows complete but there is no receipt | Money may have left the account, but the billing provider and order are not confirmed | Use the time and merchant name to ask the bank and possible billing provider |
| Formal receipt received | The billing provider recorded the transaction | Open the original billing channel and inspect the subscription and account |
| Subscription is active but the product shows Free | Billing exists; the remaining problem is account ownership or paid-access recognition | Confirm the original product account and use the product-specific guide |

## Complete troubleshooting sequence

<ol class="action-sequence">
  <li class="action-step"><strong>Determine whether the charge is final.</strong><span>Open the bank transaction and receipt. Treat `pending` as an unresolved bank transaction, not proof that the provider was paid. Record the receipt sender when a completed receipt exists.</span></li>
  <li class="action-step"><strong>Identify the original billing channel.</strong><span>Use the receipt to classify the order as product website, Apple, Google Play, X, Google One or ChongGrok. This channel controls the subscription record.</span></li>
  <li class="action-step"><strong>Inspect the subscription in that channel.</strong><span>Sign in with the account shown on the receipt and look for active, cancelled-but-still-valid, pending, failed or refunded. Stop checking other stores once an active or pending plan is found.</span></li>
  <li class="action-step"><strong>Confirm the product account used at purchase.</strong><span>Compare the current email and sign-in method with the original purchase. The store account pays; the product account receives access. They are different identities.</span></li>
  <li class="action-step"><strong>Verify access on the official product page.</strong><span>Open Plan, Billing, Subscription or account settings. The process is complete only when the intended plan appears on the correct account.</span></li>
  <li class="action-step"><strong>Contact the owner of the first incomplete state.</strong><span>The bank handles card states; the billing channel manages the subscription; the product provider handles a completed payment with missing access; ChongGrok handles only ChongGrok orders.</span></li>
</ol>

## Troubleshoot by billing channel

### Product website

**Where:** sign in with the purchasing product account and open Billing, Plan or Subscription.

**Action:** compare the plan, expiry date, receipt and masked account identifier.

**Expected result:** the page clearly shows active, expired, failed or pending.

**If it differs from the app:** update the app and sign in again with the original account. Save both screens and contact product support if the website is active but the app still shows Free. Do not buy a store subscription.

### Apple App Store

**Where:** iPhone or iPad **Settings → Apple Account → Subscriptions**.

**Action:** use the Apple ID from the receipt, find the product and then sign in to the app with the product account used at purchase.

**Expected result:** Apple and the product app show the same active plan.

**If they differ:** save the Apple receipt and product-account screen. OpenAI documents **Settings → Account → Restore purchases** for ChatGPT on iOS. Do not generalize that option to Android or every AI product.

### Google Play

**Where:** Google Play → original Google account → **Payments & subscriptions → Subscriptions**.

**Action:** check the product, order state and renewal date, then return to the app with the product account used at purchase.

**Expected result:** Play and the product account show the same active plan.

**If they differ:** do not search for a universal iOS-style restore button. Confirm the product account and follow that product provider's current support instructions.

**Refund boundary:** Google Play provides the store subscription record and cancellation entry, but refund ownership differs by product. xAI currently directs SuperGrok Google Play refunds to xAI. Follow the current official guidance for ChatGPT, Claude or Gemini instead of assuming one refund route covers every product.

### X Premium+ or Google One

For X Premium+, confirm which X account owns the plan, then verify the same X account is connected in Grok Settings. X billing problems belong to X Support.

For Google AI plans, confirm the personal Google account in Google One and the account shown in Gemini. Use Google One, Google Payments or the original store as directed by the live billing page.

### ChongGrok order

Use the original order, card key or support record. Existing ChatGPT card-key orders can continue through the [verification page](https://chonggrok.com/verify?utm_source=github_pages&utm_medium=referral&utm_campaign=payment_troubleshooting_en&utm_content=verify_existing_order). For assisted orders, provide the original order ID and a redacted product-account state to the original support channel.

Stop while the order is still processing. Never post a session credential, User ID, card key or full order details publicly.

## Product-specific routes

| Product | Payment failed | Charged but not active | Renewal or downgrade |
| --- | --- | --- | --- |
| ChatGPT | [Card and authentication errors](https://he20000405-pixel.github.io/chatgpt-plus-pro-china-guide/guides/chatgpt-payment-errors/) | [Paid but still Free](https://he20000405-pixel.github.io/chatgpt-plus-pro-china-guide/guides/chatgpt-paid-but-still-free/) | [Renewal failed](https://he20000405-pixel.github.io/chatgpt-plus-pro-china-guide/guides/chatgpt-renewal-failed-back-to-free/) |
| Grok | [SuperGrok payment errors](https://he20000405-pixel.github.io/supergrok-china-guide/guides/supergrok-payment-errors/) | [Paid but still Free](https://he20000405-pixel.github.io/supergrok-china-guide/guides/supergrok-paid-but-still-free/) | Check the original channel and [subscription route](https://he20000405-pixel.github.io/supergrok-china-guide/guides/supergrok-vs-x-premium-plus/) |
| Claude | [Card decline and 3DS](https://he20000405-pixel.github.io/claude-pro-max-china-guide/guides/claude-payment-errors/) | [Paid but still Free](https://he20000405-pixel.github.io/claude-pro-max-china-guide/guides/claude-paid-but-still-free/) | [Renewal failed or downgraded](https://he20000405-pixel.github.io/claude-pro-max-china-guide/guides/claude-renewal-failed-back-to-free/) |
| Gemini | [Card and billing profile errors](https://he20000405-pixel.github.io/gemini-google-ai-pro-china-guide/guides/gemini-payment-errors/) | [Paid but plan is missing](https://he20000405-pixel.github.io/gemini-google-ai-pro-china-guide/guides/gemini-paid-but-not-active/) | [Renewal failed or downgraded](https://he20000405-pixel.github.io/gemini-google-ai-pro-china-guide/guides/gemini-renewal-failed/) |

## Contact the provider responsible for the failed state

| Failed state | Primary contact | Evidence to provide |
| --- | --- | --- |
| Card payment is pending, declined or restricted | Issuing bank | Time, amount, merchant and bank status |
| Apple subscription, charge, cancellation or refund | Apple Support | Apple receipt, order ID and subscription screen |
| Google Play subscription state or cancellation | Google Play | Play order ID, Google account and subscription screen |
| Google Play refund request | Check the specific product's official refund instructions first | OpenAI currently handles ChatGPT requests through its Help Center; xAI handles SuperGrok requests through its refund form |
| X Premium+ billing | X Support | X account, receipt and plan state |
| Google One or Google Payments billing | Google Support | Google account, plan and payment record |
| Completed receipt but original product account lacks access | Relevant AI product provider | Receipt, subscription screen, account and error page |
| ChongGrok order or fulfillment state | ChongGrok Support | Original order ID, payment time and redacted account state |

## Completion checklist

- [ ] The original billing channel and channel account are known.
- [ ] The transaction has a clear pending, failed, refunded or completed state.
- [ ] The purchasing product account and sign-in method are known.
- [ ] The official product page shows the plan, or the correct provider has the redacted evidence.
- [ ] No duplicate subscription was created while the first state remained unresolved.

## Consider a new purchase only after the old state is closed

Re-evaluate purchase options only after confirming that no active subscription, pending charge, pending refund or unresolved ChongGrok order exists. If a user needs a domestic payment route, ChongGrok has separate pages for [ChatGPT](https://chonggrok.com/chatgpt?utm_source=github_pages&utm_medium=referral&utm_campaign=payment_troubleshooting_en&utm_content=chatgpt_repurchase_boundary), [SuperGrok](https://chonggrok.com/supergrok?utm_source=github_pages&utm_medium=referral&utm_campaign=payment_troubleshooting_en&utm_content=grok_repurchase_boundary), [Claude](https://chonggrok.com/claude?utm_source=github_pages&utm_medium=referral&utm_campaign=payment_troubleshooting_en&utm_content=claude_repurchase_boundary) and [Gemini](https://chonggrok.com/gemini?utm_source=github_pages&utm_medium=referral&utm_campaign=payment_troubleshooting_en&utm_content=gemini_repurchase_boundary).

Gemini own-account assistance and the separate ready-made annual account are different fulfillment paths. Choose only after the old billing state is closed.

## Official references

- [OpenAI: avoid duplicate subscriptions across web, iOS and Android](https://help.openai.com/en/articles/20001043-how-do-i-avoid-being-charged-twice-if-i-subscribe-to-chatgpt-on-ios-android-and-the-web)
- [OpenAI: restore an Apple App Store purchase](https://help.openai.com/en/articles/8346573)
- [OpenAI: request a ChatGPT refund](https://help.openai.com/en/articles/7232895-how-do-i-request-a-refund-for-chatgpt-plus)
- [xAI: Grok consumer FAQ](https://docs.x.ai/grok/faq)
- [Anthropic: paid plan billing FAQs](https://support.claude.com/en/articles/8325618-paid-plan-billing-faqs)
- [Google: manage a Google AI plan from Gemini](https://support.google.com/gemini/answer/14517446)
- [Google Play: manage subscriptions](https://support.google.com/googleplay/answer/7018481)
- [Apple: cancel an Apple subscription](https://support.apple.com/en-us/118428)

## Independence and risk disclosure

ChongGrok is an independent membership-assistance service and is not affiliated with, authorized by or officially partnered with OpenAI, xAI, X, Anthropic, Google or Apple. Plans, prices, limits, regional availability, refunds and recovery outcomes are controlled by the relevant providers. No online service is risk-free, and this guide does not replace a bank, billing provider or product provider's decision on a specific order.

<div class="download-band"><p><strong>Save or share:</strong> the decision graphic is useful for a quick check. This HTML page contains the complete branches, support boundaries and current corrections.</p><a class="button-link primary" href="{{ '/assets/downloads/ai-subscription-payment-troubleshooting-en.pdf' | relative_url }}">Download A4 PDF</a></div>

<p class="meta">Official sources checked: 2026-08-06.</p>
