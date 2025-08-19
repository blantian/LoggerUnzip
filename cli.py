import argparse
import os
import json
from datetime import datetime
from binascii import unhexlify

try:
    import ex
except Exception as e:  # pragma: no cover - executed only when import fails
    print(f"Failed to import decryption module: {e}")
    raise SystemExit(1)


def _parse_bytes(value: str) -> bytes:
    """Parse a command line string into bytes.

    Values that look like hex (32 hex digits) are decoded; otherwise the
    string is encoded as UTF-8.
    """
    value = value.strip()
    if len(value) == 32:
        try:
            return unhexlify(value)
        except Exception:
            pass
    return value.encode()


def _output_name(file_path: str) -> str:
    """Derive an output file name from the input."""
    name = os.path.basename(file_path)
    if name.isdigit():
        ts = int(name)
        dt = datetime.fromtimestamp(ts / 1000)
        return dt.strftime("%Y%m%d_%H_%M_%S.txt")
    return name + ".txt"


def _format_output(path: str) -> None:
    """Format the decrypted log file into human-readable text."""
    formatted: list[str] = []
    with open(path, "rb") as fh:
        for line in fh:
            try:
                line = line.decode("utf-8").strip()
            except UnicodeDecodeError:
                continue
            if not line:
                continue
            try:
                log = json.loads(line)
                ts2 = log.get("l")
                if ts2:
                    ts_fmt = datetime.fromtimestamp(ts2 / 1000).strftime(
                        "%Y-%m-%d %H:%M:%S.%f"
                    )[:-3]
                else:
                    ts_fmt = ""
                thread_id = log.get("i", "")
                tag = log.get("n", "")
                content = log.get("c", "").strip()
                formatted.append(f"{ts_fmt} {thread_id} {tag} {content}")
            except Exception as e:  # pragma: no cover - formatting failures
                formatted.append(f"Parse error: {e} {line}")
    with open(path, "w", encoding="utf-8") as fh:
        for line in formatted:
            fh.write(line + "\n")


def decrypt_file(file_path: str, out_dir: str | None, key: bytes, iv: bytes) -> str:
    """Decrypt a single log file and return the output path."""
    base_dir = os.path.dirname(file_path)
    if out_dir is None:
        out_dir = os.path.join(base_dir, "logs2")
    os.makedirs(out_dir, exist_ok=True)
    out_name = _output_name(file_path)
    out_path = os.path.join(out_dir, out_name)
    if os.path.exists(out_path):
        print(f"Skip {file_path}, output exists: {out_path}")
        return out_path
    ex.logan_parse(file_path, out_path, key, iv)
    _format_output(out_path)
    print(f"Decrypted {file_path} -> {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Decrypt log files from CLI")
    parser.add_argument("files", nargs="+", help="Log files to decrypt")
    parser.add_argument(
        "-o",
        "--out",
        default=None,
        help="Output directory (default: logs2 in each file's directory)",
    )
    parser.add_argument(
        "-k",
        "--key",
        default="1234567890abcdef",
        help="AES key (16-byte hex or text)",
    )
    parser.add_argument(
        "-i",
        "--iv",
        default="abcdef1234567890",
        help="AES IV (16-byte hex or text)",
    )
    args = parser.parse_args()

    key = _parse_bytes(args.key)
    iv = _parse_bytes(args.iv)

    for file_path in args.files:
        decrypt_file(file_path, args.out, key, iv)


if __name__ == "__main__":
    main()
