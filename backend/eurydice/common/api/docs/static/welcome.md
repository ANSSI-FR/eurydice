# Disclaimer: this is an early access Alpha version of the software

This is version `{EURYDICE_VERSION}`, if you find a bug please report it to {EURYDICE_CONTACT}.

# Introduction

## 👋 Welcome to Eurydice, learn here how to transfer your files through a network diode.

Eurydice is a RESTful API that allows you to submit files and transfer them through a diode.
With Eurydice, you can send files from one end, retrieve them from the other, and track the progress of your transfers all along.

## 🏁 New here? Here is how to setup your account.

Eurydice consists of two RESTful APIs (one for each side of the diode).
Each physical user possesses two logical user accounts: one on the origin-side API, and one on the destination-side API.
If you do not have the credentials of both of your user accounts, please ask your system administrators to create them for you.

Once you can access both APIs with their respective account, you will need to link those two accounts.
Indeed, they are initially distinct and linking them will allow you to see on the destination the files you sent from the origin.

Here is how you should proceed:

- First, on the origin-side API (where you send files), you need to generate an association token.
  This is done with the endpoint `GET /api/v1/user/association/`, which is documented in the origin documentation (you can click _Account management_ and then _Link two user accounts_ on the left-hand side of the page to jump to it).
- On the destination-side API (where you retrieve files), you need to add this association token (by manually typing it).
  This is done with the endpoint `POST /api/v1/user/association/`, which is documented in the destination documentation (you can click _Account management_ and then _Link two user accounts_ on the left-hand side of the page to jump to it).

Congratulations! You're now able to transfer files using Eurydice!

## ⚙️ How to use code snippets from this documentation?

The right-side of this documentation contains some code snippets to use the API from the command line.

For these code snippets to work, you need to setup two environment variables beforehand:

```bash
export EURYDICE_{EURYDICE_API}_HOST={EURYDICE_HOST}
 export EURYDICE_{EURYDICE_API}_AUTHTOKEN=yourAuthenticationTokenHere
```

Please note the space before the second export if you do not want your API authentication token to be saved in your shell history.

## 💽 Versioning

This instance is running Eurydice version `{EURYDICE_VERSION}`, you can view [the full changelog here](https://github.com/ANSSI-FR/eurydice/releases).

Please note that the API specification is versioned differently from the application itself (the specification's version number is at the top of this page).
