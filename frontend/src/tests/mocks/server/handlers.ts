import { transferableListResponseMock } from '@tests/mocks/transferableListResponse.mock';
import { http, HttpResponse } from 'msw';

const API_URL = import.meta.env.VITE_API_URL ?? '/api/v1';

export const handlers = [
  http.get(API_URL + '/metadata/', () => {
    return HttpResponse.json({
      contact: 'contacting the testing team',
      badge_color: '#00FF00',
      badge_content: 'badgeContent',
      encryptionEnabled: false,
      encodedPublicKey: 'gtC32LH1n6qCbkqQog/QwAr7TjxuED2+85o1CRlSl2Y=',
    });
  }),
  http.get(API_URL + '/status/', () => {
    return HttpResponse.json({
      maintenance: false,
      last_packet_sent_at: new Date(Date.now()).toUTCString(),
    });
  }),
  http.get(API_URL + '/user/association/', () => {
    return HttpResponse.json({
      expires_at: Date.now(),
      token: 'test token PHRASE',
    });
  }),
  http.get(API_URL + '/transferables/', () => {
    return HttpResponse.json(transferableListResponseMock);
  }),
  http.post(API_URL + '/user/association/', () => {
    return new HttpResponse('', { status: 204 });
  }),
  http.get(API_URL + '/transferables/*/download/', () => {
    return new HttpResponse('test content');
  }),
  // Encryption routes
  http.post(API_URL + '/transferables/init-multipart-upload/', () => {
    return HttpResponse.json({
      id: '1',
      filename: 'testFile',
      partSize: 5 * 1024 * 1024,
    });
  }),
  http.post<{ id: string }>(API_URL + '/transferables/:id/file-part/', () => {
    return new HttpResponse();
  }),
  http.get<{ id: string }>(API_URL + '/transferables/:id/finalize-multipart-upload/', () => {
    return new HttpResponse('created_transferable', { status: 201 });
  }),
];
