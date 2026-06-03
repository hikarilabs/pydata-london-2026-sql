def json_to_markdown(semantic_data: dict) -> str:
    """
    Converts the semantic layer JSON into a structured Markdown document.
    Optimized for LLM understanding and natural language to SQL generation.
    """
    lines = []

    # Header
    lines.append("#Semantic Layer\n")
    lines.append("Machine-readable semantic layer for natural language queries\n")

    # Extract tables - they're stored as a dict with table names as keys
    tables_dict = semantic_data.get("tables", {})
    tables = list(tables_dict.values()) if tables_dict else []

    lines.append(f"## Database Entities ({len(tables)} tables)\n")

    for table in tables:
        table_name = table.get("name", "Unknown")
        schema = table.get("schema", "")
        full_table_name = f"{schema}.{table_name}" if schema else table_name
        description = table.get("description", "No description available")
        primary_key = table.get("primary_key", "")

        lines.append(f"### {table_name}")
        lines.append(f"**Full Name**: {full_table_name}")
        if primary_key:
            lines.append(f"**Primary Key**: {primary_key}")
        lines.append(f"**Description**: {description}")

        # Synonyms
        synonyms = table.get("synonyms", [])
        if synonyms:
            lines.append(f"**Synonyms**: {', '.join(synonyms)}")

        # Application Context
        app_context = table.get("application_context")
        if app_context:
            lines.append(f"**Application Context**: {app_context}")

        # Business Context
        business_context = table.get("business_context")
        if business_context:
            lines.append(f"**Business Context**: {business_context.strip()}")

        lines.append("\n")
        # Columns
        columns = table.get("columns", [])
        if columns:
            lines.append("#### Columns")
            for col in columns:
                col_name = col.get("name", "unknown")
                col_type = col.get("data_type", "unknown")
                col_desc = col.get("description", "")
                privacy = col.get("privacy_level", "")
                is_fk = col.get("is_foreign_key", False)
                references = col.get("references", "")

                # Build column line
                type_info = f"{col_type}"
                if privacy:
                    type_info += f", {privacy}"

                line_parts = [f"- **{col_name}** ({type_info})"]

                if is_fk and references:
                    line_parts.append(f"ForeignKey → {references}")

                lines.append(" ".join(line_parts))

                if col_desc:
                    lines.append(f"  - {col_desc}")

                # Sample values
                sample_values = col.get("sample_values", [])
                if sample_values:
                    lines.append(
                        f"  - *Examples*: {', '.join(map(str, sample_values))}"
                    )

                # Synonyms for column
                col_synonyms = col.get("synonyms", [])
                if col_synonyms:
                    lines.append(f"  - *Synonyms*: {', '.join(col_synonyms)}")

            lines.append("")

        lines.append("---\n")

    # Relationships Section
    relationships = semantic_data.get("relationships", [])
    if relationships:
        lines.append(f"## Relationships ({len(relationships)} connections)\n")

        for rel in relationships:
            from_table = rel.get("from_table", "unknown")
            to_table = rel.get("to_table", "unknown")
            rel_type = rel.get("relationship_type", "unknown")
            join_condition = rel.get("join_condition", "")
            rel_desc = rel.get("description", "")

            lines.append(f"### {from_table} → {to_table}")
            lines.append(f"- **Type**: {rel_type}")
            lines.append(f"- **Join**: {join_condition}")
            if rel_desc:
                lines.append(f"- **Description**: {rel_desc}")
            lines.append("")

    # Summary statistics
    lines.append("## Summary")
    lines.append(f"- **Total Tables**: {len(tables)}")
    total_columns = sum(len(t.get("columns", [])) for t in tables)
    lines.append(f"- **Total Columns**: {total_columns}")
    lines.append(f"- **Total Relationships**: {len(relationships)}")

    return "\n".join(lines)
