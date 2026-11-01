"""
Xperia Keyboard Universal Patcher Package
"""

from .manifest import remove_uses_library, patch_apk_manifest
from .verifier import verify_apk_compatibility

__all__ = ["remove_uses_library", "patch_apk_manifest", "verify_apk_compatibility"]
