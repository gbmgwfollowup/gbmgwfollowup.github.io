import argparse, requests
import pandas as pd
import numpy as np
import os

def save_run_superevents_status(run, file):
    
    # for each superevent of a run, print to file whether the superevent was retracted or significant 
    print(f'Looping over GraceDB pages of {run}... looking for retracted or significant superevents')
    page_number = 0
    status_code = 200
    superevent_status_dtype = [('superevent_id', '<U25'), ('retracted', '<U25'), ('significant', '<U25')] # set entry type as string
    superevents_status = np.array([], dtype=superevent_status_dtype) 

    # loop over pages
    while status_code == 200:
        
        page_number+=1
        url = f'https://gracedb.ligo.org/superevents/public/{run}/?page={page_number}&showall=1'
        response = requests.get(url)
        status_code = response.status_code
        # when the last page has been processed, terminate loop
        if status_code != 200:
            print(f'Run {run}... finished!')
            continue
        else: pass

        # process page 
        from io import StringIO
        print(f'Run {run}, GraceDB page {page_number}... fetched')
        # convert string to StringIO object to avoid warning
        data_frame = pd.read_html(StringIO(response.text), flavor='html5lib')[0]

        # loop over superevents on that page
        for row in data_frame.iterrows():
            if_retracted = False
            if_significant = False
            superevent_id = row[1]['Event ID']
            if run == 'O3': significant = 'yes'
            else: significant = row[1]['Significant']
            comments = row[1]['Comments']
            if 'retracted' in str(comments).lower(): if_retracted = True
            if 'yes' in str(significant).lower(): if_significant = True
            # save whether a superevent was retracted or significant
            superevents_status = np.append(superevents_status, np.array((superevent_id, if_retracted, if_significant), dtype=superevent_status_dtype))

    # save results to file
    np.save(file, superevents_status, allow_pickle=False)

def main():

    parser = argparse.ArgumentParser(
        
        prog = 'get_superevents_status',
        description = 'For each superevent, get information whether the superevent was retracted or significant querying GraceDB.'
    )

    parser.add_argument('--outfile', type=str, help='Numpy file with retraction and significant status of superevents.')
    parser.add_argument('--log', type=str, help='Log file.')
    
    args = parser.parse_args()

    # currently, gather data from O4 down to O3, and save data to temporary files
    runs = ['O4', 'ER16', 'ER15', 'O3']
    for run in runs:
        try:
            save_run_superevents_status(run, f'./superevents_status_{run}.npy')    
        except Exception as msg:
            print(msg)
            with open(args.log, 'w') as infile:
                infile.write(f'{msg} \n')

    # combine npy files
    arrays_list = []
    for run in runs:
        arrays_list.append(np.load(f'./superevents_status_{run}.npy'))
    np.save(f'{args.outfile}', np.concatenate(arrays_list), allow_pickle=False)

    # remove temporary files
    for run in runs:
        os.remove(f'./superevents_status_{run}.npy')

if __name__ == '__main__':
    
    main()
    
