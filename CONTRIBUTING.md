# Contributing to SkillForge

Thanks for helping make AI agents better engineers. 🎉

## Ways to contribute
- **Improve a skill:** sharper steps, a missing edge case, a better example.
- **Add a skill:** open a [Skill request](../../issues/new?template=skill-request.yml) first so we can agree on scope.
- **Report a problem:** a skill that triggers at the wrong time, gives bad advice, or a script bug.

## Development setup
No dependencies are needed beyond Python 3.8+ and Bash.

```bash
git clone https://github.com/meyshad/skillforge.git
cd skillforge
python3 scripts/validate.py          # structure and frontmatter checks
python3 -m unittest discover tests   # tests for bundled scripts
./scripts/install.sh --project       # try your changes in a local project
```

## Adding a skill
1. Pick the right plugin (or propose a new one in your issue).
2. Copy `template/SKILL.md` to `plugins/<plugin>/skills/<your-skill>/SKILL.md`.
3. Follow the [authoring guide](docs/writing-skills.md).
4. Add the skill to the catalog in `README.md`, update the skills badge count, and add a `CHANGELOG.md` entry.
5. Open a PR. CI must be green.

## Commit messages
We use [Conventional Commits](https://www.conventionalcommits.org/): `feat(security): add sbom skill`, `fix(install): handle spaces in paths`, `docs: clarify quick start`.

## Code of conduct
By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
