# YouTube Daily Curator

## Overview

You're a Product Manager who subscribes to Lenny's Podcast, The Product Podcast, Product Growth and a dozen other sources to keep up to date with the industry.

Or an Engineer who's trying to stay on top of all the latest developments with AI, and which ones you should / shouldn't employ.

You know there's content in there that could help you work better, stay current, or get to the next level. You just don't know which specific videos, when each of the channels is pushing out 3 a week.

**What is it**

This isn't a youtube summariser. There's hundreds of those.

This tool is a filter that finds what's relevant and a translator that turns generic advice into specific action.

It monitors your channels and sends a daily email rating each video against your context, so you know what to watch and what to skip.

![Example digest email](screenshot.png)

## Why I built this

As a Head of Product at a Series A startup, I'm subscribed to 15+ channels. Lenny, SVPG, First Round, AI-focused podcasts. All good content. But I kept having the same two experiences: watching something for an hour then realising it was aimed at later stage or larger companies, or skipping something because the title sounded generic, only to hear my product colleague reference the exact content a week later.

Now I get a short daily digest. It tells me what to skip with confidence, what to watch, and, for the stuff that matters, what I should actually do with the information given my current goals.

I built this for myself, but it works better than expected, so I'm sharing it.

## Who this is for

PMs and engineers who want to be intentional about what they consume. You know there's good content out there, and you need something that connects it to your actual situation rather than just summarising it.

The tool is completely topic agnostic and learns from your specific context. The only important pre-work is to ensure your LLM of choice (connected to Anthropic/OpenAI currently) has context about your work and what you're trying to achieve.

## How it works

1. Monitors YouTube channels you choose
2. Fetches transcripts for any new videos in last 24 hours
3. Analyses each against your personal context (role, goals, current problems)
4. Emails you a daily digest with ratings and personalised takeaways. If no videos from the channels you've chosen, you won't get an email, no need to clutter an already busy inbox.

For each video you get:
- A relevance rating: **High** / **Medium** / **Low** / **Skip**
- A short summary
- For relevant videos: the "so what" - how this connects to your goals and what you might do with it

## The "Skip" rating is the point

Knowing with confidence that a video isn't relevant to your situation is just as valuable as finding one that is. No more wondering if you're missing something important.

A video about "building executive presence" might be:
- **Skip** for an engineer who's happy as an IC
- **High** for a PM trying to get promoted, with specific suggestions on how to apply the advice in their upcoming strategy presentation

Same video. Different context. Different rating. Different action.

## Your context file

The value comes from `context.md`. This is where you tell it who you are, what you're working on, and what you're trying to learn.

If you already have work context baked into Claude or ChatGPT, you know how much better AI gets when it understands your situation. Same principle here. The richer your context, the better the filtering, and the better the translation from "generic advice" to "here's what this means for you."

### The quick (and best) way: ask your LLM to generate it

If you already have context about your work in Claude or ChatGPT, paste this prompt:

```
Generate a context.md file for a YouTube content curator tool. The file should help an AI judge whether videos are relevant to my situation and translate useful content into specific actions I can take.

Include these sections:
- Role and situation (job title, company stage, team size, time in role)
- What I'm working on right now (current projects, challenges, deadlines)
- What I'm actively trying to learn (skills, knowledge gaps, career goals)
- What's NOT relevant to me right now (topics to filter out)

Be specific. Use real details from what you know about my work. The more specific the context, the better the recommendations.
```

Review what it generates, adjust anything that's wrong or missing, and save it as `context.md`.

### What makes a good context file

If you're writing it yourself, keep these principles in mind:

- **Be specific about your situation.** "PM at a startup" is weak. "Senior PM at a Series B fintech, 3 years in role, managing one junior PM, targeting Head of Product in 12 months" gives the AI something to work with.
- **Include what you're working on *right now*.** Not your job description, your actual current projects and problems. This changes over time, and your context file should too.
- **Be clear about what to filter out.** The "not relevant" section is just as important as what you want. It stops the AI from recommending content that's technically good but not useful for your situation.

### Example: Senior PM aiming for Head of Product

```markdown
## Role and situation
- Senior PM at a Series B fintech (£30m ARR, 120 people)
- 3 years in role, managing one junior PM
- Targeting Head of Product in the next 12-18 months

## What I'm working on right now
- Leading the company's biggest launch of the year (new pricing tier)
- Building the case for expanding my team to 3 PMs
- Trying to get better at influencing without authority

## What I'm actively trying to learn
- Operating at a strategic level (less feature, more outcome)
- Building and presenting product strategy to execs
- Managing and developing other PMs

## What's NOT relevant to me right now
- Founding a startup (I'm not leaving)
- Enterprise sales (we're product-led growth)
- Early-career PM advice
```

