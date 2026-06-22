"""
Website Mockup generation.

Produces two things for a lead's proposed new homepage:
  1. image_prompt — a short, descriptive prompt suitable for feeding into
     an image generation tool (Midjourney, DALL-E, Stable Diffusion, etc.)
     to visualize the hero section's look and feel.
  2. html_preview — a real, self-contained HTML document (inline Tailwind
     via CDN) that renders an actual wireframe-level homepage: hero,
     services, gallery, testimonials, about, contact, footer.

Two separate Ollama calls are used rather than one combined JSON response.
Asking a small local model (Llama 3 8B, Mistral 7B) to produce both a short
field AND a long HTML document inside a single JSON object is a common
failure mode — the model often truncates the HTML to "fit," or breaks JSON
escaping on the embedded markup. Splitting into two focused calls (a short
text generation, then a dedicated HTML generation) is far more reliable
with these model sizes.

If the lead already has an AI Report (ai_reports row) with
suggested_colors / suggested_fonts / suggested_design_style, those are
passed in and used directly — this keeps the Mockup visually consistent
with the AI Report's recommendations instead of the two features
independently inventing different palettes for the same lead.
"""
import re

from app.services.ollama_client import OllamaError, generate

DEFAULT_SECTIONS = ["hero", "services", "gallery", "testimonials", "about", "contact", "footer"]


class MockupGenerationError(Exception):
    pass


def _design_brief(ai_report: dict | None) -> str:
    if not ai_report:
        return (
            "No prior design direction has been set for this lead. Choose colors, "
            "fonts, and a style that suit the business category yourself."
        )

    colors = ", ".join(ai_report.get("suggested_colors") or []) or "your own choice"
    fonts = ", ".join(ai_report.get("suggested_fonts") or []) or "your own choice"
    style = ai_report.get("suggested_design_style") or "your own choice"

    return (
        f"Use this existing design direction, already agreed for this lead:\n"
        f"- Colors: {colors}\n"
        f"- Fonts: {fonts}\n"
        f"- Style: {style}"
    )


def _build_image_prompt_request(lead: dict, ai_report: dict | None) -> str:
    business_name = lead.get("business_name", "this business")
    category = lead.get("category") or "a local business"

    return f"""Write a single short paragraph (3-4 sentences) that could be used as an image generation prompt (for tools like Midjourney or DALL-E) to visualize the HERO SECTION of a new homepage for this business.

BUSINESS: {business_name}, category: {category}.

{_design_brief(ai_report)}

Describe the visual scene, mood, lighting, and composition concretely — not the business's services. Do not mention the business name inside the image prompt itself (image generators do not render text well). Output ONLY the prompt paragraph, nothing else — no preamble, no quotation marks."""


def _build_html_request(lead: dict, ai_report: dict | None, sections: list[str]) -> str:
    business_name = lead.get("business_name", "Your Business")
    category = lead.get("category") or "local business"
    section_list = ", ".join(sections)

    return f"""Generate a single self-contained HTML document for a homepage wireframe concept. This is a CONCEPT PREVIEW, not a production site — keep it simple, semantic, and clean.

BUSINESS: {business_name} ({category})

{_design_brief(ai_report)}

Requirements:
- Output ONLY raw HTML starting with <!DOCTYPE html> and ending with </html>. No markdown code fences (no ```), no explanation before or after.
- Include this exact line inside <head>: <script src="https://cdn.tailwindcss.com"></script>
- Use Tailwind utility classes for ALL styling. Do not write a <style> block or inline style attributes.
- Include these sections, in this order, each as a clearly identifiable <section> with a matching id attribute: {section_list}
- hero: a large heading with the business name, a short tagline, and a call-to-action button.
- services: 3 short service/offering cards in a grid.
- gallery: a grid of 4-6 placeholder image boxes (use <div> with a bg-gray-300 placeholder and a text label, not real <img> tags, since no real images exist yet).
- testimonials: 2 short fake testimonial quotes with a placeholder name.
- about: a short paragraph about the business.
- contact: a simple contact form (name, email, message fields, submit button) — non-functional, no JavaScript needed.
- footer: business name, a copyright line, and 2-3 placeholder links.
- Use real, readable placeholder copy specific to a {category} business — not lorem ipsum.
- Keep the whole document under 200 lines.
- Make it responsive using Tailwind's responsive prefixes (sm:, md:, lg:)."""


def _strip_code_fences(text: str) -> str:
    """
    Small local models frequently wrap HTML output in markdown code fences
    despite being told not to. This strips a leading/trailing ```html or
    ``` fence if present, rather than failing the whole generation over a
    cosmetic formatting habit.
    """
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:html)?\s*\n?", "", cleaned)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    return cleaned.strip()


def _validate_html(html: str) -> str | None:
    """Returns None if acceptable, or a description of the problem."""
    if not html:
        return "the response was empty"
    lower = html.lower()
    if "<!doctype html" not in lower:
        return "the response did not start with a valid <!DOCTYPE html> document"
    if "</html>" not in lower:
        return "the response did not contain a closing </html> tag"
    if "cdn.tailwindcss.com" not in lower:
        return "the response did not include the required Tailwind CDN script tag"
    if len(html) < 500:
        return "the response was too short to be a real homepage wireframe"
    return None


def generate_mockup(lead: dict, ai_report: dict | None = None, model: str | None = None) -> dict:
    sections = DEFAULT_SECTIONS

    try:
        image_prompt_raw = generate(_build_image_prompt_request(lead, ai_report), model=model)
    except OllamaError as exc:
        raise MockupGenerationError(f"Could not generate image prompt: {exc}") from exc

    image_prompt = image_prompt_raw.strip().strip('"').strip()
    if not image_prompt:
        image_prompt = (
            f"A clean, professional photograph representing a {lead.get('category', 'local business')}, "
            f"warm natural lighting, inviting composition, no visible text."
        )

    max_attempts = 2
    html_preview = None
    last_problem = None

    for attempt in range(1, max_attempts + 1):
        prompt = _build_html_request(lead, ai_report, sections)
        if last_problem:
            prompt += f"\n\nYour previous attempt had a problem: {last_problem}. Fix this and output the corrected HTML document."

        try:
            raw_html = generate(prompt, model=model, timeout=120.0)
        except OllamaError as exc:
            raise MockupGenerationError(f"Could not generate HTML preview: {exc}") from exc

        cleaned = _strip_code_fences(raw_html)
        problem = _validate_html(cleaned)

        if problem is None:
            html_preview = cleaned
            break

        last_problem = problem

    if html_preview is None:
        raise MockupGenerationError(
            f"AI did not return a usable HTML preview after {max_attempts} attempts. Last problem: {last_problem}"
        )

    return {
        "sections": sections,
        "image_prompt": image_prompt,
        "html_preview": html_preview,
    }
