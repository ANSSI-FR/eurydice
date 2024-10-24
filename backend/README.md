# 🖥️ Eurydice backend

## 👪 Populate database

In the developement environment, you can populate the database on the origin and the destination side with the following commands:

```bash
docker exec eurydice-backend-origin-1 python manage.py populate_db
docker exec eurydice-backend-destination-1 python manage.py populate_db
```

You can customize the population scripts with arguments which you can list using `--help`.

## 👮‍♀️ Code formatting

Access the shell of the application container.

```bash
docker compose exec backend-origin sh
```

Once in the container, you can access the project files. The directory of the project is by default mounted at the location `/home/eurydice`.

The code must be formatted with [Black](https://black.readthedocs.io/en/stable/) and [isort](https://github.com/timothycrosley/isort).

```bash
make format
```

To check that the code is properly formatted, run the following commands:

```bash
make black-check
make isort-check
```

## 🔎 Static analysis

[Flake8](http://flake8.pycqa.org/en/latest/) is the _linter_ integrated in the project. Run it with the command below:

```bash
make flake8
```

[MyPy](http://mypy-lang.org/) and [Pytype](https://google.github.io/pytype/) are used to check the typing of the code.

```bash
make mypy
make pytype
```

[Bandit](https://bandit.readthedocs.io/en/latest/) and [Safety](https://github.com/pyupio/safety) allow to analyze respectively the security of the code and the security of the dependencies.

```bash
make bandit
make safety
```

All tools to check code quality (Flake8, MyPy, Pytype, Bandit, Safety, Isort, and Black) can be launched with a single command.

```bash
make checks
```

## 🧪 Testing

Unit tests are performed with [Pytest](https://docs.pytest.org/en/latest/).
The coverage of the tests is measured with [Coverage.py](https://coverage.readthedocs.io/en/coverage-5.0.3/).

Run the tests with the following command:

```bash
make tests
```

## ⚙️ Configuration

### 📚 Principles

The method adopted to configure the application according to the execution environment is inspired by [The Twelve-Factor App](https://12factor.net/config) and [Two Scoops of Django 1.11: Best Practices for the Django Web Framework](https://www.roygreenfeld.com/) :

- the preferred method for configuration is the use of environment variables.
- when the use of environment variables would make things too complex, it is possible to define configuration items in the
  appropriate `eurydice/(common|origin|destination)/settings/*.py` file.

### 🥼 Environments

The base environment is the production environment. The test and development environments are configured from the base environment by adding configuration items.

In development and testing, it is necessary to set the value of the environment variable `DJANGO_ENV`.

| **Environment** | **DJANGO_ENV** | **Description**                                                            | **Settings file** |
| --------------- | -------------- | -------------------------------------------------------------------------- | ----------------- |
| Base            | /              | Corresponds to the production environment.                                 | base.py           |
| Development     | DEV            | Corresponds to the environment used by the developer locally.              | dev.py            |
| Test            | TEST           | Corresponds to the environment used to perform the tests (used by the CI). | test.py           |
