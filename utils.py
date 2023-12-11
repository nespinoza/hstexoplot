import numpy as np
import pandas as pd
import requests
import urllib.request

from bs4 import BeautifulSoup

# Python PDF readers:
from PyPDF2 import PdfReader
import tabula #tabula-py

def get_all_HST_programs():

    # Get page data:
    r = requests.get("https://www.stsci.edu/ftp/presto/ops/program-lists/HST-TAC.html")

    # Soup-ify the webpage data:
    soup = BeautifulSoup(r.content)

    # Extract every row of the table:
    rows = soup.findAll('tr')    

    # First, save headers:
    output_data = {}

    all_columns = rows[0].getText().split('\n')[1:-1]
    ncolumns = len(all_columns)    

    for columns in all_columns:

        output_data[columns] = []

    # Now, iterate through rows, save in dictionaries only GO data:
    for i in range(len(rows)-1):

        information_vector = rows[i+1].getText().split('\n')[1:-1]

        if information_vector[1] == 'GO' and ( len(information_vector) == ncolumns ) and (information_vector[-1] != 'unknown'):

            k = 0
            for column in all_columns:

                if column == 'Allocated Orbits':

                    if 'hours' in information_vector[k]:

                        # If in hours, convert from hours-to-orbits using a 1.6 conversion factor (1 orbit = hours / 1.6), because 
                        # 1.6 hours is 96 minutes:
                        information_vector[k] = float(information_vector[k].split('hours')[0]) / 1.6

                    else:

                        information_vector[k] = float(information_vector[k])

                if column == 'Cycle':

                    information_vector[k] = float(information_vector[k])

                if column == 'ID':

                    information_vector[k] = int(information_vector[k])

                output_data[column].append(information_vector[k])

                k += 1

    # Convert dict to dataframe:
    df = pd.DataFrame.from_dict(output_data)

    # Return dataframe:
    return df

def get_science_themes(cycle):
    
    if cycle == 31:

        url = 'https://www.stsci.edu/files/live/sites/www/files/home/hst/proposing/approved-programs/_documents/HSTCycle31-Approved-Abstracts.pdf'

    elif cycle == 29 or cycle == 30 or cycle == 27:

        url = 'https://www.stsci.edu/files/live/sites/www/files/home/hst/proposing/approved-programs/_documents/Cycle'+str(cycle)+'-Abstract-Catalog.pdf'

    elif cycle == 28 or (cycle <= 26 and cycle >= 21):

        url = 'https://www.stsci.edu/files/live/sites/www/files/home/hst/proposing/approved-programs/_documents/Cycle'+str(cycle)+'-Approved-Abstracts.pdf'

    # Download abstracts:
    urllib.request.urlretrieve(url, "abstracts-cycle"+str(cycle)+".pdf")

    # Read PDF for abstracts:
    reader = PdfReader("abstracts-cycle"+str(cycle)+".pdf")

    # Iterate through all pages and extract scientific categories for all programs:
    number_of_pages = len(reader.pages)

    programs = {}
    for i in range(number_of_pages):

        rows = reader.pages[i].extract_text().split('\n')
        for row in rows:

            if 'Scientific Category' in row:

                sc = row.split(':')[-1].lstrip().rstrip()

            if 'ID' in row:

                pid = row.split(':')[-1].lstrip().rstrip()
                break

        programs[int(pid)] = sc

    return programs

def get_all_HST_exposures(cycle):
    """
    Note: cycles prior to 17 have a different format on the PDFs, hence why they are not being included.
    """

    if cycle == 31:

        url = 'https://www.stsci.edu/files/live/sites/www/files/home/hst/proposing/approved-programs/_documents/HSTCycle31-Approved-Exposures.pdf'

    elif cycle > 20 and cycle < 31:

        url = 'https://www.stsci.edu/files/live/sites/www/files/home/hst/proposing/approved-programs/_documents/Cycle'+str(cycle)+'-Exposure-Catalog.pdf'

    elif cycle == 20:

        url = 'https://www.stsci.edu/files/live/sites/www/files/home/hst/proposing/approved-programs/_documents/Cycle20-Approved-Exposure.pdf'

    elif cycle == 19:

        url = 'https://www.stsci.edu/files/live/sites/www/files/home/hst/proposing/approved-programs/_documents/Cycle19-Exposure-Catalog.pdf'
       
    elif cycle == 18:

        url = 'https://www.stsci.edu/files/live/sites/www/files/home/hst/proposing/approved-programs/_documents/Cycle18-exposure-catalog.pdf'

    elif cycle == 17:

        url = 'https://www.stsci.edu/files/live/sites/www/files/home/hst/proposing/approved-programs/_documents/cycle17-exposure-catalog.pdf' 

    urllib.request.urlretrieve(url, "exposure-catalog-cycle"+str(cycle)+".pdf")

    dfs = tabula.read_pdf("exposure-catalog-cycle"+str(cycle)+".pdf", pages="all")

    # Iterate through pages:
    for i in range(len(dfs)):

        if i == 0:

            try:

                df2 = pd.DataFrame().assign(PID=dfs[i]['Unnamed: 0'], Instrument=dfs[i]['Unnamed: 7'], PrimeOrbits=dfs[i]['Unnamed: 10'])

            except:

                df2 = pd.DataFrame().assign(PID=dfs[i]['ID'], Instrument=dfs[i]['Configuration'], PrimeOrbits=dfs[i]['Prime'])

        else:

            try:

                dfnew = pd.DataFrame().assign(PID=dfs[i]['Unnamed: 0'], Instrument=dfs[i]['Unnamed: 7'], PrimeOrbits=dfs[i]['Unnamed: 10'])

            except:

                dfnew = pd.DataFrame().assign(PID=dfs[i]['ID'], Instrument=dfs[i]['Configuration'], PrimeOrbits=dfs[i]['Prime'])

            df2 = pd.concat([df2, dfnew], ignore_index=True)

    return df2
