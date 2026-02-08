type TxStatus = "pending" | "success" | "failed"

export type TxEntry = {
  txId: string
  createdAt: number
  status: TxStatus
  error?: string
  payload: any
}

type Listener = (entries: TxEntry[]) => void

export class TxLog {
  private entries: TxEntry[] = []
  private listeners: Listener[] = []

  subscribe(fn: Listener) {
    this.listeners.push(fn)
    fn(this.entries.slice())
    return () => {
      this.listeners = this.listeners.filter(l => l !== fn)
    }
  }

  private notify() {
    const copy = this.entries.slice()
    this.listeners.forEach(l => l(copy))
  }

  add(payload: any): TxEntry {
    const txId = `tx_${Date.now()}_${Math.floor(Math.random() * 1e6)}`
    const entry: TxEntry = { txId, createdAt: Date.now(), status: "pending", payload }
    this.entries.unshift(entry)
    this.notify()
    return entry
  }

  markSuccess(txId: string) {
    const e = this.entries.find(x => x.txId === txId)
    if (e) {
      e.status = "success"
      this.notify()
    }
  }

  markFailed(txId: string, error?: string) {
    const e = this.entries.find(x => x.txId === txId)
    if (e) {
      e.status = "failed"
      e.error = error
      this.notify()
    }
  }

  getAll(): TxEntry[] {
    return this.entries.slice()
  }
}

export const txLog = new TxLog()
