import gspread
from google.oauth2 import service_account

from src.logger import logger


class GoogleSheet:
    SERVICE_ACCOUNT_FILE = 'data/creds.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
    CREDENTIALS = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    def __init__(self, sheet_id: str):
        self.sheet_id = sheet_id
        self.gc = gspread.authorize(self.CREDENTIALS)
        self.worksheet = self.gc.open_by_key(sheet_id).sheet1


    def create_col(self, col_name: str, col_idx: int):
        try:
            headers = self.worksheet.row_values(1)

            if col_name in headers:
                logger.debug(f"Column {col_name} already exists.")
                return

            self.worksheet.insert_cols([[col_name]], col_idx)

            logger.debug(f"Column {col_name} is inserted.")

        except Exception as e:
            logger.error(e)


    def get_col_values(self, col_name: str):
        try:
            target_col = self.worksheet.find(col_name).col

            websites = self.worksheet.col_values(target_col)
            return websites

        except Exception as e:
            logger.error(e)


    def insert(self, col_name: str, values: list):
        try:
            target_col = self.worksheet.find(col_name).col

            cells = self.worksheet.range(2, target_col, len(values) + 1, target_col)

            for i, cell in enumerate(cells):
                cell.value = values[i]

            self.worksheet.update_cells(cells)
            logger.debug("values inserted.")

        except Exception as e:
            logger.error(e)