"""
AI Report generation.

Builds a structured prompt from the lead's profile plus their latest
website_analyses row (if one exists), asks Ollama for a JSON object
matching the ai_reports schema, and validates the result before returning
it to the route — Ollama's `format: "json"` mode guarantees syntactically
valid JSON but NOT the specific keys/types we need, so this module is
responsible for that contract.

Strategy:
  1. Build a prompt that explicitly lists every required key, its type,
     and a short instruction for what good content looks like — small
     local models (Llama 3 8B, Mistral 7B) follow an explicit schema far
     more reliably than an implied one.
  2. Call Ollama once. Validate the result.
  3. If validation fails (missing key, wrong type), retry once with a
     corrective follow-up prompt that names exactly what was wrong. Local
     models are inconsistent enough that a bare retry-with-same-prompt
     often repeats the same mistake; telling it what it got wrong fixes
     this most of the time without a third attempt.
  4. If it still fails, raise a clear error rather than silently
     fabricating a report or persisting partial/garbage data.

This intentionally does NOT fall back to a non-AI template if Ollama is
unreachable — unlike whatsapp.py, which can degrade to a template message,
there's no honest non-AI substitute for "business summary" and
"suggested redesign direction" that wouldn't just be generic boilerplate
presented as analysis.
"""
import re

from app.services.ollama_client import OllamaError, generate_json

REQUIRED_SCHEMA = {
    "business_summary": str,
    "weaknesses": list,
    "improvements": list,
    "estimated_lost_customers_per_month": int,
    "estimated_revenue_increase_monthly": (int, float),
    "suggested_features": list,
    "suggested_colors": list,
    "suggested_fonts": list,
    "suggested_design_style": str,
}

MAX_ATTEMPTS = 2


class AIReportError(Exception):
    pass


def _describe_analysis(analysis: dict | None) -> str:
    if not analysis:
        return (
            "No technical website analysis is available for this lead yet "
            "(either they have no website, or it hasn't been analyzed). "
            "Base your assessment on the business category and the fact "
            "that they may not have a strong web presence."
        )

    lines = []
    lines.append(f"Overall website score: {analysis.get('overall_score', 'unknown')}/100")
    lines.append(f"Performance score: {analysis.get('performance_score', 'unknown')}/100")
    lines.append(f"SEO score: {analysis.get('seo_score', 'unknown')}/100")
    lines.append(f"Accessibility score: {analysis.get('accessibility_score', 'unknown')}/100")
    lines.append(f"Image optimization score: {analysis.get('image_optimization_score', 'unknown')}/100")
    lines.append(f"Has valid SSL: {analysis.get('has_ssl')}")
    lines.append(f"Is mobile responsive: {analysis.get('is_responsive')}")
    lines.append(f"Has contact form: {analysis.get('has_contact_form')}")
    lines.append(f"Has WhatsApp button: {analysis.get('has_whatsapp_button')}")
    lines.append(f"Has Google Maps embed: {analysis.get('has_google_maps_embed')}")
    lines.append(f"Has social media links: {analysis.get('has_social_links')}")
    lines.append(f"Has dark mode support: {analysis.get('has_dark_mode')}")
    lines.append(f"Broken links found: {analysis.get('broken_links_count', 'unknown')}")
    lines.append(f"Loading speed: {analysis.get('loading_speed_ms', 'unknown')} ms")
    return "\n".join(f"- {line}" for line in lines)


