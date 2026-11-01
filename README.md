# Sony Xperia™ Keyboard - Universal Port (Android 14 & 15 Ready)

[![Android](https://img.shields.io/badge/Android-4.4%20to%2015%20(Vanilla%20Ice%20Cream)-3DDC84?logo=android&logoColor=white)](#compatibility-matrix)
[![Architecture](https://img.shields.io/badge/Arch-arm64--v8a%20%7C%20armeabi--v7a-blue)](#architecture--hardware)
[![16KB Page Size](https://img.shields.io/badge/Android%2015-16%20KB%20Page%20Aligned-success)](#android-15--16-kb-page-size-readiness)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)](#building-from-source)

A clean, modern universal port of the legendary **Sony Xperia™ Keyboard** (`v8.0.A.0.110`), engineered and verified to install and run smoothly on modern Android versions (**Android 14 and Android 15**) across all major OEM brands (**Samsung, Xiaomi / HyperOS, Oppo / ColorOS, OnePlus, Vivo / OriginOS, Google Pixel**, and more).

---

## ✨ Features

- **SwiftKey-Powered Prediction Engine**: Accurate word completion, multilingual autocompletion, and personalized dictionary.
- **Classic Minimalist Xperia Design**: High-contrast, clean layout, tactile response, and iconic Sony styling.
- **Customization & Themes**: Light, Dark, Xperia Classic, and Accent themes, along with adjustable keyboard height.
- **One-Handed Mode**: Instant resizing and docking to the left or right for easy one-handed typing on modern large displays.
- **Swipe / Gesture Input (Trace Typing)**: Fluid and responsive swipe typing.
- **Symbols & Numeric Quick Access**: Long-press symbols, dedicated number row options, and full emoji support.
- **Full 64-bit ARM Support**: Native `arm64-v8a` binary included—fully compatible with Snapdragon 8 Gen 2 / Gen 3 / Gen 4, Google Tensor, and MediaTek Dimensity processors.

---

## 🛠️ The Technical Fix: Why Original APKs Failed

When attempting to install original Xperia Keyboard APKs on modern Android devices (such as the Samsung Galaxy S23 on Android 14), the installer failed with:
> *"App not installed as app isn't compatible with your phone"* (or `INSTALL_FAILED_MISSING_SHARED_LIBRARY`).

### 1. Missing Proprietary Sony Framework (`com.sony.device`)
The original `AndroidManifest.xml` included:
```xml
<uses-library android:name="com.sony.device" />
```
Because `android:required="false"` was omitted, Android's `PackageManagerService` treated Sony's proprietary framework library as **mandatory**. On non-Sony devices (Samsung, Pixel, Xiaomi, Oppo, Vivo), this library does not exist in `/system/framework/`, causing immediate installation failure.

**Our Fix**: We surgically excised the `<uses-library>` tag at the binary AXML byte level without decompiling resources, maintaining 100% of the internal layouts, dictionaries, and assets.

### 2. Android 14 & 15 Minimum Target SDK Compliance
- **Android 14** blocks installation of apps targeting SDK versions below 23.
- **Android 15** raises the platform installation threshold (`PLATFORM_MIN_SUPPORTED_TARGET_SDK_VERSION = 24`).
- This port targets **API 24 (Android 7.0)**. It passes Android 14 and 15 package installer verification out-of-the-box without requiring ADB bypass flags. Furthermore, targeting API 24 prevents modern strict runtime checks (such as API 31 `android:exported` and API 34 `RECEIVER_EXPORTED` crashes) from affecting legacy keyboard background services.

### 3. Android 15 & 16 KB Page Size Readiness
Android 15 introduces support for **16 KB memory page size** kernels (found in newer Snapdragon 8 Gen 3/4 and Tensor devices). Native shared libraries must have `PT_LOAD` segments aligned to at least 16 KB or 64 KB.
- `lib/arm64-v8a/libswiftkeysdk-java.so` was verified to have `align=0x10000` (**64 KB page alignment**), making it fully compatible with 16 KB Android 15 devices.

### 4. Modern Signature Schemes (v1 + v2 + v3)
Modern OEM package installers (especially Xiaomi HyperOS, Samsung One UI, and Google Pixel) reject packages signed solely with legacy v1 JAR signatures.
- This port is 4-byte zip-aligned and signed using **APK Signature Scheme v1, v2, and v3** with 2048-bit RSA keys.

---

## 📱 Compatibility Matrix

| Brand / OS | Supported Versions | Status | Notes |
| :--- | :--- | :---: | :--- |
| **Samsung (One UI)** | One UI 5 / 6 / 7 (Android 13, 14, 15) | **Supported** | Tested on Galaxy S23 (Snapdragon 8 Gen 2). Installs natively. |
| **Google Pixel** | Android 13, 14, 15 (Vanilla Ice Cream) | **Supported** | 64-bit ARM compliant; passes 16 KB page size kernel checks. |
| **Xiaomi / POCO / Redmi (HyperOS / MIUI)** | HyperOS 1.0+, MIUI 14 (Android 13, 14, 15) | **Supported** | Clean signature passes HyperOS Security Verification. |
| **Oppo / Realme (ColorOS)** | ColorOS 13 / 14 / 15 | **Supported** | `directBootAware` ensures responsiveness upon boot. |
| **OnePlus (OxygenOS)** | OxygenOS 13 / 14 / 15 | **Supported** | Smooth operation; gesture typing fully supported. |
| **Vivo / iQOO (FuntouchOS / OriginOS)** | FuntouchOS 13 / 14 / 15 | **Supported** | Enable auto-launch / background permission if prompted. |
| **Motorola / Nothing / Asus** | Android 13, 14, 15 | **Supported** | Standard AOSP input method binding. |

---

## 📥 Installation Guide

### Step 1: Download the Pre-built APK
Download the latest release from the [`release/`](release/) directory:
- **[`Xperia-Keyboard-Universal-v8.0.A.0.110.apk`](release/Xperia-Keyboard-Universal-v8.0.A.0.110.apk)**

### Step 2: Install on Your Device
1. Transfer the APK to your phone via Quick Share, USB, or Google Drive (or download directly from your mobile browser).
2. Open your device's **Files** or **Downloads** app and tap the APK to install.
3. If prompted with *"Install unknown apps"*, toggle **Allow from this source**.

### Step 3: Enable the Keyboard
> **Note**: Because this is an Input Method Editor (IME), it will not create a standalone icon in your home screen app drawer. Configure it via system settings:

#### **Samsung (One UI)**
1. Open **Settings** > **General management**.
2. Tap **Keyboard list and default**.
3. Turn on the toggle for **Xperia™ keyboard**.
4. Tap **Default keyboard** and select **Xperia™ keyboard**.

#### **Xiaomi / POCO / Redmi (HyperOS / MIUI)**
1. Open **Settings** > **Additional settings** > **Languages & input**.
2. Tap **Manage keyboards**.
3. Toggle on **Xperia™ keyboard**.
4. Tap **Current keyboard** and select **Xperia™ keyboard**.

#### **Google Pixel / Motorola / Nothing (Stock Android)**
1. Open **Settings** > **System** > **Languages & input** (or **Keyboard**).
2. Tap **On-screen keyboard** > **Manage on-screen keyboards**.
3. Enable **Xperia™ keyboard** and choose it as default.

#### **Oppo / OnePlus / Realme (ColorOS / OxygenOS)**
1. Open **Settings** > **System settings** (or **Additional settings**).
2. Tap **Keyboard & input method** > **Manage keyboards**.
3. Enable **Xperia™ keyboard**.

#### **Vivo / iQOO (Funtouch OS / OriginOS)**
1. Open **Settings** > **System** > **Languages & input**.
2. Tap **On-screen keyboard** > enable **Xperia™ keyboard**.

---

## 🏗️ Building from Source / Patching Your Own APK

The automated build pipeline handles binary manifest excision, zip alignment, signing, and compatibility auditing in a single step.

### Prerequisites
- Python 3.8+
- Android SDK Build-Tools (`zipalign` and `apksigner`)
- Java JDK / `keytool`

### Run the Build Pipeline

```bash
# Clone the repository
git clone https://github.com/your-username/xperia-keyboard-universal.git
cd xperia-keyboard-universal

# Run automated build (cross-platform)
python build.py

# Or on Windows PowerShell:
.\build.ps1
```

### Run Compatibility Audit Separately

```bash
python patcher/verifier.py release/Xperia-Keyboard-Universal-v8.0.A.0.110.apk
```

---

## 📂 Repository Structure

```text
├── .github/
│   └── workflows/
│       └── build.yml               # Automated GitHub Actions CI/CD pipeline
├── patcher/
│   ├── __init__.py
│   ├── manifest.py                 # Pure binary AXML patcher (zero 3rd-party dependencies)
│   └── verifier.py                 # Multi-brand & Android 14/15 compatibility audit suite
├── release/
│   └── Xperia-Keyboard-Universal-v8.0.A.0.110.apk  # Pre-built, signed, ready-to-install APK
├── build.py                        # Automated build & signing script
├── build.ps1                       # One-click Windows PowerShell build script
├── release.keystore                # Reusable signing keystore
├── .gitignore                      # Git ignore rules for build artifacts
├── LICENSE                         # MIT License & IP disclaimer
└── README.md                       # Documentation & installation guide
```

---

## ⚖️ Legal & Attribution

- **Sony Mobile Communications**: Original developer and copyright holder of the Xperia™ Keyboard app and SwiftKey integration.
- This project is an independent open-source patching toolkit distributed for compatibility and device interoperability under the **MIT License**.
