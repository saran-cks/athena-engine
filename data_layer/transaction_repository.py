import pandas as pd
from typing import List, Union
from io import BytesIO
from domain.entities import Transaction

class TransactionRepository:
    """
    Parses and sanitizes CSV or XLSX files into uniform domain Transaction structures.
    """
    
    @staticmethod
    def load_from_file(file_or_path: Union[str, BytesIO], filename: str, fund_id: str, portfolio_id: str) -> List[Transaction]:
        """
        Supports CSV and XLSX. Resolves file type using filename extension.
        Requires exactly two columns loosely named 'date' and 'amount'.
        """
        if filename.endswith('.csv'):
            df = pd.read_csv(file_or_path)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_or_path)
        else:
            raise ValueError(f"Unsupported file format for {filename}")
            
        # Clean column names
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        # Verify required columns exist
        if 'date' not in df.columns or 'amount' not in df.columns:
            raise ValueError("Parsed file must contain exactly two columns: 'date' and 'amount'")
            
        df['date'] = pd.to_datetime(df['date']).dt.date
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df.dropna(subset=['date', 'amount'])
        
        transactions: List[Transaction] = []
        for _, row in df.iterrows():
            transactions.append(Transaction(
                date=row['date'],
                amount=row['amount'],
                instrument_id=fund_id,
                portfolio_id=portfolio_id
            ))
            
        return transactions
