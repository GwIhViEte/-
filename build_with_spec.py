#!/usr/bin/env python3
"""
Build script for AI Novel Generator using the spec file.
This ensures consistent packaging with proper module inclusion.
"""

import os
import sys
import subprocess
import shutil
import time


def main():
    print("=" * 60)
    print("  AI Novel Generator - Spec File Build Script")
    print("=" * 60)

    # Check that spec file exists
    spec_file = "AI_Novel_Generator.spec"
    if not os.path.exists(spec_file):
        print(f"ERROR: {spec_file} not found!")
        msg1 = "Please ensure AI_Novel_Generator.spec"
        msg2 = "exists in the project root."
        print(f"{msg1} {msg2}")
        sys.exit(1)

    # Check PyInstaller is installed
    try:
        import PyInstaller  # type: ignore[import-untyped]

        print(f"✓ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pyinstaller>=6.0.0",
            ]
        )
        print("✓ PyInstaller installed")

    # Clean previous build
    print("\nCleaning previous build artifacts...")
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            print(f"  Removing {dir_name}/")
            shutil.rmtree(dir_name)

    # Build with PyInstaller
    print(f"\nBuilding with {spec_file}...")
    print("This may take several minutes...\n")

    start_time = time.time()

    cmd = ["pyinstaller", "--clean", "--noconfirm", spec_file]

    print("Command:", " ".join(cmd))
    result = subprocess.run(cmd)

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print(f"✓ Build completed successfully in {minutes}m {seconds}s")
        print("=" * 60)

        if os.path.exists("dist/AI_Novel_Generator"):
            output_path = os.path.abspath("dist/AI_Novel_Generator")
            print(f"\nOutput location: {output_path}")

            # Copy documentation
            docs = ["README.md", "LICENSE.txt"]
            for doc in docs:
                if os.path.exists(doc):
                    shutil.copy(doc, "dist/AI_Novel_Generator/")
                    print(f"  Copied {doc}")

            # Create empty config file
            config_path = "dist/AI_Novel_Generator/novel_generator_config.json"
            if not os.path.exists(config_path):
                import json

                default_config = {
                    "api_key": "",
                    "model": "gemini-2.0-flash",
                    "language": "中文",
                    "max_workers": 3,
                    "context_length": 100000,
                    "novel_type": "奇幻冒险",
                    "target_length": 20000,
                    "num_novels": 1,
                    "auto_summary": True,
                    "auto_summary_interval": 10000,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "generate_cover": False,
                    "generate_music": False,
                }
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                print("  Created default config")

            print("\n✓ Build package is ready!")
        else:
            print("\nWARNING: dist/AI_Novel_Generator directory not found")
    else:
        print("\n" + "=" * 60)
        print("✗ Build failed!")
        print("=" * 60)
        print("\nPlease check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
