# Law Reading Robot: Data
Runs the ETL layer that extracts relevant information from RSS feeds and GPT4 API
Houses supabase configuration, database schemas, and server functions

## Getting Started

### Requirements
* Python 3.11
* Windows Users
    * py launcher (Should be auto-installed alongside python 3.11)

### Initial Setup
* Windows Users
    * `.\setup.bat`
* Mac and Linux Users
    * `chmod +x ./configure`
    * `./configure`

### Convenience Scripts
* Windows Users
    * `.\__python.bat` - Runs any script within the Pipenv environment
    * `.\__pipenv.bat` - Runs pipenv with python 3.11
* Mac and Linux Users
    * `./__python` - Runs any script within the pipenv environment
    * `./__pipenv` - Runs pipenv with python 3.11

### Linting and Formatting

Formatter: "black"

Linters: "pylint", "flake8"

* Windows Users
    * `.\__python.bat -m black <OPTIONS>`
    * `.\__python.bat -m pylint <OPTIONS>`
    * `.\__python.bat -m flake8 <OPTIONS>`
* Mac and Linux Users
    * `./__python -m black <OPTIONS>`
    * `./__python -m pylint <OPTIONS>`
    * `./__python -m flake8 <OPTIONS>`

### Using Supabase With Docker
@todo

### Guidelines for Contribution
@todo

