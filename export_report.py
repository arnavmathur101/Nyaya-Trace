import sqlite3
import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_audit_excel_report(db_path: str = "nyayatrace.db", output_file: str = "NyayaTrace_Audit_Report.xlsx"):
    conn = sqlite3.connect(db_path)
    
    # Query full contradictions joined with documents/bundle info
    query = """
    SELECT 
        c.bundle_id,
        c.rule_id,
        c.severity,
        c.narrative,
        c.statute,
        c.event_ids,
        c.created_at
    FROM contradictions c
    ORDER BY c.bundle_id, 
        CASE c.severity
            WHEN 'CRITICAL' THEN 1
            WHEN 'HIGH' THEN 2
            WHEN 'MEDIUM' THEN 3
            ELSE 4
        END
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("No contradictions found in nyayatrace.db to export.")
        return

    # Sheet 2: Summary Pivot (rule_id as rows, severity as columns, count as values)
    summary_pivot = pd.crosstab(df['rule_id'], df['severity']).reindex(columns=['CRITICAL', 'HIGH', 'MEDIUM'], fill_value=0)
    summary_pivot['Total'] = summary_pivot.sum(axis=1)
    summary_pivot = summary_pivot.reset_index()

    # Sheet 3: By Bundle (total contradiction count per bundle_id, sorted highest to lowest)
    bundle_summary = df.groupby('bundle_id').size().reset_index(name='total_contradictions')
    bundle_summary = bundle_summary.sort_values(by='total_contradictions', ascending=False)

    abs_output_path = os.path.abspath(output_file)

    # Export using pandas.DataFrame.to_excel() with openpyxl engine
    with pd.ExcelWriter(abs_output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="All Contradictions", index=False)
        summary_pivot.to_excel(writer, sheet_name="Summary", index=False)
        bundle_summary.to_excel(writer, sheet_name="By Bundle", index=False)

    # Apply openpyxl styling & formatting
    wb = openpyxl.load_workbook(abs_output_path)
    
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    
    fills = {
        "CRITICAL": PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),
        "HIGH":     PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid"),
        "MEDIUM":   PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    }
    fonts = {
        "CRITICAL": Font(name="Calibri", size=11, bold=True, color="9C0006"),
        "HIGH":     Font(name="Calibri", size=11, bold=True, color="9C6500"),
        "MEDIUM":   Font(name="Calibri", size=11, bold=True, color="806000")
    }
    regular_font = Font(name="Calibri", size=11)
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # -------------------------------------------------------------
    # Sheet 1: All Contradictions
    # -------------------------------------------------------------
    ws1 = wb["All Contradictions"]
    ws1.freeze_panes = "A2"

    for col_idx in range(1, len(df.columns) + 1):
        cell = ws1.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row in ws1.iter_rows(min_row=2, max_row=ws1.max_row, min_col=1, max_col=ws1.max_column):
        for cell in row:
            cell.font = regular_font
            cell.border = thin_border
            col_name = ws1.cell(row=1, column=cell.column).value
            if col_name in ["bundle_id", "rule_id", "severity", "event_ids", "created_at"]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

            if col_name == "severity":
                sev_val = str(cell.value).upper()
                if sev_val in fills:
                    cell.fill = fills[sev_val]
                    cell.font = fonts[sev_val]

    # Auto-fit Column Widths for Sheet 1
    ws1.column_dimensions['A'].width = 20  # bundle_id
    ws1.column_dimensions['B'].width = 14  # rule_id
    ws1.column_dimensions['C'].width = 16  # severity
    ws1.column_dimensions['D'].width = 68  # narrative
    ws1.column_dimensions['E'].width = 32  # statute
    ws1.column_dimensions['F'].width = 16  # event_ids
    ws1.column_dimensions['G'].width = 22  # created_at

    # -------------------------------------------------------------
    # Sheet 2: Summary (Pivot Table)
    # -------------------------------------------------------------
    ws2 = wb["Summary"]
    ws2.freeze_panes = "A2"

    for col_idx in range(1, len(summary_pivot.columns) + 1):
        cell = ws2.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row in ws2.iter_rows(min_row=2, max_row=ws2.max_row, min_col=1, max_col=ws2.max_column):
        for cell in row:
            cell.font = regular_font
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center", vertical="center")

    for col in ws2.columns:
        col_letter = get_column_letter(col[0].column)
        ws2.column_dimensions[col_letter].width = 20

    # -------------------------------------------------------------
    # Sheet 3: By Bundle (Sorted Highest to Lowest)
    # -------------------------------------------------------------
    ws3 = wb["By Bundle"]
    ws3.freeze_panes = "A2"

    for col_idx in range(1, len(bundle_summary.columns) + 1):
        cell = ws3.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row in ws3.iter_rows(min_row=2, max_row=ws3.max_row, min_col=1, max_col=ws3.max_column):
        for cell in row:
            cell.font = regular_font
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center", vertical="center")

    for col in ws3.columns:
        col_letter = get_column_letter(col[0].column)
        ws3.column_dimensions[col_letter].width = 26

    wb.save(abs_output_path)

    print(f"[EXPORT SUCCESSFUL] Excel report created at: {abs_output_path}")
    print(f"Total Rows Exported ('All Contradictions'): {len(df)}")

    return abs_output_path, len(df), summary_pivot, bundle_summary

if __name__ == "__main__":
    filepath, row_count, s_pivot, b_summary = generate_audit_excel_report()
    
    print("\n=====================================================================")
    print("                    SUMMARY SHEET CONTENT PREVIEW                    ")
    print("=====================================================================")
    print("\n--- SHEET 2: SUMMARY (RULE_ID vs SEVERITY PIVOT) ---")
    print(s_pivot.to_string(index=False))
    
    print("\n--- SHEET 3: BY BUNDLE (TOTAL CONTRADICTIONS SORTED HIGH TO LOW) ---")
    print(b_summary.to_string(index=False))
    print("=====================================================================\n")
