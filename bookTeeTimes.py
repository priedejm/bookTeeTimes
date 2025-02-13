import sys

def main():
    # Check if the required number of arguments is provided
    if len(sys.argv) != 6:
        print("Usage: python bookTeeTimes.py <course> <day> <minTime> <maxTime> <players>")
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

if __name__ == "__main__":
    main()
