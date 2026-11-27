"""Jinja2 environment, Markdown rendering, and page writing helpers."""
from pathlib import Path

import markdown as md
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup


def markdown_to_html(text):
    """Render trusted repository Markdown to HTML."""
    if not text:
        return Markup("")
    return Markup(md.markdown(text, extensions=["tables", "sane_lists"], output_format="html"))


def make_env(templates_dir):
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["markdown"] = markdown_to_html
    return env


def root_for(rel_path):
    """Relative prefix from a page's directory back to the site root.

    rel_path is the page's output path relative to the site root, e.g.
    "index.html" -> "", "2027-ireland/index.html" -> "../",
    "2027-ireland/day/3/index.html" -> "../../../".
    """
    depth = len(Path(rel_path).parts) - 1
    return "../" * depth


class PageWriter:
    def __init__(self, env, out_dir, common):
        self.env = env
        self.out_dir = Path(out_dir)
        self.common = common
        self.written = []

    def write(self, rel_path, template, **context):
        html = self.env.get_template(template).render(root=root_for(rel_path), **self.common, **context)
        self.write_text(rel_path, html)

    def write_text(self, rel_path, text):
        path = self.out_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        self.written.append(rel_path)
