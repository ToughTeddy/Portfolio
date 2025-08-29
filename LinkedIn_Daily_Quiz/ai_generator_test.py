from openai import OpenAI
import my_info as me

client = OpenAI(api_key=me.OPENAI_KEY)

response = client.responses.create(
    model="gpt-5",
    input="Please tell me if you received this question?"
)

print(response.output_text)