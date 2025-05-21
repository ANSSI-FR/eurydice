import { transferableListResponseMock } from '@tests/mocks/transferableListResponse.mock';
import { http, HttpResponse } from 'msw';

const API_URL = import.meta.env.VITE_API_URL ?? '/api/v1';

export const handlers = [
  http.get(API_URL + '/metadata/', () => {
    return HttpResponse.json({
      contact: 'contacting the testing team',
      badge_color: '#00FF00',
      badge_content: 'badgeContent',
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
];
