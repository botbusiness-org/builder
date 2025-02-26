import operator
import os
from functools import reduce

from langflow.base.models import LCModelComponent, PatchedChatModel
from langflow.field_typing import LanguageModel
from langflow.field_typing.range_spec import RangeSpec
from langflow.inputs import BoolInput, DictInput, DropdownInput, FloatInput, IntInput
from langflow.inputs.inputs import HandleInput


class BotbusinessAIModelComponent(LCModelComponent):
    display_name = "Botbusiness AI"
    description = "Generate text using LLMs provided by Botbusiness."
    icon = "MessagesSquare"
    name = "BotbusinessAIModel"
    model_names = os.getenv("BOTBUSINESS_AI_MODEL_NAMES", "").split(",")

    inputs = [
        *LCModelComponent._base_inputs,
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            advanced=True,
            info="The maximum number of tokens to generate. Set to 0 for unlimited tokens.",
            range_spec=RangeSpec(min=0, max=128000),
        ),
        DictInput(name="model_kwargs", display_name="Model Kwargs", advanced=True),
        BoolInput(
            name="json_mode",
            display_name="JSON Mode",
            advanced=True,
            info="If True, it will output JSON regardless of passing a schema.",
        ),
        DictInput(
            name="output_schema",
            is_list=True,
            display_name="Schema",
            advanced=True,
            info="The schema for the Output of the model. "
            "You must pass the word JSON in the prompt. "
            "If left blank, JSON mode will be disabled. [DEPRECATED]",
        ),
        DropdownInput(
            name="model_name",
            display_name="Model Name",
            advanced=False,
            options=model_names,
            value=model_names[0] if model_names else None,
        ),
        FloatInput(name="temperature", display_name="Temperature", value=0.1),
        IntInput(
            name="seed",
            display_name="Seed",
            info="The seed controls the reproducibility of the job.",
            advanced=True,
            value=1,
        ),
        HandleInput(
            name="output_parser",
            display_name="Output Parser",
            info="The parser to use to parse the output of the model",
            advanced=True,
            input_types=["OutputParser"],
        ),
    ]

    def build_model(self) -> LanguageModel:  # type: ignore[type-var]
        # self.output_schema is a list of dictionaries
        # let's convert it to a dictionary
        output_schema_dict: dict[str, str] = reduce(operator.ior, self.output_schema or {}, {})
        temperature = self.temperature
        model_name: str = self.model_name
        max_tokens = self.max_tokens
        model_kwargs = self.model_kwargs or {}
        json_mode = bool(output_schema_dict) or self.json_mode
        seed = self.seed

        botbusiness_ai_api_key = os.getenv("BOTBUSINESS_AI_TOKEN")
        if not botbusiness_ai_api_key:
            msg = "BOTBUSINESS_AI_TOKEN is not set."
            raise ValueError(msg)

        botbusiness_ai_api_base = os.getenv("BOTBUSINESS_AI_URL")
        if not botbusiness_ai_api_base:
            msg = "BOTBUSINESS_AI_URL is not set."
            raise ValueError(msg)

        output = PatchedChatModel(
            max_tokens=max_tokens or None,
            model_kwargs=model_kwargs,
            model=model_name,
            base_url=botbusiness_ai_api_base,
            api_key=botbusiness_ai_api_key,
            temperature=temperature if temperature is not None else 0.1,
            seed=seed,
        )
        if json_mode:
            if output_schema_dict:
                output = output.with_structured_output(schema=output_schema_dict, method="json_mode")
            else:
                output = output.bind(response_format={"type": "json_object"})

        return output

    def _get_exception_message(self, e):
        if e.body and isinstance(e.body, dict):
            message = e.body.get("message")
            if message:
                return message
        return str(e)
