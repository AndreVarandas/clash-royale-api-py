"""The base every model shares.

Wire format is camelCase JSON; Python sees warm, familiar snake_case.
Unknown fields are kept (the API grows faster than the docs), so you can
always reach for ``model.extra_field`` or ``model.raw``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ClashRoyaleModel(BaseModel):
    """Base class for all response models."""

    model_config = ConfigDict(
        extra="allow",  # keep fields the docs don't know about yet
        populate_by_name=True,  # accept both snake_case and camelCase input
        alias_generator=to_camel,  # expose snake_case, speak camelCase
    )

    @property
    def raw(self) -> dict[str, Any]:
        """This object as a plain dict, back in the API's camelCase shape.

        Useful when you need a field the library doesn't model — though with
        ``extra`` attributes, you usually don't. Note this is a re-serialization
        of the validated model, not the byte-for-byte original response.
        """
        return self.model_dump(mode="json", by_alias=True)

    def __repr__(self) -> str:
        cls_name = type(self).__name__
        parts = []
        name = getattr(self, "name", None)
        if name is not None:
            parts.append(repr(str(name)))
        tag = getattr(self, "tag", None)
        if tag:
            parts.append(f"tag={tag!r}")
        if not parts:
            return f"<{cls_name}>"
        return f"<{cls_name} {' '.join(parts)}>"

    # ``print(model)`` reads the same as ``repr(model)`` — no field dumps.
    __str__ = __repr__
