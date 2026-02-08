export type PatchOp = {
  op: "add" | "remove" | "replace"
  path: string
  value?: any
  prev?: any
}

export function applyPatch(obj: any, ops: PatchOp[]): any {
  const root = JSON.parse(JSON.stringify(obj))
  for (const op of ops) {
    const keys = op.path.replace(/^\//, "").split("/")
    let target = root
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i]
      if (!(k in target)) target[k] = {}
      target = target[k]
    }
    const last = keys[keys.length - 1]
    if (op.op === "add" || op.op === "replace") {
      target[last] = op.value
    } else if (op.op === "remove") {
      delete target[last]
    }
  }
  return root
}

export function inversePatch(obj: any, ops: PatchOp[]): PatchOp[] {
  const inverses: PatchOp[] = []
  for (const op of ops) {
    const keys = op.path.replace(/^\//, "").split("/")
    let target = obj
    for (let i = 0; i < keys.length - 1; i++) {
      target = target[keys[i]] || {}
    }
    const last = keys[keys.length - 1]
    const current = target ? target[last] : undefined
    if (op.op === "add") {
      inverses.push({ op: "remove", path: op.path })
    } else if (op.op === "remove") {
      inverses.push({ op: "add", path: op.path, value: current })
    } else if (op.op === "replace") {
      inverses.push({ op: "replace", path: op.path, value: op.prev })
    }
  }
  return inverses
}
