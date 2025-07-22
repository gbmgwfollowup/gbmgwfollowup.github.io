import argparse, requests, json

def main():
    
    parser = argparse.ArgumentParser(
        
        prog = 'get_superevents_data',
        description = 'Download superevents data from GraceDB API in JSON format.'
    )

    parser.add_argument('--outfile', type=str, help='JSON file with the superevents data from GraceDB.')
    parser.add_argument('--log', type=str, help='Log file.')
    
    args = parser.parse_args()

    url = f'https://gracedb.ligo.org/api/superevents/?count=1000000&start=0'
    response = requests.get(url)

    if response.status_code == 200:

        data = response.json()
        with open(args.outfile, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    else:
        msg = f'Failed to fetch data. Status code: {response.status_code}'
        print(msg)
        with open(args.log, 'w') as infile:
            infile.write(f'{msg} \n')
            
if __name__ == '__main__':

    main()
    
