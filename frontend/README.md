# ✨ Eurydice frontend

## 🧪 Testing

Unit tests are performed with [Jest](https://jestjs.io/).

Run the tests with the following command:

```bash
make tests
```

## 👮‍♀️ Code formatting and 🔎 Static analysis

[ESLint](https://eslint.org/) is the project's linter.
The [Prettier](https://prettier.io/) formatter is integrated in the linter.
You can Launch them with the following command:

```bash
make lint
```

To automatically fix errors detected by the linter, use the following command:

```bash
make lint-fix
```

CSS, SCSS, YAML, JSON and Markdown files can be formatted with the following command:

```bash
make format
```
