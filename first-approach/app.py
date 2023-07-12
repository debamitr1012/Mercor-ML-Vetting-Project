from flask import Flask, render_template, request
import requests
import openai
import os
import shutil

# Set up OpenAI GPT API credentials
#openai.api_key = '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'
openai.api_key = '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'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    github_url = request.form['github_url']
    most_complex_repository = analyze_github_user(github_url)

    if most_complex_repository:
        repo_name = most_complex_repository['name']
        complexity_score = most_complex_repository['complexity_score']
        return render_template('result.html', repo_name=repo_name, complexity_score=complexity_score)
    else:
        return render_template('error.html')

# Fetch a user's repositories from their GitHub user URL
def fetch_user_repositories(url):
    username = url.split("/")[-1]
    api_url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(api_url)
    if response.status_code == 200:
        try:
            repositories = response.json()
            return repositories
        except ValueError as e:
            print("Invalid JSON response:", e)
            return None
    else:
        print("Error fetching repositories:", response.status_code)
        return None

# Preprocess the code in repositories
import tempfile
def preprocess_code(repository):
    # Clone the repository to a temporary directory
    with tempfile.TemporaryDirectory() as temp_directory:
        repository_url = repository["clone_url"]
        os.system(f"git clone {repository_url} {temp_directory}")
        # Implement your code preprocessing techniques here
        preprocessed_code = ""
        # Example: Read all Python files in the repository and concatenate their contents
        for root, dirs, files in os.walk(temp_directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as file:
                        preprocessed_code += file.read()
    return preprocessed_code


# Implement prompt engineering for code evaluation using GPT
def evaluate_code_complexity(code):
    # Define the prompt for GPT evaluation
    prompt = f"Assess the technical complexity of the following code:\n\n{code}\n\nComplexity Score:"

    # Generate a completion using OpenAI GPT-3.5 API
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=10,  # Adjust the max tokens based on your requirements
        n=1,  # Number of completions to generate
        stop=None,  # Customize stop conditions if needed
    )

    # Extract the generated complexity score from the completion response
    complexity_score = response.choices[0].text.strip()

    # Return the complexity score
    return complexity_score

# Identify the most technically complex repository
def find_most_complex_repository(repositories):
    most_complex_repository = None
    max_complexity_score = 0

    for repository in repositories:
        code = preprocess_code(repository)
        complexity_score = evaluate_code_complexity(code)

        # Convert the complexity score to a numeric value if necessary
        complexity_score = float(complexity_score)

        if complexity_score > max_complexity_score:
            max_complexity_score = complexity_score
            most_complex_repository = repository

    return most_complex_repository

# Main function to analyze a user's GitHub repositories
def analyze_github_user(url):
    repositories = fetch_user_repositories(url)

    if repositories:
        most_complex_repository = find_most_complex_repository(repositories)
        if most_complex_repository:
            most_complex_repository['complexity_score'] = evaluate_code_complexity(
                preprocess_code(most_complex_repository)
            )
        return most_complex_repository
    else:
        return None


if __name__ == '__main__':
    app.run(debug=True)
