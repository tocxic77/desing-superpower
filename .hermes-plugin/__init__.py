import os
import re
from pathlib import Path

BOOTSTRAP_MARKER = "design-superpowers:using-design-superpowers bootstrap for hermes"


def _skills_dir() -> str:
    """Locate the stock skills/ tree for either supported install layout.

    - git-clone install (`hermes plugins install <repo>`): the plugin
      dir is the repo root, so `.hermes-plugin/` and `skills/` are siblings and
      this module resolves `../skills`.
    - flattened install (plugin files copied to the plugin dir root): `skills/`
      sits next to this module.

    Raises loudly when neither matches — a bootstrap that silently skips is how
    a broken install masquerades as a working one.
    """
    here = os.path.dirname(os.path.realpath(__file__))
    candidates = (
        os.path.realpath(os.path.join(here, "..", "skills")),
        os.path.realpath(os.path.join(here, "skills")),
    )
    for cand in candidates:
        if os.path.isfile(os.path.join(cand, "core", "design-orchestration", "SKILL.md")):
            return cand
    raise RuntimeError(
        "design-superpowers plugin: cannot find the skills/ tree "
        f"(looked at {candidates}). Reinstall with "
        "`hermes plugins install <repo>`."
    )


def _strip_frontmatter(content: str) -> str:
    match = re.match(r"^---\n[\s\S]*?\n---\n([\s\S]*)$", content)
    return (match.group(1) if match else content).strip()


def _frontmatter_value(content: str, key: str) -> str:
    """Return a flat ``key: value`` scalar from a SKILL.md frontmatter block.

    Hermes reads a skill's description from ``register_skill``'s ``description``
    argument, which defaults to "" — registering only the path left every stock
    skill with a blank description in the skill catalogue, so the model had
    nothing to select on. Stock frontmatter is a flat block of single-line
    scalars, so a line scan covers it without a YAML dependency.
    """
    match = re.match(r"^---\n([\s\S]*?)\n---\n", content)
    if not match:
        return ""
    for line in match.group(1).splitlines():
        name, sep, value = line.partition(":")
        if sep and name.strip() == key:
            return value.strip().strip('"\'')
    return ""


def _build_bootstrap(skills_dir: str) -> str:
    # Load the core bootstrap skill (using-design-superpowers equivalent)
    bootstrap_skill_path = os.path.join(skills_dir, "core", "design-orchestration", "SKILL.md")
    if os.path.isfile(bootstrap_skill_path):
        with open(bootstrap_skill_path, encoding="utf-8") as f:
            body = _strip_frontmatter(f.read())
    else:
        body = "Design Superpowers core skill not found."

    # Load tool mapping reference if it exists
    tools_path = os.path.join(skills_dir, "core", "design-orchestration", "references", "hermes-tools.md")
    tool_mapping = ""
    if os.path.isfile(tools_path):
        with open(tools_path, encoding="utf-8") as f:
            tool_mapping = f.read().strip()

    return (
        f"<EXTREMELY_IMPORTANT>\n"
        f"{BOOTSTRAP_MARKER}\n\n"
        f"You have design superpowers.\n\n"
        f"The design-orchestration skill content is included below and is already "
        f"loaded for this Hermes session. Follow it now. "
        f"Do not try to load design-orchestration again.\n\n"
        f"{body}\n\n"
        f"## Loading Design Superpowers Skills on Hermes\n\n"
        f"Design Superpowers skills are registered with Hermes' native skill loader: "
        f'invoke one with `skill_view("design-superpowers:skill-name")` '
        f'(for example `skill_view("design-superpowers:conversion-strategy")`). '
        f"If a namespaced lookup returns 'not found', read the skill file "
        f"directly instead:\n"
        f'`read_file("{skills_dir}/<category>/<skill-name>/SKILL.md")`\n\n'
        f"The design-superpowers skills directory is: `{skills_dir}`\n\n"
        f"{tool_mapping}\n"
        f"</EXTREMELY_IMPORTANT>"
    )


def register(ctx):
    skills_dir = _skills_dir()
    bootstrap = _build_bootstrap(skills_dir)

    # Register every stock skill with Hermes' native loader so skill_view can
    # load them on demand. Standard markdown; no conversion (plugin guide).
    # register_skill requires a pathlib.Path — a str raises AttributeError and
    # hermes silently disables the whole plugin (verified 2026-07-23).
    for category in sorted(os.listdir(skills_dir)):
        category_path = os.path.join(skills_dir, category)
        if not os.path.isdir(category_path):
            continue
        for name in sorted(os.listdir(category_path)):
            skill_md = os.path.join(category_path, name, "SKILL.md")
            if os.path.isfile(skill_md):
                with open(skill_md, encoding="utf-8") as f:
                    description = _frontmatter_value(f.read(), "description")
                # Use namespaced name: category/skill-name
                full_name = f"{category}/{name}"
                ctx.register_skill(full_name, Path(skill_md), description=description)

    # pre_llm_call returning {"context": ...} is the documented injection path
    # (on_session_start return values are ignored, and ctx.inject_message
    # refuses from that hook — verified empirically 2026-07-23). The context is
    # appended to the first turn's user message. delegate_task children run
    # with platform="subagent" and an empty history, so every child's first
    # turn would otherwise get the controller bootstrap too.
    def pre_llm_call(
        session_id=None,
        user_message=None,
        conversation_history=None,
        is_first_turn=None,
        model=None,
        platform=None,
        **kwargs,
    ):
        if is_first_turn and platform != "subagent":
            return {"context": bootstrap}
        return None

    ctx.register_hook("pre_llm_call", pre_llm_call)