'''
Created on 18 Oct 2021

@author: Jim.Strange
'''
# Import modules
from datetime import datetime   # date/time functions
from jira import JIRA           # Jira functions
from sys import argv            # Command line arguments
from configparser import ConfigParser, NoOptionError

def main(argv):
    
    #Check for config file being passed
    if not argv:
        print('No config file passed, exiting.')
        exit()
        
    # Parse the config file to extract token values
    print('Parsing config file...', end='', flush=True)
    config = ConfigParser()
    config['DEFAULT']={}
    try:
        with open(argv[0]) as f:
            config.read_file(f)
    except IOError:
        print('Config file does not exist, exiting.')
        quit()
         
    # Get options from config file
    try:
        jira_url = config.get('DEFAULT', 'jira_url')
    except NoOptionError:
        print('Jira URL not provided in config file, exiting.')
        quit()

    try:
        auth_user = config.get('DEFAULT', 'auth_user')
    except NoOptionError:
        print('User name not provided in config file, exiting.')
        quit()

    try:
        auth_token = config.get('DEFAULT', 'auth_token')
    except NoOptionError:
        print('Authentication token not provided in config file, exiting.')
        quit()

    try:
        project_id = config.get("DEFAULT","project_id")
    except NoOptionError:
        print('No project ID provided in config file, exiting.')
        quit()
        
    # Authenticate with Jira
    auth_jira = JIRA(jira_url, basic_auth=(auth_user, auth_token))
    
    components = auth_jira.project_components(project_id)
    
    if len(components) == 0:
        print ('No components in project EPD')
        quit()
    
    print (f'Extracting components from project {project_id}...')
        # Define filename with current date/time suffix
    dt = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_name = 'C:\\Users\\Jim.Strange\\Valtech\\UK.Client.Wiggle - General\\01 Delivery Management\\WiggleCRC Jira Tracking\\Deep Dive\\' + project_id + ' Components Export ' + dt + '.csv'
        
    # Open file for writing data
    with open(file_name, 'w') as output_file:
        
        print('Writing components...'),
        # Loop through all issues and write status change info
        for component in components:
            output_file.write(f'{component.name}\n')
    print('Finished.')
    
    
if __name__ == '__main__':
    main(argv[1:])