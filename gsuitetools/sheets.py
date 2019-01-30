import pandas as pd

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'


def make_sheets_api_service(token_json_filename):
    store = file.Storage(token_json_filename)
    cred = store.get()
    if not cred or cred.invalid:
        flow = client.flow_from_clientsecrets("credentials.json", SCOPES)
        cred = tools.run_flow(flow, store)
    service = build("sheets", "v4", http=cred.authorize(Http()))
    return service


def get_data_from_google_spreadsheet(service, spreadsheet_id, range_name, as_df=False):
    result = (
        service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name).execute()
    )

    if result:
        if not as_df:
            return result.get("values")
        return df_from_result(result.get('values'))


def df_from_result(result):
    if result:
        return pd.DataFrame(result)

