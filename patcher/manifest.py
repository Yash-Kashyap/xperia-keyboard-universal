"""
Binary Android XML (AXML) Manifest Patcher
Excises vendor-specific <uses-library> dependencies without decompilation.
"""

import struct
import zipfile
import tempfile
import os
import shutil


def remove_uses_library(axml_bytes: bytes, library_name: str = "com.sony.device") -> bytes:
    """
    Surgically remove a <uses-library android:name="..."/> tag from a binary AndroidManifest.xml.
    Returns the modified binary AXML bytes.
    """
    magic, file_size = struct.unpack('<II', axml_bytes[0:8])
    if magic != 0x00080003:
        raise ValueError(f"Invalid AXML magic: 0x{magic:08x} (expected 0x00080003)")

    # Chunk 1: String Pool
    offset = 8
    chunk_type, header_size, chunk_size = struct.unpack('<HHI', axml_bytes[offset:offset + 8])
    if chunk_type != 0x0001:
        raise ValueError(f"Expected String Pool chunk (0x0001), got 0x{chunk_type:04x}")

    string_count, style_count, flags, strings_start, styles_start = struct.unpack(
        '<IIIII', axml_bytes[offset + 8:offset + 28]
    )
    is_utf8 = bool(flags & (1 << 8))
    offsets = [
        struct.unpack('<I', axml_bytes[offset + 28 + i * 4:offset + 28 + (i + 1) * 4])[0]
        for i in range(string_count)
    ]
    pool_data = axml_bytes[offset + strings_start:]
    strings = []
    for off in offsets:
        if is_utf8:
            pos = off
            u16len = pool_data[pos]
            pos += 1
            if u16len & 0x80:
                u16len = ((u16len & 0x7f) << 8) | pool_data[pos]
                pos += 1
            u8len = pool_data[pos]
            pos += 1
            if u8len & 0x80:
                u8len = ((u8len & 0x7f) << 8) | pool_data[pos]
                pos += 1
            s = pool_data[pos:pos + u8len].decode('utf-8', errors='replace')
        else:
            pos = off
            u16len = struct.unpack('<H', pool_data[pos:pos + 2])[0]
            pos += 2
            if u16len & 0x8000:
                u16len = ((u16len & 0x7fff) << 16) | struct.unpack('<H', pool_data[pos:pos + 2])[0]
                pos += 2
            s = pool_data[pos:pos + u16len * 2].decode('utf-16le', errors='replace')
        strings.append(s)

    tag_idx = strings.index('uses-library') if 'uses-library' in strings else None
    lib_idx = strings.index(library_name) if library_name in strings else None

    if tag_idx is None or lib_idx is None:
        print(f"[Patcher] '{library_name}' or 'uses-library' not found in string pool. Manifest unchanged.")
        return axml_bytes

    offset += chunk_size

    # Skip Resource Map (0x0180) if present
    chunk_type, header_size, chunk_size = struct.unpack('<HHI', axml_bytes[offset:offset + 8])
    if chunk_type == 0x0180:
        offset += chunk_size

    start_tag_off = None
    start_tag_len = None
    end_tag_off = None
    end_tag_len = None

    while offset < len(axml_bytes):
        chunk_type, header_size, chunk_size = struct.unpack('<HHI', axml_bytes[offset:offset + 8])

        if chunk_type == 0x0102:  # START_TAG
            # header_size is usually 16. attrExt is at offset + 16.
            ns_idx, name_idx, attr_start, attr_size, attr_count = struct.unpack(
                '<IIHHH', axml_bytes[offset + 16:offset + 30]
            )
            if name_idx == tag_idx:
                cur_attr = offset + 16 + attr_start
                for _ in range(attr_count):
                    a_ns, a_name, a_raw_val = struct.unpack('<III', axml_bytes[cur_attr:cur_attr + 12])
                    if a_raw_val == lib_idx:
                        start_tag_off = offset
                        start_tag_len = chunk_size
                        break
                    cur_attr += attr_size
        elif chunk_type == 0x0103:  # END_TAG
            ns_idx, name_idx = struct.unpack('<II', axml_bytes[offset + 16:offset + 24])
            if name_idx == tag_idx and start_tag_off is not None and end_tag_off is None:
                end_tag_off = offset
                end_tag_len = chunk_size
                break

        offset += chunk_size

    if start_tag_off is None or end_tag_off is None:
        print(f"[Patcher] Target <uses-library android:name=\"{library_name}\"/> node not found. Manifest unchanged.")
        return axml_bytes

    # Slice out the START_TAG and END_TAG chunks
    cut_end = end_tag_off + end_tag_len
    new_data = bytearray(axml_bytes[:start_tag_off] + axml_bytes[cut_end:])

    # Update file size in header (bytes 4..8)
    struct.pack_into('<I', new_data, 4, len(new_data))
    print(f"[Patcher] Successfully excised '{library_name}' ({cut_end - start_tag_off} bytes removed).")
    return bytes(new_data)


def patch_apk_manifest(input_apk: str, output_apk: str, library_to_remove: str = "com.sony.device"):
    """
    Reads input_apk, extracts and patches AndroidManifest.xml,
    strips old META-INF signatures, and writes output_apk.
    """
    print(f"[Patcher] Reading: {input_apk}")
    with zipfile.ZipFile(input_apk, 'r') as zin:
        orig_manifest = zin.read('AndroidManifest.xml')
        patched_manifest = remove_uses_library(orig_manifest, library_to_remove)

        print(f"[Patcher] Writing repackaged APK: {output_apk}")
        with zipfile.ZipFile(output_apk, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                # Strip old META-INF signature files
                if item.filename.startswith('META-INF/') and (
                    item.filename.endswith('.SF') or
                    item.filename.endswith('.RSA') or
                    item.filename.endswith('.DSA') or
                    item.filename.endswith('.MF')
                ):
                    continue

                if item.filename == 'AndroidManifest.xml':
                    zout.writestr(item, patched_manifest)
                else:
                    zout.writestr(item, zin.read(item.filename))

    print(f"[Patcher] APK repackaged successfully: {output_apk}")
