#!/usr/bin/env python3
"""
schema_validator.py — Bryan FinTech Intelligence Phase 05A.1.3
Pure-Python JSON Schema Draft 2020-12 Standards-Compliant Structural Validator

Supports:
- Internal JSON pointer resolution ($ref) across arbitrary nesting
- Draft 2020-12 core vocabulary (type, required, properties, patternProperties)
- Strict additionalProperties enforcement (boolean false/true and subschema)
- Value constraints (enum, const, pattern, minLength, format)
- Array constraints (minItems, maxItems, items)
- Numeric constraints (minimum, maximum)
- Composition & conditional evaluation (allOf, anyOf, oneOf, if / then)
"""

import re
from datetime import datetime


class SchemaValidationError(Exception):
    """Raised when an object fails JSON Schema validation."""
    def __init__(self, message, path=""):
        self.message = message
        self.path = path
        super().__init__(f"Schema validation error at '{path}': {message}")


class JsonSchemaValidator:
    """Validates arbitrary JSON objects against JSON Schema Draft 2020-12 specifications."""

    def __init__(self, schema: dict):
        self.raw_schema = schema
        self.definitions = schema.get("contractDefinitions", {})

    def resolve_ref(self, ref_str: str) -> dict:
        """Resolves internal JSON pointers like #/contractDefinitions/xyz."""
        if not ref_str.startswith("#/"):
            raise SchemaValidationError(f"External or non-standard $ref not supported: {ref_str}")
        
        parts = ref_str[2:].split("/")
        curr = self.raw_schema
        for p in parts:
            if isinstance(curr, dict) and p in curr:
                curr = curr[p]
            else:
                raise SchemaValidationError(f"Unresolvable $ref pointer: {ref_str} at part '{p}'")
        return curr

    def validate(self, instance, subschema=None, path=""):
        """Recursively validates an instance against subschema or root."""
        schema = subschema if subschema is not None else self.raw_schema

        # Handle $ref
        if "$ref" in schema:
            resolved = self.resolve_ref(schema["$ref"])
            # If the schema has only $ref, validate against resolved
            # If it has other keywords alongside $ref (Draft 2020-12 allows this), merge them
            if len(schema) == 1:
                return self.validate(instance, resolved, path)
            else:
                merged = dict(resolved)
                for k, v in schema.items():
                    if k != "$ref":
                        merged[k] = v
                return self.validate(instance, merged, path)

        # Handle allOf
        if "allOf" in schema:
            for i, item_schema in enumerate(schema["allOf"]):
                self.validate(instance, item_schema, f"{path}.allOf[{i}]")

        # Handle anyOf
        if "anyOf" in schema:
            any_passed = False
            errors = []
            for i, item_schema in enumerate(schema["anyOf"]):
                try:
                    self.validate(instance, item_schema, f"{path}.anyOf[{i}]")
                    any_passed = True
                    break
                except SchemaValidationError as e:
                    errors.append(e)
            if not any_passed:
                err_msgs = "; ".join([e.message for e in errors])
                raise SchemaValidationError(f"Failed all anyOf subschemas: {err_msgs}", path)

        # Handle oneOf
        if "oneOf" in schema:
            passed_count = 0
            errors = []
            for i, item_schema in enumerate(schema["oneOf"]):
                try:
                    self.validate(instance, item_schema, f"{path}.oneOf[{i}]")
                    passed_count += 1
                except SchemaValidationError as e:
                    errors.append(e)
            if passed_count != 1:
                raise SchemaValidationError(
                    f"Expected exactly one passing oneOf subschema, but {passed_count} passed", path
                )

        # Handle if / then
        if "if" in schema and "then" in schema:
            if_passes = self._check_passes(instance, schema["if"], path)
            if if_passes:
                self.validate(instance, schema["then"], f"{path}.then")
            elif "else" in schema:
                self.validate(instance, schema["else"], f"{path}.else")

        # Handle type
        if "type" in schema:
            self._validate_type(instance, schema["type"], path)

        # If instance is null, we have already validated if null is allowed
        if instance is None:
            return True

        # Handle enum
        if "enum" in schema:
            if instance not in schema["enum"]:
                raise SchemaValidationError(
                    f"Value '{instance}' not in allowed enum {schema['enum']}", path
                )

        # Handle const
        if "const" in schema:
            if instance != schema["const"]:
                raise SchemaValidationError(
                    f"Value '{instance}' does not match const '{schema['const']}'", path
                )

        # Handle String validations
        if isinstance(instance, str):
            if "minLength" in schema and len(instance) < schema["minLength"]:
                raise SchemaValidationError(
                    f"String length {len(instance)} is less than minLength {schema['minLength']}", path
                )
            if "maxLength" in schema and len(instance) > schema["maxLength"]:
                raise SchemaValidationError(
                    f"String length {len(instance)} exceeds maxLength {schema['maxLength']}", path
                )
            if "pattern" in schema:
                pattern = schema["pattern"]
                if not re.search(pattern, instance):
                    raise SchemaValidationError(
                        f"String '{instance}' does not match pattern '{pattern}'", path
                    )
            if "format" in schema:
                self._validate_format(instance, schema["format"], path)

        # Handle Numeric validations
        if isinstance(instance, (int, float)) and not isinstance(instance, bool):
            if "minimum" in schema and instance < schema["minimum"]:
                raise SchemaValidationError(
                    f"Value {instance} is less than minimum {schema['minimum']}", path
                )
            if "maximum" in schema and instance > schema["maximum"]:
                raise SchemaValidationError(
                    f"Value {instance} is greater than maximum {schema['maximum']}", path
                )

        # Handle Array validations
        if isinstance(instance, list):
            if "minItems" in schema and len(instance) < schema["minItems"]:
                raise SchemaValidationError(
                    f"Array item count {len(instance)} is less than minItems {schema['minItems']}", path
                )
            if "maxItems" in schema and len(instance) > schema["maxItems"]:
                raise SchemaValidationError(
                    f"Array item count {len(instance)} exceeds maxItems {schema['maxItems']}", path
                )
            if "items" in schema:
                for idx, item in enumerate(instance):
                    self.validate(item, schema["items"], f"{path}[{idx}]")

        # Handle Object validations
        if isinstance(instance, dict):
            # 1. Required properties
            if "required" in schema:
                for req_key in schema["required"]:
                    if req_key not in instance:
                        raise SchemaValidationError(f"Missing required property: '{req_key}'", path)

            # 2. Known properties
            properties = schema.get("properties", {})
            for prop_key, prop_val in instance.items():
                if prop_key in properties:
                    self.validate(prop_val, properties[prop_key], f"{path}.{prop_key}")

            # 3. additionalProperties enforcement
            if "additionalProperties" in schema:
                add_props = schema["additionalProperties"]
                known_keys = set(properties.keys())
                for inst_key, inst_val in instance.items():
                    if inst_key not in known_keys:
                        # Check patternProperties if present
                        matches_pattern = False
                        if "patternProperties" in schema:
                            for p_pat in schema["patternProperties"]:
                                if re.search(p_pat, inst_key):
                                    matches_pattern = True
                                    self.validate(
                                        inst_val, schema["patternProperties"][p_pat], f"{path}.{inst_key}"
                                    )
                                    break
                        if matches_pattern:
                            continue

                        if add_props is False:
                            raise SchemaValidationError(
                                f"Additional property '{inst_key}' is not allowed", f"{path}.{inst_key}"
                            )
                        elif isinstance(add_props, dict):
                            self.validate(inst_val, add_props, f"{path}.{inst_key}")

        return True

    def _validate_type(self, instance, type_def, path):
        types = type_def if isinstance(type_def, list) else [type_def]
        matched = False
        for t in types:
            if t == "null" and instance is None:
                matched = True
                break
            elif t == "string" and isinstance(instance, str):
                matched = True
                break
            elif t == "boolean" and isinstance(instance, bool):
                matched = True
                break
            elif t == "integer" and isinstance(instance, int) and not isinstance(instance, bool):
                matched = True
                break
            elif t == "number" and isinstance(instance, (int, float)) and not isinstance(instance, bool):
                matched = True
                break
            elif t == "object" and isinstance(instance, dict):
                matched = True
                break
            elif t == "array" and isinstance(instance, list):
                matched = True
                break

        if not matched:
            raise SchemaValidationError(
                f"Instance of type '{type(instance).__name__}' does not match allowed types {types}",
                path
            )

    def _validate_format(self, value: str, fmt: str, path: str):
        if fmt == "date-time":
            try:
                v = value.replace("Z", "+00:00")
                datetime.fromisoformat(v)
            except Exception:
                raise SchemaValidationError(f"String '{value}' is not valid ISO date-time", path)
        elif fmt == "date":
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except Exception:
                raise SchemaValidationError(f"String '{value}' is not valid ISO date (YYYY-MM-DD)", path)
        elif fmt == "uri":
            if not (value.startswith("http://") or value.startswith("https://")):
                raise SchemaValidationError(f"String '{value}' is not a valid URI", path)

    def _check_passes(self, instance, subschema, path) -> bool:
        """Helper to test conditional subschemas without raising."""
        try:
            self.validate(instance, subschema, path)
            return True
        except SchemaValidationError:
            return False
