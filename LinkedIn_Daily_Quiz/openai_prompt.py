from openai import OpenAI
import json
import os

class OpenAIPrompt:
    """
        A helper class for generating structured JSON responses from the OpenAI API.
        It tries the newer Responses API first, and falls back to the Chat Completions API
        with JSON mode if needed.
    """
    def __init__(self, prompt=None, api_key=None, model="gpt-5"):
        """
            Create a new OpenAIPrompt instance.
            :param prompt: The main prompt text to send to the model (optional).
            :param api_key: Your OpenAI API key. If not provided, will try to use
                            the OPENAI_API_KEY environment variable.
            :param model: The model name to use (default: "gpt-5").
        """
        self.client = self._get_client(api_key)
        self.model = model
        self.prmpt = prompt

    @staticmethod
    def _get_client(api_key):
        """
            Create an OpenAI client using the provided API key.
            If no key is provided, try to load it from the OPENAI_API_KEY environment variable.
            Raises an error if no key is found.
        """
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError(
                "OpenAI API key missing: pass api_key=... or set OPENAI_API_KEY"
            )
        return OpenAI(api_key=key)

    @staticmethod
    def _loads_or_trim_braces(s):
        """
            Parse a string as JSON.
            - First, try normal JSON parsing.
            - If that fails, try to extract the portion between the first '{' and the last '}'
            and parse that.
            - If parsing still fails, re-raise the original error.
        """
        if not s:
            raise ValueError("Empty string passed to JSON parser")
        try:
            return json.loads(s)
        except Exception:
            start = s.find("{")
            end = s.rfind("}")
            if start == -1 or end == -1 or end <= start:
                # Give original error context if trimming is impossible
                raise
            return json.loads(s[start: end + 1])

    def generate_json(self, *, system_prompt, user_prompt, seed=None):
        """
            Send prompts to OpenAI and return a structured JSON response.
            Steps:
            1. Try the new Responses API first.
            2. If parsing fails or an error occurs, fall back to the older
            Chat Completions API with JSON mode.
            3. Always return the parsed JSON as a Python dictionary.

            :param system_prompt: Instructions for how the model should behave.
            :param user_prompt: The actual question or input to generate output from.
            :param seed: Optional integer to make results reproducible.
            :return: A Python dictionary parsed from the model’s JSON response.
        """
        # First, try using the newer "Responses" API from OpenAI
        try:
            resp = self.client.responses.create(
                model=self.model,  # which model to use (default is gpt-5)
                input=[
                    {"role": "system", "content": system_prompt},  # system role defines behavior
                    {"role": "user", "content": user_prompt},  # user role gives the actual question
                ],
                seed=int(seed) if seed is not None else None,  # optional seed for reproducibility
            )

            # Try to grab the text directly from the response
            text = getattr(resp, "output_text", "") or ""

            if not text:
                # Some SDK versions don’t provide `output_text`, so fall back
                text = str(resp)

            # Parse the response text into a Python dictionary
            return self._loads_or_trim_braces(text)

        except Exception:
            # If the Responses API fails for any reason, fall back to the older "Chat Completions" API
            chat = self.client.chat.completions.create(
                model=self.model,  # same model as above
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},  # force JSON output format
                seed=int(seed) if seed is not None else None,
            )

            # Get the generated JSON text from the chat response
            content = chat.choices[0].message.content

            # Parse the JSON string into a Python dictionary and return it
            return json.loads(content)
