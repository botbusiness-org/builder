import time

import httpx
from loguru import logger

from langflow.custom import Component
from langflow.io import DropdownInput, MessageTextInput, Output, SecretStrInput, StrInput
from langflow.schema import Data
from langflow.schema.content_block import ContentBlock
from langflow.schema.content_types import MediaContent
from langflow.schema.message import Message


class OpenAIImageGenerationComponent(Component):
    display_name = "OpenAI Image Generation"
    description = "Generate images using OpenAI DALL-E or compatible APIs"
    icon = "OpenAI"
    name = "OpenAIImageGeneration"

    inputs = [
        StrInput(
            name="base_url",
            display_name="Base URL",
            advanced=True,
            info="Base URL for the API (default: https://api.openai.com/v1)",
            value="https://api.openai.com/v1",
        ),
        SecretStrInput(
            name="api_key",
            display_name="OpenAI API Key",
            info="Your OpenAI API key or compatible API key",
            advanced=False,
            value="OPENAI_API_KEY",
            required=True,
        ),
        MessageTextInput(
            name="prompt",
            display_name="Prompt",
            info="A text description of the desired image(s)",
            required=True,
            tool_mode=True,
        ),
        DropdownInput(
            name="model",
            display_name="Model",
            info="The model to use for image generation",
            options=["dall-e-3"],
            value="dall-e-3",
        ),
        DropdownInput(
            name="size",
            display_name="Size",
            info="The size of the generated images",
            options=["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"],
            value="1024x1024",
        ),
        DropdownInput(
            name="quality",
            display_name="Quality",
            info="The quality of the generated images",
            options=["standard", "hd"],
            value="hd",
            advanced=True,
        ),
        DropdownInput(
            name="style",
            display_name="Style",
            info="The style of the generated images",
            options=["vivid", "natural"],
            value="vivid",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Images Data", name="data", method="generate_images"),
        Output(display_name="Images Message", name="message", method="generate_images_message"),
    ]

    async def generate_images(self) -> list[Data]:
        try:
            # Prepare the payload for the API request
            payload = {
                "model": self.model,
                "prompt": self.prompt,
                "quality": self.quality,
                "size": self.size,
                "response_format": "b64_json",
            }

            if self.style and self.style != "default":
                payload["style"] = self.style

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            url = f"{self.base_url.rstrip('/')}/images/generations"

            # Make the API request
            start_time = time.time()
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
            end_time = time.time()
            duration = int((end_time - start_time) * 1000)

            # Process the response and create Data objects
            images_data = []
            for i, image_data in enumerate(result.get("data", [])):
                data_dict = {
                    "index": i,
                    "prompt": self.prompt,
                    "model": self.model,
                    "size": self.size,
                    "quality": self.quality,
                    "style": self.style,
                    "created": result.get("created"),
                    "duration": duration,
                    "b64_json": image_data.get("b64_json"),
                    "image_data": image_data.get("b64_json"),
                }

                text_content = f"Generated image {i + 1} (base64 encoded)"

                if "revised_prompt" in image_data:
                    data_dict["revised_prompt"] = image_data["revised_prompt"]
                    text_content += f"\nRevised prompt: {image_data['revised_prompt']}"

                images_data.append(Data(text=text_content, data=data_dict))

            self.status = f"Successfully generated {len(images_data)} image(s)"

        except httpx.TimeoutException:
            error_message = "Request timed out. Image generation can take some time, please try again."
            logger.error(error_message)
            self.status = error_message
            return [Data(text=error_message, data={"error": error_message})]

        except httpx.HTTPStatusError as exc:
            error_message = f"API Error {exc.response.status_code}: {exc.response.text}"
            logger.error(error_message)
            self.status = error_message
            return [Data(text=error_message, data={"error": error_message})]

        except httpx.RequestError as exc:
            error_message = f"Request error: {exc}"
            logger.error(error_message)
            self.status = error_message
            return [Data(text=error_message, data={"error": error_message})]

        else:
            return images_data

    async def generate_images_message(self) -> Message:
        """Generate images and return as a message."""
        images_data = await self.generate_images()

        if not images_data:
            return Message(text="No images were generated.")

        if images_data[0].data.get("error"):
            raise RuntimeError(images_data[0].data["error"])

        return Message(
            data={"images_data": images_data},
            content_blocks=[
                ContentBlock(
                    title="Media Block",
                    contents=[
                        MediaContent(
                            type="media",
                            urls=["data:image/png;base64," + data.data.get("image_data", "")],
                            duration=data.data.get("duration", 0),
                            caption=data.data.get("prompt"),
                        )
                        for data in images_data
                        if data.data.get("image_data")
                    ],
                )
            ],
        )
