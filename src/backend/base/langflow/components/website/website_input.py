import json

from langflow.custom import Component
from langflow.io import BoolInput, MultilineInput, Output, TableInput
from langflow.schema import Data, Message


class WebsiteInputComponent(Component):
    display_name = "Website Input"
    name = "WebsiteInput"
    icon = "tablet-smartphone"
    description = "Entry point for a website. It receives the path and parameters from the request."

    inputs = [
        MultilineInput(
            name="path",
            display_name="Path",
            info="Receives the path of the current page.",
            value="/",
            advanced=True,
        ),
        MultilineInput(
            name="data",
            display_name="Parameters",
            info="Receives HTTP GET or POST parameters.",
            advanced=True,
        ),
        MultilineInput(
            name="url",
            display_name="URL",
            value="WEBSITE_URL",
            advanced=False,
            copy_field=True,
            input_types=[],
        ),
        BoolInput(
            name="use_store",
            display_name="Use Page Store",
            info="If enabled, generated pages will be stored to speed up future requests.",
            value=True,
        ),
        TableInput(
            name="page_store",
            display_name="Page Store",
            info=(
                "Contains stored pages. Pages in the store will not be generated again to make requests faster. "
                "Delete a page from the store to regenerate it."
            ),
            table_schema=[
                {
                    "name": "path",
                    "display_name": "Path",
                    "type": "str",
                    "description": "Page path",
                },
                {
                    "name": "content",
                    "display_name": "Content",
                    "type": "str",
                    "description": "Page content",
                },
            ],
            value=[],
            input_types=["Data"],
        ),
        BoolInput(
            name="require_link",
            display_name="Allow linked pages only",
            info=(
                'If enabled, only the home page ("/") and all pages that are linked on any generated page will be '
                "accessible. This is useful to prevent users from generating arbitrary pages. Requires the store to be "
                "enabled."
            ),
            value=True,
            advanced=True,
        ),
    ]
    outputs = [
        Output(display_name="Path", name="output_path", method="build_path"),
        Output(display_name="Parameters", name="output_data", method="build_data"),
    ]

    def build_path(self) -> Message:
        path = self.path or "/"
        if not path.startswith("/"):
            path = "/" + path
        return Message(text=path)

    def build_data(self) -> Data:
        message: str | Data = ""
        if not self.data:
            self.status = "No data provided."
            return Data(data={})
        try:
            body = json.loads(self.data or "{}")
        except json.JSONDecodeError:
            body = {"payload": self.data}
            message = f"Invalid JSON payload. Please check the format.\n\n{self.data}"
        data = Data(data=body)
        if not message:
            message = data
        self.status = message
        return data
