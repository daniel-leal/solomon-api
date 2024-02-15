from abc import ABC, abstractmethod
from io import BytesIO

import pandas as pd

from app.solomon.common.exceptions import ExcelGenerationError


class FileExporter(ABC):
    @staticmethod
    @abstractmethod
    def export(data: pd.DataFrame) -> bytes:
        """
        Export the data to a file format.

        Parameters:
            data (pd.DataFrame): The DataFrame containing the data to be exported.

        Returns:
            bytes: The exported file content.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """


class ExcelExporter(FileExporter):
    @staticmethod
    def export(data: pd.DataFrame) -> BytesIO:
        """
        Export the data to an Excel file.

        Parameters:
            data (pd.DataFrame): The DataFrame containing the data to be exported.

        Returns:
            bytes: The exported Excel file content.

        Raises:
            ExcelGenerationError: If an error occurs during the generation of the Excel
            file.
        """
        excel_file = BytesIO()
        try:
            data.to_excel(excel_file, index=False, sheet_name="Data", engine="openpyxl") # noqa
            excel_file.seek(0)
            return excel_file
        except Exception as e:
            raise ExcelGenerationError(f"Error generating Excel file: {e}")
