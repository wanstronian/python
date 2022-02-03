'''
Created on 30 Nov 2021

@author: Jim.Strange

Purpose: Takes a Jira export with columns in any order and produces an output file with
         consistent ordering, that can be used in Excel etc. Also merges multi-partite
         fields (such as labels, sprints) into a single field to ensure consistent
         column count
'''
import csv
from sys import argv, exit
from os.path import exists
from os import rename

def main(argv):
    #Check for input file being passed
    if not argv: # If not passed as argument, ask for it
        input_filename = input('Enter input file name: ')
    else:
        input_filename = argv[0]

    if not exists(input_filename):
        print(f'File "{input_filename}" does not exist, exiting.')
        exit()
    
    # Initialise message sets
    messages = []
    ticket_messages = []
    
    # Set column header mapping
    #                  Input column                   Output column
    column_mapping = (['Issue key',                   'Issue key'],
                      ['Priority',                    'Priority'],
                      ['Summary',                     'Summary'],
                      ['Issue Type',                  'Issue type'],
                      ['Description',                 'Description'],
                      ['Status',                      'Status'],
                      ['Components',                  'Component'],
                      ['Reporter',                    'Reporter'],
                      ['Assignee',                    'Assignee'],
                      ['Created',                     'Created'],
                      ['Updated',                     'Updated'],
                      ['Resolved',                    'Resolved'],
                      ['Resolution',                  'Resolution'],
                      ['Custom field (EPD Team)',     'EPD team'],
                      ['Custom field (Epic Link)',    'Epic link'],
                      ['Custom field (Epic Name)',    'Epic name'],
                      ['Custom field (Story Points)', 'Story points'],
                      ['Fix versions',                'Fix versions'],
                      ['Sprint',                      'Sprints'],
                      ['Labels',                      'Labels'],
                      ['Original estimate',           'Original estimate'],
                      ['Remaining Estimate',          'Remaining estimate'],
                      ['Time Spent',                  'Time spent'],
                      ['Custom field (Flagged)',      'Flagged'])
    
    # Set output field list and order
    # Note the text must match the output column text in the mapping above
    output_list = ('Issue key',
                   'Priority',
                   'Summary',
                   'Issue type',
                   'Description',
                   'Status',
                   'Component',
                   'Reporter',
                   'Assignee',
                   'Created',
                   'Updated',
                   'Resolved',
                   'Resolution',
                   'EPD team',
                   'Epic link',
                   'Epic name',
                   'Story points',
                   'Fix versions',
                   'Sprints',
                   'Labels',
                   'Original estimate',
                   'Remaining estimate',
                   'Time spent',
                   'Flagged')
    
    # Create a dict from the output list
    output_dict = dict.fromkeys(output_list)
    
    # Open the input file with UTF-8 encoding (Jira encoding)
    with open(input_filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        data = list(reader)
        
    # Identify which columns hold multi-partite data
    sprint_cols = []
    labels_cols = []
    components_cols = []
    for index, col in enumerate(data[0]):
        if col == "Sprint":
            sprint_cols.append(index)
        elif col == "Labels":
            labels_cols.append(index)
        elif col == "Components":
            components_cols.append(index)
                      
    #Create the output filename from the input filename, appended with '_transformed'
    output_filename = input_filename.split('.csv')[0] + "_transformed.csv"
    
    # Check for output file already open
    if exists(output_filename):
        try:
            rename(output_filename, output_filename)
        except OSError:
            print(f'Access error on {output_filename} - Check it\'s not open elsewhere')
            exit()
            
    # If all good, open the file for output
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
    
        # Intialise the writer and write the header row
        writer = csv.DictWriter(csvfile, fieldnames = output_list)
        writer.writeheader()
        
        # Loop through all rows, re-ordering and combining data
        # Starting at second row so we don't process the header row
        total_rows = 0
        for row in enumerate(data[1:]):
            # Match input data item with appropriate output column
            for index, col in enumerate(data[0]):
                for source, dest in column_mapping:
                    if col == source:
                        output_dict[dest]= row[1][index]
                
            # Now add labels, sprints, components multi-partite field
            labels = ''
            first_label = True
            for i in labels_cols:
                label = row[1][i]
                if label != '':
                    if not first_label:
                        labels = labels + "|"
                    labels = labels + label
                    first_label = False
    
            sprints = ''
            first_sprint = True
            for i in sprint_cols:
                sprint = row[1][i]
                if sprint != '':
                    if not first_sprint:
                        sprints = sprints + "|"
                    sprints = sprints + sprint
                    first_sprint = False
                    
            components = ''
            comp_count = 0
            first_component = True
            for i in components_cols:
                component = row[1][i]
                if component != '':
                    if not first_component:
                        components = components + "|"
                    comp_count = comp_count + 1
                    components = components + component
                    first_component = False
            if comp_count > 1:
                ticket_messages.append(f'\nWarning - {output_dict["Issue key"]} has multiple components set')
                    
            # Set the field values
            output_dict['Sprints'] = sprints
            output_dict['Labels'] = labels
            output_dict['Component'] = components
            
            total_rows = total_rows + 1 # Increment row count
            
            # Write the line to output file
            writer.writerow(output_dict)
        
    # Close the file
#    csvfile.close()

    # Build  and print the status message set
    messages.append(f'\nDone - {total_rows} rows processed.')
    for message in ticket_messages:
        messages.append(message)
    print(' '.join(messages))
    
    
if __name__ == '__main__':
    main(argv[1:])
