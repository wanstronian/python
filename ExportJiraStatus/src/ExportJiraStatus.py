'''
 Export Jira status changes with dates
 To be used for  understanding flow for different ticket sizes
'''

# TODO
# Retrieve URL and auth info from config file DONE
# Retrieve project TLA from config file DONE
# Get output file path and name from config file
# Retrieve search query from config file
# Pass config file name as argument to program DONE
# Get field config/order from config file?
# Update to extract > 1000 issues https://stackoverflow.com/questions/41858291/exporting-1000-issues-from-jira



# Import modules
from datetime import datetime   # date/time functions
from jira import JIRA           # Jira functions
from sys import argv, exit      # Command line arguments
from configparser import ConfigParser, NoOptionError
import pytz

# Function to convert Jira date to Excel date.
def ConvertDate(jira_date, tz_correction=False):
    fmt = '%d/%m/%Y %H:%M:%S'
    datetimeObj = datetime.strptime(jira_date,'%Y-%m-%dT%H:%M:%S.%f%z')
    # Correct for DST if required
    if tz_correction:
        lon = pytz.timezone('Europe/London')
        issue_dt = datetime(datetimeObj.year, datetimeObj.month, datetimeObj.day, datetimeObj.hour, datetimeObj.minute, datetimeObj.second, tzinfo=pytz.utc)
        datetimeObj = issue_dt.astimezone(lon)

    return datetimeObj.strftime(fmt)


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
        
    try:
        convert_dst = config.get('DEFAULT', 'convert_dst')
    except NoOptionError:
        print('No DST correction flag provided in config file, exiting.')
                
    print('done.')
    # Authenticate with Jira
    auth_jira = JIRA(jira_url, basic_auth=(auth_user, auth_token))
    
    print (f'Extracting issues from project {project_id}...', end='', flush=True)
    # Get all issues from selected project in issue order.
    # Setting maxResults to false returns all records
    # Expanding changelog returns all change details, which include status transitions
    search_string = 'project=' + project_id + ' ORDER BY issue ASC'
    issues = auth_jira.search_issues(search_string, maxResults=0, expand=['changelog'])
    print('done.')
    
    # Check there are records to process
    if len(issues) > 0:
        # Define filename with current date/time suffix
        dt = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        
        file_name = 'C:\\Users\\Jim.Strange\\Valtech\\UK.Client.Wiggle - General\\01 Delivery Management\\WiggleCRC Jira Tracking\\Deep Dive\\Jira Status Export ' + dt + '.csv'
        
        # Open file for writing data
        with open(file_name, 'w') as output_file:
            # Heading for tabular file output
            output_file.write('Issue, Issue Type, Date, From, To')
            
            print('Creating change log...', end='', flush=True),
            # Loop through all issues and write status change info
            for issue in issues:
                for history in issue.changelog.histories:
                    for item in history.items:
                        if item.field == 'status':#
#                            if new_issue:
#                                converted_date = ConvertDate(issue.fields.created, convert_dst)
#                                output_file.write(f'\n{issue.key},{issue.fields.issuetype.name},{converted_date},None,{item.fromString}')
#                                new_issue = False
                            # Convert Jira date format to Excel-compatible
                            converted_date = ConvertDate(history.created, convert_dst)
                            from_string = item.fromString
                            output_file.write(f'\n{issue.key},{issue.fields.issuetype.name},{converted_date},{item.fromString},{item.toString}')
                            #print(f'\n{issue.key},{issue.fields.issuetype.name},{converted_date},{item.fromString},{item.toString}')
                converted_date = ConvertDate(issue.fields.created, convert_dst)
                output_file.write(f'\n{issue.key},{issue.fields.issuetype.name},{converted_date},None,{from_string}')   
    
    print('Finished.')
    
    
if __name__ == '__main__':
    main(argv[1:])