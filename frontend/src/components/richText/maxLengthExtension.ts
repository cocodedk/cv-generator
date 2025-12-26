import { Extension } from '@tiptap/core'
import { Plugin } from 'prosemirror-state'

export const MaxLength = Extension.create<{ maxLength: number | null }>({
  name: 'maxLength',

  addOptions() {
    return { maxLength: null }
  },

  addProseMirrorPlugins() {
    if (!this.options.maxLength) return []
    const maxLength = this.options.maxLength

    return [
      new Plugin({
        filterTransaction: (transaction, state) => {
          if (!transaction.docChanged) return true

          const oldLen = state.doc.textBetween(0, state.doc.content.size, '\n', '\n').length
          const newState = state.apply(transaction)
          const newLen = newState.doc.textBetween(0, newState.doc.content.size, '\n', '\n').length

          if (newLen <= maxLength) return true
          return newLen <= oldLen
        },
      }),
    ]
  },
})
