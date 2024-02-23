# OhMyAWS

Tired of wrestling with CloudFormation templates for AWS? OhMyAWS simplifies interactions by allowing you to ingest documentation into a MongoDB database and query it using natural language, thanks to the integration with OpenAI's GPT models. Whether you're looking to understand `boto3` or navigate AWS services, OhMyAWS is your go-to tool.

## Prerequisites

Before you get started, ensure you have the following:

- Python 3.8 or newer.
- MongoDB instance (local or Atlas).
- OpenAI API key for GPT model access.

## Installation

Clone the OhMyAWS repository and navigate to the project directory:

```bash
git clone https://github.com/umuthopeyildirim/OhMyAWS.git
cd OhMyAWS
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Install the `pandoc` for RTS packages:

```bash
brew install pandoc # macOS
sudo apt-get install pandoc # Ubuntu
```

This command installs `langchain`, `langchain-openai`, and all other dependencies necessary for running OhMyAWS.

## Configuration

Create a `.env` file in the root of your project directory with the following contents, replacing the placeholders with your actual MongoDB URI and OpenAI API key:

```plaintext
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Ingesting Documents

To import documents into MongoDB for subsequent searches, utilize the `ingest.py` script. It accepts PDF and RST file formats. Alternatively, extract the contents of [ohmyaws.documents.json.zip](ohmyaws.documents.json.zip) for JSON data. For assistance and to view available options, employ the `-h` command.

```bash
python ingest.py -h
```

Example of ingesting a RTS document:

```bash
python ingest.py --loader_type rst --fname boto3/docs/source/guide/clients.rst
```

Example of ingesting a PDF document:

```bash
python ingest.py --loader_type pdf --fname boto3/docs/source/guide/clients.pdf
```

Example of ingesting folder of RST documents:

```bash
python wrapper.py boto3  # Ingests all RST files in the boto3 folder
```

### Querying

After ingesting documents, you can query the database using natural language questions through the `main.py` script:

```bash
python main.py "What is boto3?"
```

The system retrieves relevant context from MongoDB and uses OpenAI's GPT models to generate a response based on the ingested documents.

## Troubleshooting

- **Dependency Warnings**: If you encounter warnings about deprecated classes, ensure you've installed the latest versions of `langchain` and `langchain-openai`. Use `pip list` to check installed versions and `pip install --upgrade package-name` to upgrade.

- **Execution Errors**: Ensure all environment variables in the `.env` file are correctly set. Verify MongoDB connectivity and that your OpenAI API key is valid.

For more detailed error resolutions, refer to the official `langchain` and `langchain-openai` documentation or the respective support forums.

## Contributing

Contributions to OhMyAWS are welcome! Please refer to the CONTRIBUTING.md file for guidelines on how to contribute to this project.
