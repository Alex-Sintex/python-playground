import subprocess
import sys

def get_current_volume():
    """Fetch the current volume level using osascript."""
    get_volume_cmd = ['osascript', '-e', 'output volume of (get volume settings)']
    current_volume = subprocess.run(get_volume_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return int(current_volume.stdout.decode().strip())

def display_dialog(message, buttons, default_button="Yes", icon="note"):
    """Display an AppleScript dialog with customizable message, buttons, and icon."""
    ask_adjust_cmd = ['osascript', '-e', f'display dialog "{message}" with icon {icon} buttons {buttons} default button "{default_button}"']
    response = subprocess.run(ask_adjust_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return response.stdout.decode().strip()

def ask_for_new_volume(current_volume):
    """Prompt user to input a new volume level."""
    cmd = ['osascript', '-e', f'display dialog "Set the desired volume" with icon caution default answer "{current_volume}" buttons {{"Cancel", "OK"}} default button "OK"']
    response = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return response.stdout.decode().strip()

def set_volume(new_volume):
    """Set the system volume to the provided level between 0 and 100."""
    if 0 <= new_volume <= 100:
        set_volume_cmd = ['osascript', '-e', f'set volume output volume {new_volume}']
        subprocess.run(set_volume_cmd, stderr=subprocess.DEVNULL)
        print(f"Volume set to {new_volume}%")
    else:
        print("Invalid volume level. It must be between 0 and 100.")

def main():
    try:
        # Step 1: Get the current volume
        current_volume = get_current_volume()

        # Step 2: Ask user if they want to adjust the volume
        adjust_response = display_dialog(f"Current Volume is {current_volume}%. Do you want to adjust it?", buttons='{"No", "Yes"}')

        # Step 3: If user selects "Yes", ask for the new volume level
        if "Yes" in adjust_response:
            cmd_response = ask_for_new_volume(current_volume)

            # Extract the new volume level from the response
            if "OK" in cmd_response:
                try:
                    new_volume = int(cmd_response.split(":")[-1].strip())
                    set_volume(new_volume)
                except ValueError:
                    print("Invalid input, exiting program...")
                    sys.exit(1)

        else:
            print("Volume adjustment canceled.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running osascript: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()