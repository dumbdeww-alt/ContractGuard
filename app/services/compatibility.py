"""Compatibility Engine Service.

Evaluates schema evolution between two versions of the same contract according
to the Contract Guard compatibility policy:

1. Existing field unchanged: NON_BREAKING
2. Existing field type changed: BREAKING
3. Existing required field removed: BREAKING
4. Existing optional field removed: BREAKING
5. New required field added: BREAKING
6. New optional field added: NON_BREAKING
7. Description or non-validation metadata changes: NON_BREAKING
8. Stricter validation constraints: BREAKING
"""

from typing import Any

from app.schemas.compatibility import (
    ChangeSeverity,
    ChangeType,
    CompatibilityReportResponse,
    CompatibilityStatus,
    SchemaChangeDetail,
)


class CompatibilityEngine:
    """Core domain service for comparing JSON Schema specifications."""

    @staticmethod
    def _extract_type_str(field_spec: Any) -> str:
        """Extract a readable string representation of a field's type."""
        if not isinstance(field_spec, dict):
            return str(field_spec) if field_spec is not None else "any"
        ftype = field_spec.get("type")
        if isinstance(ftype, list):
            return " | ".join(str(t) for t in ftype)
        if isinstance(ftype, str):
            return ftype
        if "$ref" in field_spec:
            return f"$ref({field_spec['$ref']})"
        return "any"

    @classmethod
    def compare_schemas(
        cls,
        old_schema: dict[str, Any],
        new_schema: dict[str, Any],
        old_version: int,
        new_version: int,
        contract_id: int,
        contract_name: str,
    ) -> CompatibilityReportResponse:
        """Compare two JSON schemas and return a structured compatibility evaluation."""
        changes: list[SchemaChangeDetail] = []

        # 1. Validate root schema type
        old_root_type = old_schema.get("type", "object") if isinstance(old_schema, dict) else "unknown"
        new_root_type = new_schema.get("type", "object") if isinstance(new_schema, dict) else "unknown"
        if old_root_type != new_root_type:
            changes.append(
                SchemaChangeDetail(
                    path="$",
                    change_type=ChangeType.TYPE_CHANGED,
                    old_value=str(old_root_type),
                    new_value=str(new_root_type),
                    severity=ChangeSeverity.BREAKING,
                    reason=f"Root schema type changed from {old_root_type} to {new_root_type}.",
                )
            )

        # 2. Check root additionalProperties restriction
        old_add_props = old_schema.get("additionalProperties") if isinstance(old_schema, dict) else None
        new_add_props = new_schema.get("additionalProperties") if isinstance(new_schema, dict) else None
        if old_add_props is True and new_add_props is False:
            changes.append(
                SchemaChangeDetail(
                    path="$",
                    change_type=ChangeType.FIELD_CONSTRAINT_STRICTER,
                    old_value="additionalProperties: true",
                    new_value="additionalProperties: false",
                    severity=ChangeSeverity.BREAKING,
                    reason="Schema closed to additional properties (additionalProperties changed from true to false).",
                )
            )

        # 3. Compare properties and required lists
        old_properties: dict[str, Any] = old_schema.get("properties", {}) if isinstance(old_schema, dict) else {}
        new_properties: dict[str, Any] = new_schema.get("properties", {}) if isinstance(new_schema, dict) else {}

        old_required = set(old_schema.get("required", [])) if isinstance(old_schema, dict) else set()
        new_required = set(new_schema.get("required", [])) if isinstance(new_schema, dict) else set()

        # Properties added in new_schema
        added_props = set(new_properties.keys()) - set(old_properties.keys())
        for prop in sorted(added_props):
            new_spec = new_properties[prop]
            new_type = cls._extract_type_str(new_spec)
            if prop in new_required:
                changes.append(
                    SchemaChangeDetail(
                        path=prop,
                        change_type=ChangeType.REQUIRED_FIELD_ADDED,
                        old_value=None,
                        new_value=new_type,
                        severity=ChangeSeverity.BREAKING,
                        reason=f"New required field '{prop}' was added.",
                    )
                )
            else:
                changes.append(
                    SchemaChangeDetail(
                        path=prop,
                        change_type=ChangeType.OPTIONAL_FIELD_ADDED,
                        old_value=None,
                        new_value=new_type,
                        severity=ChangeSeverity.NON_BREAKING,
                        reason=f"New optional field '{prop}' was added.",
                    )
                )

        # Properties removed from old_schema
        removed_props = set(old_properties.keys()) - set(new_properties.keys())
        for prop in sorted(removed_props):
            old_spec = old_properties[prop]
            old_type = cls._extract_type_str(old_spec)
            if prop in old_required:
                changes.append(
                    SchemaChangeDetail(
                        path=prop,
                        change_type=ChangeType.REQUIRED_FIELD_REMOVED,
                        old_value=old_type,
                        new_value=None,
                        severity=ChangeSeverity.BREAKING,
                        reason=f"Required field '{prop}' was removed.",
                    )
                )
            else:
                changes.append(
                    SchemaChangeDetail(
                        path=prop,
                        change_type=ChangeType.OPTIONAL_FIELD_REMOVED,
                        old_value=old_type,
                        new_value=None,
                        severity=ChangeSeverity.BREAKING,
                        reason=f"Optional field '{prop}' was removed.",
                    )
                )

        # Properties present in both schemas
        common_props = set(old_properties.keys()) & set(new_properties.keys())
        for prop in sorted(common_props):
            old_spec = old_properties[prop]
            new_spec = new_properties[prop]

            old_type = cls._extract_type_str(old_spec)
            new_type = cls._extract_type_str(new_spec)

            # Check type change
            if old_type != new_type:
                changes.append(
                    SchemaChangeDetail(
                        path=prop,
                        change_type=ChangeType.TYPE_CHANGED,
                        old_value=old_type,
                        new_value=new_type,
                        severity=ChangeSeverity.BREAKING,
                        reason=f"Field '{prop}' changed type from {old_type} to {new_type}.",
                    )
                )

            # Check requiredness change
            was_required = prop in old_required
            is_required = prop in new_required
            if not was_required and is_required:
                changes.append(
                    SchemaChangeDetail(
                        path=prop,
                        change_type=ChangeType.FIELD_MADE_REQUIRED,
                        old_value="optional",
                        new_value="required",
                        severity=ChangeSeverity.BREAKING,
                        reason=f"Existing optional field '{prop}' was made required.",
                    )
                )
            elif was_required and not is_required:
                changes.append(
                    SchemaChangeDetail(
                        path=prop,
                        change_type=ChangeType.FIELD_MADE_OPTIONAL,
                        old_value="required",
                        new_value="optional",
                        severity=ChangeSeverity.NON_BREAKING,
                        reason=f"Existing required field '{prop}' was made optional.",
                    )
                )

            # Check field-level constraint restrictions
            if isinstance(old_spec, dict) and isinstance(new_spec, dict):
                # Enum restrictions
                old_enum = old_spec.get("enum")
                new_enum = new_spec.get("enum")
                if isinstance(old_enum, list) and isinstance(new_enum, list):
                    removed_enums = set(old_enum) - set(new_enum)
                    if removed_enums:
                        changes.append(
                            SchemaChangeDetail(
                                path=prop,
                                change_type=ChangeType.FIELD_CONSTRAINT_STRICTER,
                                old_value=str(old_enum),
                                new_value=str(new_enum),
                                severity=ChangeSeverity.BREAKING,
                                reason=f"Field '{prop}' removed allowed enum values: {sorted(str(v) for v in removed_enums)}.",
                            )
                        )

                # Numeric minimum restrictions
                old_min = old_spec.get("minimum")
                new_min = new_spec.get("minimum")
                if isinstance(old_min, (int, float)) and isinstance(new_min, (int, float)) and new_min > old_min:
                    changes.append(
                        SchemaChangeDetail(
                            path=prop,
                            change_type=ChangeType.FIELD_CONSTRAINT_STRICTER,
                            old_value=f"minimum: {old_min}",
                            new_value=f"minimum: {new_min}",
                            severity=ChangeSeverity.BREAKING,
                            reason=f"Field '{prop}' minimum constraint increased from {old_min} to {new_min}.",
                        )
                    )

                # Numeric maximum restrictions
                old_max = old_spec.get("maximum")
                new_max = new_spec.get("maximum")
                if isinstance(old_max, (int, float)) and isinstance(new_max, (int, float)) and new_max < old_max:
                    changes.append(
                        SchemaChangeDetail(
                            path=prop,
                            change_type=ChangeType.FIELD_CONSTRAINT_STRICTER,
                            old_value=f"maximum: {old_max}",
                            new_value=f"maximum: {new_max}",
                            severity=ChangeSeverity.BREAKING,
                            reason=f"Field '{prop}' maximum constraint decreased from {old_max} to {new_max}.",
                        )
                    )

                # Metadata changes (only if type and requiredness stayed identical)
                if old_type == new_type and was_required == is_required:
                    old_desc = old_spec.get("description")
                    new_desc = new_spec.get("description")
                    if old_desc != new_desc and (old_desc is not None or new_desc is not None):
                        changes.append(
                            SchemaChangeDetail(
                                path=prop,
                                change_type=ChangeType.METADATA_CHANGED,
                                old_value=old_desc,
                                new_value=new_desc,
                                severity=ChangeSeverity.NON_BREAKING,
                                reason=f"Description or metadata for field '{prop}' was updated.",
                            )
                        )

        # Calculate totals
        breaking_count = sum(1 for c in changes if c.severity == ChangeSeverity.BREAKING)
        non_breaking_count = sum(1 for c in changes if c.severity == ChangeSeverity.NON_BREAKING)
        is_compatible = breaking_count == 0
        status = CompatibilityStatus.NON_BREAKING if is_compatible else CompatibilityStatus.BREAKING

        return CompatibilityReportResponse(
            contract_id=contract_id,
            contract_name=contract_name,
            old_version=old_version,
            new_version=new_version,
            compatible=is_compatible,
            status=status,
            breaking_changes=breaking_count,
            non_breaking_changes=non_breaking_count,
            changes=changes,
        )
