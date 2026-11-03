"""Prompt manager: versioned templates, validation, rollback. Offline."""
from __future__ import annotations

import hashlib
import string
from dataclasses import dataclass, field


@dataclass(frozen=True)
class PromptVersion:
    name: str
    version: int
    template: str
    sha: str  # content hash for audit/log correlation

    @property
    def variables(self) -> set[str]:
        return {f for _, f, _, _ in string.Formatter().parse(self.template) if f}


@dataclass
class PromptManager:
    _store: dict[str, list[PromptVersion]] = field(default_factory=dict)
    _active: dict[str, int] = field(default_factory=dict)

    def register(self, name: str, template: str, activate: bool = True) -> PromptVersion:
        versions = self._store.setdefault(name, [])
        if versions and versions[-1].template == template:
            return versions[-1]  # identical content: no new version
        pv = PromptVersion(name, len(versions) + 1, template,
                           hashlib.sha256(template.encode()).hexdigest()[:8])
        versions.append(pv)
        if activate:
            self._active[name] = pv.version
        return pv

    def get(self, name: str, version: int | None = None) -> PromptVersion:
        if name not in self._store:
            raise KeyError(f"no prompt named {name!r}")
        v = version or self._active[name]
        if not 1 <= v <= len(self._store[name]):
            raise KeyError(f"{name} has no version {v}")
        return self._store[name][v - 1]

    def rollback(self, name: str, version: int) -> None:
        self.get(name, version)  # validates
        self._active[name] = version

    def render(self, name: str, version: int | None = None, **kwargs: str) -> tuple[str, str]:
        pv = self.get(name, version)
        missing = pv.variables - kwargs.keys()
        if missing:
            raise ValueError(f"missing variables: {sorted(missing)}")
        extra = kwargs.keys() - pv.variables
        if extra:
            raise ValueError(f"unexpected variables: {sorted(extra)}")
        return pv.template.format(**kwargs), f"{name}@v{pv.version}:{pv.sha}"


if __name__ == "__main__":
    pm = PromptManager()
    pm.register("classify", "Give the HS code for: {product}")
    pm.register("classify", "You are a customs expert. Give HS code + reason for: {product}")
    text, tag = pm.render("classify", product="LED bulb")
    print(tag, "->", text)
    pm.rollback("classify", 1)
    print(pm.render("classify", product="LED bulb")[1])
    try:
        pm.render("classify")
    except ValueError as e:
        print("error:", e)
