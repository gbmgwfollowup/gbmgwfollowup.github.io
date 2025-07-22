import argparse, requests, json
import numpy as np

def main():

    from gdt.missions.fermi.time import Time
    
    parser = argparse.ArgumentParser(
        
        prog = 'prepare_public_table_data',
        description = 'Prepare data to be displayed on the public table.'
    )

    parser.add_argument('--infile_superevents_data', type=str, help='JSON file with the superevents data from GraceDB.')
    parser.add_argument('--infile_superevents_status', type=str, help='npy file with retraction and significant status of superevents.')
    parser.add_argument('--p_astro_directory', type=str, help='Path to the directory where the p_astro files are being downloaded.')
    parser.add_argument('--outfile', type=str, help='JSON file with data feed for the public table.')
    
    args = parser.parse_args()

    # read json file with superevents data
    with open(args.infile_superevents_data, 'r') as json_file:
        superevents_data = json.load(json_file)

    # read npy file with superevents status
    superevents_status = np.load(args.infile_superevents_status)
        
    # build data for the public table    
    public_table_data = []

    # parse time intervals of LVK runs from gracebd
    import requests
    import pandas as pd
    import ast

    url = 'https://gracedb.ligo.org/documentation/queries.html#id7'
    response = requests.get(url)
    data = response.text

    dataframe = pd.read_html(data, flavor='html5lib')[1]

    run_interval = {}
    for index, row in dataframe.iterrows():
        run_interval[row['runid']] = ast.literal_eval(row['gpstime/t_0 range'])

    # loop over superevents, select and format data 
    for superevent in superevents_data['superevents']:

        # skip mock superevents
        if superevent['preferred_event_data']['superevent'][:1] == 'M': continue

        # skip retracted superevents
        mask = superevents_status['superevent_id'] == superevent['preferred_event_data']['superevent']
        if superevents_status['retracted'][mask][0] == 'True': continue

        # get significant status
        if superevents_status['significant'][mask][0] == 'True': significant = 'True'
        else: significant = 'False'
         
        try:
            # get classification of the superevent and its probability to be astrophysical
            p_astro_file = f'{args.p_astro_directory}/{superevent["preferred_event_data"]["superevent"]}_{superevent["preferred_event_data"]["pipeline"].lower()}_p_astro.json'
            with open(p_astro_file, 'r') as json_file:
                p_astro_data = json.load(json_file)
                # sort data by decreasing p_astro and get the first element
                superevent_type, superevent_p_astro = sorted(p_astro_data.items(), key=lambda x:x[1], reverse=True)[0]
                
        except:
            # superevents with no p_astro file raise an exception. Skip those superevents
            superevent_type, superevent_p_astro = 'n.a.', 'n.a.'

        if isinstance(superevent_p_astro, str): pass
        else: superevent_p_astro = round(superevent_p_astro*100.0, 0)

        # determine the LVK run id comparing the gps time of the superevent with the LVK run (ref: https://gracedb.ligo.org/documentation/queries.html#id7)
        time_gps = superevent['preferred_event_data']['gpstime']

        # parse html table using https://docs.python.org/3/library/html.parser.html
        # compare time_gps and table to determine runid
        for run, interval in run_interval.items():
            if isinstance(interval[0], tuple): continue # skip O4 entry, maintain distinction in O4a, b and c.
            if time_gps > interval[0] and time_gps < interval[1]: runid = run
        
        # format and add superevent entry to data
        entry = { 'id': superevent['preferred_event_data']['superevent'],
                  'gracedb': superevent['links']['self'].replace('/api',''), # point to the main page of the superevent
                  'run_id': runid,
                  'time_gps': round(time_gps, 3),
                  'time_fermi': round(Time(time_gps, format='gps', scale='utc').fermi, 3),
                  'time_iso': Time(time_gps, format='gps', scale='utc').iso,
                  'significant': significant,
                  'far': '{:.3e}'.format(superevent['preferred_event_data']['far']),
                  'type': superevent_type,
                  'pastro': superevent_p_astro,
                  'plots': 'n.a.'
                 }

        public_table_data.append(entry)

    # write data to json file
    with open(args.outfile, 'w') as json_file:
        json.dump(public_table_data, json_file, indent=4)

if __name__ == '__main__':

    main()
    
