import apiClient from '@common/api/api-client';
import { useServerStatusStore } from '@common/store/server-status.store';

export const getStatus = async (params = {}): Promise<StatusOrigin | StatusDestination> => {
  return apiClient.get('/status/', params);
};

export const refreshServerStatus = async () => {
  const serverStatusStore = useServerStatusStore();
  const status = await getStatus();
  if (status) {
    if ('maintenance' in status) {
      serverStatusStore.setIsServerInMaintenance(status.maintenance);
    }
    const lastPacketDate =
      'lastPacketReceivedAt' in status ? status.lastPacketReceivedAt : status.lastPacketSentAt;
    const lastPacketTimestamp: number = !Number.isNaN(Date.parse(lastPacketDate))
      ? Date.parse(lastPacketDate)
      : 0;
    const timeSinceLastPacketInMs = Date.now() - lastPacketTimestamp;
    const serverDownIntervalInMs = import.meta.env.VITE_SERVER_DOWN_INTERVAL_IN_MS ?? 180000;
    serverStatusStore.setIsServerDown(timeSinceLastPacketInMs > serverDownIntervalInMs);
  }
};
