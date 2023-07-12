import os

from behave.model import Background
from behave.model import Scenario
from behave.model import ScenarioOutline
from behave.parser import Parser


def parse_feature_files(feature_files):
    scenarios = {}
    parser = Parser()

    for feature_file in feature_files:
        with open(feature_file, 'r') as file:
            feature_content = file.read()  # Read the file content as a string
            feature = parser.parse(feature_content, filename=feature_file)

            feature_name = feature.name  # Get the feature name
            feature_scenarios = []
            background_steps = []

            # Find and extract background steps
            for element in feature:
                if isinstance(element, Background):
                    background_steps = [step.keyword + ' ' + step.name for step in element.steps]

            # Find and extract scenarios
            for element in feature:
                if isinstance(element, (ScenarioOutline, Scenario)):
                    scenario_steps = [step.keyword + ' ' + step.name for step in element.steps]
                    if background_steps:
                        # Prepend background steps to scenario steps
                        scenario_steps = background_steps + scenario_steps
                    feature_scenarios.append({
                        'name': element.name,
                        'description': element.description,
                        'steps': scenario_steps,
                    })

            scenarios[feature_name] = {
                'file_paths': [feature_file],  # Store the file paths as a list
                'scenarios': feature_scenarios,
            }

    return scenarios


# Set the root directory for feature files
root_directory = 'bdd/features/pilot'

# Collect all feature file paths within the root directory and its subdirectories
feature_files = []
for root, dirs, files in os.walk(root_directory):
    for file in files:
        if file.endswith('.feature'):
            feature_files.append(os.path.join(root, file))

# Call the function to parse the feature files and retrieve the scenarios
scenarios = parse_feature_files(feature_files)

# Create and open the output file in write mode
output_file_path = 'docs/output.md'
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
with open(output_file_path, 'w') as output_file:
    # Write the extracted scenarios per feature to the output file
    for feature, feature_data in scenarios.items():
        file_paths = feature_data['file_paths']
        file_path = file_paths[
            0] if file_paths else ''  # Access the first element or use an empty string if no file path exists
        output_file.write(f'## Feature: [{feature}]({file_path})\n\n')
        for scenario in feature_data['scenarios']:
            output_file.write(f'### Scenario: {scenario["name"]}\n')
            output_file.write(f'Description: {scenario["description"]}\n')
            output_file.write('<details>\n')
            output_file.write('<summary>Steps (Click to expand)</summary>\n')
            output_file.write(f'\n')
            steps = '\n\n'.join(f'- {step}' for step in scenario['steps'])
            output_file.write(f'{steps}\n')
            output_file.write('</details>\n')
            output_file.write('\n---\n')

# Read the contents of the output file
with open(output_file_path, 'r') as output_file:
    output_content = output_file.read()

# Print a message to indicate successful file generation
print(f'Output file generated: {output_file_path}')
