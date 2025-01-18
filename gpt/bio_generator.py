import openai


class BioGenerator:
    def __init__(self, api_key):
        openai.api_key = api_key

    def generate_bio(self, bio_examples, prompt="Generate a dating bio based on the following examples:"):
        examples_text = "\n".join(bio_examples)
        full_prompt = f"{prompt}\n\n{examples_text}\n\nBio:"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "You are an assistant that generates dating bios based on examples provided."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=50,
            temperature=0.7,
        )

        bio = response['choices'][0]['message']['content'].strip()
        return bio
