# This script finds the line with the smallest length in a file.

BEGIN {
  # Initialize smallest to a very large number.
  smallest_line = $0
  smallest = length($0)
}

# This block is executed for each line of the input file.
{
  if (length($0) < smallest) {
    smallest = length($0)
    smallest_line = $0
  }
}

# This block is executed after all lines have been processed.
END {
  print "Smallest line length:", smallest
  print "Line:", smallest_line
}