With this context, a video about "running a product strategy offsite" doesn't just get summarised. It gets rated High, and the digest explains how you could adapt the framework for your pricing tier launch.

### Example: Engineer stepping into tech lead

```markdown
## Role and situation
- Senior Software Engineer, 2 years at a mid-stage startup
- Just asked to lead a team of 4 for a new initiative
- First leadership role, still expected to ship code

## What I'm working on right now
- Defining architecture for a new service
- Learning to delegate while still contributing
- Running my first sprint planning sessions

## What I'm actively trying to learn
- Technical leadership and system design at scale
- Giving code review feedback without being a bottleneck
- Staying current with AI/ML developments
- Running effective 1:1s

## What's NOT relevant to me right now
- Management-only content (I'm still coding 50%)
- Startup founding / fundraising
- Frontend frameworks (I'm backend focused)
```

With this context, a video about "delegation for engineering managers" gets rated Medium (you're not fully a manager yet) with specific notes on which parts apply to your hybrid IC/lead role.

## Requirements

- **Python 3.9 or higher** (uses modern type hints like `list[str]`)
- API keys for AI analysis, transcripts, and email (see below)

## Setup

```bash
git clone https://github.com/Joeckick/youtube-daily-curator.git
cd youtube-daily-curator

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python setup.py
```

The setup wizard guides you through creating your context file and configuring API keys.

### API keys you'll need

| Service | Purpose | Free tier |
|---------|---------|-----------|
| [Anthropic](https://console.anthropic.com) or [OpenAI](https://platform.openai.com) | AI analysis | Pay-as-you-go |
| [Supadata](https://supadata.ai) | YouTube transcripts | 200/month |
| [Resend](https://resend.com) | Email delivery | 3,000/month |

### Choose your channels

Edit `channels.yml` with 3-10 channels. More than that and you'll likely get diminishing returns (and higher API costs).

```yaml
channels:
  - name: "Lenny's Podcast"
    id: UC6t1O76G0jYXOAoYCm153dA
```

**Some suggestions to get you started:**

For product managers:
- Lenny's Podcast (@LennysPodcast)
- Product School (@ProductSchoolSF)
- Mind the Product (@MindTheProduct)
- The Product Podcast (@TheProductPodcast)

For engineers:
- Pragmatic Engineer (@mrgergelyorosz)
- LeadDev (@TheLeadDev)
- Continuous Delivery (@ContinuousDelivery)
- ThePrimeagen (@ThePrimeTimeagen)

**To find a channel ID:** Go to the channel page, view source, and search for `channel_id`. Or use a tool like [commentpicker.com/youtube-channel-id.php](https://commentpicker.com/youtube-channel-id.php) - paste the channel URL and it gives you the ID.

## Running

```bash
# First, verify your configuration
python main.py --dry-run    # Process videos, print to console (no email sent)

# Once verified, run the full digest
python main.py              # Full run: process videos and send email

# Or test email delivery only
python main.py --test-email # Send a test email to verify email config
```

**Note:** `--dry-run` still requires valid API keys (ANTHROPIC/OPENAI and SUPADATA) to analyze videos. It only skips sending the email.

## Deployment (one-time setup, daily value)

The repo includes a GitHub Actions workflow that runs daily at 8am UTC.

1. Fork this repo
2. Add secrets in Settings → Secrets → Actions:
   - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
   - `SUPADATA_API_KEY`
   - `RESEND_API_KEY`
   - `EMAIL_FROM`
   - `EMAIL_TO`
3. Enable the workflow

That's it. You'll get your first digest tomorrow morning.

## Costs

| Model | Cost per video | 10 videos/day |
|-------|----------------|---------------|
| Claude Sonnet (default) | ~£0.01-0.03 | ~£10/month |
| GPT-4o | ~£0.01-0.02 | ~£8/month |

Supadata and Resend free tiers are plenty for personal use.

## Development

To run tests and linting:

```bash
pip install -r requirements-dev.txt
pytest                    # Run tests
ruff check .              # Linting
black --check .           # Formatting
```

## Troubleshooting

**No transcript available:** Some videos don't have transcripts (disabled by creator, or very new). The digest notes these.

**Rate limits:** Processing many videos may hit API limits. Reduce channels or run at off-peak times.

## Ready?

Fork this repo, spend 10 minutes on your context file, and start getting content that's actually relevant to you.

## Licence

MIT
