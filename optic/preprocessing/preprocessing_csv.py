from __future__ import annotations
from ..type_definitions import *
import numpy as np
from PyQt5.QtCore import Qt

"""
Build pandas DataFrames for CSV export from the ROI curation table and the trace data.
Column order follows the table's own column order, so the CSV mirrors what the user sees.
"""

# column name of the ROI id in the exported CSV
COLUMN_CELL_ID = "Cell_ID"
# column name holding the celltype (radiobutton) chosen for each ROI
COLUMN_CELLTYPE = "Celltype"
# frame index / time columns of the trace CSV
COLUMN_FRAME = "Frame"
COLUMN_TIME = "Time_s"


# read the celltype (checked radiobutton) of every table row
# rows with no checked radiobutton get "" (can happen right after a TableColumns change)
def getCelltypeOfEachRow(
        q_table         : QTableWidget,
        table_columns   : TableColumns,
        ) -> Dict[int, str]:
    dict_row_celltype = {}
    list_col_celltype = [
        (col_name, col_info["order"])
        for col_name, col_info in table_columns.getColumns().items()
        if col_info["type"] == "celltype"
    ]
    for row in range(q_table.rowCount()):
        dict_row_celltype[row] = ""
        for col_name, col_order in list_col_celltype:
            radio_button = q_table.cellWidget(row, col_order)
            if radio_button and radio_button.isChecked():
                dict_row_celltype[row] = col_name
                break
    return dict_row_celltype


# "Cell_ID" of a row; falls back to the row index when the id column is missing/unparsable
def getCellIdOfRow(
        q_table         : QTableWidget,
        table_columns   : TableColumns,
        row             : int,
        ) -> int:
    for col_name, col_info in table_columns.getColumns().items():
        if col_info["type"] == "id":
            item = q_table.item(row, col_info["order"])
            try:
                return int(item.text())
            except (ValueError, AttributeError):
                return row
    return row


# ROI ids (not row indices) whose celltype is one of list_celltype
def getROIIdsOfCelltype(
        q_table         : QTableWidget,
        table_columns   : TableColumns,
        list_celltype   : List[str],
        ) -> List[int]:
    set_celltype = set(list_celltype)
    dict_row_celltype = getCelltypeOfEachRow(q_table, table_columns)
    return [
        getCellIdOfRow(q_table, table_columns, row)
        for row in range(q_table.rowCount())
        if dict_row_celltype.get(row, "") in set_celltype
    ]


# table contents -> DataFrame; one row per ROI
# columns: Cell_ID, Celltype, then every checkbox / string column in table order
def buildDataFrameROICelltype(
        q_table         : QTableWidget,
        table_columns   : TableColumns,
        ) -> "pd.DataFrame":
    import pandas as pd

    dict_row_celltype = getCelltypeOfEachRow(q_table, table_columns)
    row_count = q_table.rowCount()

    data = {
        COLUMN_CELL_ID: [getCellIdOfRow(q_table, table_columns, row) for row in range(row_count)],
        COLUMN_CELLTYPE: [dict_row_celltype.get(row, "") for row in range(row_count)],
    }
    for col_name, col_info in sorted(table_columns.getColumns().items(), key=lambda x: x[1]["order"]):
        if col_info["type"] == "checkbox":
            values = []
            for row in range(row_count):
                item = q_table.item(row, col_info["order"])
                values.append(bool(item.checkState() == Qt.Checked) if item else False)
            data[col_name] = values
        elif col_info["type"] == "string":
            values = []
            for row in range(row_count):
                item = q_table.item(row, col_info["order"])
                values.append(item.text() if item else "")
            data[col_name] = values

    return pd.DataFrame(data)


# trace array (n_roi, n_frames) -> DataFrame; one row per frame, one column per ROI
# fs is used to add a Time_s column; pass None (or 0) to omit it
def buildDataFrameTrace(
        traces          : np.ndarray,
        list_roi_id     : List[int],
        fs              : Optional[float] = None,
        ) -> "pd.DataFrame":
    import pandas as pd

    traces = np.asarray(traces)
    n_frames = traces.shape[1]

    data = {COLUMN_FRAME: np.arange(n_frames, dtype=np.int32)}
    if fs:
        data[COLUMN_TIME] = np.arange(n_frames, dtype=np.float64) / float(fs)
    for roi_id in list_roi_id:
        # ROIs without a trace (id beyond the trace array) are skipped rather than
        # silently exported as zeros
        if roi_id < 0 or roi_id >= traces.shape[0]:
            continue
        data[f"ROI_{roi_id}"] = traces[roi_id]

    return pd.DataFrame(data)
