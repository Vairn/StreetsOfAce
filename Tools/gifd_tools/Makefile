CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2
AR = ar
ARFLAGS = rcs

# Library files
LIB_SOURCES = gif_delta_reader.c
LIB_OBJECTS = $(LIB_SOURCES:.c=.o)
LIB_NAME = libgifd.a

# Test program (if you want to create one later)
TEST_SOURCES = test_reader.c
TEST_OBJECTS = $(TEST_SOURCES:.c=.o)
TEST_EXECUTABLE = test_reader

.PHONY: all clean library test

# Default target
all: library

# Build the static library
library: $(LIB_NAME)

$(LIB_NAME): $(LIB_OBJECTS)
	$(AR) $(ARFLAGS) $@ $^
	@echo "Library $(LIB_NAME) created successfully"

# Build object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Test target (if test_reader.c exists)
test: $(TEST_EXECUTABLE)

$(TEST_EXECUTABLE): $(TEST_OBJECTS) $(LIB_NAME)
	$(CC) $(CFLAGS) $^ -o $@
	@echo "Test executable $(TEST_EXECUTABLE) created successfully"

# Clean up build files
clean:
	rm -f $(LIB_OBJECTS) $(TEST_OBJECTS) $(LIB_NAME) $(TEST_EXECUTABLE)
	@echo "Cleaned up build files"

# Install library (optional)
install: library
	@echo "To install, copy $(LIB_NAME) and gif_delta_reader.h to your system library paths"
	@echo "Example:"
	@echo "  sudo cp $(LIB_NAME) /usr/local/lib/"
	@echo "  sudo cp gif_delta_reader.h /usr/local/include/"

# Show usage
help:
	@echo "Available targets:"
	@echo "  all      - Build the library (default)"
	@echo "  library  - Build the static library"
	@echo "  test     - Build the test program (if test_reader.c exists)"
	@echo "  clean    - Remove all build files"
	@echo "  install  - Show installation instructions"
	@echo "  help     - Show this help message"

# Dependencies
gif_delta_reader.o: gif_delta_reader.c gif_delta_reader.h 