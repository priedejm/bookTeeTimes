import sys
import subprocess

def remove_cron_job(course, day, min_time, max_time, players):
    # Recreate the cron command from the input parameters
    cron_command = f"python3 /home/teetimesuser/bookTeeTimes/bookTeeTimes.py '{course}' '{day}' '{min_time}' '{max_time}' '{players}'"

    # Build the cron timing part (the part that specifies when the cron job should run)
    # This should match the cron job timing used when adding the job.
    cron_hour = 7  # Fixed to 7:00 AM
    cron_minute = 0  # Fixed to 0 minute
    cron_day = int(day.split('-')[2])  # Extract the day from the date (YYYY-MM-DD)
    cron_month = int(day.split('-')[1])  # Extract the month from the date (YYYY-MM-DD)

    # Full cron timing
    cron_timing = f"{cron_minute} {cron_hour} {cron_day} {cron_month} *"
    
    # Full cron job entry to search for (timing + command)
    cron_job = f"{cron_timing} {cron_command}"

    # Get the current crontab
    try:
        result = subprocess.run(["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        current_cron = result.stdout.decode()
    except subprocess.CalledProcessError as e:
        print("Error reading crontab.")
        return

    # Check if the specific cron job exists
    if cron_job in current_cron:
        # Remove the matching cron job
        new_cron = "\n".join([line for line in current_cron.splitlines() if cron_job not in line])
        
        # Update the crontab
        try:
            subprocess.run(
                f"echo \"{new_cron}\" | crontab -",
                shell=True,
                check=True
            )
            print(f"Cron job removed successfully:\n{cron_job}")
        except subprocess.CalledProcessError as e:
            print(f"Error removing cron job: {e}")
    else:
        print("Cron job not found!")

def main():
    # Check if the required number of arguments is provided
    if len(sys.argv) != 6:
        print("Usage: python3 bookTeeTimes.py <course> <day> <minTime> <maxTime> <players>")
        sys.exit(1)

    # Get parameters from the command line
    course = sys.argv[1]
    day = sys.argv[2]
    min_time = sys.argv[3]
    max_time = sys.argv[4]
    players = sys.argv[5]

    # Assign the values to variables (already done above)
    print(f"Course: {course}")
    print(f"Day: {day}")
    print(f"Min Time: {min_time}")
    print(f"Max Time: {max_time}")
    print(f"Players: {players}")

    # Call the function to remove the cron job
    remove_cron_job(course, day, min_time, max_time, players)

if __name__ == "__main__":
    main()


# python3 createCronJob.py "Charleston Municipal" "2025-03-15" "08:00" "10:00" "4"
