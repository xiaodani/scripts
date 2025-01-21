import gspread
from google.oauth2 import service_account

import ssl
import socket
import datetime

from urllib.parse import urlparse

DATE_EXPIRE_COLUMN_NUM = 7
WEBSITE_COLUMN_NUM = 3

URL_ROW_START = 2
URL_ROW_END = 25

SERVICE_ACCOUNT_FILE = ''
SCOPES = ['']
SPREADSHEET_ID = ''
WORKSHEET_NAME = ''

def extract_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain


def get_ssl_certificate_info(website):
    if website == '':
        return ['-']
    PORT = 443

    # Establish SSL connection
    context = ssl.create_default_context()
    with socket.create_connection((website, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=website) as ssock:
            cert = ssock.getpeercert()

    # Extract certificate end date
    expiration_date_str = cert['notAfter']
    expiration_date = datetime.datetime.strptime(expiration_date_str, "%b %d %H:%M:%S %Y %Z")

    # Convert expiration date to GMT+9 timezone
    gmt_plus_9_date = expiration_date + datetime.timedelta(hours=9)

    # format date
    formatted_date = gmt_plus_9_date.strftime("%Y-%m-%d")

    # Return certificate information
    return [
        formatted_date
    ]

def update_excel_ssl_info(start=0, end=0):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    gc = gspread.authorize(credentials)
    worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)
    
    #fetch websites
    if start == end and start >= 0 and end >= 0:
        values = worksheet.cell(start+1, WEBSITE_COLUMN_NUM).value
    elif start > 0 and end > 0:
        values = worksheet.col_values(WEBSITE_COLUMN_NUM)[start:end+1]
    elif start > 0:
        values = worksheet.col_values(WEBSITE_COLUMN_NUM)[start:]
    
    domain_list = list(map(extract_domain, values))
    ssl_list = list(map(get_ssl_certificate_info, domain_list))
    
    # Iterate over both lists simultaneously using zip()
    for website, ssldate in zip(domain_list, ssl_list):
        print(f"{website}\n{ssldate[0]}\n")
    
    # update using cell
    for index, value in enumerate(ssl_list):
        worksheet.update_cell(index+start+1, DATE_EXPIRE_COLUMN_NUM, value[0])
    

print('script start')
update_excel_ssl_info(URL_ROW_START, URL_ROW_END)
print('script end')