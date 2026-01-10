"""
YouTube Digest Demo

A simple Streamlit app to demonstrate the YouTube Digest concept.
Users can paste their context and see how Claude or GPT would analyse a sample video.

Run locally: streamlit run demo_app.py
Deploy free: streamlit.io/cloud
"""

import anthropic
import openai
import streamlit as st

# Sample transcript (same as sample_transcript.txt)
SAMPLE_TRANSCRIPT = """Welcome back to the show. Today we're talking about something that I think is really underrated in product management, which is the skill of developing product intuition.

So I've been thinking about this a lot lately because I see so many PMs who are really good at the process side of things - they can run a sprint, they can write a spec, they can manage stakeholders - but they struggle with the fundamental question of "what should we build?"

And I think the reason is that product intuition isn't taught. It's this thing that people assume you either have or you don't. But I actually think it's a skill that can be developed.

So let me share three ways that I've seen great PMs develop their product intuition.

The first one is customer exposure. And I don't mean reading research reports or looking at dashboards. I mean actually talking to customers regularly. The best PMs I know spend at least 4 hours a week in direct customer contact. They're doing support shifts, they're joining sales calls, they're running user interviews.

And here's the key insight: they're not doing this to validate specific ideas. They're doing it to build a mental model of the customer. They want to be able to predict how a customer will react to something before they even test it.

The second way is studying other products obsessively. Great PMs are constantly signing up for new products, going through onboarding flows, analysing pricing pages. They're building a library in their head of patterns that work and patterns that don't.

I talked to a PM at Stripe recently who told me she signs up for at least 5 new products every week. Not because she needs them, but because she's studying them. She's looking at how they handle activation, how they communicate value, how they structure their pricing.

The third way is making bets and tracking them. This is something I learned from a product leader at Airbnb. Every week, before they look at the data, they write down what they think happened and why. Then they compare their predictions to reality.

Over time, this builds calibration. You start to notice where your intuition is strong and where it's weak. And that awareness is actually more valuable than being right all the time.

So to summarise: customer exposure, studying other products, and making explicit predictions. These are the three ways I've seen PMs develop genuine product intuition.

Now let me take some questions from the audience..."""

SAMPLE_CONTEXT = """## Role and situation

- **Current role:** Senior PM at a Series B fintech (60 people), 2 years in role
- **Team:** Leading 1 other PM, working closely with 2 designers
- **Company context:** B2C payments app, profitable but growth slowing

## What I'm working on

- Shipping a new pricing tier in Q1 to improve ARPU
- Reducing time-to-value for new users (activation is our weak spot)
- Building the case for a proper experimentation platform

## Career goals

- **Short-term:** Get promoted to Lead PM by end of year
- **Longer-term:** Become a product leader at a company I believe in

## What I care about learning

- How to develop better product intuition
- Pricing strategy for consumer products
- Building and leading small product teams
- Using AI tools to ship faster as a PM

## What's NOT useful for me

- Enterprise sales motions (we're consumer-focused)
- Fundraising content (not my domain)
- Very early stage startup advice (we're past that)"""


def get_system_prompt(user_context: str) -> str:
    return f"""You are a research assistant that analyses video content for relevance to a specific person's situation and goals.

Your job is to be ruthlessly honest about what's worth their time. A "Skip" rating is valuable - it saves them an hour. Don't inflate relevance to seem helpful.

Here is the context about the person you're helping:

---
{user_context}
---

Use this context to judge relevance. Generic advice that could apply to anyone is LOW relevance. Content that specifically connects to their situation, goals, or challenges is HIGH relevance."""


