import json

import markdown
from jinja2 import Template

from langflow.custom import Component
from langflow.io import (
    BoolInput,
    MessageTextInput,
    MultilineInput,
    Output,
    TableInput,
)
from langflow.schema import Data

TEMPLATE = """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    {{ meta_tags }}
    <title>{{ title }}</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        .container {
            {% if sidebar_content %}
            display: grid;
            grid-template-columns: 1fr 220px;
            gap: 2rem;
            {% endif %}
            max-width: 900px;
            margin: 40px auto;
            padding: 0 2.5rem;
        }
        {% if sidebar_content %}
        main {
            grid-column: 1;
        }
        aside {
            grid-column: 2;
            padding: 1.2rem 1rem;
            min-height: 140px;
        }
        {% endif %}
        @media (max-width: 900px) {
            .container {
                grid-template-columns: 1fr;
                gap: 1.2rem;
                padding: 0 1.2rem;
            }
            aside {
                grid-column: 1;
                margin-top: 2rem;
            }
        }
        nav {
            margin-bottom: 2rem;
        }
        nav ul#main-menu {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
            list-style: none;
            padding: 0.5rem;
            margin: 0;
        }
        nav ul#main-menu li a {
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            transition: background 0.2s;
        }
        .menu-toggle {
            display: none;
            background: none;
            border: none;
            font-size: 2rem;
            cursor: pointer;
        }
        @media (max-width: 600px) {
            nav ul#main-menu {
                display: none;
                flex-direction: column;
                width: 100%;
                position: absolute;
                left: 0;
                top: 60px;
                z-index: 10;
            }
            nav ul#main-menu.open {
                display: flex;
                background: inherit;
            }
            .menu-toggle {
                display: block;
            }
        }
        footer {
            margin-top: 2rem;
        }
        .content {
            margin-top: 1.8rem;
        }
        {{ custom_style }}
    </style>
    <script>
        function toggleMenu() {
            var menu = document.getElementById('main-menu');
            if (menu.classList.contains('open')) {
                menu.classList.remove('open');
            } else {
                menu.classList.add('open');
            }
        }
    </script>
</head>
<body>
    {% if header_content %}
    <header>
        {{ header_content }}
    </header>
    {% endif %}
    <nav>
        <button class=\"menu-toggle\" onclick=\"toggleMenu()\">&#9776;</button>
        <ul id=\"main-menu\">
            {% for page in menu_pages %}
                <li><a href=\"{{ page.url }}\">{{ page.title }}</a></li>
            {% endfor %}
        </ul>
    </nav>
    <div class=\"container\">
        <main class=\"content\">
            {{ content }}
        </main>
        {% if sidebar_content %}
        <aside>
            {{ sidebar_content }}
        </aside>
        {% endif %}
    </div>
    {% if footer_content %}
    <footer>
        {{ footer_content }}
    </footer>
    {% endif %}
</body>
</html>"""


