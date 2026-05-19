import io
import requests
import pandas as pd
from typing import Optional, List, Dict


class AmfiClient:
    """
    Client for fetching Net Asset Value (NAV) data.
    Provides methods to fetch daily ALL NAV from AMFI and historical NAV via mfapi.
    """

    DAILY_URL = "https://portal.amfiindia.com/spages/NAVAll.txt"

    def fetch_daily_all(self) -> Optional[pd.DataFrame]:
        """
        Fetches the latest daily NAVs for all schemes from the official AMFI text file.
        Returns a DataFrame with columns: ['scheme_code', 'scheme_name', 'nav', 'date'].
        """
        try:
            response = requests.get(self.DAILY_URL, timeout=30)
            response.raise_for_status()
            text_data = response.text

            # The AMFI file mixes category headers and data rows. Data rows contain ';'.
            lines = text_data.split("\n")
            valid_lines = [
                line for line in lines if ";" in line and "Scheme Name" not in line
            ]
            clean_data = "\n".join(valid_lines)

            # Parsing: Scheme Code;ISIN Div;ISIN Growth;Scheme Name;Net Asset Value;Date
            df = pd.read_csv(
                io.StringIO(clean_data), sep=";", header=None, on_bad_lines="skip"
            )
            df.columns = [
                "scheme_code",
                "isin_div",
                "isin_reinv",
                "scheme_name",
                "nav",
                "date",
            ]

            df = df[["scheme_code", "scheme_name", "nav", "date"]]
            df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
            df["date"] = pd.to_datetime(
                df["date"], format="%d-%b-%Y", errors="coerce"
            ).dt.date

            df = df.dropna(subset=["scheme_code", "nav", "date"])
            df["scheme_code"] = df["scheme_code"].astype(str)

            return df
        except Exception as e:
            print(f"Failed to fetch Daily AMFI data: {e}")
            return None

    def fetch_history(self, scheme_code: str) -> Optional[List[Dict]]:
        """
        Fetches historical NAV timeline using mfapi.in, returning a list of dicts:
        [{'date': 'dd-mm-yyyy', 'nav': '123.45'}, ...]
        Essential for simulating past investments over years.
        """
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            if "data" in data:
                return data["data"]
            return None
        except Exception as e:
            print(f"Failed to fetch history for {scheme_code}: {e}")
            return None
