from langchain_openai import ChatOpenAI
from langchain_openai.chat_models import base

# pylint: disable-next=protected-access
original_create_usage_metadata = base._create_usage_metadata


def patched_create_usage_metadata(*args, **kwargs):
    oai_token_usage: dict = args[0]

    prompt_tokens = oai_token_usage.get("prompt_tokens")
    if not prompt_tokens:
        oai_token_usage["prompt_tokens"] = 0

    completion_tokens = oai_token_usage.get("completion_tokens")
    if not completion_tokens:
        oai_token_usage["completion_tokens"] = 0

    return original_create_usage_metadata(*args, **kwargs)


# pylint: disable-next=protected-access
base._create_usage_metadata = patched_create_usage_metadata


class PatchedChatModel(ChatOpenAI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
