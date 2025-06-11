# Frontend Eurydice

## Install

### Developer dependencies

This command will install all developer dependencies:

```bash
make install-dev 
```

## Lint the code

If you want to lint and fix fixeable lint errors, you can launch this command:

```bash
make lint-fix
```

OR

```bash
make lint
```

If you only want to check the lint errors (in CI for example):

```bash
make lint-check
```

## Format the code

If you want to fix the format of all files :

```bash
make format-fix
```

OR

```bash
make format
```

If you want to check the format of all files (for example in CI):

```bash
make format-check
```

## Test

To run unit and component tests run:

```bash
make tests
```

TODO: playwright

## Build the frontend

```bash
make build
```

## Launch the frontend alone

**Note:** If you want to run the frontend alone locally you can use the following commands. Otherwise you should use the method described in the [developper.md](../docs/developers.md) guide.

If you are developing the app, you can run the following command:

```bash
make run-watch
```

The app runs on 0.0.0.0:8080, watch for changes in code and reload the page automatically.
⚠️ The port is fixed and the app crashes if you are running on different ports. ⚠️

If you want to preview the built application, you can run the app in preview mode.

```bash
make run-preview
```

This command builds the app and launch a static website server to serve your app.
