import openai
from git_massage.utils import print_error

SYSTEM_PROMPT = """You are a helpful assistant that writes semantic Git commit messages. You must output the message following the Conventional Commits specification. Format: <type>(<optional-scope>): <subject> Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert. Rules:

Use imperative mood ("add" not "added").

First line max 72 characters.

If the changes are significant, add a bulleted body description.

Do not output markdown code blocks (```). Just the raw message.
"""


def generate_message(diff: str, model: str, api_key: str) -> str:
    if not diff.strip():
        return ""

    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Generate a commit message for the following diff:\n\n{diff}",
                },
            ],
            temperature=1,
        )

        content = response.choices[0].message.content
        return content.strip() if content else ""

    except openai.AuthenticationError:
        print_error("Invalid OpenAI API Key. Please check your configuration.")
        raise
    except Exception as e:
        print_error(f"Error generating message: {e}")
        raise
