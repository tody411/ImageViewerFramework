
# -*- coding: utf-8 -*-
## @package ivf.io_util.gspread_sheet
#
#  ivf.io_util.gspread_sheet utility package.
#  @author      tody
#  @date        2016/01/25



import os
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

_root = __file__


def authorize():
    key_file='ShadingAnalysis-004babda5ab2.json'
    json_key = json.load(open(os.path.join(_root, "../" + key_file)))
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
    gc = gspread.authorize(credentials)
    return gc


def loadSheetFile(file_name="ShadingAnalysisData"):
    gc = authorize()
    return gc.open(file_name)


def loadWorkSheet(sheet, worksheet_name):
    try:
        worksheet = sheet.worksheet(worksheet_name)
    except:
        worksheet = sheet.add_worksheet(title=worksheet_name, rows="100", cols="20")

    return worksheet


def cellValue(worksheet, row, col):
    return worksheet.cell(row, col).value


def colValues(worksheet, col):
    return worksheet.col_values(col)


def rowValues(worksheet, row):
    return worksheet.row_values(row)


def updateCell(worksheet, row, col, val):
    worksheet.update_cell(row, col, val)
