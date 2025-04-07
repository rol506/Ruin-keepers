# Importing required library 
import pygsheets 

# Create the Client 
# Enter the name of the downloaded KEYS 
# file in service_account_file 
client = pygsheets.authorize(service_account_file="ruin-keepers-f8e11e9c1f47.json") 

# Sample command to verify successful 
# authorization of pygsheets 
# Prints the names of the spreadsheet 
# shared with or owned by the service 
# account 
print(client.spreadsheet_titles()) 