def _build_prompt(lead: dict, analysis: dict | None, correction: str | None = None) -> str:
    business_name = lead.get("business_name", "this business")
    category = lead.get("category") or "a local business"
    city = lead.get("city") or "their city"
    has_website = lead.get("has_website", False)
    rating = lead.get("google_rating")
    review_count = lead.get("review_count")

    rating_line = (
        f"Google rating: {rating}/5 from {review_count} reviews"
        if rating is not None
        else "Google rating: not available"
    )

    prompt = f"""You are a web design consultant analyzing a local business as part of a sales outreach tool. A freelance web developer will use your analysis to decide whether to pitch this business a new website.

BUSINESS:
- Name: {business_name}
- Category: {category}
- City: {city}
- Has a website: {has_website}
- {rating_line}

WEBSITE ANALYSIS:
{_describe_analysis(analysis)}

Respond with ONLY a JSON object (no markdown, no explanation before or after) with exactly these keys:

{{
  "business_summary": "2-3 sentence plain-English summary of this business and its current web presence",
  "weaknesses": ["3-5 specific weaknesses, each a short phrase, based on the analysis above"],
  "improvements": ["3-5 specific, actionable improvements a web developer could make"],
  "estimated_lost_customers_per_month": <integer, a reasonable estimate of customers lost per month due to website weaknesses, based on the category and the analysis>,
  "estimated_revenue_increase_monthly": <number, estimated monthly revenue increase in USD if the website were fixed, based on a typical transaction value for this business category>,
  "suggested_features": ["3-5 specific features this business's new website should include, e.g. online booking, photo gallery, WhatsApp click-to-chat"],
  "suggested_colors": ["2-4 hex color codes, e.g. #1A2B3C, that would suit this business's brand and category"],
  "suggested_fonts": ["2-3 real font names, e.g. Poppins, Inter, Playfair Display, that suit this business's category"],
  "suggested_design_style": "one short phrase describing the recommended visual style, e.g. 'warm and rustic' or 'clean and modern'"
}}

Rules:
- weaknesses and improvements must be specific to THIS business, not generic.
- All numbers must be plain numbers, not strings, and not null.
- suggested_colors must be valid hex codes starting with #.
- Do not include any text outside the JSON object."""

    if correction:
        prompt += f"\n\nYour previous response had a problem: {correction}\nFix this and respond again with ONLY the corrected JSON object."

    return prompt


def _validate(data: dict) -> str | None:
    """Returns None if valid, or a human-readable description of the first problem found."""
    if not isinstance(data, dict):
        return "the response was not a JSON object"

    for key, expected_type in REQUIRED_SCHEMA.items():
        if key not in data:
            return f"the key '{key}' was missing"
        value = data[key]
        # isinstance(True, int) is True in Python, so explicitly reject
        # booleans here — a model returning `true` for a numeric field
        # should fail validation, not silently pass as 1.
        if isinstance(value, bool):
            return f"the key '{key}' should be of type {expected_type}, but got bool"
        if not isinstance(value, expected_type):
            return f"the key '{key}' should be of type {expected_type}, but got {type(value).__name__}"

    for key in ("weaknesses", "improvements", "suggested_features", "suggested_colors", "suggested_fonts"):
        if len(data[key]) == 0:
            return f"the key '{key}' was an empty list"
        if not all(isinstance(item, str) for item in data[key]):
            return f"the key '{key}' must be a list of strings"

    hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")
    for color in data["suggested_colors"]:
        if not hex_pattern.match(color):
            return f"'{color}' in suggested_colors is not a valid hex color code"

    return None


def generate_report(lead: dict, latest_analysis: dict | None, model: str | None = None) -> dict:
    correction: str | None = None
    last_error: str | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        prompt = _build_prompt(lead, latest_analysis, correction=correction)

        try:
            result = generate_json(prompt, model=model)
        except OllamaError as exc:
            raise AIReportError(str(exc)) from exc

        problem = _validate(result)
        if problem is None:
            return {
                "business_summary": result["business_summary"],
                "weaknesses": result["weaknesses"],
                "improvements": result["improvements"],
                "estimated_lost_customers_per_month": int(result["estimated_lost_customers_per_month"]),
                "estimated_revenue_increase_monthly": float(result["estimated_revenue_increase_monthly"]),
                "suggested_features": result["suggested_features"],
                "suggested_colors": result["suggested_colors"],
                "suggested_fonts": result["suggested_fonts"],
                "suggested_design_style": result["suggested_design_style"],
                "model_used": model or "llama-3.3-70b-versatile",
            }

        last_error = problem
        correction = problem  # used to build a corrective follow-up prompt on the next attempt

    raise AIReportError(
        f"AI did not return a usable report after {MAX_ATTEMPTS} attempts. Last problem: {last_error}"
    )
