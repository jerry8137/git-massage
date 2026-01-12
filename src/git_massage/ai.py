import openai
from typing import Optional
from git_massage.utils import print_error

SYSTEM_PROMPT = """You are a helpful assistant that writes semantic Git commit messages. You must output the message following the Conventional Commits specification. Format: <type>(<optional-scope>): <subject> Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert. Rules:

Use imperative mood ("add" not "added").

First line max 72 characters.

If the changes are significant, add a bulleted body description.

Do not output markdown code blocks (```). Just the raw message.
"""

SYSTEM_PROMPT_GITMOJI = """You are a helpful assistant that writes semantic Git commit messages.
You must output the message following the Conventional Commits specification.

Format: <emoji> <type>(<optional-scope>): <subject>

Types and their emojis:
- feat: ✨ (new feature)
- fix: 🐛 (bug fix)
- docs: 📝 (documentation)
- style: 🎨 (formatting, code style)
- refactor: ♻️ (code refactoring)
- perf: ⚡️ (performance improvement)
- test: ✅ (adding/updating tests)
- build: 🔧 (build system, dependencies)
- ci: 👷 (CI configuration)
- chore: 🔧 (maintenance tasks)
- revert: ⏪️ (reverting changes)

Additional context emojis (use when applicable):
- 🔒️ for security-related fixes
- 💥 for breaking changes
- 🔥 for removing code/files
- 🚧 for work in progress

Rules:
- Always start with the appropriate emoji
- Use imperative mood ("add" not "added")
- First line max 72 characters (including emoji)
- If changes are significant, add a bulleted body description
- Do not output markdown code blocks. Just the raw message.
"""


def generate_message(
    diff: str,
    model: str,
    api_key: str,
    hint: Optional[str] = None,
    use_gitmoji: bool = True,
) -> str:
    if not diff.strip():
        return ""

    client = openai.OpenAI(api_key=api_key)

    # Select prompt based on gitmoji setting
    prompt = SYSTEM_PROMPT_GITMOJI if use_gitmoji else SYSTEM_PROMPT

    # Build user message with optional hint
    user_content = f"Generate a commit message for the following diff:\n\n{diff}"
    if hint:
        user_content += f"\n\nAdditional guidance: {hint}"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_content},
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
