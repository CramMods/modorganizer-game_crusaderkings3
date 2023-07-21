import re
from typing import List


class Descriptor:
    _version: str = ""
    _name: str = ""
    _tags: List[str] = []
    _supported_version: str = ""

    def __init__(self, descriptor_path: str):
        with open(
            descriptor_path, "r", encoding="utf-8-sig"
        ) as descriptor_file:
            content = descriptor_file.read()

        match = re.search(r"^version=\"(.+)\"$", content, re.MULTILINE)
        if match:
            self._version = match.group(1)

        match = re.search(r"tags={\n*(.*)\n*}", content, re.DOTALL)
        if match:
            tags_chunk = match.group(1)
            self._tags = re.findall(
                r"^\s*\"(.+)\"\s*$", tags_chunk, re.MULTILINE
            )

        match = re.search(r"^name=\"(.+)\"$", content, re.MULTILINE)
        if match:
            self._name = match.group(1)

        match = re.search(
            r"^supported_version=\"(.+)\"$", content, re.MULTILINE
        )
        if match:
            self._supported_version = match.group(1)

    def version(self) -> str:
        return self._version

    def tags(self) -> List[str]:
        return self._tags

    def name(self) -> str:
        return self._name

    def supported_version(self) -> str:
        return self._supported_version
