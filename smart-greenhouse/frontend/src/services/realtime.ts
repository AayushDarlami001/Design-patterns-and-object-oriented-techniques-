export type RealtimeEvent = {
  type: string;
  payload: unknown;
};

export function subscribeRealtime(
  _handler: (event: RealtimeEvent) => void,
): () => void {
  // Phase 12 will replace this no-op
  // implementation with the dashboard WebSocket.
  return () => {};
}