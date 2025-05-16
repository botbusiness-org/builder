from langflow.base.io.text import TextComponent
from langflow.io import MultilineInput, Output
from langflow.schema.data import Data
from langflow.schema.message import Message


class WebsiteOutputComponent(TextComponent):
    display_name = "Website Output"
    description = "Displays HTML code as web page."
    icon = "file-code"
    name = "WebsiteOutput"

    inputs = [
        MultilineInput(
            name="input_value",
            display_name="HTML",
            info="HTML to be passed as output.",
            input_types=["Data", "Message"],
        ),
    ]
    outputs = [
        Output(display_name="HTML", name="html", method="html_response"),
    ]

    def html_response(self) -> Data:
        if isinstance(self.input_value, str):
            html = self.input_value
        elif isinstance(self.input_value, Message):
            html = self.input_value.get_text()
        elif isinstance(self.input_value, Data):
            if self.input_value.get_text() is None:
                msg = "Empty Data object"
                raise ValueError(msg)
            html = self.input_value.get_text()
        else:
            html = str(self.input_value)
        return Data(data={"html": html}, text_key="html")
