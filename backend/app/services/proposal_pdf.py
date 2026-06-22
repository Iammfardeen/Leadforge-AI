"""
Proposal PDF rendering — STUB (foundation phase).

Planned implementation: use WeasyPrint (free, open-source, HTML/CSS -> PDF)
to render an HTML template populated with proposal + lead data, including a
canvas-captured signature image embedded as base64, then upload the
resulting PDF to Supabase Storage bucket STORAGE_BUCKET_PROPOSALS.

Returns the storage path (str) on success.
"""


def render_pdf(proposal: dict, lead: dict) -> str:
    raise NotImplementedError("Proposal PDF rendering will be implemented in the feature-build phase")
