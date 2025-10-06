# Using OpenRouter with AI Research Assistant

OpenRouter allows you to access multiple AI models through a single API, including models from OpenAI, Anthropic, Meta, Google, and more.

## Quick Setup

1. **Get your OpenRouter API key**
   - Visit https://openrouter.ai/keys
   - Create an account and generate an API key
   - Add credits to your account (pay-as-you-go pricing)

2. **Configure your `.env` file**
   ```bash
   # Set the provider to openrouter
   LLM_PROVIDER=openrouter

   # Add your OpenRouter API key
   OPENROUTER_API_KEY=sk-or-v1-...

   # Choose your model
   LLM_MODEL=anthropic/claude-3-5-sonnet
   ```

3. **Run the agent**
   ```bash
   uv run python main.py
   ```

## Popular Model Options

### Anthropic Claude Models
```bash
# Claude 3.5 Sonnet (Recommended - great balance of speed/quality)
LLM_MODEL=anthropic/claude-3-5-sonnet

# Claude 3 Opus (Most capable, slower)
LLM_MODEL=anthropic/claude-3-opus

# Claude 3 Haiku (Fastest, most affordable)
LLM_MODEL=anthropic/claude-3-haiku
```

### OpenAI Models via OpenRouter
```bash
# GPT-4o (Latest GPT-4 model)
LLM_MODEL=openai/gpt-4o

# GPT-4o Mini (Fast and affordable)
LLM_MODEL=openai/gpt-4o-mini

# GPT-4 Turbo
LLM_MODEL=openai/gpt-4-turbo
```

### Meta Llama Models
```bash
# Llama 3.1 405B (Most capable open model)
LLM_MODEL=meta-llama/llama-3.1-405b-instruct

# Llama 3.1 70B (Good balance)
LLM_MODEL=meta-llama/llama-3.1-70b-instruct

# Llama 3.1 8B (Fast and affordable)
LLM_MODEL=meta-llama/llama-3.1-8b-instruct
```

### Google Models
```bash
# Gemini Pro 1.5
LLM_MODEL=google/gemini-pro-1.5

# Gemini Flash 1.5 (Fast)
LLM_MODEL=google/gemini-flash-1.5
```

## Browse All Models

Visit https://openrouter.ai/models to see:
- All available models
- Pricing per million tokens
- Context windows
- Performance benchmarks

## Pricing

OpenRouter uses pay-as-you-go pricing. Examples (as of 2024):
- Claude 3.5 Sonnet: ~$3/million input tokens, ~$15/million output tokens
- GPT-4o Mini: ~$0.15/million input tokens, ~$0.60/million output tokens
- Llama 3.1 8B: ~$0.05/million input tokens, ~$0.05/million output tokens

Check current pricing at: https://openrouter.ai/models

## Benefits of OpenRouter

1. **Single API**: Access multiple providers with one integration
2. **Fallback**: Automatically fallback to alternative models if primary fails
3. **Cost Optimization**: Compare and choose most cost-effective models
4. **No Rate Limits**: Pool across multiple providers
5. **Latest Models**: Access to newest models as they're released

## Troubleshooting

### Invalid API Key Error
```
ValueError: OPENROUTER_API_KEY is required when LLM_PROVIDER=openrouter
```
**Solution**: Make sure you set `OPENROUTER_API_KEY` in your `.env` file

### Model Not Found Error
**Solution**: Check the model name format. OpenRouter models use the format: `provider/model-name`
Example: `anthropic/claude-3-5-sonnet`, not just `claude-3-5-sonnet`

### Insufficient Credits
**Solution**: Add credits to your OpenRouter account at https://openrouter.ai/credits

## Example `.env` Configuration

```bash
# LLM Provider
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-12....
LLM_MODEL=anthropic/claude-3-5-sonnet
LLM_TEMPERATURE=0.7

# Required APIs
TAVILY_API_KEY=tvly-...

# Optional
LANGSMITH_API_KEY=ls-...
```

## Switching Back to OpenAI

To switch back to using OpenAI directly:

```bash
# In your .env file
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```
