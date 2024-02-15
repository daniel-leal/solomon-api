from io import BytesIO

import pandas as pd

from app.solomon.common.exceptions import ExcelGenerationError
from app.solomon.common.file_exporter import ExcelExporter


class TestExcelExporter:
    def test_success_export(self):
        data = pd.DataFrame(
            [
                {"description": "iFood", "amount": 100.15},
                {"description": "Uber", "amount": 25.12},
            ]
        )

        excel_file = ExcelExporter.export(data=data)

        assert isinstance(excel_file, BytesIO)

    def test_failure_export(self):
        data = []

        try:
            ExcelExporter.export(data)  # type: ignore
        except ExcelGenerationError as e:
            assert (
                str(e)
                == "Error generating Excel file: 'list' object has no attribute 'to_excel'"
            )
