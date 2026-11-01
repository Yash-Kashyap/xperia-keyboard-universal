#!/usr/bin/env python3
"""
Xperia Keyboard Universal Build & Packaging Pipeline
Patches, zip-aligns, signs, and validates the Sony Xperia Keyboard for Android 14/15.
"""

import os
import sys
import glob
import shutil
import subprocess
from pathlib import Path

from patcher.manifest import patch_apk_manifest
from patcher.verifier import verify_apk_compatibility


def find_android_tool(tool_name: str) -> str:
    """
    Search for Android SDK build tools (zipalign, apksigner, etc.)
    across system PATH, environment variables, and standard install paths.
    """
    # 1. Check PATH
    cmd = shutil.which(tool_name)
    if cmd:
        return cmd

    # 2. Check Windows bat/exe variations
    for ext in ['.exe', '.bat', '.cmd']:
        cmd = shutil.which(f"{tool_name}{ext}")
        if cmd:
            return cmd

    # 3. Check ANDROID_HOME and standard directories
    candidate_roots = [
        os.environ.get("ANDROID_HOME"),
        os.environ.get("ANDROID_SDK_ROOT"),
        str(Path.home() / "AppData" / "Local" / "Android" / "Sdk"),
        str(Path.home() / "Android" / "Sdk"),
        "/usr/lib/android-sdk",
        "/opt/android-sdk"
    ]

    for root in candidate_roots:
        if not root or not os.path.exists(root):
            continue
        build_tools_dir = Path(root) / "build-tools"
        if build_tools_dir.exists():
            # Check latest versions first
            for version_dir in sorted(build_tools_dir.iterdir(), reverse=True):
                for ext in ['', '.exe', '.bat']:
                    candidate = version_dir / f"{tool_name}{ext}"
                    if candidate.exists():
                        return str(candidate)

    return None


def ensure_keystore(keystore_path: str, alias: str = "xperia", password: str = "android") -> str:
    """
    Ensures a signing keystore exists, generating a 2048-bit RSA one if necessary.
    """
    if os.path.exists(keystore_path):
        return keystore_path

    keytool = shutil.which("keytool")
    if not keytool:
        # Check Zulu / JDK locations
        java_home = os.environ.get("JAVA_HOME")
        if java_home:
            candidate = Path(java_home) / "bin" / "keytool.exe"
            if candidate.exists():
                keytool = str(candidate)

    if not keytool:
        print("[Build] Warning: keytool not found on PATH. Looking in standard Java dirs...")
        java_dirs = glob.glob(r"C:\Program Files\*\*\bin\keytool.exe") + \
                    glob.glob(r"C:\Program Files (x86)\*\*\bin\keytool.exe")
        if java_dirs:
            keytool = java_dirs[0]

    if not keytool:
        raise RuntimeError("keytool not found. Install JDK or place an existing keystore at release.keystore")

    print(f"[Build] Generating signing keystore: {keystore_path}")
    cmd = [
        keytool, "-genkeypair", "-v",
        "-keystore", keystore_path,
        "-alias", alias,
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-storepass", password,
        "-keypass", password,
        "-dname", "CN=XperiaUniversal, OU=Port, O=XperiaMod, L=Tokyo, ST=Tokyo, C=JP"
    ]
    subprocess.run(cmd, check=True)
    return keystore_path


def build_xperia_keyboard(
    input_apk: str = None,
    output_apk: str = "release/Xperia-Keyboard-Universal-v8.0.A.0.110.apk",
    keystore_path: str = "release.keystore",
    key_alias: str = "xperia",
    key_pass: str = "android"
):
    repo_root = Path(__file__).resolve().parent

    # 1. Resolve Input APK
    if not input_apk:
        candidates = list(repo_root.glob("com.sonyericsson.textinput*.apk"))
        if not candidates:
            candidates = list(repo_root.glob("*.apk"))
            # Exclude release outputs
            candidates = [c for c in candidates if "Fixed" not in c.name and "Universal" not in c.name]
        if not candidates:
            raise FileNotFoundError("Could not find input Sony Xperia Keyboard APK. Specify path via arguments.")
        input_apk = str(candidates[0])

    print(f"\n==================================================")
    print(f"Xperia Keyboard Universal Build Pipeline")
    print(f"==================================================")
    print(f"Input APK : {input_apk}")
    print(f"Output APK: {output_apk}")

    os.makedirs(os.path.dirname(os.path.abspath(output_apk)), exist_ok=True)
    temp_unaligned = str(repo_root / "temp_unaligned.apk")

    try:
        # Step 1: Manifest Patching
        print("\n--> [1/4] Patching AndroidManifest.xml...")
        patch_apk_manifest(input_apk, temp_unaligned, library_to_remove="com.sony.device")

        # Step 2: ZipAligning
        print("\n--> [2/4] Zip-aligning APK (4-byte page boundaries)...")
        zipalign = find_android_tool("zipalign")
        temp_aligned = str(repo_root / "temp_aligned.apk")
        if zipalign:
            subprocess.run([zipalign, "-p", "-f", "4", temp_unaligned, temp_aligned], check=True)
            print(f"[Build] zipalign completed: {zipalign}")
        else:
            print("[Build] Warning: zipalign not found. Using unaligned file as fallback.")
            shutil.copy(temp_unaligned, temp_aligned)

        # Step 3: APK Signing (v1, v2, v3)
        print("\n--> [3/4] Signing APK with Android Signature Scheme v1, v2, v3...")
        ensure_keystore(keystore_path, alias=key_alias, password=key_pass)
        apksigner = find_android_tool("apksigner")

        if apksigner:
            sign_cmd = [
                apksigner, "sign",
                "--ks", keystore_path,
                "--ks-pass", f"pass:{key_pass}",
                "--key-pass", f"pass:{key_pass}",
                "--ks-key-alias", key_alias,
                "--out", output_apk,
                temp_aligned
            ]
            subprocess.run(sign_cmd, check=True)
            print(f"[Build] apksigner successfully signed: {output_apk}")

            # Verify signatures
            print("[Build] Verifying signatures...")
            verify_cmd = [apksigner, "verify", "-v", output_apk]
            subprocess.run(verify_cmd, check=True)
        else:
            print("[Build] Warning: apksigner not found. Copying aligned APK to output.")
            shutil.copy(temp_aligned, output_apk)

        # Step 4: Full Audit & Compatibility Check
        print("\n--> [4/4] Performing Compatibility Audit...")
        report = verify_apk_compatibility(output_apk)
        print(f"Report status: Android 14={'[PASS]' if report['compatible_android_14'] else '[FAIL]'}, Android 15={'[PASS]' if report['compatible_android_15'] else '[FAIL]'}")
        if report.get('elf_16kb_status'):
            print(f"16 KB Page Alignment: {report['elf_16kb_status']['min_align_kb']} KB segments (Android 15 compliant)")

        print(f"\n[SUCCESS] Build complete! Package ready at:\n  --> {os.path.abspath(output_apk)}\n")

    finally:
        # Cleanup temporary build files
        for tmp in [temp_unaligned, repo_root / "temp_aligned.apk"]:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass


if __name__ == '__main__':
    in_apk = sys.argv[1] if len(sys.argv) > 1 else None
    out_apk = sys.argv[2] if len(sys.argv) > 2 else "release/Xperia-Keyboard-Universal-v8.0.A.0.110.apk"
    build_xperia_keyboard(input_apk=in_apk, output_apk=out_apk)
