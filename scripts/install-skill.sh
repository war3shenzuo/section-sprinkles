#!/usr/bin/env bash

set -euo pipefail

script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repository_root="$(cd "${script_directory}/.." && pwd -P)"
source_skill="${repository_root}/skills/section-sprinkles"
target='codex'
destination=''
target_was_set='false'

show_help() {
  printf '%s\n' \
    'Install the Section Sprinkles Skill for AI coding tools.' \
    '' \
    'Usage:' \
    '  bash scripts/install-skill.sh [--target TOOL]' \
    '  bash scripts/install-skill.sh --destination PATH' \
    '' \
    'Options:' \
    '  --target TOOL       codex (default), claude-code, workbuddy, or all.' \
    '  --destination PATH  Install to an exact Skill directory for another tool.' \
    '  -h, --help          Show this help message.'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      if [[ $# -lt 2 || -z "$2" ]]; then
        printf '%s\n' 'Error: --target requires a tool name.' >&2
        exit 2
      fi
      if [[ -n "$destination" ]]; then
        printf '%s\n' 'Error: --target and --destination cannot be used together.' >&2
        exit 2
      fi
      target="$2"
      target_was_set='true'
      shift 2
      ;;
    --destination)
      if [[ $# -lt 2 || -z "$2" ]]; then
        printf '%s\n' 'Error: --destination requires a path.' >&2
        exit 2
      fi
      if [[ "$target_was_set" == 'true' ]]; then
        printf '%s\n' 'Error: --target and --destination cannot be used together.' >&2
        exit 2
      fi
      destination="$2"
      target='custom'
      shift 2
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      printf 'Error: unknown argument: %s\n\n' "$1" >&2
      show_help >&2
      exit 2
      ;;
  esac
done

if [[ ! -f "${source_skill}/SKILL.md" ]]; then
  printf 'Error: Skill source not found: %s\n' "$source_skill" >&2
  exit 1
fi

if ! grep -q '^name: section-sprinkles$' "${source_skill}/SKILL.md"; then
  printf 'Error: invalid Skill metadata in %s\n' "${source_skill}/SKILL.md" >&2
  exit 1
fi

install_one() {
  local tool="$1"
  local install_path="$2"
  local destination_parent
  local staging_directory
  local staged_skill
  local backup_path=''

  destination_parent="$(dirname "$install_path")"
  mkdir -p "$destination_parent"

  staging_directory="$(mktemp -d "${destination_parent}/.section-sprinkles-install.XXXXXX")"
  staged_skill="${staging_directory}/section-sprinkles"
  cp -R "$source_skill" "$staged_skill"

  if [[ -e "$install_path" || -L "$install_path" ]]; then
    backup_path="${install_path}.backup-$(date '+%Y%m%d-%H%M%S')-$$"
    mv "$install_path" "$backup_path"
  fi

  if ! mv "$staged_skill" "$install_path"; then
    if [[ -n "$backup_path" && -e "$backup_path" ]]; then
      mv "$backup_path" "$install_path"
    fi
    printf 'Error: could not install the Skill at %s\n' "$install_path" >&2
    exit 1
  fi

  rmdir "$staging_directory"

  printf '\n✅ Section Sprinkles Skill installed for %s.\n' "$tool"
  printf '   Installed at: %s\n' "$install_path"
  if [[ -n "$backup_path" ]]; then
    printf '   Previous version: %s\n' "$backup_path"
  fi
}

codex_destination="${HOME:?HOME is required}/.agents/skills/section-sprinkles"
claude_destination="${HOME:?HOME is required}/.claude/skills/section-sprinkles"
workbuddy_destination="${HOME:?HOME is required}/.codebuddy/skills/section-sprinkles"

case "$target" in
  codex)
    install_one 'Codex' "$codex_destination"
    ;;
  claude-code|claude)
    install_one 'Claude Code' "$claude_destination"
    ;;
  workbuddy|codebuddy)
    install_one 'WorkBuddy / CodeBuddy Code' "$workbuddy_destination"
    ;;
  all)
    install_one 'Codex' "$codex_destination"
    install_one 'Claude Code' "$claude_destination"
    install_one 'WorkBuddy / CodeBuddy Code' "$workbuddy_destination"
    ;;
  custom)
    install_one 'custom tool' "$destination"
    ;;
  *)
    printf 'Error: unsupported target: %s\n\n' "$target" >&2
    show_help >&2
    exit 2
    ;;
esac

cat <<'USAGE'

Open the Section Sprinkles repository before using the Skill. Examples:

  Codex:
  $section-sprinkles 帮我挑选 3 个低信息密度、带人物照片的中文首屏参考。

  Claude Code:
  /section-sprinkles 查找适合 B2B SaaS、包含图表且语气理性的参考图。

  WorkBuddy / CodeBuddy Code:
  使用 section-sprinkles，对比 pricing-04 和 pricing-19 并推荐一个方向。

  Text-only localization:
  使用 section-sprinkles，把 hero-07 中的文字翻译成中文；除文字外不要改变任何视觉元素。

If a newly created top-level Skill directory is not detected in the current
session, restart the AI tool once.
USAGE
