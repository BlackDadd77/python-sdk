#!/bin/bash
# Test script for multi-language examples
# This script validates all examples in the multi-lang directory

# Don't exit on first error - we want to run all tests
# set -e

echo "=================================="
echo "Multi-Language Examples Test Suite"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXAMPLES_DIR="$SCRIPT_DIR"

success_count=0
fail_count=0

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
        ((success_count++))
    else
        echo -e "${RED}✗ $2${NC}"
        ((fail_count++))
    fi
}

# Test JSON files
echo "Testing JSON files..."
for json_file in "$EXAMPLES_DIR/json"/*.json; do
    if [ -f "$json_file" ]; then
        python3 -m json.tool "$json_file" > /dev/null 2>&1
        print_result $? "JSON validation: $(basename "$json_file")"
    fi
done
echo ""

# Test Python syntax
echo "Testing Python files..."
for py_file in "$EXAMPLES_DIR/python"/*.py; do
    if [ -f "$py_file" ]; then
        python3 -m py_compile "$py_file" > /dev/null 2>&1
        print_result $? "Python syntax: $(basename "$py_file")"
    fi
done
echo ""

# Test Ruby syntax (if ruby is available)
echo "Testing Ruby files..."
if command -v ruby &> /dev/null; then
    for rb_file in "$EXAMPLES_DIR/ruby"/*.rb; do
        if [ -f "$rb_file" ]; then
            ruby -c "$rb_file" > /dev/null 2>&1
            print_result $? "Ruby syntax: $(basename "$rb_file")"
        fi
    done
else
    echo -e "${YELLOW}⚠ Ruby not installed, skipping Ruby tests${NC}"
fi
echo ""

# Test Kotlin syntax (if kotlinc is available)
echo "Testing Kotlin files..."
if command -v kotlinc &> /dev/null; then
    for kt_file in "$EXAMPLES_DIR/kotlin"/*.kt; do
        if [ -f "$kt_file" ]; then
            kotlinc -nowarn "$kt_file" -d /tmp/kotlin-test.jar 2>&1
            print_result $? "Kotlin syntax: $(basename "$kt_file")"
            rm -f /tmp/kotlin-test.jar
        fi
    done
else
    echo -e "${YELLOW}⚠ Kotlin not installed, skipping Kotlin tests${NC}"
fi
echo ""

# Test Docker files
echo "Testing Docker files..."
if command -v docker &> /dev/null; then
    dockerfile="$EXAMPLES_DIR/docker/Dockerfile"
    if [ -f "$dockerfile" ]; then
        # Just check if file is readable and has valid syntax (basic check)
        grep -q "FROM" "$dockerfile" && grep -q "WORKDIR" "$dockerfile"
        print_result $? "Docker syntax: Dockerfile"
    fi
    
    composefile="$EXAMPLES_DIR/docker/docker-compose.yml"
    if [ -f "$composefile" ]; then
        # Check basic YAML syntax
        python3 -c "import yaml; yaml.safe_load(open('$composefile'))" 2>&1
        print_result $? "Docker Compose syntax: docker-compose.yml"
    fi
else
    echo -e "${YELLOW}⚠ Docker not installed, skipping Docker tests${NC}"
fi
echo ""

# Test HTML files
echo "Testing HTML files..."
for html_file in "$EXAMPLES_DIR/html"/*.html; do
    if [ -f "$html_file" ]; then
        # Basic HTML validation - check for html, head, body tags
        grep -q "<html" "$html_file" && grep -q "<head" "$html_file" && grep -q "<body" "$html_file"
        print_result $? "HTML structure: $(basename "$html_file")"
    fi
done
echo ""

# Test PowerShell files (basic syntax check)
echo "Testing PowerShell files..."
for ps_file in "$EXAMPLES_DIR/powershell"/*.ps1; do
    if [ -f "$ps_file" ]; then
        # Basic check - file exists and is readable
        [ -r "$ps_file" ]
        print_result $? "PowerShell file: $(basename "$ps_file")"
    fi
done
echo ""

# Print summary
echo "=================================="
echo "Test Summary"
echo "=================================="
echo -e "${GREEN}Passed: $success_count${NC}"
if [ $fail_count -gt 0 ]; then
    echo -e "${RED}Failed: $fail_count${NC}"
else
    echo -e "${GREEN}Failed: $fail_count${NC}"
fi
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
