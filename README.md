# 🤑 Solomon

[![Build Status](https://github.com/daniel-leal/solomon-api/actions/workflows/ci.yml/badge.svg)](https://github.com/daniel-leal/solomon-api/actions)
[![Coverage Status](https://coveralls.io/repos/github/daniel-leal/solomon-api/badge.svg?branch=main)](https://coveralls.io/github/daniel-leal/solomon-api?branch=main)

Solomon is a personal finance application designed to help you manage your finances effectively.

## 📚 Documentation

The `/docs` folder contains detailed documentation about the different aspects of the project.

### Transaction Definition and Rules

A transaction in Solomon represents a single instance of money exchange. It could be income, expense, or transfer. For a detailed explanation of the definition and rules of a transaction, please refer to the [Transaction Documentation](./docs/use_cases/transaction.md).

For more details about other aspects of the project, please refer to the `/docs` folder.

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### 🗒️ Prerequisites

- 🐍 Python 3.11
- 🐳 Docker / Docker Compose
- 🐘 PostgresSQL 12.1

### 🐳 Running the Project Locally with docker

1. Clone the repository:

```sh
git clone https://github.com/daniel-leal/solomon-api
```

2. Naviagate to the project directory

```sh
cd solomon-api
```

3. Build the docker
```sh
make docker-build
```

4. Run the docker application
```sh
make docker-up
```

### 🐍 If you want to run locally:

1. Create virtual env

```sh
python -m venv .venv
```

2. Activate virtual env

```sh
source .venv/bin/activate
```

3. Run the application

```sh
make run-local
```


The application will be available at (http://localhost:8000).


### ✅ Running the Tests

To run the tests, use the following command:

```sh
make test
```

To generate a coverage report use the following command:

```sh
make test-coverage
```

### ⚙️ Migrations
- Running migrations
```sh
make migrate
```

- Create migration
```sh
make migration name="<name of migration>"
```

- Rollback latest migration
```sh
make rollback
```

### Contributing
Please read CONTRIBUTING.md for details on our code of conduct, and the process
of submitting pull requests to us.

### License
This project is licensed under the MIT License - see the LICENSE.md file for details
