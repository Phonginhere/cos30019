import os
import re

def extract_test_cases(input_file, output_dir):
    """Extract individual test cases from the main test cases file."""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Split the content by test case headers
    pattern = r'### Test Case (\d+): (.+?)\nNodes:'
    matches = re.finditer(pattern, content)
    
    test_cases = []
    for match in matches:
        case_num = match.group(1)
        case_name = match.group(2)
        start_pos = match.start()
        
        # Find the start of the next test case or end of file
        next_match = re.search(r'### Test Case \d+:', content[start_pos + 1:])
        if next_match:
            end_pos = start_pos + 1 + next_match.start()
        else:
            end_pos = len(content)
        
        # Extract the test case content
        test_case = content[start_pos:end_pos].strip()
        test_cases.append((case_num, case_name, test_case))
    
    # Write each test case to a separate file
    for case_num, case_name, test_case in test_cases:
        output_file = os.path.join(output_dir, f'test_case_{case_num.zfill(2)}.txt')
        
        # Create a clean version without the header comment
        clean_test_case = re.sub(r'### Test Case \d+: .+?\n', '', test_case)
        
        with open(output_file, 'w') as f:
            f.write(clean_test_case)
        
        print(f"Created test case {case_num}: {case_name}")
    
    print(f"Extracted {len(test_cases)} test cases to {output_dir}")

if __name__ == "__main__":
    input_file = 'c:\\Users\\pink\\Documents\\Study\\Uni Study\\Second Year\\Semester 2\\COS30019_IntroAI\\cos30019\\Tests\\test_cases.txt'
    output_dir = 'c:\\Users\\pink\\Documents\\Study\\Uni Study\\Second Year\\Semester 2\\COS30019_IntroAI\\cos30019\\Tests\\TestCases'
    
    extract_test_cases(input_file, output_dir)