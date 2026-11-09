"""Unit tests for the bundled skill scripts. Run: python3 -m unittest discover tests"""
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(rel_path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # required by dataclasses on Python < 3.10
    spec.loader.exec_module(module)
    return module


secrets = load("plugins/security/skills/secret-scanner/scripts/scan_secrets.py", "scan_secrets")
patterns = load("plugins/security/skills/security-audit/scripts/scan_patterns.py", "scan_patterns")
changelog = load("plugins/docs/skills/changelog-keeper/scripts/changelog.py", "changelog")

# Fake credentials are assembled at runtime so this file never contains a literal token.
FAKE_AWS = "AKIA" + "Q7XK2MZ4P9WB3N6R"
FAKE_GH = "ghp" + "_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8"


class SecretScannerTests(unittest.TestCase):
    def rules(self, line):
        return [r for r, _, _ in secrets.scan_line(line)]

    def test_detects_known_token_formats(self):
        self.assertIn("aws-access-key-id", self.rules(f'key = "{FAKE_AWS}"'))
        self.assertIn("github-token", self.rules(f"TOKEN={FAKE_GH}"))
        self.assertIn("private-key-block", self.rules("-----BEGIN " + "RSA PRIVATE KEY-----"))
        self.assertIn("credentials-in-url", self.rules("postgres://admin:s3cretPass@db.internal:5432/app"))  # secretscan:ignore

    def test_generic_rule_uses_entropy_and_ignores_placeholders(self):
        self.assertIn("generic-secret-assignment", self.rules('api_key = "Zx9Lq2Vb7Nw4Rt8Ys1Kp"'))  # secretscan:ignore
        self.assertEqual(self.rules('api_key = "your_api_key_here_please"'), [])
        self.assertEqual(self.rules('password = "aaaaaaaaaaaaaaaa"'), [])

    def test_ignore_marker_suppresses(self):
        self.assertEqual(self.rules(f'k = "{FAKE_AWS}"  # secretscan:ignore'), [])

    def test_masks_output(self):
        previews = [p for _, _, p in secrets.scan_line(f'"{FAKE_AWS}"')]
        self.assertTrue(previews and FAKE_AWS not in previews[0])

    def test_scan_tree_skips_node_modules(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "app.py").write_text(f'KEY = "{FAKE_AWS}"\n')
            os.makedirs(Path(tmp, "node_modules"))
            Path(tmp, "node_modules", "dep.js").write_text(f'k="{FAKE_AWS}"\n')
            findings = secrets.scan_tree(tmp)
            self.assertEqual([f.file for f in findings], ["app.py"])
            self.assertEqual(findings[0].line, 1)


class PatternScannerTests(unittest.TestCase):
    def ids(self, code, ext):
        return {h.rule for h in patterns.scan_text(code, ext, "x" + ext)}

    def test_python_rules(self):
        self.assertIn("py-shell-true", self.ids("subprocess.run(cmd, shell=True)", ".py"))
        self.assertIn("py-yaml-load", self.ids("yaml.load(data)", ".py"))
        self.assertNotIn("py-yaml-load", self.ids("yaml.load(data, Loader=yaml.SafeLoader)", ".py"))
        self.assertIn("py-fstring-sql", self.ids('cur.execute(f"SELECT * FROM t WHERE id={x}")', ".py"))

    def test_js_rules_do_not_fire_on_python(self):
        self.assertIn("js-innerhtml", self.ids("el.innerHTML = html", ".ts"))
        self.assertNotIn("js-innerhtml", self.ids("el.innerHTML = html", ".py"))

    def test_nosec_suppresses(self):
        self.assertEqual(self.ids("eval(x)  # nosec", ".py"), set())


class ChangelogTests(unittest.TestCase):
    def test_parse_conventional_commit(self):
        c = changelog.parse_commit("abc1234def", "feat(api): add search endpoint", "Closes #42")
        self.assertEqual((c.type, c.scope, c.description, c.refs), ("feat", "api", "Add search endpoint", ["42"]))
        self.assertFalse(c.breaking)

    def test_breaking_changes(self):
        self.assertTrue(changelog.parse_commit("a", "feat!: drop node 16").breaking)
        c = changelog.parse_commit("b", "refactor: new config", "BREAKING CHANGE: config moved to yaml")
        self.assertTrue(c.breaking)
        self.assertEqual(c.breaking_note, "config moved to yaml")

    def test_non_conventional_is_ignored(self):
        self.assertIsNone(changelog.parse_commit("a", "Update stuff"))

    def test_suggest_bump(self):
        p = changelog.parse_commit
        self.assertEqual(changelog.suggest_bump("v1.2.3", [p("a", "fix: x")]), "1.2.4")
        self.assertEqual(changelog.suggest_bump("v1.2.3", [p("a", "feat: x")]), "1.3.0")
        self.assertEqual(changelog.suggest_bump("v1.2.3", [p("a", "feat!: x")]), "2.0.0")
        self.assertEqual(changelog.suggest_bump("0.4.1", [p("a", "feat!: x")]), "0.5.0")

    def test_render_groups_sections_and_hides_chores(self):
        p = changelog.parse_commit
        out = changelog.render("1.0.0", "2026-01-01", [p("a" * 40, "feat: new"), p("b" * 40, "fix: bug"),
                                                      p("c" * 40, "chore: tidy")])
        self.assertIn("## [1.0.0] - 2026-01-01", out)
        self.assertIn("### Added", out)
        self.assertIn("### Fixed", out)
        self.assertNotIn("Tidy", out)


if __name__ == "__main__":
    unittest.main()
