#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git操作脚本
默认对ttnt-runtime/ThirdParty和ttnt-godot/Engine目录下的每个库执行指定的git操作

使用示例:
    python repo_foreach.py "git status"
    python repo_foreach.py "git fetch --all"
    python repo_foreach.py "git log --oneline -5"
    python repo_foreach.py "git checkout main"
    python repo_foreach.py status              # 也可以省略git前缀
"""

import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Sequence, Tuple


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


def is_pull_command(git_command: str) -> bool:
    stripped = git_command.strip()
    return stripped == 'git pull' or stripped.startswith('git pull ')


def is_detached_head(repo_path: Path) -> bool:
    result = subprocess.run(
        ['git', 'symbolic-ref', '--quiet', '--short', 'HEAD'],
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    return result.returncode != 0


class GitOperationManager:
    def __init__(self, base_dirs: Sequence[str] | None = None):
        """
        初始化Git操作管理器

        Args:
            base_dirs: 仓库目录路径列表，默认为ttnt-runtime/ThirdParty和ttnt-godot/Engine
        """
        if base_dirs is None:
            self.base_dirs = get_default_repo_dirs()
        else:
            self.base_dirs = [Path(base_dir).absolute() for base_dir in base_dirs]

        print("工作目录:")
        for base_dir in self.base_dirs:
            print(f"  - {base_dir}")

    def find_git_repositories(self) -> List[Path]:
        """
        查找所有包含.git目录的子目录

        Returns:
            包含git仓库的目录列表
        """
        git_repos = []

        for base_dir in self.base_dirs:
            if not base_dir.is_dir():
                raise FileNotFoundError(f"仓库目录不存在: {base_dir}")

            for item in base_dir.iterdir():
                if item.is_dir() and (item / '.git').exists():
                    git_repos.append(item)

        git_repos.sort()
        return git_repos

    def execute_git_command(self, repo_path: Path, git_command: str) -> Tuple[bool, str, str]:
        """
        在指定的仓库中执行git命令

        Args:
            repo_path: git仓库路径
            git_command: 完整的git命令字符串

        Returns:
            (成功标志, 标准输出, 错误输出)
        """
        try:
            result = subprocess.run(
                git_command,
                cwd=repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                shell=True,
                timeout=60
            )

            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

        except subprocess.TimeoutExpired:
            return False, "", "命令执行超时 (60秒)"
        except Exception as e:
            return False, "", f"执行出错: {str(e)}"

    def run_git_operation(self, git_command: str, skip_on_error: bool = True):
        """
        对所有git仓库执行指定的git操作

        Args:
            git_command: 完整的git命令字符串
            skip_on_error: 是否在遇到错误时跳过继续执行
        """
        repos = self.find_git_repositories()

        if not repos:
            print("❌ 没有找到任何git仓库")
            return

        print(f"🔍 找到 {len(repos)} 个git仓库")
        print(f"📝 执行命令: {git_command}")
        print("=" * 60)

        if is_pull_command(git_command):
            detached_repos = [repo for repo in repos if is_detached_head(repo)]
            if detached_repos:
                print("⚠️  检测到 detached HEAD，git pull 无法自动确定要合并的分支。")
                print("这些目录由 submodule 或 vendor 仓库管理时，这种状态是预期行为。")
                print("建议改用仓库根目录下的 `git submodule update --remote --recursive`，")
                print("或者先在目标子仓库中 checkout 到一个本地分支后再执行 pull。")
                print("受影响仓库: " + ', '.join(format_repo_path(repo) for repo in detached_repos))
                return

        success_count = 0
        error_count = 0

        for repo in repos:
            repo_name = format_repo_path(repo)
            print(f"\n📁 {repo_name}")
            print("-" * 40)

            success, stdout, stderr = self.execute_git_command(repo, git_command)

            if success:
                success_count += 1
                if stdout:
                    lines = stdout.split('\n')
                    if len(lines) > 20:
                        print('\n'.join(lines[:15]))
                        print(f"... (省略 {len(lines) - 15} 行)")
                    else:
                        print(stdout)
                else:
                    print("✅ 命令执行成功 (无输出)")
            else:
                error_count += 1
                print("❌ 命令执行失败:")
                if stderr:
                    print(f"错误信息: {stderr}")
                if stdout:
                    print(f"输出信息: {stdout}")

                if not skip_on_error:
                    print(f"\n❌ 在 {repo_name} 中遇到错误，停止执行")
                    break

        print("\n" + "=" * 60)
        print("📊 执行结果统计:")
        print(f"   ✅ 成功: {success_count}")
        print(f"   ❌ 失败: {error_count}")
        print(f"   📁 总计: {len(repos)}")


def main():
    parser = argparse.ArgumentParser(
          description="默认对ttnt-runtime/ThirdParty和ttnt-godot/Engine目录下的所有git仓库执行指定操作",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s "git status"                     # 查看所有仓库状态
  %(prog)s "git fetch --all"                # 获取所有远程分支
  %(prog)s "git log --oneline -5"           # 查看最近5次提交
  %(prog)s "git checkout main"              # 切换到main分支
  %(prog)s "git reset --hard HEAD"          # 重置到HEAD
  %(prog)s "git clean -fd"                  # 清理未跟踪文件
      %(prog)s status                           # 默认扫描 ThirdParty 和 Engine
      %(prog)s status --dir ttnt-godot/Engine   # 仅扫描指定目录
        """
    )

    parser.add_argument(
        'command',
        nargs='+',
        help='要执行的完整git命令（可包含git前缀，也可省略）'
    )

    parser.add_argument(
        '--dir', '-d',
        action='append',
        default=None,
        help='仓库目录路径，可重复传入；默认扫描ttnt-runtime/ThirdParty和ttnt-godot/Engine'
    )

    parser.add_argument(
        '--stop-on-error',
        action='store_true',
        help='遇到错误时停止执行 (默认跳过错误继续执行)'
    )

    parser.add_argument(
        '--list-repos',
        action='store_true',
        help='仅列出找到的git仓库，不执行命令'
    )

    args = parser.parse_args()

    manager = GitOperationManager(args.dir)

    if args.list_repos:
        repos = manager.find_git_repositories()
        if repos:
            print(f"找到 {len(repos)} 个git仓库:")
            for repo in repos:
                print(f"  📁 {format_repo_path(repo)}")
        else:
            print("❌ 没有找到任何git仓库")
        return

    command_parts = args.command

    if command_parts[0] != 'git':
        command_parts.insert(0, 'git')

    git_command = ' '.join(command_parts)

    try:
        manager.run_git_operation(git_command, skip_on_error=not args.stop_on_error)
    except KeyboardInterrupt:
        print("\n\n⚠️  操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()