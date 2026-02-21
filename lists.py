# Python allows the dynamic typing
'''
#   ██▓███ ▓██   ██▓▄▄▄█████▓ ██░ ██  ▒█████   ███▄    █ 
#  ▓██░  ██▒▒██  ██▒▓  ██▒ ▓▒▓██░ ██▒▒██▒  ██▒ ██ ▀█   █ 
#  ▓██░ ██▓▒ ▒██ ██░▒ ▓██░ ▒░▒██▀▀██░▒██░  ██▒▓██  ▀█ ██▒
#  ▒██▄█▓▒ ▒ ░ ▐██▓░░ ▓██▓ ░ ░▓█ ░██ ▒██   ██░▓██▒  ▐▌██▒
#  ▒██▒ ░  ░ ░ ██▒▓░  ▒██▒ ░ ░▓█▒░██▓░ ████▓▒░▒██░   ▓██░
#  ▒▓▒░ ░  ░  ██▒▒▒   ▒ ░░    ▒ ░░▒░▒░ ▒░▒░▒░ ░ ▒░   ▒ ▒ 
#  ░▒ ░     ▓██ ░▒░     ░     ▒ ░▒░ ░  ░ ▒ ▒░ ░ ░░   ░ ▒░
#  ░░       ▒ ▒ ░░    ░       ░  ░░ ░░ ░ ░ ▒     ░   ░ ░ 
#           ░ ░               ░  ░  ░    ░ ░           ░ 
#           ░ ░                                          
'''
# Lists

# Create variable to save the list
list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
list2 = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", 40, 5.67, [1,2,3], True]
list3 = [1,2,4,5]

# Add a new element
list3.append(6)
list3.append("Anonymous")
# Insert a new element in a position (index, value)
list3.insert(2,3)
# Add several elements to the list
list4 = [1,2,3,4,5]
# extend([value1, value2, value3, ...])
list4.extend([6,7,8])
# Sum 2 lists
lis1 = [1,2,3,4,5]
lis2 = [6,7,8]

# Concatenate list
lis3 = lis1+lis2

# Search for an element in list
lis4 = [1,2,3,4,5,"Anonymous"]
# Check if a value in list exists [True or false]
#print(3 in lis4)
# Another way to get an element if exists in list
#print(lis4.index("Anonymous"))

# Disordered list
lis5 = [1,2,3,4,5,"Anonymous"]
# Determine how many values there are in list [count()]
#print(lis5.count(4))

# Delete an element in list .pop(index), if empty delete the last one
#lis5.pop(2)
# Another way of deleting an element without knowing the index
#lis5.remove("Anonymous")
# Delete all the list
#lis5.clear()
# Reverse the values from last one to first one
lis5.reverse()

print(lis5)
# Print list
#print(lis3)
#print(len(list2))