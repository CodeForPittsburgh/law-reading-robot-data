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
    * run `setup.bat`
* Mac and Linux Users
    * `chmod +x ./configure`
    * `./configure`

### Convenience Scripts
* Windows Users
    * `.\__python.bat` - Runs any script within the Pipenv environment
    * `.\__pipenv.bat` - Runs pipenv with python 3.11
    * `.\__flake8.bat` - Runs flake8 with python 3.11
    * `.\__pylint.bat` - Runs pylint with python 3.11
    * `.\__black.bat` - Runs black with python 3.11
* Mac and Linux Users
    * `./__python` - Runs any script within the pipenv environment
    * `./__pipenv` - Runs pipenv with python 3.11
    * `./__flake8` - Runs flake8 with python 3.11
    * `./__pylint` - Runs pylint with python 3.11
    * `./__black` - Runs black with python 3.11

### Using Supabase With Docker
@todo

### Guidelines for Contribution

