import argparse
import os

import yaml
from behave.model import Scenario
from behave.model import ScenarioOutline
from behave.parser import Parser

CLI = argparse.ArgumentParser()
CLI.add_argument(
    '--exclude-tags',
    nargs='*',
    type=str,
    default=['skip', 'need_fix'],  # default if nothing is provided
)

args = CLI.parse_args()

excluded_tags = args.exclude_tags


def parse_feature_files(feat_files):
    feature_scenarios = {}
    parser = Parser()

    for curr_feature_file in feat_files:
        with open(curr_feature_file, 'r') as f:
            feature_content = f.read()
            feature = parser.parse(feature_content, filename=curr_feature_file)

            curr_feature_file = feature.name
            scenarios = []

            for element in feature:
                if isinstance(element, (ScenarioOutline, Scenario)):
                    # Extract only scenario name and description
                    scenario_name = element.name
                    scenario_description = element.description
                    scenario_tags = element.tags
                    scenarios.append({
                        'name': scenario_name,
                        'description': scenario_description,
                        'tags': scenario_tags + feature.tags
                    })

            if scenarios:
                # Use the original feature file name (without extension) as the key
                feature_file_name = os.path.splitext(os.path.basename(curr_feature_file))[0]
                feature_scenarios[feature_file_name] = {
                    'feature_name': feature_file_name,
                    'scenarios': scenarios,
                }

    return feature_scenarios


root_directory = 'bdd/features'
feature_files = []
for root, dirs, files in os.walk(root_directory):
    for file in files:
        if file.endswith('.feature'):
            feature_files.append(os.path.join(root, file))

all_scenarios = []
scenarios_by_feature = parse_feature_files(feature_files)

output_directory = 'docs/features'  # Save feature-specific MD files under 'docs/features'
os.makedirs(output_directory, exist_ok=True)

# Create index.md to list features and link to respective pages
index_content = '# Features\n\n'

nav_links = []

for curr_feature_file_name, data in scenarios_by_feature.items():
    feature_name = data['feature_name']
    output_file_name = f'{curr_feature_file_name}.md'
    feature_file_path = os.path.join(output_directory, output_file_name)

    # Create a link to the feature's page
    index_content += f"- [{feature_name}]({os.path.join('features', output_file_name)})\n"

    # Append a navigation link for the feature
    nav_links.append(
        {feature_name: f'features/{curr_feature_file_name}.md'}
    )

    # Save the feature-specific MD file in 'docs/features' subdirectory
    with open(feature_file_path, 'w') as feature_file:
        feature_file.write(f'# Feature: {feature_name}\n\n')
        for scenario in data['scenarios']:
            if not set(excluded_tags).intersection(set(scenario['tags'])):
                all_scenarios.append(scenario['name'])
                feature_file.write(f'* {scenario["name"]}\n')

# Save index.md in 'docs' directory
index_file_path = os.path.join('docs', 'index.md')
with open(index_file_path, 'w') as index_file:
    index_file.write(index_content)

    # Add a link to the Azure DevOps pipeline
    azure_devops_link = 'Azure DevOps pipeline analytics'
    azure_devops_url = 'https://dev.azure.com/pagopaspa/cstar-platform-app-projects/_test/analytics?definitionId=1385&contextType=build'
    azure_devops_badge = '[![Build Status](https://dev.azure.com/pagopaspa/cstar-platform-app-projects/_apis/build/status%2Fidpay%2Fidpay-functional-testing%2Fidpay-functional-testing.discount-flow?branchName=main&jobName=Run_functional_tests)](https://dev.azure.com/pagopaspa/cstar-platform-app-projects/_build/latest?definitionId=1385&branchName=main)'
    index_file.write(f'\n\n **[{azure_devops_link}]({azure_devops_url})**')
    index_file.write(f'\n\n {azure_devops_badge}')

# Update the MkDocs configuration file (mkdocs.yml) to include navigation link
mkdocs_config = {
    'site_name': 'IDPay Functional Testing',
    'site_url': 'https://pagopa.github.io/idpay-functional-testing',
    'repo_name': 'pagopa/idpay-functional-testing',
    'repo_url': 'https://github.com/pagopa/idpay-functional-testing',
    'site_author': 'PagoPA',
    'use_directory_urls': True,
    'nav': [
        {'Home': 'index.md'},
        {'Features': nav_links},
        {'Azure DevOps Pipeline': azure_devops_url}
    ],
    'theme': {
        'name': 'material',
        'font': {'text': 'Roboto', 'code': 'Roboto Mono'},
    },
}

# Save the updated MkDocs configuration to mkdocs.yml
mkdocs_yaml_path = 'mkdocs.yml'
with open(mkdocs_yaml_path, 'w') as mkdocs_yaml:
    yaml.dump(mkdocs_config, mkdocs_yaml)
