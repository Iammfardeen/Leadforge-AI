"""
WhatsApp message generation.

Builds a personalized outreach message via Ollama, varying tone (professional /
friendly / luxury), length (short / long), and language (English / Hindi).
Falls back to a deterministic, non-AI template if Ollama is unreachable, so
a temporarily-down local model doesn't block the whole feature — the
person can still get a usable starting message and edit it by hand.

This module NEVER sends anything anywhere. It only returns plain text for
the frontend's Copy button. There is intentionally no WhatsApp Business
API client, no webhook, no outbound call of any kind here — by design,
per the product brief.
"""
from app.services.ollama_client import OllamaError, generate

TONE_GUIDANCE = {
    "professional": "Professional and respectful, like a consultant reaching out to a potential client. Confident but not pushy.",
    "friendly": "Warm and conversational, like a friendly local recommending a service. Casual but still credible.",
    "luxury": "Polished and exclusive, like a premium boutique agency. Understated confidence, no slang, no exclamation marks.",
}

LENGTH_GUIDANCE = {
    "short": "3-4 sentences maximum. Get straight to the point.",
    "long": "6-9 sentences. Add more context about the specific weaknesses noticed and what could be improved, while staying focused on this one business.",
}

LANGUAGE_GUIDANCE = {
    "en": "Write the entire message in natural, conversational English.",
    "hi": "Write the entire message in natural, conversational Hindi (Devanagari script), as a native Hindi speaker would write it — not a literal translation of English phrasing.",
}


class WhatsAppGenerationError(Exception):
    pass


def _build_prompt(lead: dict, tone: str, length: str, language: str) -> str:
    business_name = lead.get("business_name", "your business")
    category = lead.get("category") or "a local business"
    has_website = lead.get("has_website", False)

    if has_website:
        context = (
            f"This business already has a website, but it has some weaknesses "
            f"(e.g. outdated design, slow loading, not mobile-friendly, or missing "
            f"features) that a web developer could improve."
        )
    else:
        context = "This business does not currently have a website at all."

    return f"""You are writing a single WhatsApp outreach message on behalf of a freelance web developer, to send to a local business owner. The goal is to start a conversation about possibly building or improving their website — NOT to close a sale in this message.

BUSINESS:
- Name: {business_name}
- Category: {category}
- {context}

TONE: {TONE_GUIDANCE[tone]}
LENGTH: {LENGTH_GUIDANCE[length]}
LANGUAGE: {LANGUAGE_GUIDANCE[language]}

Requirements:
- Mention the business by name naturally, early in the message.
- Reference that you noticed something specific about their online presence (their website, or lack of one) — don't be generic.
- Offer a free homepage concept / mockup as a low-commitment next step.
- End with a soft, low-pressure question inviting a reply (e.g. asking if they'd be interested), not a hard call-to-action.
- Do NOT include a greeting line like "Dear" or a formal letter structure — this is a WhatsApp message, written the way real people text.
- Do NOT invent or include any phone number, email address, or link — none of that information was given to you, so do not make any up.
- Do NOT add a signature, business name sign-off, or "Best regards" — WhatsApp messages don't end that way.
- Output ONLY the message text itself. No preamble, no explanation, no quotation marks around it."""


def _fallback_template(lead: dict, tone: str, length: str, language: str) -> str:
    """
    Used only if Ollama is unreachable. A simple deterministic template so
    the feature still produces something usable, rather than failing
    outright — clearly less personalized than the AI version, which is why
    Ollama is tried first and this is documented as a fallback, not the
    primary path.
    """
    business_name = lead.get("business_name", "there")

    if language == "hi":
        base = (
            f"नमस्ते {business_name}, मैंने आपके बिज़नेस को ऑनलाइन खोजते हुए देखा। "
            f"आपकी वेबसाइट में कुछ सुधार की संभावनाएं नज़र आईं, जैसे मोबाइल पर सही तरीके से दिखना और लोडिंग स्पीड। "
            f"मैं ऐसी वेबसाइटें बनाता हूं जो ज़्यादा ग्राहक लाने में मदद करती हैं। "
            f"क्या आप एक फ्री होमपेज कॉन्सेप्ट देखना चाहेंगे?"
        )
    else:
        base = (
            f"Hello {business_name}, I came across your business while searching online. "
            f"I noticed a few opportunities to improve your website, including mobile "
            f"responsiveness and loading speed. I specialize in designing modern "
            f"websites that help businesses generate more customers. I'd be happy to "
            f"create a free homepage concept for your business. Would you be interested?"
        )

    if length == "long":
        if language == "hi":
            base += " इसमें कोई जल्दी नहीं है, बस एक छोटी सी बातचीत से शुरुआत करते हैं।"
        else:
            base += " No pressure at all — just thought it was worth a quick conversation."

    return base


def generate_message(lead: dict, tone: str, length: str, language: str, model: str | None = None) -> str:
    prompt = _build_prompt(lead, tone, length, language)

    try:
        text = generate(prompt, model=model)
    except OllamaError:
        return _fallback_template(lead, tone, length, language)

    cleaned = text.strip().strip('"').strip()
    if not cleaned:
        return _fallback_template(lead, tone, length, language)

    return cleaned
