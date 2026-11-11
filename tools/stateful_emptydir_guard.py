#!/usr/bin/env python3
"""Offline Kustomize guard for stateful paths mounted from emptyDir."""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_EXCEPTION_FIELDS = (
    "workload",
    "namespace",
    "container",
    "mountPath",
    "volume",
    "path",
    "reason",
    "owner",
    "issue",
    "reviewer",
    "created_at",
)


def scalar(value: str) -> str:
    return value.strip().strip('"\'')


def load_contract(path: Path) -> dict:
    try:
        contract = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid contract: {error}") from error
    paths = contract.get("stateful_paths")
    if not isinstance(paths, list) or not paths or not all(isinstance(path, str) and path.startswith("/") for path in paths):
        raise ValueError("stateful_paths must be a non-empty list of absolute paths")
    exceptions = contract.get("exceptions", [])
    if not isinstance(exceptions, list):
        raise ValueError("exceptions must be a list")
    for index, exception in enumerate(exceptions):
        if not isinstance(exception, dict):
            raise ValueError(f"exception {index} must be an object")
        missing = [field for field in REQUIRED_EXCEPTION_FIELDS if not isinstance(exception.get(field), str) or not exception[field].strip()]
        if missing:
            raise ValueError(f"exception {index} missing required fields: {', '.join(missing)}")
        if exception["path"] not in paths:
            raise ValueError(f"exception {index} path is not stateful: {exception['path']}")
    corrections = contract.get("corrections", [])
    if not isinstance(corrections, list):
        raise ValueError("corrections must be a list")
    for index, correction in enumerate(corrections):
        if not isinstance(correction, dict):
            raise ValueError(f"correction {index} must be an object")
        missing = [field for field in ("workload", "path", "issue") if not isinstance(correction.get(field), str) or not correction[field].strip()]
        if missing:
            raise ValueError(f"correction {index} missing required fields: {', '.join(missing)}")
        if correction["path"] not in paths:
            raise ValueError(f"correction {index} path is not stateful: {correction['path']}")
    return contract


def render(target: Path, kustomize: str) -> str:
    result = subprocess.run([kustomize, "build", str(target)], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "kustomize build failed")
    return result.stdout


def documents(rendered: str):
    return [document for document in re.split(r"^---\s*$", rendered, flags=re.MULTILINE) if document.strip()]


def parse_document(document: str) -> dict:
    lines = document.splitlines()
    kind = ""
    name = ""
    namespace = "default"
    metadata_indent = None
    volumes = {}
    mounts = []
    mode = None
    mode_indent = -1
    current_volume = None
    current_mount = None
    current_container = ""
    container_indent = None

    for line in lines:
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped in {"containers:", "initContainers:"}:
            container_indent = indent
            current_container = ""
            continue
        if container_indent is not None and indent < container_indent:
            container_indent = None
            current_container = ""
        elif container_indent is not None and indent == container_indent:
            match = re.match(r"-\s+name:\s*(.+)$", stripped)
            if match:
                current_container = scalar(match.group(1))
            elif stripped.startswith("- "):
                current_container = ""
        elif container_indent is not None and indent == container_indent + 2:
            match = re.match(r"name:\s*(.+)$", stripped)
            if match:
                current_container = scalar(match.group(1))
        if indent == 0 and stripped.startswith("kind:"):
            kind = scalar(stripped.split(":", 1)[1])
        if indent == 0 and stripped == "metadata:":
            metadata_indent = indent
            continue
        if metadata_indent is not None and indent <= metadata_indent and stripped != "metadata:":
            metadata_indent = None
        if metadata_indent is not None and indent == metadata_indent + 2 and stripped.startswith("name:"):
            name = scalar(stripped.split(":", 1)[1])
        if metadata_indent is not None and indent == metadata_indent + 2 and stripped.startswith("namespace:"):
            namespace = scalar(stripped.split(":", 1)[1])

        if stripped == "volumes:":
            mode, mode_indent, current_volume, current_mount = "volumes", indent, None, None
            continue
        if stripped == "volumeMounts:":
            mode, mode_indent, current_mount = "mounts", indent, None
            continue
        if mode and indent < mode_indent:
            mode, current_volume, current_mount = None, None, None
        if mode == "volumes":
            match = re.match(r"-\s+name:\s*(.+)$", stripped)
            if match:
                current_volume = scalar(match.group(1))
                volumes.setdefault(current_volume, {"empty_dir": False})
            elif stripped.startswith("- "):
                current_volume = "__pending_empty_dir__" if stripped.startswith("- emptyDir:") else None
            elif stripped.startswith("emptyDir:"):
                if current_volume:
                    volumes[current_volume]["empty_dir"] = True
                else:
                    current_volume = "__pending_empty_dir__"
            elif current_volume == "__pending_empty_dir__" and stripped.startswith("name:"):
                current_volume = scalar(stripped.split(":", 1)[1])
                volumes[current_volume] = {"empty_dir": True}
        elif mode == "mounts":
            match = re.match(r"-\s+name:\s*(.+)$", stripped)
            if match:
                current_mount = {"container": current_container, "name": scalar(match.group(1)), "mount_path": ""}
                mounts.append(current_mount)
            elif stripped.startswith("- "):
                current_mount = {"container": current_container, "name": "", "mount_path": ""}
                mounts.append(current_mount)
                if stripped.startswith("- mountPath:"):
                    current_mount["mount_path"] = scalar(stripped.split(":", 1)[1])
            elif current_mount and stripped.startswith("mountPath:"):
                current_mount["mount_path"] = scalar(stripped.split(":", 1)[1])
            elif current_mount and stripped.startswith("name:"):
                current_mount["name"] = scalar(stripped.split(":", 1)[1])
    return {"workload": f"{kind}/{name}", "namespace": namespace, "volumes": volumes, "mounts": mounts}


