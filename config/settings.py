import sys
import json
import uuid
import os
import urllib3
from pathlib import Path
from rich.console import Console

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

APP_VERSION      = "0.0.6 (patch 1)"
APP_AUTHOR       = "SakerLy"
GITHUB_ZIP_URL   = "https://github.com/SakerLy/SupportDLPikPak/archive/refs/heads/main.zip"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/SakerLy/SupportDLPikPak/refs/heads/main/config/settings.py"
GITHUB_RELEASE_URL = "https://github.com/SakerLy/SupportDLPikPak/releases"

IS_FROZEN = getattr(sys, 'frozen', False)
BASE_DIR  = Path(sys.executable).parent if IS_FROZEN else Path(__file__).resolve().parent.parent

console = Console()

class Language:
    STRINGS = {
        "en": {
            "menu_title":     "PikPak Downloader",
            "menu_dev":       "Developed by SakerLy",
            "menu_1":         "Login PikPak Account",
            "menu_2":         "Download from Link",
            "menu_3":         "Settings (Proxy, Threads, Path)",
            "menu_4":         "Cache Manager",
            "menu_5":         "View Config",
            "menu_6":         "Manage Extra Accounts",
            "menu_0":         "Exit",
            "prompt_choice":  "Select Option",
            "login_header":   "LOGIN TO PIKPAK",
            "login_user":     "Email / Phone / Username",
            "login_pass":     "Password",
            "login_wait":     "Logging in...",
            "login_fail":     "✖ Login failed! Check your credentials.",
            "login_success":  "✓ Login successful!",
            "token_missing":  "✖ Refresh Token not found. Please Login first.",
            "set_header":     "SYSTEM SETTINGS",
            "set_proxy":      "Configure Proxy",
            "set_adv":        "Advanced (Workers, Path, Timeout)",
            "proxy_status":   "Proxy Status",
            "proxy_toggle":   "Enable/Disable Proxy?",
            "thread_prompt":  "Threads per file (Default 8)",
            "prem_status":    "Premium Mode",
            "prem_toggle":    "Use Premium Account to proxy ALL downloads?",
            "save_success":   "✓ Settings saved!",
            "worker_prompt":  "Max Concurrent Files",
            "path_prompt":    "Download Path",
            "timeout_prompt": "Timeout (seconds)",
            "cache_prompt":   "Use Cache?",
            "cache_info":     "CACHE INFORMATION",
            "cache_files":    "Files count",
            "cache_size":     "Total size",
            "cache_clear":    "Clear all cache?",
            "cache_cleared":  "✓ Cache cleared!",
            "input_link":     "Enter PikPak Link",
            "input_pwd":      "Password (if any)",
            "analyzing":      "➜ Analyzing folder structure...",
            "link_invalid":   "✖ Invalid URL!",
            "no_files":       "✖ No files found in this link.",
            "link_info":      "LINK INFORMATION",
            "total_files":    "Total Files",
            "total_size":     "Total Size",
            "dl_opt_1":       "Download All",
            "dl_opt_2":       "Select Files",
            "dl_opt_0":       "Cancel",
            "dl_complete":    "COMPLETED!",
            "dl_success":     "Success",
            "dl_skip":        "Skipped",
            "dl_error":       "Error",
            "update_check":   "Checking for updates...",
            "update_found":   "🚀 NEW UPDATE AVAILABLE",
            "update_ask_web": "Open browser to download now?",
            "update_ask_src": "Auto-update source code now?",
            "update_done":    "✓ Update successful! Restarting...",
            "update_fail":    "✖ Update failed",
            "global_stats":   "GLOBAL STATISTICS",
            "status_restore": "Restoring...",
            "status_check":   "Checking...",
            "status_getlink": "Get Link...",
            "status_dl":      "Multi-DL...",
            "status_clean":   "Deleting...",
            "acc_header":     "EXTRA ACCOUNTS",
            "acc_info":       "Each extra account adds ~11 MB/s to total speed.",
            "acc_list":       "Current accounts",
            "acc_add":        "Add extra account",
            "acc_remove":     "Remove extra account",
            "acc_test":       "Test all accounts",
            "acc_none":       "No extra accounts configured.",
            "acc_added":      "✓ Account added!",
            "acc_removed":    "✓ Account removed!",
            "acc_invalid":    "✖ Invalid index.",
            "acc_pool_size":  "Active accounts in pool",
        }
    }

    @classmethod
    def get(cls, key):
        return cls.STRINGS["en"].get(key, key)


