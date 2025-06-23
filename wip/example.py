remaining_upsets = int(input("Enter remaining upsets: "))  # default 4
remaining_fights = int(input("Enter remaining fights: "))   # default 13



while remaining_fights > 0:
  percent = remaining_upsets / remaining_fights * 100
  print(f"{remaining_upsets} upsets out of {remaining_fights} fights ({percent:.0f}%)")
 # remaining_upsets -= 1
  remaining_fights -= 1

'''
def get_yes_no_input(prompt_message):
    """
    Prompts the user for a yes/no response and returns True for 'yes' or 'y',
    and False for 'no' or 'n'. Handles case-insensitivity and invalid input.
    """
    while True:
        user_input = input(f"{prompt_message} (yes/no): ").lower().strip()
        if user_input in ["yes", "y"]:
            return True
        elif user_input in ["no", "n"]:
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

# Example usage:
if get_yes_no_input("Do you want to continue?"):
    print("Continuing the process...")
else:
    print("Exiting the process.")# Example of a simple program to track upsets in fights
'''