def stateful_path(path: str, paths: list[str]) -> str | None:
    for candidate in paths:
        if path == candidate or path.startswith(candidate + "/"):
            return candidate
    return None


def exception_identity(entry: dict) -> tuple[str, str, str, str, str, str]:
    return (
        entry["workload"],
        entry["namespace"],
        entry["container"],
        entry["mountPath"],
        entry["volume"],
        entry["path"],
    )


def run(target: Path, contract: dict, kustomize: str) -> dict:
    exceptions = {}
    for entry in contract["exceptions"]:
        identity = exception_identity(entry)
        exceptions.setdefault(identity, []).append(entry)
    corrections = {(entry["workload"], entry["path"]): entry["issue"] for entry in contract.get("corrections", [])}
    violations, allowed = [], []
    for document in documents(render(target, kustomize)):
        parsed = parse_document(document)
        for mount in parsed["mounts"]:
            path = stateful_path(mount["mount_path"], contract["stateful_paths"])
            volume = parsed["volumes"].get(mount["name"], {})
            if not path or not volume.get("empty_dir"):
                continue
            item = {
                "workload": parsed["workload"],
                "namespace": parsed["namespace"],
                "container": mount["container"],
                "mountPath": mount["mount_path"],
                "path": path,
                "volume": mount["name"],
                "correction": corrections.get((parsed["workload"], path)),
            }
            matches = exceptions.get((item["workload"], item["namespace"], item["container"], item["mountPath"], item["volume"], item["path"]), [])
            if len(matches) == 1:
                exception = matches[0]
                allowed.append(item | {"reason": exception["reason"], "owner": exception["owner"], "issue": exception["issue"], "reviewer": exception["reviewer"], "created_at": exception["created_at"]})
            elif len(matches) > 1:
                violations.append(item | {"error": "ambiguous exception rules"})
            else:
                violations.append(item)
    return {"target": str(target), "violations": violations, "allowed_by_design": allowed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--contract", type=Path, default=Path("contracts/stateful-paths.json"))
    parser.add_argument("--kustomize", default=shutil.which("kustomize") or "kustomize")
    args = parser.parse_args()
    try:
        contract = load_contract(args.contract)
        inventory = run(args.target, contract, args.kustomize)
        inventory["status"] = "pass" if not inventory["violations"] else "fail"
    except (ValueError, RuntimeError) as error:
        inventory = {"status": "error", "error": str(error)}
    print(json.dumps(inventory, indent=2, sort_keys=True))
    return 0 if inventory["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