def get_analysis_prompt(title: str, channel: str) -> str:
    return f"""Analyse this video transcript.

**Video:** "{title}"
**Channel:** {channel}

---

**Relevance:** [High / Medium / Low / Skip]
Be honest. If this doesn't connect to their situation, say "Skip". That's a useful output - it saves them 60 minutes.

**What it's actually about:** 2-3 sentences summarising the video's core content. Always include this, even for Skip - they want to know what they're not missing.

**Why this rating:** One sentence explaining why it is or isn't relevant to their specific context.

**If Medium or High relevance, also include:**

**Key insights:** What specifically applies to their situation? Reference their goals, challenges, or context directly.

**The one thing:** If they can only take one insight from this video, what is it and why does it matter for their specific situation?

---

Be direct and specific. Generic advice is noise. Only surface what genuinely connects to their context.

---

TRANSCRIPT:

"""


def analyse_with_anthropic(api_key: str, context: str, transcript: str) -> str:
    """Send transcript to Claude for analysis."""
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        system=get_system_prompt(context),
        messages=[
            {
                "role": "user",
                "content": get_analysis_prompt(
                    "How to develop product intuition", "Lenny's Podcast"
                )
                + transcript,
            }
        ],
    )

    return message.content[0].text


def analyse_with_openai(api_key: str, context: str, transcript: str) -> str:
    """Send transcript to GPT for analysis."""
    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        messages=[
            {"role": "system", "content": get_system_prompt(context)},
            {
                "role": "user",
                "content": get_analysis_prompt(
                    "How to develop product intuition", "Lenny's Podcast"
                )
                + transcript,
            },
        ],
    )

    return response.choices[0].message.content


# Streamlit UI
st.set_page_config(page_title="YouTube Digest Demo", page_icon="📺", layout="wide")

st.title("📺 YouTube Digest Demo")
st.markdown(
    """
See how YouTube Digest filters content based on *your* context.

This demo analyses a sample video transcript against your situation and goals,
showing you exactly what a daily digest would look like.
"""
)

# Privacy notice
st.info(
    """
🔒 **Privacy:** Your context is processed in memory only and sent directly to the AI API.
Nothing is stored, logged, or saved. You provide your own API key.
"""
)

# Two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Your API Key")

    provider = st.radio(
        "Choose provider", ["Anthropic (Claude)", "OpenAI (GPT-4o)"], horizontal=True
    )

    if provider == "Anthropic (Claude)":
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-...",
            help="Get one at console.anthropic.com",
        )
    else:
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Get one at platform.openai.com",
        )

    st.subheader("Your Context")
    st.markdown("*Edit this to match your situation:*")
    context = st.text_area(
        "Context", value=SAMPLE_CONTEXT, height=400, label_visibility="collapsed"
    )

with col2:
    st.subheader("Sample Video")
    st.markdown(
        """
    **"How to develop product intuition"**
    *Lenny's Podcast*
    """
    )

    with st.expander("View transcript"):
        st.text(SAMPLE_TRANSCRIPT)

    st.subheader("Analysis")

    if st.button("🔍 Analyse Video", type="primary", use_container_width=True):
        if not api_key:
            st.error(
                f"Please enter your {'Anthropic' if 'Anthropic' in provider else 'OpenAI'} API key"
            )
        elif not context.strip():
            st.error("Please enter your context")
        else:
            with st.spinner("Analysing..."):
                try:
                    if "Anthropic" in provider:
                        result = analyse_with_anthropic(
                            api_key, context, SAMPLE_TRANSCRIPT
                        )
                    else:
                        result = analyse_with_openai(
                            api_key, context, SAMPLE_TRANSCRIPT
                        )
                    st.markdown(result)
                except anthropic.AuthenticationError:
                    st.error(
                        "Invalid Anthropic API key. Check your key at console.anthropic.com"
                    )
                except openai.AuthenticationError:
                    st.error(
                        "Invalid OpenAI API key. Check your key at platform.openai.com"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.markdown(
            "*Click 'Analyse Video' to see how this video would be rated for you.*"
        )

st.divider()

st.markdown(
    """
### Want this as a daily email?

YouTube Digest monitors your favourite channels and sends you a personalised digest every morning.

**[Get the code on GitHub →](https://github.com/joewapshott/youtube-digest)**

Setup takes 10 minutes. Runs free on GitHub Actions.
"""
)
