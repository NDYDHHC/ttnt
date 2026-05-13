#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified script to sync forks using GitHub CLI.
This executes 'gh repo sync <owner>/<repo>' to trigger GitHub server-side sync.
By default it scans both ttnt-runtime/ThirdParty and ttnt-godot/Engine.
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import List


def get_workspace_root() -> Path:
    return Path(__file__).resolve().parent


def get_default_repo_dirs() -> List[Path]:
    workspace_root = get_workspace_root()
    return [
        (workspace_root / 'ttnt-runtime' / 'ThirdParty').resolve(),
        (workspace_root / 'ttnt-godot' / 'Engine').resolve(),
    ]


def format_repo_path(repo_path: Path) -> str:
    try:
        return str(repo_path.relative_to(get_workspace_root()))
    except ValueError:
        return str(repo_path)


def get_repo_slug(repo_path):
    """
    Get the 'owner/repo' slug from the 'origin' remote URL.
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode != 0:
            return None

        url = result.stdout.strip()

        match = re.search(r'github\.com[:/]([^/]+)/([^/\.]+)', url)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
        return None
    except Exception:
        return None


def sync_forks():
    repos = []
    for base_dir in get_default_repo_dirs():
        if not base_dir.is_dir():
            print(f"Error: repository directory not found: {base_dir}")
            sys.exit(1)
        repos.extend(d for d in base_dir.iterdir() if d.is_dir() and (d / ".git").exists())

    repos.sort()

    print(f"Found {len(repos)} repositories across default directories")
    print("-" * 50)

    for repo in repos:
        print(f"Processing {format_repo_path(repo)}...")

        slug = get_repo_slug(repo)
        if not slug:
            print(f"⚠️  [{format_repo_path(repo)}] Could not determine GitHub repository slug (checking origin remote)")
            print("   Skipping. Ensure 'origin' remote points to GitHub.")
            print("-" * 50)
            continue

        print(f"Syncing {slug}...")
        try:
            result = subprocess.run(
                ["gh", "repo", "sync", slug],
                cwd=repo,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )

            if result.returncode == 0:
                print(f"✅ [{format_repo_path(repo)}] Synced successfully")
            else:
                stderr_output = result.stderr.strip()
                print(f"❌ [{format_repo_path(repo)}] Sync failed (Exit code: {result.returncode})")
                if stderr_output:
                    print(f"   Error: {stderr_output}")

                if "403" in stderr_output and "access token" in stderr_output:
                    print("   Tip: Your GitHub token might lack permissions. Try running: gh auth refresh -s workflow")
                elif "No default remote" in stderr_output:
                    print("   Tip: Run 'gh repo set-default' in the repository.")

        except Exception as e:
            print(f"❌ [{format_repo_path(repo)}] System Error: {str(e)}")

        print("-" * 50)


if __name__ == "__main__":
    try:
        subprocess.run(["gh", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    except Exception:
        print("Error: 'gh' command not found. Please install GitHub CLI.")
        sys.exit(1)

    auth_check = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    if auth_check.returncode != 0:
        print("\n❌ Error: You are not logged into GitHub CLI.")
        print("Please run the following command to authenticate:")
        print("    gh auth login")
        print("-" * 50)
        sys.exit(1)

    sync_forks()