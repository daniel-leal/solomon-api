from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class DataTransformationError(Exception):
    """Exception class for transform errors."""

    pass


class DataTransformation(ABC):
    @classmethod
    @abstractmethod
    def transform_data(cls, raw_data: Any) -> pd.DataFrame:
        """
        Abstract method for data transformation.

        Parameters:
            raw_data: raw data to be transformed.

        Returns:
            pd.DataFrame: A DataFrame containing the transformed data.
        """
