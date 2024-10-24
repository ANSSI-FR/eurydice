import { postAssociationToken } from "@destination/api/association";
import UserAssociation from "@destination/views/UserAssociation";
import { createLocalVue, mount } from "@vue/test-utils";
import Vuetify from "vuetify";

jest.mock("@destination/api/association", () => ({
  postAssociationToken: jest.fn(() => Promise.resolve("")),
}));
jest.mock("@destination/settings", () => ({
  associationTokenWordCount: 2,
}));

describe("UserAssociation", () => {
  const localVue = createLocalVue();
  const vuetify = new Vuetify();
  let wrapper;
  let div;

  beforeEach(() => {
    div = document.createElement("div");
    div.id = "root";
    document.body.appendChild(div);
    wrapper = mount(UserAssociation, {
      localVue,
      vuetify,
      attachTo: "#root",
    });
  });

  afterEach(() => {
    wrapper.destroy();
  });

  it.each`
    data                                                                    | submitButtonDisabled
    ${{ token: "an invalid token" }}                                        | ${true}
    ${{ token: "valid token" }}                                             | ${false}
    ${{ token: "valid token", tokenSubmissionErrorMessages: ["An error"] }} | ${true}
    ${{ token: "invalid token1" }}                                          | ${true}
  `(
    "has a submit button with disabled=$submitButtonDisabled when data is $data",
    async ({ data, submitButtonDisabled }) => {
      const submitButton = wrapper.find("#UserAssociation-SubmitButton");
      expect(submitButton.element.disabled).toBe(true);
      await wrapper.setData(data);
      await wrapper.vm.$nextTick();

      expect(submitButton.element.disabled).toBe(submitButtonDisabled);
    }
  );

  it.each`
    tokenSubmissionSuccess | submitButtonShown | continueButtonShown | textAreaClearable | textAreaReadOnlyAttr
    ${true}                | ${false}          | ${true}             | ${false}          | ${"readonly"}
    ${null}                | ${true}           | ${false}            | ${true}           | ${undefined}
    ${false}               | ${true}           | ${false}            | ${true}           | ${undefined}
  `(
    "displays correctly when tokenSubmissionSuccess is $tokenSubmissionSuccess",
    async ({
      tokenSubmissionSuccess,
      submitButtonShown,
      continueButtonShown,
      textAreaClearable,
      textAreaReadOnlyAttr,
    }) => {
      await wrapper.setData({ tokenSubmissionSuccess });
      await wrapper.vm.$nextTick();

      const submitButton = wrapper.find("#UserAssociation-SubmitButton");
      expect(submitButton.exists()).toBe(submitButtonShown);

      const continueButton = wrapper.find("#UserAssociation-ContinueButton");
      expect(continueButton.exists()).toBe(continueButtonShown);

      const textArea = wrapper.find("#UserAssociation-TextArea");
      expect(textArea.attributes().readonly).toBe(textAreaReadOnlyAttr);

      await wrapper.setData({ token: "this is the way" });
      const clearIcon = wrapper.find(".v-input__icon--clear");
      expect(clearIcon.exists()).toBe(textAreaClearable);
    }
  );

  it.each`
    token                  | valid
    ${""}                  | ${false}
    ${"word"}              | ${false}
    ${"two words"}         | ${true}
    ${"una fruta popular"} | ${false}
    ${"2 words"}           | ${false}
    ${"two words!"}        | ${false}
  `(
    "Given a token '$token' its validity should be $valid",
    async ({ token, valid }) => {
      await wrapper.setData({
        token,
      });
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.tokenIsValid).toBe(valid);
    }
  );

  it.each`
    token
    ${"valid token"}
    ${"an invalid token"}
    ${"invalid token2"}
  `("form behaves correctly with $token", async ({ token }) => {
    const submitButton = wrapper.find("#UserAssociation-SubmitButton");
    // the submit button should exist but be disabled
    expect(submitButton.element.disabled).toBe(true);
    // while the continue button should not exist
    expect(wrapper.find("#UserAssociation-ContinueButton").exists()).toBe(
      false
    );
    expect(wrapper.element).toMatchSnapshot("no token inputted");

    const textArea = wrapper.find("#UserAssociation-TextArea");
    await textArea.setValue(token);
    await wrapper.vm.$nextTick();

    // the submit button should only be disabled when the token is invalid
    expect(submitButton.element.disabled).toBe(!wrapper.vm.tokenIsValid);
    expect(wrapper.element).toMatchSnapshot("token inputted");

    submitButton.trigger("click");
    await wrapper.vm.$nextTick();

    expect(wrapper.element).toMatchSnapshot("token is submitting");

    await wrapper.vm.$nextTick();

    // the submit button will be replaced by the continue button only
    // when the token is successfully submitted
    // NOTE: we have to wrapper.find the button again because
    //       its existence might have change
    expect(wrapper.find("#UserAssociation-SubmitButton").exists()).toBe(
      !wrapper.vm.tokenIsValid
    );
    expect(wrapper.find("#UserAssociation-ContinueButton").exists()).toBe(
      wrapper.vm.tokenIsValid
    );
    expect(wrapper.element).toMatchSnapshot("token submitted");

    wrapper.destroy();
  });

  it("form correctly displays API error", async () => {
    const errorMessage =
      "Nous ne pouvons pas aider un peuple qui ne veut pas s'aider lui-même";
    postAssociationToken.mockImplementationOnce(
      jest.fn(() => {
        const error = Error();
        error.response = { data: { error: errorMessage } };
        throw error;
      })
    );

    const textArea = wrapper.find("#UserAssociation-TextArea");
    await textArea.setValue("a token");
    // the token should be inputted with the submit button disabled
    await wrapper.vm.$nextTick();

    const submitButton = wrapper.find("#UserAssociation-SubmitButton");
    submitButton.trigger("click");

    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    const formMessages = wrapper.findAll(".v-messages__message");

    expect(formMessages.length).toBe(1);
    expect(formMessages.at(0).text()).toEqual(errorMessage);

    // the error message should be displayed
    expect(wrapper.element).toMatchSnapshot(
      "token submitted and error is displayed"
    );

    wrapper.destroy();
  });
});
