# 🤑 Solomon

Solomon is a personal finance application designed to help you manage your finances effectively.

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### 🗒️ Prerequisites

- Python 3.11
- Docker
- Docker Compose

### 🐳 Running the Project Locally with docker

1. Clone the repository:

```sh
git clone <repository_url>
```

2. Naviagate to the project directory

```sh
cd <project_directory>
```

3. Create virtual env

```sh
python -m venv .venv
```

4. Activate virtual env
```sh
source .venv/bin/activate
```

5. Build the docker
```sh
make docker-build
```

6. Run the docker application
```sh
make docker-up
```


7. Run the migrations
```sh
make migrate
```

The application will be available at (http://localhost:8000).


If you want to run locally:

```sh
make run-local
```


### ✅ Running the Tests

To run the tests, use the following command:

```sh
make test
```

To generate a coverage report use the following command:

```sh
make test-coverage
```

### ⚙️ Generate Migrations

```sh
make migration name="<name of migration>"
```

### Contributing
Please read CONTRIBUTING.md for details on our code of conduct, and the process
of submitting pull requests to us.

### License
This project is licensed under the MIT License - see the LICENSE.md file for details
