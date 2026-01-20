export default class SodiumTools {
  /*
    Class to use Sodium for encrypting files from the browser with libsodium-wrapper.
    Create a new instance for everyfile, so that the state and header are different
  */
  static sodiumInstance: any;
  static pubKey: any;

  symKey: any;
  state: any;
  header: any;

  constructor(sodium: any = null, encodedPublicKey: string | null = null) {
    if (!SodiumTools.sodiumInstance) {
      if (sodium && encodedPublicKey) {
        SodiumTools.sodiumInstance = sodium;
        SodiumTools.pubKey = this.getPublicKey(encodedPublicKey);
      } else {
        throw new Error(
          'Sodium instance and encoded public key are required for the first initialization.',
        );
      }
    }
    this.initState();
  }

  initState() {
    this.symKey = this.initSymmetricalKey();
    const res = SodiumTools.sodiumInstance.crypto_secretstream_xchacha20poly1305_init_push(
      this.symKey,
    );
    this.state = res.state;
    this.header = res.header;
  }

  initSymmetricalKey() {
    return SodiumTools.sodiumInstance.crypto_secretstream_xchacha20poly1305_keygen();
  }

  getPublicKey(encodedKey: string) {
    const pubkeyDecoded = atob(encodedKey);
    const decodedPubkeyBytes = new Uint8Array(pubkeyDecoded.length);
    for (let i = 0; i < pubkeyDecoded.length; i++) {
      decodedPubkeyBytes[i] = pubkeyDecoded.charCodeAt(i);
    }

    return decodedPubkeyBytes;
  }

  encryptDataSymmetrical(data: Uint8Array) {
    const encryptedData = SodiumTools.sodiumInstance.crypto_secretstream_xchacha20poly1305_push(
      this.state,
      data,
      null,
      SodiumTools.sodiumInstance.crypto_secretstream_xchacha20poly1305_TAG_MESSAGE,
    );
    return encryptedData;
  }

  decryptDataSymmetrical(encryptedData: ArrayBuffer) {
    const state_in = SodiumTools.sodiumInstance.crypto_secretstream_xchacha20poly1305_init_pull(
      this.header,
      this.symKey,
    );
    const r1 = SodiumTools.sodiumInstance.crypto_secretstream_xchacha20poly1305_pull(
      state_in,
      encryptedData,
    );
    const msg = SodiumTools.sodiumInstance.to_string(r1.message);
    return msg;
  }

  async encryptDataAsymmetrical(data: ArrayBuffer) {
    return SodiumTools.sodiumInstance.crypto_box_seal(data, SodiumTools.pubKey);
  }

  async getEncryptedSymKey() {
    return await this.encryptDataAsymmetrical(this.symKey);
  }
}
