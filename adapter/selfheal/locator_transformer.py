from adapter.selfheal.models import LocatorDescriptor
from adapter.selfheal.snapshot_helper import find_elements_by_text
import re
from adapter.selfheal.roles import ARIA_ROLES


class LocatorTransformer:

    def transform(
        self, *, original: LocatorDescriptor, snapshot: list
    ) -> list[LocatorDescriptor] | None:
        """
        Returns a refined locator or None if deterministic narrowing fails
        """
        matches = find_elements_by_text(snapshot, original.value)

        # 1️⃣ Upgrade to ROLE if possible
        role_locators = self._to_role(matches)
        if role_locators:
            return role_locators
        # 2️⃣ Next upgrade to text if possible
        text_locators = self._to_text(matches)
        if text_locators:
            return text_locators

        # 3️⃣ Add landmark scope
        scoped_locators = self._add_parent_scope(matches, original)
        if scoped_locators:
            return scoped_locators

        # No safe narrowing possible → escalate
        return None

    ROLE_NAME_RE = re.compile(r'(?:-\s*)?(?P<role>[a-zA-Z_]+)\s+"(?P<name>[^"]+)"')

    def extract_role_and_name(self, line: str):
        match = self.ROLE_NAME_RE.match(line)
        if not match:
            return None, None

        return match.group("role"), match.group("name")

    def _to_role(self, matches) -> list[LocatorDescriptor] | None:
        roles: list[LocatorDescriptor] = []
        for text, root_parent, curr_parent in matches:
            loc: LocatorDescriptor = None
            (role, role_name) = self.extract_role_and_name(text)
            if role in ARIA_ROLES:
                loc = LocatorDescriptor(
                    strategy="role",
                    value=role_name,
                    role=role,
                    name=role_name,
                    landmark=root_parent.partition(" ")[0],
                    scope=curr_parent.partition(" ")[0],
                )
                loc.exact = True
                roles.append(loc)
        return roles

    def _to_text(self, matches) -> list[LocatorDescriptor] | None:
        texts: list[LocatorDescriptor] = []
        for text, root_parent, curr_parent in matches:
            loc: LocatorDescriptor = None
            if curr_parent == "text":
                loc = LocatorDescriptor(
                    strategy="text",
                    value=text,
                    role=None,
                    name=None,
                    landmark=root_parent.partition(" ")[0],
                    scope=curr_parent.partition(" ")[0],
                )
                loc.exact = True
                texts.append(loc)
        return texts

    def _add_parent_scope(
        self, matches, locator: LocatorDescriptor
    ) -> LocatorDescriptor | None:

        parents = set(
            parent.partition(" ")[0]
            for _, parent, scope in matches
            if parent and scope in ARIA_ROLES
        )
        if len(parents) == 1:
            parent = parents.pop()

            return LocatorDescriptor(
                strategy="scoped_role",
                value=locator.role,
                name=locator.name,
                landmark=parent,
            )

        return None
