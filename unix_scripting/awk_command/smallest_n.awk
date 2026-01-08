# This script finds the line with the smallest length in a file.
# This version is more robust and correctly handles empty files.

# Rule for the first line (NR == 1):
# Initialize 'smallest' and 'smallest_line' with the values from the very first line.
NR == 1 {
  smallest = length($0)
  smallest_line = $0
}

# Rule for subsequent lines (NR > 1):
# Compare the current line's length with the 'smallest' found so far.
NR > 1 {
  if (length($0) < smallest) {
    smallest = length($0)
    smallest_line = $0
  }
}

# The END block runs after all lines are processed.
END {
  # Only print results if at least one line was processed (i.e., the file was not empty).
  if (NR > 0) {
    print "Smallest line length:", smallest
    print "Line:", smallest_line
  }
}
