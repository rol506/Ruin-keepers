import pygsheets
import numpy as np

gc = pygsheets.authorize()

# Open spreadsheet and then worksheet
sh = gc.open('my new sheet')
wks = sh.sheet1

# Update a cell with value (just to let him know values is updated ;) )
wks.update_value('A1', "Hey yank this numpy array")
my_nparray = np.random.randint(10, size=(3, 4))

# update the sheet with array
wks.update_values('A2', my_nparray.tolist())

# share the sheet with your friend
sh.share("myFriend@gmail.com")