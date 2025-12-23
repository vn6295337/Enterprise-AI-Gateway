# Enterprise AI Gateway - Business User Guide

**One gateway. Multiple AI providers. Zero downtime.**

---

## What It Does

The Enterprise AI Gateway sits between your applications and AI providers (Google Gemini, Groq, OpenRouter). Instead of connecting directly to one provider and hoping it stays up, requests go through this gateway which automatically switches to a backup if one fails.

Think of it like a phone system that automatically redirects calls to another line when the first one is busy.

---

## Business Benefits

| Challenge | Solution |
|-----------|----------|
| AI provider goes down | Automatically switches to backup provider |
| Sensitive data in prompts | Blocks emails, credit cards, SSNs before they reach AI |
| Prompt manipulation attempts | Detects tricks like "ignore your rules" and blocks them |
| Unpredictable AI costs | Tracks every request and estimates cost |
| No visibility into AI usage | Live dashboard showing all activity |

**Key Metrics:** 99.8% uptime | 87-200ms response (under 1/5 of a second) | Zero infrastructure cost

---

## User Guide (Hugging Face Spaces)

### Step 1: Open the Demo

Go to: **[huggingface.co/spaces/vn6295337/Enterprise-AI-Gateway](https://huggingface.co/spaces/vn6295337/Enterprise-AI-Gateway)**

### Step 2: Try the Pre-built Scenarios

Click any button to see the gateway in action:

| Button | What It Shows |
|--------|---------------|
| **Prove Uptime** | First provider "fails" → gateway automatically uses backup |
| **Protect Security** | Someone tries to trick the AI → gateway blocks it |
| **Optimize Costs** | Gateway picks the cheapest provider for simple tasks |
| **Measure Speed** | Shows how fast responses come back |

### Step 3: Submit Your Own Prompt

1. **Enter your question** in the text box (e.g., "Explain quantum computing")
2. **API Key** is pre-filled for the demo (like a password that grants access)
3. **Adjust settings** (optional):
   - **Max Tokens**: How long the AI response can be. Higher = longer answers. (default: 256 ≈ 1 paragraph)
   - **Temperature**: How creative vs predictable the AI is. 0 = factual/consistent, 2 = creative/varied. (default: 0.7 = balanced)
4. Click **Submit Prompt**
5. Watch the security checks animate (Auth → Guard → Route → Infer)
6. View the AI response with details

### Step 4: Understanding the Results

After each request, you'll see:

| Field | What It Means |
|-------|---------------|
| **Provider Used** | Which AI answered (Gemini, Groq, or OpenRouter) |
| **Latency** | Response time. 100ms = 1/10th of a second. Lower is faster. |
| **Cascade Path** | If the first provider failed, shows the backup chain used |
| **Cost Estimate** | Approximate cost of this single request (usually fractions of a cent) |

---

## Security Features Explained

| Feature | Plain English | Business Impact |
|---------|---------------|-----------------|
| **API Key** | Password required to use the system | Only your team can access |
| **Rate Limiting** | Max 10 requests per minute per user | Stops runaway costs from bugs or abuse |
| **PII Detection** | Catches personal info (emails, SSNs, credit cards) | Prevents data leaks to AI providers |
| **Injection Blocking** | Blocks tricks like "ignore your instructions" | Stops people from misusing the AI |

---

## Use Cases

| Scenario | How It Helps |
|----------|--------------|
| **Enterprise AI Access** | One secure entry point for all teams using AI |
| **Regulated Industries** | Logs every request for compliance audits |
| **Cost Management** | See exactly what AI costs across the organization |
| **Mission-Critical Apps** | If one AI provider fails, service continues |

---

## Video Walkthrough

Watch the 2-minute demo: **[Product Demo Video](http://github.com/vn6295337/Enterprise-AI-Gateway/issues/2)**

---

## Want to Deploy Your Own?

See the [Technical README](README.md) for installation instructions.
