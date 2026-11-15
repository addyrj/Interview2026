// Expo SDK 52 (check current docs - APIs change between SDKs)
// Pure logic: offline queue of pending actions. Storage is injected so it can be tested without a device.
// In the app pass AsyncStorage (@react-native-async-storage/async-storage).
const KEY = 'pending_actions'; // storage key

export function createSyncQueue(storage, sendToServer) {
  // read queue from disk
  const read = async () => JSON.parse((await storage.getItem(KEY)) || '[]');
  // write queue to disk
  const write = (q) => storage.setItem(KEY, JSON.stringify(q));

  return {
    read, // expose for UI (pending count)
    async enqueue(action) { // add action while offline
      const q = await read(); // current queue
      q.push({ ...action, id: action.id || String(Date.now()) + Math.random() }); // unique id
      await write(q); // persist (survives app kill)
    },
    async flush() { // call when internet returns
      const q = await read(); // all pending
      const remaining = []; // failed ones
      for (const action of q) { // keep ORDER: one by one
        try {
          await sendToServer(action); // retry send (server must be idempotent via action.id)
        } catch (e) {
          remaining.push(action); // keep for next time
        }
      }
      await write(remaining); // save leftovers
      return { sent: q.length - remaining.length, failed: remaining.length }; // report
    },
  };
}
