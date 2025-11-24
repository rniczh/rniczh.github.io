#!/usr/bin/env python3
"""
Blog Responsive CSS Patcher
"""

import os
import re
from pathlib import Path

PATCH_CSS = """
        /* Responsive handling */
        @media screen and (max-width: 1023px) {
            body.quarkdown-plain > main {
                min-width: 80%;
                max-width: 100%;
            }
        }
"""


def is_patched(content):
    """Check if the file is already patched"""
    if "/* Responsive handling */" in content:
        return True

    return re.search(
        r"body\.quarkdown-plain\s*>\s*main\s*\{[^}]*min-width:\s*0", content, re.DOTALL
    )


def find_insertion_point(content):
    """Find the insertion point for the CSS patch"""
    pattern = r"(body\.quarkdown-plain\s*\{[^}]*margin:[^}]*\})"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        return match.end()

    style_match = re.search(r"<style>\s*", content)
    if style_match:
        return style_match.end()

    return None


def patch_file(file_path, content):
    """Patch the file"""
    try:
        insertion_point = find_insertion_point(content)
        if insertion_point is None:
            print(f"Cannot find the insertion point: {file_path}")
            return False

        new_content = content[:insertion_point] + PATCH_CSS + content[insertion_point:]

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"Patched: {file_path}")
        return True

    # pylint: disable=broad-exception-caught
    except Exception as e:
        print(f"Failed to patch {file_path}: {str(e)}")
        return False


def main():
    """main"""
    script_dir = Path(__file__).parent
    blog_dir = script_dir / "blog"

    if not blog_dir.exists():
        print(f"Cannot find the blog directory: {blog_dir}")
        return

    html_files = []
    for root, _, files in os.walk(blog_dir):
        if root == str(blog_dir):
            continue

        if "index.html" in files:
            html_file = Path(root) / "index.html"
            try:
                with open(html_file, "r", encoding="utf-8") as f:
                    preview = f.read(300)
                    if "quarkdown" in preview or "quarkdown-plain" in preview:
                        html_files.append(html_file)
            # pylint: disable=broad-exception-caught
            except Exception:
                pass

    if not html_files:
        print("No blog articles to process")
        return

    patched_count = 0
    skipped_count = 0
    failed_count = 0

    for html_file in html_files:
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
            if is_patched(content):
                print(f"Skipped (already patched): {html_file}")
                skipped_count += 1
                continue
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(f"Failed to read {html_file}: {str(e)}")
            failed_count += 1
            continue

        result = patch_file(html_file, content)

        if result is True:
            patched_count += 1
        else:
            failed_count += 1

    print("\n" + "=" * 60)
    print("Statistics:")
    print(f"    Patched: {patched_count} files")
    print(f"    Skipped: {skipped_count} files")
    print(f"    Failed: {failed_count} files")
    print(f"    Total: {len(html_files)} files")


if __name__ == "__main__":
    main()
