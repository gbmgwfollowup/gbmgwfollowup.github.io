import argparse, requests, json

def main():
    
    parser = argparse.ArgumentParser(
        
        prog = 'get_superevents_p_astro',
        description = 'Download superevents p_astro data in JSON format.'
    )

    parser.add_argument('--infile', type=str, help='JSON file with the superevents data from GraceDB.')
    parser.add_argument('--p_astro_directory', type=str, help='Path to the directory where the p_astro files are being downloaded.')
    parser.add_argument('--log', type=str, help='Log file.')
    
    args = parser.parse_args()
        
    with open(args.infile, 'r') as json_file:
        superevents_data = json.load(json_file)
    
    for superevent in superevents_data['superevents']:

        superevent_data = superevent['preferred_event_data']
        superevent_id = superevent_data['superevent']
        
        # skip mock events
        if superevent_id[:1] == 'M': continue
   
        # get url to p_astro file
        pipeline = superevent_data['pipeline'].lower()
        p_astro_url = f'https://gracedb.ligo.org/api/superevents/{superevent_id}/files/{pipeline}.p_astro.json'
        
        # download data of p_astro file and save the data to disk
        response = requests.get(p_astro_url)

        if response.status_code == 200:

            p_astro_data = response.json()
            p_astro_outfile = f'{args.p_astro_directory}/{superevent_id}_{pipeline}_p_astro.json'
            with open(p_astro_outfile, 'w') as json_file:
                json.dump(p_astro_data, json_file)

        else:
            
            download_failed = f'No p_astro file for {superevent_id}.\n'
            with open(args.log, 'a') as infile:
                infile.write(download_failed)
                
if __name__ == '__main__':

    main()
    
