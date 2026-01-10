# YouTube Digest

Automated daily digest of YouTube content, filtered by *your* context. Stop watching hour-long videos that aren't relevant. Get a personalised summary that tells you what's worth your time.

![Example digest email](screenshot.png)

## Try the demo (no setup required)

👉 **[Live Demo](https://youtube-digest-demo.streamlit.app)** - See how it works in 30 seconds

Paste your context, click analyse, see the magic. Your context is processed in memory only - nothing stored.

## Try it locally in 60 seconds

```bash
git clone https://github.com/joewapshott/youtube-digest.git
cd youtube-digest
pip install -r requirements.txt

# Use either Anthropic or OpenAI - whichever you have
export ANTHROPIC_API_KEY=sk-ant-...  # console.anthropic.com
# OR
export OPENAI_API_KEY=sk-...         # platform.openai.com

python main.py --demo
```

That's it. You'll see a sample analysis using sample context. No other API keys needed for the demo.

## What it does

1. Monitors YouTube channels you care about via RSS
2. Fetches transcripts for new videos
3. Analyses each transcript against your personal context (role, goals, interests)
4. Emails you a daily digest with relevance ratings: High / Medium / Low / Skip

The "Skip" rating is the real value - it saves you an hour by telling you what you don't need to watch.

## Full setup

```bash
# Clone the repo
git clone https://github.com/joewapshott/youtube-digest.git
cd youtube-digest

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up your context
cp context.example.md context.md
# Edit context.md with your situation, goals, and interests

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Test it
python main.py --dry-run
```

## Configuration

### 1. Add your context

The magic is in `context.md`. Copy `context.example.md` and fill in:

- Your role and situation
- What you're working on
- Your goals (short and long term)
- What you want to learn
- What's NOT useful for you

The more specific you are, the better the filtering. "PM at a startup" gives generic results. "Senior PM at a Series B fintech, trying to get promoted to Lead while shipping a new pricing model" gives useful results.

### 2. Set up API keys

Create a `.env` file:

```
# Use ONE of these AI providers
ANTHROPIC_API_KEY=sk-ant-api...
# OPENAI_API_KEY=sk-...

SUPADATA_API_KEY=your-supadata-key
RESEND_API_KEY=re_...
EMAIL_FROM=YouTube Digest <onboarding@resend.dev>
EMAIL_TO=your.email@example.com
```

**AI Provider** (one required):
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com) - Claude Sonnet recommended
- **OpenAI**: [platform.openai.com](https://platform.openai.com) - GPT-4o recommended

If both keys are set, Anthropic is used by default. Override with `AI_PROVIDER=openai`.

**Supadata** (required): Free transcript API that works from cloud IPs. Sign up at [supadata.ai](https://supadata.ai). Free tier: 200 requests/month.

**Resend** (required): Free email API. Sign up at [resend.com](https://resend.com). Free tier: 3,000 emails/month.

### 3. Choose your channels

Edit `config.py` to add/remove channels:

```python
CHANNELS = [
    Channel(
        name="Lenny's Podcast",
        channel_id="UC6t1O76G0jYXOAoYCm153dA"
    ),
    # Add your own...
]
```

To find a channel ID:
1. Go to the channel page on YouTube
2. View page source (Ctrl+U / Cmd+U)
3. Search for `channel_id` - you'll find `"channel_id":"UC..."`

## Running

```bash
# Demo mode - see sample output (only needs one AI API key)
python main.py --demo

# Dry run - process real videos, print to console (needs AI + Supadata keys)
python main.py --dry-run

# Full run - process videos and send email
python main.py

# Test email only
python main.py --test-email
```

## Deployment

### GitHub Actions (recommended)

Free, runs on a schedule. The repo includes `.github/workflows/digest.yml`.

1. Push to a private GitHub repo
2. Add secrets: Settings → Secrets and variables → Actions
   - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` (at least one)
   - `SUPADATA_API_KEY`
   - `RESEND_API_KEY`
   - `EMAIL_FROM`
   - `EMAIL_TO`
3. The workflow runs daily at 8am UTC

### Local cron

```bash
crontab -e
# Add:
0 8 * * * cd /path/to/youtube-digest && /path/to/venv/bin/python main.py
```

## Costs

**Claude Sonnet** (Anthropic default):
- ~£0.01-0.03 per video
- 10 videos/day ≈ £10/month

**GPT-4o** (OpenAI default):
- ~£0.01-0.02 per video
- 10 videos/day ≈ £8/month

**Claude Opus** (change `ANTHROPIC_MODEL` in config.py):
- ~£0.10-0.25 per video
- 10 videos/day ≈ £50-75/month

Supadata and Resend free tiers are plenty for personal use.

## How it works

The system prompt includes your full context from `context.md`. When the AI analyses each transcript, it's not just summarising - it's asking "does this matter for this specific person?"

A video about enterprise sales might be "High" relevance for someone building a sales team, and "Skip" for someone at a product-led company. Same video, different context, different rating.

## Troubleshooting

**No transcript available:** Some videos don't have transcripts (disabled by creator, or it's a new upload). The digest will note these.

**Shorts appearing:** Videos under 90 seconds of speech are auto-filtered, but some slip through. The analysis will typically rate them "Skip".

**Rate limits:** If processing many videos, add a delay or run at off-peak times.

## Credits

Inspired by [Jordi Visser's workflow](https://www.youtube.com/@JordiVisser) for consuming 10x more content by using AI to filter for relevance.

## Hosting the demo

The Streamlit demo (`demo_app.py`) can be hosted free on Streamlit Cloud:

1. Fork this repo
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub and select this repo
4. Set `demo_app.py` as the main file
5. Deploy

No environment variables needed - users bring their own API key.

## Licence

MIT
