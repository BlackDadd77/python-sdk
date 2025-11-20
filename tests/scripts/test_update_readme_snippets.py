"""Tests for update_readme_snippets.py script."""

import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from update_readme_snippets import get_language_from_extension, process_snippet_block  # noqa: E402


class TestGetLanguageFromExtension:
    """Test the get_language_from_extension function."""

    def test_python_extension(self):
        """Test Python file extension."""
        assert get_language_from_extension("example.py") == "python"
        assert get_language_from_extension("path/to/file.py") == "python"

    def test_shell_extensions(self):
        """Test shell script extensions."""
        assert get_language_from_extension("script.sh") == "bash"
        assert get_language_from_extension("script.bash") == "bash"

    def test_html_extensions(self):
        """Test HTML extensions."""
        assert get_language_from_extension("page.html") == "html"
        assert get_language_from_extension("page.htm") == "html"

    def test_json_extension(self):
        """Test JSON extension."""
        assert get_language_from_extension("config.json") == "json"

    def test_ruby_extension(self):
        """Test Ruby extension."""
        assert get_language_from_extension("script.rb") == "ruby"

    def test_yaml_extensions(self):
        """Test YAML extensions."""
        assert get_language_from_extension("config.yml") == "yaml"
        assert get_language_from_extension("config.yaml") == "yaml"

    def test_case_insensitive(self):
        """Test that extension detection is case insensitive."""
        assert get_language_from_extension("FILE.PY") == "python"
        assert get_language_from_extension("FILE.SH") == "bash"
        assert get_language_from_extension("FILE.JSON") == "json"

    def test_unknown_extension(self):
        """Test unknown extension returns empty string."""
        assert get_language_from_extension("file.txt") == ""
        assert get_language_from_extension("file.unknown") == ""
        assert get_language_from_extension("file") == ""


class TestProcessSnippetBlock:
    """Test the process_snippet_block function."""

    def test_python_snippet_processing(self, tmp_path):
        """Test processing a Python snippet."""
        # Create a test Python file
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        # Create a mock match object
        import re

        readme_content = f"""<!-- snippet-source {test_file} -->
```python
old content
```

_Full example: [{test_file}](url)_
<!-- /snippet-source -->"""

        pattern = r"^(\s*)<!-- snippet-source ([^\s]+) -->\n" r"(.*?)" r"^\1<!-- /snippet-source -->"
        match = re.search(pattern, readme_content, flags=re.MULTILINE | re.DOTALL)

        result = process_snippet_block(match, check_mode=False)

        assert "```python" in result
        assert "print('hello')" in result
        assert f"<!-- snippet-source {test_file} -->" in result
        assert "<!-- /snippet-source -->" in result

    def test_shell_snippet_processing(self, tmp_path):
        """Test processing a shell snippet."""
        # Create a test shell file
        test_file = tmp_path / "test.sh"
        test_file.write_text("#!/bin/bash\necho 'hello'")

        import re

        readme_content = f"""<!-- snippet-source {test_file} -->
<!-- /snippet-source -->"""

        pattern = r"^(\s*)<!-- snippet-source ([^\s]+) -->\n" r"(.*?)" r"^\1<!-- /snippet-source -->"
        match = re.search(pattern, readme_content, flags=re.MULTILINE | re.DOTALL)

        result = process_snippet_block(match, check_mode=False)

        assert "```bash" in result
        assert "#!/bin/bash" in result
        assert "echo 'hello'" in result

    def test_json_snippet_processing(self, tmp_path):
        """Test processing a JSON snippet."""
        # Create a test JSON file
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')

        import re

        readme_content = f"""<!-- snippet-source {test_file} -->
<!-- /snippet-source -->"""

        pattern = r"^(\s*)<!-- snippet-source ([^\s]+) -->\n" r"(.*?)" r"^\1<!-- /snippet-source -->"
        match = re.search(pattern, readme_content, flags=re.MULTILINE | re.DOTALL)

        result = process_snippet_block(match, check_mode=False)

        assert "```json" in result
        assert '"key": "value"' in result

    def test_yaml_snippet_processing(self, tmp_path):
        """Test processing a YAML snippet."""
        # Create a test YAML file
        test_file = tmp_path / "test.yml"
        test_file.write_text("key: value")

        import re

        readme_content = f"""<!-- snippet-source {test_file} -->
<!-- /snippet-source -->"""

        pattern = r"^(\s*)<!-- snippet-source ([^\s]+) -->\n" r"(.*?)" r"^\1<!-- /snippet-source -->"
        match = re.search(pattern, readme_content, flags=re.MULTILINE | re.DOTALL)

        result = process_snippet_block(match, check_mode=False)

        assert "```yaml" in result
        assert "key: value" in result

    def test_html_snippet_processing(self, tmp_path):
        """Test processing an HTML snippet."""
        # Create a test HTML file
        test_file = tmp_path / "test.html"
        test_file.write_text("<html><body>Hello</body></html>")

        import re

        readme_content = f"""<!-- snippet-source {test_file} -->
<!-- /snippet-source -->"""

        pattern = r"^(\s*)<!-- snippet-source ([^\s]+) -->\n" r"(.*?)" r"^\1<!-- /snippet-source -->"
        match = re.search(pattern, readme_content, flags=re.MULTILINE | re.DOTALL)

        result = process_snippet_block(match, check_mode=False)

        assert "```html" in result
        assert "<html><body>Hello</body></html>" in result

    def test_ruby_snippet_processing(self, tmp_path):
        """Test processing a Ruby snippet."""
        # Create a test Ruby file
        test_file = tmp_path / "test.rb"
        test_file.write_text("puts 'hello'")

        import re

        readme_content = f"""<!-- snippet-source {test_file} -->
<!-- /snippet-source -->"""

        pattern = r"^(\s*)<!-- snippet-source ([^\s]+) -->\n" r"(.*?)" r"^\1<!-- /snippet-source -->"
        match = re.search(pattern, readme_content, flags=re.MULTILINE | re.DOTALL)

        result = process_snippet_block(match, check_mode=False)

        assert "```ruby" in result
        assert "puts 'hello'" in result

    def test_missing_file(self, tmp_path):
        """Test handling of missing file."""
        test_file = tmp_path / "nonexistent.py"

        import re

        readme_content = f"""<!-- snippet-source {test_file} -->
old content
<!-- /snippet-source -->"""

        pattern = r"^(\s*)<!-- snippet-source ([^\s]+) -->\n" r"(.*?)" r"^\1<!-- /snippet-source -->"
        match = re.search(pattern, readme_content, flags=re.MULTILINE | re.DOTALL)

        result = process_snippet_block(match, check_mode=False)

        # Should return the original content when file is missing
        assert result == match.group(0)
