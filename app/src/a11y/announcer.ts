export type AnnounceChannel = 'alerts' | 'status'
export type AnnounceHandler = (text: string, channel?: AnnounceChannel) => void

let handler: AnnounceHandler = () => {}

export function setAnnouncer(next: AnnounceHandler) {
  handler = next
}

export function announce(text: string, channel: AnnounceChannel = 'status') {
  handler(text, channel)
}