class Config:
    BASE_DIR    = BASE_DIR
    CONFIG_FILE = BASE_DIR / "config.json"
    LOG_DIR     = BASE_DIR / "logs"
    LOG_FILE    = LOG_DIR / "pikpak_tool.log"

    REFRESH_TOKEN = ""; DEVICE_ID = ""; CAPTCHA_TOKEN = ""
    USE_PROXY = False; PROXY_TYPE = "http"; PROXY_HOST = ""
    PROXY_PORT = ""; PROXY_USERNAME = ""; PROXY_PASSWORD = ""
    FORCE_PREMIUM_MODE = False
    MAX_WORKERS        = 3
    DOWNLOAD_PATH_STR  = "downloads"
    TIMEOUT            = 30
    USE_CACHE          = True
    CONCURRENT_THREADS = 8
    EXTRA_ACCOUNTS: list = []

    @classmethod
    def get_download_dir(cls):
        cls.load_config()
        if os.path.isabs(cls.DOWNLOAD_PATH_STR):
            return Path(cls.DOWNLOAD_PATH_STR)
        return cls.BASE_DIR / cls.DOWNLOAD_PATH_STR

    @classmethod
    def get_proxy_dict(cls):
        if not cls.USE_PROXY: return None
        host = (cls.PROXY_HOST or "").strip()
        port = (cls.PROXY_PORT or "").strip()
        if not host or not port: return None
        ptype = (cls.PROXY_TYPE or "http").strip().lower()
        user  = (cls.PROXY_USERNAME or "").strip()
        pwd   = (cls.PROXY_PASSWORD or "").strip()
        if user:
            from urllib.parse import quote
            auth = f"{quote(user, safe='')}:{quote(pwd, safe='')}@"
        else:
            auth = ""
        url = f"{ptype}://{auth}{host}:{port}"
        return {"http": url, "https": url}

    @classmethod
    def test_proxy(cls) -> tuple:
        proxy = cls.get_proxy_dict()
        if not proxy: return False, "Proxy not configured"

        import requests as _req, urllib3 as _ul3
        _ul3.disable_warnings()
        session = _req.Session()
        session.proxies.update(proxy)
        session.verify = False

        is_socks = (cls.PROXY_TYPE or "").lower() in ("socks4", "socks5")
        try:
            test_url = "http://api.ipify.org" if is_socks else "http://www.gstatic.com/generate_204"
            session.get(test_url, timeout=10)
        except Exception as e:
            session.close()
            err = str(e)
            if "407" in err or "Proxy Authentication" in err: return False, "Proxy requires authentication"
            if "No module" in err and "socks" in err.lower(): return False, "Missing requests[socks] library"
            if "SOCKS" in err or "socks" in err.lower(): return False, f"SOCKS proxy type error ({cls.PROXY_TYPE})"
            return False, f"Connection failed: {e}"

        try:
            r  = session.get("https://api.ipify.org?format=json", timeout=10)
            ip = r.json().get("ip", "?")
            session.close()
            return True, f"OK — IP via proxy: {ip}"
        except Exception as e:
            session.close()
            err = str(e)
            if "SSLError" in err or "CONNECT" in err or "tunnel" in err.lower(): return False, "HTTPS tunnel not supported"
            if "407" in err or "Proxy Authentication" in err: return False, "Authentication required"
            if "timed out" in err.lower() or "Timeout" in err: return False, "Proxy timeout"
            return False, f"HTTPS failed: {e}"

    @classmethod
    def load_config(cls):
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                cls.REFRESH_TOKEN      = d.get("refresh_token",    "")
                cls.DEVICE_ID          = d.get("device_id",        "")
                cls.CAPTCHA_TOKEN      = d.get("captcha_token",    "")
                cls.MAX_WORKERS        = int(d.get("max_workers",  3))
                cls.DOWNLOAD_PATH_STR  = d.get("download_path",   "downloads")
                cls.TIMEOUT            = int(d.get("timeout",      30))
                cls.USE_CACHE          = d.get("use_cache",        True)

                cls.USE_PROXY          = d.get("use_proxy",        False)
                cls.PROXY_TYPE         = d.get("proxy_type",       "http")
                cls.PROXY_HOST         = d.get("proxy_host",       "")
                cls.PROXY_PORT         = d.get("proxy_port",       "")
                cls.PROXY_USERNAME     = d.get("proxy_username",   "")
                cls.PROXY_PASSWORD     = d.get("proxy_password",   "")
                cls.CONCURRENT_THREADS = int(d.get("concurrent_threads", 8))
                cls.FORCE_PREMIUM_MODE = d.get("force_premium_mode", False)
                cls.EXTRA_ACCOUNTS     = d.get("extra_accounts",   [])
            except: pass
        if not cls.DEVICE_ID:
            cls.DEVICE_ID = uuid.uuid4().hex

    @classmethod
    def save_config(cls):
        try:
            data = {
                "refresh_token":      cls.REFRESH_TOKEN,
                "device_id":          cls.DEVICE_ID,
                "captcha_token":      cls.CAPTCHA_TOKEN,
                "max_workers":        cls.MAX_WORKERS,
                "download_path":      cls.DOWNLOAD_PATH_STR,
                "timeout":            cls.TIMEOUT,
                "use_cache":          cls.USE_CACHE,

                "use_proxy":          cls.USE_PROXY,
                "proxy_type":         cls.PROXY_TYPE,
                "proxy_host":         cls.PROXY_HOST,
                "proxy_port":         cls.PROXY_PORT,
                "proxy_username":     cls.PROXY_USERNAME,
                "proxy_password":     cls.PROXY_PASSWORD,
                "concurrent_threads": cls.CONCURRENT_THREADS,
                "force_premium_mode": cls.FORCE_PREMIUM_MODE,
                "extra_accounts":     cls.EXTRA_ACCOUNTS,
            }
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except: return False

    @classmethod
    def migrate_config(cls):
        if not cls.CONFIG_FILE.exists(): return
        cls.load_config()
        cls.save_config()

    @classmethod
    def setup_dirs(cls):
        try: cls.get_download_dir().mkdir(parents=True, exist_ok=True)
        except: pass