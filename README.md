# YouTube Digest

**Stop watching hour-long videos that waste your time.**

YouTube is full of valuable content, but finding what's actually relevant to *you* is exhausting. You subscribe to great channels, but most videos don't apply to your specific situation. You either waste hours watching everything, or miss the gems buried in content that looked irrelevant.

YouTube Digest solves this by filtering videos through your personal context. Tell it who you are, what you're working on, and what you care about - and it tells you exactly which videos are worth your time.

A video about "enterprise sales strategies" might be:
- **High** relevance for someone building a sales team
- **Skip** for someone at a product-led startup

Same video. Different context. Different rating.

The **Skip** rating is the real value - it saves you an hour by confidently telling you what you *don't* need to watch.

![Example digest email](screenshot.png)

## How it works

1. Monitors YouTube channels you choose via RSS
2. Fetches transcripts for new videos
3. Analyses each transcript against your personal context
4. Emails you a daily digest with ratings: **High** / **Medium** / **Low** / **Skip**

Each video gets a summary and explanation of why it is or isn't relevant to your specific situation.

## Setup

```bash
git clone https://github.com/joewapshott/youtube-digest.git
cd youtube-digest

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python setup.py
```

The setup wizard will guide you through:
1. Creating your personal context file
2. Configuring API keys
3. Validating your setup

### API keys you'll need

| Service | Purpose | Free tier |
|---------|---------|-----------|
| [Anthropic](https://console.anthropic.com) or [OpenAI](https://platform.openai.com) | AI analysis | Pay-as-you-go |
| [Supadata](https://supadata.ai) | YouTube transcripts | 200/month |
| [Resend](https://resend.com) | Email delivery | 3,000/month |

### Your context

The magic is in `context.md`. The more specific you are, the better the filtering:

```markdown
## Role and situation
- Senior PM at a Series B fintech, 2 years in role
- Leading a team of 2 PMs, trying to get promoted to Lead

## What I'm working on
- Shipping a new pricing tier in Q1
- Reducing time-to-value for new users

## What I care about learning
- Pricing strategy for consumer products
- Building and leading small product teams

## What's NOT useful for me
- Enterprise sales (we're product-led)
- Fundraising content (not my domain)
```

### Choose your channels

Edit `channels.yml`:

```yaml
channels:
  - name: "Lenny's Podcast"
    id: UC6t1O76G0jYXOAoYCm153dA

  - name: "My Favourite Channel"
    id: UCxxxxxxxxxxxxxxxxxxxxxxx
```

To find a channel ID: go to the channel page, view source, search for `channel_id`.

## Running

```bash
python main.py --demo      # Test with sample data (just needs AI key)
python main.py --dry-run   # Process real videos, print to console
python main.py             # Full run - process and send email
```

## Deployment

### GitHub Actions (recommended)

The repo includes a workflow that runs daily at 8am UTC.

1. Fork this repo
2. Add secrets in Settings → Secrets → Actions:
   - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
   - `SUPADATA_API_KEY`
   - `RESEND_API_KEY`
   - `EMAIL_FROM`
   - `EMAIL_TO`
3. Enable the workflow

## Costs

| Model | Cost per video | 10 videos/day |
|-------|---------------|---------------|
| Claude Sonnet (default) | ~£0.01-0.03 | ~£10/month |
| GPT-4o | ~£0.01-0.02 | ~£8/month |

Supadata and Resend free tiers are plenty for personal use.

## Troubleshooting

**No transcript available:** Some videos don't have transcripts (disabled by creator, or new upload). The digest will note these.

**Rate limits:** If processing many videos, the workflow may hit API limits. Reduce the number of channels or run at off-peak times.

## Credits

Inspired by [Jordi Visser's workflow](https://www.youtube.com/@JordiVisser) for using AI to filter content by relevance.

## Licence

MIT