class HTMLGeneratorComponent(Component):
    display_name = "HTML Generator"
    description = "Generate HTML pages with customizable styling."
    icon = "code"
    name = "HTMLGenerator"

    inputs = [
        MessageTextInput(
            name="title",
            display_name="Page Title",
            info="The title of the HTML page",
            required=True,
        ),
        MultilineInput(
            name="content",
            display_name="Content",
            info="The main content of the page (supports Markdown if enabled)",
            required=True,
        ),
        TableInput(
            name="menu_pages",
            display_name="Menu",
            info="List of pages for the navigation menu.",
            table_schema=[
                {
                    "name": "title",
                    "display_name": "Title",
                    "type": "str",
                    "description": "Page title",
                },
                {
                    "name": "url",
                    "display_name": "URL",
                    "description": "Page URL",
                },
            ],
            value=[],
            input_types=["Data"],
        ),
        MultilineInput(
            name="header_content",
            display_name="Header Content",
            info="HTML or Markdown for the header (optional).",
            value="",
        ),
        MultilineInput(
            name="sidebar_content",
            display_name="Sidebar Content",
            info="HTML or Markdown for the sidebar (optional).",
            value="",
        ),
        MultilineInput(
            name="footer_content",
            display_name="Footer Content",
            info="HTML or Markdown for the footer (optional).",
            value="",
        ),
        MultilineInput(
            name="style",
            display_name="CSS Style",
            info="Add CSS styles for the page",
            value="",
        ),
        BoolInput(
            name="use_markdown",
            display_name="Use Markdown",
            info="Convert content from Markdown to HTML",
            value=True,
        ),
        MultilineInput(
            name="template",
            display_name="HTML Template",
            info="Jinja2 template for the HTML page.",
            value=TEMPLATE,
            advanced=True,
        ),
        MessageTextInput(
            name="meta_description",
            display_name="Meta Description",
            info="SEO meta description",
            advanced=True,
        ),
        MessageTextInput(
            name="meta_keywords",
            display_name="Meta Keywords",
            info="SEO meta keywords (comma-separated)",
            advanced=True,
        ),
        BoolInput(
            name="rewrite_root_links",
            display_name="Rewrite root links",
            info="Rewrites links starting with / to be relative to the current page",
            value=True,
            advanced=True,
        ),
    ]

    outputs = [
        Output(name="html_output", display_name="HTML", method="generate_html"),
    ]

    def build_meta_tags(self) -> str:
        """Build meta tags for SEO."""
        meta_tags = []
        if self.meta_description:
            meta_tags.append(f'<meta name="description" content="{self.meta_description}">')
        if self.meta_keywords:
            meta_tags.append(f'<meta name="keywords" content="{self.meta_keywords}">')
        return "\n    ".join(meta_tags)

    def build_menu_pages(self) -> list:
        """Build the menu pages for the navigation."""
        menu_pages = self.menu_pages or []

        if isinstance(self.menu_pages, Data):
            menu_pages = json.loads(self.menu_pages.get_text())
        elif hasattr(self.menu_pages, "__iter__"):
            menu_pages = [json.loads(page.get_text()) if isinstance(page, Data) else page for page in self.menu_pages]
        menu_pages = menu_pages[0] if len(menu_pages) == 1 else menu_pages

        if self.rewrite_root_links:
            for page in menu_pages:
                if isinstance(page, dict) and page.get("url", "").startswith("/"):
                    page["url"] = f".{page['url']}"

        return menu_pages

    def sanitize_content(self, content: str) -> str:
        """Fix common LLM output issues with the content."""
        content = content.replace("```markdown", "").replace("```", "")
        if self.rewrite_root_links:
            content = content.replace('href="/', 'href="./')
        return content

    def process_content(self, content: str) -> str:
        """Process the content based on the use_markdown flag."""
        if self.use_markdown:
            content = markdown.markdown(content)
        return self.sanitize_content(content)

    def generate_html(self) -> Data:
        """Generate the HTML page based on the inputs."""
        try:
            content = self.process_content(self.content or "")
            header_content = self.process_content(self.header_content or "")
            sidebar_content = self.process_content(self.sidebar_content or "")
            footer_content = self.process_content(self.footer_content or "")
            meta_tags = self.build_meta_tags()
            menu_pages = self.build_menu_pages()
            style = (self.style or "").replace("```css", "").replace("```", "")
            template = self.template or TEMPLATE

            html = Template(template).render(
                title=self.title,
                meta_tags=meta_tags,
                custom_style=style,
                menu_pages=menu_pages or [],
                content=content,
                header_content=header_content,
                sidebar_content=sidebar_content,
                footer_content=footer_content,
            )

            self.status = f"Generated HTML page: {self.title}"
            return Data(data={"html": html}, text_key="html")

        except Exception as e:
            error_msg = f"Error generating HTML: {e}"
            self.status = error_msg
            raise ValueError(error_msg) from e
