import store from "@common/store";
import axiosClient, {
  responseInterceptorIndex,
  setUsernameResponseInterceptorIndex,
} from "@common/utils/request";
import Vue from "vue";

describe("setUsernameResponseInterceptor", () => {
  const setUsernameResponseInterceptor =
    axiosClient.interceptors.response.handlers[
      setUsernameResponseInterceptorIndex
    ];

  test.each`
    headers                                   | expectedCallValue
    ${{ "authenticated-user": "billmurray" }} | ${"billmurray"}
    ${{}}                                     | ${null}
    ${{ "authenticated-user": "" }}           | ${null}
  `(
    "updates store with username '$expectedCallValue' from successful response header '$headers'",
    ({ headers, expectedCallValue }) => {
      const axiosResponse = {
        headers,
      };
      store.commit = jest.fn();

      setUsernameResponseInterceptor.fulfilled(axiosResponse);

      expect(store.commit).toHaveBeenCalledWith(
        "setUsername",
        expectedCallValue
      );
    }
  );

  test("updates store with username from error response header", () => {
    const username = "billmurray";
    const axiosError = {
      response: {
        headers: { "authenticated-user": username },
      },
      message: "MSG_123456789", // expect(...).toThrow(x) uses `x.message` for equality
    };
    store.commit = jest.fn();

    const axiosInterceptor = () => {
      setUsernameResponseInterceptor.rejected(axiosError);
    };

    expect(axiosInterceptor).toThrow(axiosError);
    expect(store.commit).toHaveBeenCalledWith("setUsername", username);
  });

  test("skips updating store with username from response when no response", () => {
    const axiosError = {
      message: "MSG_123456789", // expect(...).toThrow(x) uses `x.message` for equality
    };
    store.commit = jest.fn();

    const axiosInterceptor = () => {
      setUsernameResponseInterceptor.rejected(axiosError);
    };

    expect(axiosInterceptor).toThrow(axiosError);
    expect(store.commit).not.toHaveBeenCalled();
  });
});

describe("responseInterceptor", () => {
  const responseInterceptor =
    axiosClient.interceptors.response.handlers[responseInterceptorIndex];

  test.each`
    response           | expectedAlertMessage                        | expectAlertToHaveBeenCalled
    ${{ status: 404 }} | ${"Cette ressource n'existe pas."}          | ${true}
    ${{ status: 500 }} | ${"Une erreur serveur est survenue."}       | ${true}
    ${{ status: 400 }} | ${"Cette erreur ne passera pas par $alert"} | ${false}
  `(
    "raises '$expectedAlertMessage' when given response '$response'",
    ({ response, expectedAlertMessage, expectAlertToHaveBeenCalled }) => {
      Vue.prototype.$alert = jest.fn();
      const axiosError = {
        response,
        message: "MSG_123456789", // expect(...).toThrow(x) uses `x.message` for equality
      };
      const axiosInterceptor = () => {
        responseInterceptor.rejected(axiosError);
      };

      expect(axiosInterceptor).toThrow(axiosError);
      if (expectAlertToHaveBeenCalled) {
        expect(Vue.prototype.$alert).toHaveBeenCalledWith(
          expectedAlertMessage,
          "error",
          expect.anything()
        );
      } else {
        expect(Vue.prototype.$alert).not.toHaveBeenCalled();
      }
    }
  );

  test("correctly handles errors without an HTTP response", () => {
    Vue.prototype.$alert = jest.fn();
    const axiosError = {
      message:
        "Evil breaks its chains and runs through the world like a mad dog.",
    };
    const axiosInterceptor = () => {
      responseInterceptor.rejected(axiosError);
    };

    expect(axiosInterceptor).toThrow(axiosError);
    expect(Vue.prototype.$alert).toHaveBeenCalledWith(
      axiosError.message,
      "error",
      expect.anything()
    );
  });

  test("correctly gets session cookie after a 401 error", async () => {
    const axiosError = {
      response: { status: 401 },
      config:
        "Evil breaks its chains and runs through the world like a mad dog.",
    };

    const fullfilledResponse =
      "I'm Worried I Fucked With Your Gender Expression";

    axiosClient.request = jest.fn().mockResolvedValue(fullfilledResponse);

    const requestRetryData = await responseInterceptor.rejected(axiosError);

    // expect original request to be fullfilled after retry
    expect(requestRetryData).toBe(fullfilledResponse);

    expect(axiosClient.request).toHaveBeenCalledTimes(2);
    // expect initial login attempt
    expect(axiosClient.request).toHaveBeenNthCalledWith(1, "/user/login/");
    // expect subsequent retry of original request
    expect(axiosClient.request).toHaveBeenNthCalledWith(2, axiosError.config);
  });

  test("notifies errors when getting session cookie after a 401 error", async () => {
    const axiosError = {
      response: { status: 401 },
      config:
        "Evil breaks its chains and runs through the world like a mad dog.",
    };
    const rejectedResponse = {
      message: "That's Not A Kid, That's My Business Partner",
    };

    Vue.prototype.$alert = jest.fn();
    axiosClient.request = jest.fn().mockRejectedValue(rejectedResponse);

    await responseInterceptor.rejected(axiosError);

    // expect a login attempt
    expect(axiosClient.request).toHaveBeenCalledTimes(1);
    expect(axiosClient.request).toHaveBeenCalledWith("/user/login/");
    // expect returned error to have been logged
    expect(Vue.prototype.$alert).toHaveBeenCalledWith(
      rejectedResponse.message,
      "error",
      expect.anything()
    );
  });
});
