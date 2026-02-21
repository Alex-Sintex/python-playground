# Correct password
password = "securepassword"

# Get the user's guess
guess = input("Enter the password: ")

# While the guess is not equal to the password, keep asking
while guess != password:
    print("Incorrect password, try again.")
    guess = input("Enter the password: ")

# Once the correct password is entered
print("ACCESS GRANTED")
